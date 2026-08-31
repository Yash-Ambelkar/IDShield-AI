import os
import gc
import cv2


# ==========================================================
# IDShield AI - LIGHTWEIGHT DOCUMENT PORTRAIT EXTRACTION
# ==========================================================
#
# Purpose:
#   Find and crop the portrait/photo inside an identity
#   document without using DeepFace or RetinaFace.
#
# Pipeline:
#
#   Identity Document
#          ↓
#   OpenCV Haar Cascade
#          ↓
#   Face candidates
#          ↓
#   Candidate filtering
#          ↓
#   Best portrait selection
#          ↓
#   Portrait crop
#          ↓
#   Save crop
#
#
# IMPORTANT:
#
# This module ONLY extracts the document portrait.
#
# It does NOT perform identity verification.
#
# Identity verification is handled by:
#
#     face/verifier.py
#
# ==========================================================


# ==========================================================
# CONFIGURATION
# ==========================================================

MIN_FACE_SIZE = 30

PADDING_RATIO = 0.25

# Minimum confidence is not available with Haar Cascade.
# Instead, candidates are scored using size, position,
# and detection quality.

# Reject a detection if it occupies almost the entire
# document.
MAX_DOCUMENT_AREA_RATIO = 0.75

# Prefer portrait boxes that are not extremely wide/tall.
MIN_FACE_ASPECT_RATIO = 0.35
MAX_FACE_ASPECT_RATIO = 1.80


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

def cleanup_memory():

    try:

        gc.collect()

    except Exception:

        pass


# ==========================================================
# VALIDATE DOCUMENT IMAGE
# ==========================================================

def validate_document_image(
    image_path
):

    if not image_path:

        return {
            "valid": False,
            "message": "Document image was not provided."
        }


    if not os.path.exists(
        image_path
    ):

        return {
            "valid": False,
            "message":
                f"Document image not found: {image_path}"
        }


    image = cv2.imread(
        image_path
    )


    if image is None:

        return {
            "valid": False,
            "message":
                "Document image could not be read."
        }


    height, width = image.shape[:2]


    del image

    cleanup_memory()


    if width < 100 or height < 100:

        return {
            "valid": False,
            "message":
                "Document image is too small."
        }


    return {

        "valid": True,

        "width": width,

        "height": height,

        "message":
            "Document image is valid."

    }


# ==========================================================
# LOAD OPENCV FACE DETECTOR
# ==========================================================

def load_face_detector():

    """
    Load OpenCV's built-in Haar Cascade.

    This does not download a large external model.
    """

    try:

        cascade_path = (

            cv2.data.haarcascades
            +
            "haarcascade_frontalface_default.xml"

        )


        detector = cv2.CascadeClassifier(
            cascade_path
        )


        if detector.empty():

            print(
                "\n❌ OpenCV Haar Cascade could not be loaded."
            )

            return None


        print(
            "\n✅ Lightweight OpenCV face detector loaded."
        )


        return detector


    except Exception as e:

        print(
            "\n❌ Failed to load OpenCV face detector:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# DETECT FACES
# ==========================================================

def detect_faces(
    image_path
):

    """
    Detect faces using OpenCV Haar Cascade.

    Returns:

        [
            {
                "x": ...,
                "y": ...,
                "w": ...,
                "h": ...,
                "confidence": ...
            }
        ]

    Haar Cascade does not provide a true confidence
    probability, so confidence is represented as a
    normalized heuristic score.
    """

    detector = load_face_detector()


    if detector is None:

        return []


    image = cv2.imread(
        image_path
    )


    if image is None:

        return []


    try:

        gray = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )


        # --------------------------------------------------
        # Improve contrast slightly
        # --------------------------------------------------

        gray = cv2.equalizeHist(
            gray
        )


        # --------------------------------------------------
        # Detect faces
        # --------------------------------------------------

        faces = detector.detectMultiScale(

            gray,

            scaleFactor=1.08,

            minNeighbors=5,

            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE)

        )


        detections = []


        image_height, image_width = image.shape[:2]


        document_area = (

            image_width *

            image_height

        )


        for (
            x,
            y,
            w,
            h
        ) in faces:

            face_area = (

                w *

                h

            )


            area_ratio = (

                face_area /

                document_area

            )


            # --------------------------------------------------
            # Heuristic confidence
            # --------------------------------------------------
            #
            # Haar does not expose a probability.
            #
            # We combine:
            #
            #   - face size
            #   - reasonable dimensions
            #   - detection area
            #
            # --------------------------------------------------

            size_score = min(

                1.0,

                max(

                    0.0,

                    area_ratio * 8

                )

            )


            aspect_ratio = (

                w /

                float(h)

            )


            aspect_score = 1.0


            if (

                aspect_ratio <
                MIN_FACE_ASPECT_RATIO

                or

                aspect_ratio >
                MAX_FACE_ASPECT_RATIO

            ):

                aspect_score = 0.3


            confidence = (

                0.65

                +

                (

                    size_score * 0.20

                )

                +

                (

                    aspect_score * 0.15

                )

            )


            confidence = min(

                0.99,

                confidence

            )


            detections.append({

                "x": int(x),

                "y": int(y),

                "w": int(w),

                "h": int(h),

                "confidence":
                    round(
                        confidence,
                        4
                    )

            })


        del gray
        del image

        cleanup_memory()


        return detections


    except Exception as e:

        print(
            "\n⚠️ OpenCV face detection failed:"
        )

        print(
            str(e)
        )


        try:

            del gray

        except Exception:

            pass


        try:

            del image

        except Exception:

            pass


        cleanup_memory()


        return []


# ==========================================================
# FILTER FACE CANDIDATES
# ==========================================================

def filter_face_candidates(
    detections,
    image_width,
    image_height
):

    candidates = []


    document_area = (

        image_width *

        image_height

    )


    for detection in detections:

        x = detection["x"]

        y = detection["y"]

        w = detection["w"]

        h = detection["h"]

        confidence = detection["confidence"]


        # ==================================================
        # SIZE CHECK
        # ==================================================

        if (

            w < MIN_FACE_SIZE

            or

            h < MIN_FACE_SIZE

        ):

            print(
                "⚠️ Rejected tiny face:",
                detection
            )

            continue


        # ==================================================
        # COORDINATE CHECK
        # ==================================================

        if x < 0 or y < 0:

            continue


        if (

            x >= image_width

            or

            y >= image_height

        ):

            continue


        # ==================================================
        # CLAMP
        # ==================================================

        x2 = min(

            x + w,

            image_width

        )


        y2 = min(

            y + h,

            image_height

        )


        w = x2 - x

        h = y2 - y


        if w <= 0 or h <= 0:

            continue


        # ==================================================
        # AREA RATIO
        # ==================================================

        face_area = (

            w *

            h

        )


        area_ratio = (

            face_area /

            document_area

        )


        # ==================================================
        # FULL DOCUMENT PROTECTION
        # ==================================================

        if (

            area_ratio >

            MAX_DOCUMENT_AREA_RATIO

        ):

            print(
                "⚠️ Rejected oversized detection:",
                detection
            )

            continue


        # ==================================================
        # ASPECT RATIO
        # ==================================================

        aspect_ratio = (

            w /

            float(h)

        )


        if (

            aspect_ratio < MIN_FACE_ASPECT_RATIO

            or

            aspect_ratio > MAX_FACE_ASPECT_RATIO

        ):

            print(
                "⚠️ Rejected unusual face shape:",
                detection
            )

            continue


        # ==================================================
        # STORE CANDIDATE
        # ==================================================

        candidates.append({

            "x": x,

            "y": y,

            "w": w,

            "h": h,

            "confidence":
                confidence,

            "area_ratio":
                area_ratio,

            "aspect_ratio":
                aspect_ratio

        })


    return candidates


# ==========================================================
# SELECT BEST FACE
# ==========================================================

def select_best_face(
    candidates,
    image_width,
    image_height
):

    if not candidates:

        return None


    # ------------------------------------------------------
    # Center of document
    # ------------------------------------------------------

    document_center_x = (
        image_width / 2
    )

    document_center_y = (
        image_height / 2
    )


    def score(
        candidate
    ):

        x = candidate["x"]

        y = candidate["y"]

        w = candidate["w"]

        h = candidate["h"]


        confidence = candidate[
            "confidence"
        ]


        area_ratio = candidate[
            "area_ratio"
        ]


        # ==================================================
        # FACE CENTER
        # ==================================================

        face_center_x = (
            x + w / 2
        )

        face_center_y = (
            y + h / 2
        )


        # ==================================================
        # DISTANCE FROM DOCUMENT CENTER
        # ==================================================

        dx = (

            face_center_x
            -
            document_center_x

        )


        dy = (

            face_center_y
            -
            document_center_y

        )


        max_distance = (

            (

                image_width ** 2

                +

                image_height ** 2

            )

            **

            0.5

        )


        distance = (

            (

                dx ** 2

                +

                dy ** 2

            )

            **

            0.5

        )


        center_score = max(

            0.0,

            1.0
            -
            (
                distance /
                max_distance
            )

        )


        # ==================================================
        # SIZE SCORE
        # ==================================================

        size_score = min(

            1.0,

            area_ratio * 8

        )


        # ==================================================
        # FINAL SCORE
        # ==================================================

        return (

            confidence * 0.55

            +

            center_score * 0.25

            +

            size_score * 0.20

        )


    candidates.sort(

        key=score,

        reverse=True

    )


    return candidates[0]


# ==========================================================
# CROP FACE
# ==========================================================

def crop_face(
    image,
    face
):

    height, width = image.shape[:2]


    x = face["x"]

    y = face["y"]

    w = face["w"]

    h = face["h"]


    # ======================================================
    # PADDING
    # ======================================================

    padding_x = int(

        w *

        PADDING_RATIO

    )


    padding_y = int(

        h *

        PADDING_RATIO

    )


    # ======================================================
    # CROP COORDINATES
    # ======================================================

    x1 = max(

        0,

        x - padding_x

    )


    y1 = max(

        0,

        y - padding_y

    )


    x2 = min(

        width,

        x + w + padding_x

    )


    y2 = min(

        height,

        y + h + padding_y

    )


    # ======================================================
    # CROP
    # ======================================================

    crop = image[

        y1:y2,

        x1:x2

    ]


    if crop is None:

        return None


    if crop.size == 0:

        return None


    return crop


# ==========================================================
# EXTRACT DOCUMENT PORTRAIT
# ==========================================================

def extract_document_face(
    document_path,
    output_path=None
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "IDSHIELD AI - LIGHTWEIGHT DOCUMENT PORTRAIT"
    )

    print(
        "=" * 60
    )


    # ======================================================
    # STEP 1 - VALIDATE
    # ======================================================

    validation = validate_document_image(

        document_path

    )


    if not validation["valid"]:

        print(
            "❌",
            validation["message"]
        )

        return {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                validation["message"]

        }


    # ======================================================
    # STEP 2 - LOAD DOCUMENT
    # ======================================================

    image = cv2.imread(

        document_path

    )


    if image is None:

        return {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                "Unable to load document image."

        }


    height, width = image.shape[:2]


    print(
        f"\n📄 Document size: "
        f"{width} x {height}"
    )


    # ======================================================
    # STEP 3 - DETECT
    # ======================================================

    print(
        "\n🔎 Detecting document portrait..."
    )


    detections = detect_faces(

        document_path

    )


    print(
        f"🔎 Raw detections: "
        f"{len(detections)}"
    )


    # ======================================================
    # STEP 4 - FILTER
    # ======================================================

    candidates = filter_face_candidates(

        detections,

        width,

        height

    )


    print(
        f"✅ Valid candidates: "
        f"{len(candidates)}"
    )


    # ======================================================
    # NO FACE
    # ======================================================

    if not candidates:

        del image

        cleanup_memory()


        return {

            "status":
                "REVIEW",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                (
                    "No reliable portrait could "
                    "be detected in the identity document."
                )

        }


    # ======================================================
    # STEP 5 - SELECT
    # ======================================================

    best_face = select_best_face(

        candidates,

        width,

        height

    )


    if best_face is None:

        del image

        cleanup_memory()


        return {

            "status":
                "REVIEW",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                "No reliable portrait candidate found."

        }


    print(
        "\n🎯 Selected document portrait:"
    )


    print(
        best_face
    )


    # ======================================================
    # STEP 6 - CROP
    # ======================================================

    face_crop = crop_face(

        image,

        best_face

    )


    if face_crop is None:

        del image

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                best_face["confidence"],

            "facial_area":
                best_face,

            "message":
                "Unable to crop detected portrait."

        }


    # ======================================================
    # STEP 7 - OUTPUT PATH
    # ======================================================

    if output_path is None:

        output_path = os.path.join(

            os.path.dirname(
                document_path
            ),

            "document_face_crop.jpg"

        )


    output_directory = os.path.dirname(

        output_path

    )


    if output_directory:

        os.makedirs(

            output_directory,

            exist_ok=True

        )


    # ======================================================
    # STEP 8 - SAVE
    # ======================================================

    success = cv2.imwrite(

        output_path,

        face_crop

    )


    if not success:

        del face_crop

        del image

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                best_face["confidence"],

            "facial_area":
                best_face,

            "message":
                "Unable to save portrait crop."

        }


    # ======================================================
    # DISPLAY
    # ======================================================

    try:

        crop_height, crop_width = (
            face_crop.shape[:2]
        )

        print(
            "\n📐 Portrait crop size: "
            f"{crop_width} x {crop_height}"
        )

    except Exception:

        pass


    print(
        "\n✅ Portrait crop saved:"
    )

    print(
        output_path
    )


    # ======================================================
    # CLEANUP
    # ======================================================

    del face_crop

    del image

    cleanup_memory()


    # ======================================================
    # FINAL RESULT
    # ======================================================

    return {

        "status":
            "FOUND",

        "face_found":
            True,

        "face_path":
            output_path,

        "confidence":
            round(

                best_face["confidence"],

                4

            ),

        "facial_area": {

            "x":
                best_face["x"],

            "y":
                best_face["y"],

            "w":
                best_face["w"],

            "h":
                best_face["h"]

        },

        "message":
            (
                "Identity document portrait "
                "detected successfully."
            )

    }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    test_document = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        "..",

        "ocr",

        "test_documents",

        "sample_document_with_face.jpg"

    )


    test_document = os.path.abspath(
        test_document
    )


    result = extract_document_face(

        test_document

    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL RESULT"
    )

    print(
        "=" * 60
    )

    print(
        result
    )

    print(
        "=" * 60
    )