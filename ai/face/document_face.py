import os
import gc
import cv2


# ==========================================================
# IDShield AI - DOCUMENT PORTRAIT EXTRACTION
# ==========================================================
#
# Purpose:
#   Find the portrait/photo inside an identity document.
#
#
# Pipeline:
#
#   Identity Document
#          ↓
#   RetinaFace
#          ↓
#   Face candidate detection
#          ↓
#   Candidate validation
#          ↓
#   Suspicious detection filtering
#          ↓
#   Select best portrait
#          ↓
#   Crop portrait
#          ↓
#   Save temporary face image
#
#
# IMPORTANT:
#
#   This module does NOT perform identity verification.
#
#   It only extracts the portrait from the document.
#
#
# Face verification is handled separately by:
#
#   face/verifier.py
#
# ==========================================================


# ==========================================================
# CONFIGURATION
# ==========================================================

# ----------------------------------------------------------
# Face detector
# ----------------------------------------------------------

DETECTOR_BACKEND = "retinaface"


# ----------------------------------------------------------
# Minimum detector confidence
# ----------------------------------------------------------

MIN_FACE_CONFIDENCE = 0.50


# ----------------------------------------------------------
# Minimum detected face dimensions
# ----------------------------------------------------------

MIN_FACE_SIZE = 40


# ----------------------------------------------------------
# Standard maximum area ratio
#
# Used for normal / larger documents.
# ----------------------------------------------------------

MAX_DOCUMENT_AREA_RATIO = 0.35


# ----------------------------------------------------------
# Maximum area ratio for small document images
#
# Small ID images can contain a portrait occupying a much
# larger percentage of the image.
#
# Example:
#
# Document:
#     160 x 203
#
# Detected portrait:
#     102 x 143
#
# Area ratio:
#     ~45%
#
# Therefore 35% is too strict for small images.
# ----------------------------------------------------------

SMALL_DOCUMENT_AREA_RATIO = 0.60


# ----------------------------------------------------------
# Small document threshold
#
# If either dimension is <= this value, the image is
# considered a small document image.
# ----------------------------------------------------------

SMALL_DOCUMENT_MAX_DIMENSION = 300


# ----------------------------------------------------------
# Extremely large detection protection
#
# Even for small documents, a face detector should not
# normally return almost the entire image as a face.
#
# Example:
#
#     95%+ of document area
#
# is considered suspicious.
# ----------------------------------------------------------

ABSOLUTE_MAX_DOCUMENT_AREA_RATIO = 0.85


# ----------------------------------------------------------
# Minimum face bounding-box aspect ratio
#
# Face boxes are generally taller than wide.
#
# This is intentionally permissive because document photos
# can be rotated, compressed, or distorted.
# ----------------------------------------------------------

MIN_FACE_ASPECT_RATIO = 0.35


# ----------------------------------------------------------
# Maximum face bounding-box aspect ratio
# ----------------------------------------------------------

MAX_FACE_ASPECT_RATIO = 1.80


# ----------------------------------------------------------
# Padding around detected face
# ----------------------------------------------------------

PADDING_RATIO = 0.25


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

def cleanup_memory():

    try:

        gc.collect()

    except Exception:

        pass


# ==========================================================
# VALIDATE IMAGE
# ==========================================================

def validate_document_image(
    image_path
):

    # ------------------------------------------------------
    # Path check
    # ------------------------------------------------------

    if not image_path:

        return {

            "valid":
                False,

            "message":
                "Document image was not provided."

        }


    # ------------------------------------------------------
    # File existence
    # ------------------------------------------------------

    if not os.path.exists(
        image_path
    ):

        return {

            "valid":
                False,

            "message":
                (
                    "Document image not found: "
                    f"{image_path}"
                )

        }


    # ------------------------------------------------------
    # Read image
    # ------------------------------------------------------

    image = cv2.imread(
        image_path
    )


    if image is None:

        return {

            "valid":
                False,

            "message":
                "Document image could not be read."

        }


    # ------------------------------------------------------
    # Image dimensions
    # ------------------------------------------------------

    height, width = image.shape[:2]


    del image

    cleanup_memory()


    # ------------------------------------------------------
    # Minimum resolution
    # ------------------------------------------------------

    if width < 100 or height < 100:

        return {

            "valid":
                False,

            "message":
                "Document image is too small."

        }


    return {

        "valid":
            True,

        "message":
            "Document image is valid."

    }


# ==========================================================
# LOAD DEEPFACE
# ==========================================================

def load_deepface():

    try:

        from deepface import DeepFace

        return DeepFace

    except Exception as e:

        print(
            "\n❌ Unable to load DeepFace:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# DETECT FACES IN IMAGE
# ==========================================================

def detect_faces(
    image_path
):

    """
    Detect faces using RetinaFace.

    Returns a list of dictionaries containing:

        x
        y
        w
        h
        confidence
    """


    DeepFace = load_deepface()


    if DeepFace is None:

        return []


    try:

        print(
            f"\n🔎 Detecting faces in: {image_path}"
        )


        results = DeepFace.extract_faces(

            img_path=image_path,

            detector_backend=DETECTOR_BACKEND,

            enforce_detection=False,

            align=True

        )


        detections = []


        for result in results:

            # ------------------------------------------------
            # Facial area
            # ------------------------------------------------

            facial_area = result.get(

                "facial_area",

                {}

            )


            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------

            confidence = result.get(

                "confidence",

                0

            )


            try:

                confidence = float(
                    confidence
                )

            except Exception:

                confidence = 0.0


            # ------------------------------------------------
            # Coordinates
            # ------------------------------------------------

            x = int(

                facial_area.get(
                    "x",
                    0
                )

            )


            y = int(

                facial_area.get(
                    "y",
                    0
                )

            )


            w = int(

                facial_area.get(
                    "w",
                    0
                )

            )


            h = int(

                facial_area.get(
                    "h",
                    0
                )

            )


            detection = {

                "x":
                    x,

                "y":
                    y,

                "w":
                    w,

                "h":
                    h,

                "confidence":
                    confidence

            }


            detections.append(
                detection
            )


        return detections


    except Exception as e:

        print(
            "\n⚠️ RetinaFace detection failed:"
        )

        print(
            str(e)
        )

        return []


# ==========================================================
# DETERMINE AREA LIMIT
# ==========================================================

def get_area_limit(
    image_width,
    image_height
):

    """
    Determine the maximum allowed face area.

    Small identity-document images often have portraits
    occupying a larger percentage of the image.

    Therefore:

        Small image
            → 60%

        Normal image
            → 35%

    Regardless of image size, detections above the absolute
    maximum are rejected.
    """


    max_dimension = max(

        image_width,

        image_height

    )


    if max_dimension <= SMALL_DOCUMENT_MAX_DIMENSION:

        return SMALL_DOCUMENT_AREA_RATIO


    return MAX_DOCUMENT_AREA_RATIO


# ==========================================================
# FILTER FACE CANDIDATES
# ==========================================================

def filter_face_candidates(
    detections,
    image_width,
    image_height
):

    candidates = []


    # ======================================================
    # DOCUMENT AREA
    # ======================================================

    document_area = (

        image_width *

        image_height

    )


    # ======================================================
    # DETERMINE AREA LIMIT
    # ======================================================

    area_limit = get_area_limit(

        image_width,

        image_height

    )


    print(
        f"\n📊 Portrait area limit: "
        f"{area_limit * 100:.0f}%"
    )


    # ======================================================
    # PROCESS DETECTIONS
    # ======================================================

    for detection in detections:

        x = detection["x"]

        y = detection["y"]

        w = detection["w"]

        h = detection["h"]

        confidence = detection["confidence"]


        # ==================================================
        # CONFIDENCE CHECK
        # ==================================================

        if confidence < MIN_FACE_CONFIDENCE:

            print(

                "⚠️ Rejected low-confidence "
                "detection:",

                detection

            )

            continue


        # ==================================================
        # SIZE CHECK
        # ==================================================

        if (

            w < MIN_FACE_SIZE

            or

            h < MIN_FACE_SIZE

        ):

            print(

                "⚠️ Rejected tiny detection:",

                detection

            )

            continue


        # ==================================================
        # COORDINATE CHECK
        # ==================================================

        if x < 0 or y < 0:

            print(

                "⚠️ Rejected invalid coordinates:",

                detection

            )

            continue


        if (

            x >= image_width

            or

            y >= image_height

        ):

            print(

                "⚠️ Rejected out-of-image detection:",

                detection

            )

            continue


        # ==================================================
        # CLAMP COORDINATES
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
        # FACE AREA
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
        # ABSOLUTE LARGE-BOX PROTECTION
        # ==================================================
        #
        # This protects against RetinaFace returning almost
        # the entire document as one giant face.
        #
        # This is different from the normal area check.
        #
        # Small documents can have large portrait ratios,
        # but an 85%+ document detection is still suspicious.
        #
        # ==================================================

        if (

            area_ratio >

            ABSOLUTE_MAX_DOCUMENT_AREA_RATIO

        ):

            print(

                "⚠️ Rejected suspicious/"
                "full-document detection:",

                detection

            )

            print(

                f"   Area ratio: "
                f"{area_ratio * 100:.2f}%"

            )

            continue


        # ==================================================
        # STANDARD AREA CHECK
        # ==================================================

        if area_ratio > area_limit:

            print(

                "⚠️ Rejected oversized "
                "portrait candidate:",

                detection

            )

            print(

                f"   Area ratio: "
                f"{area_ratio * 100:.2f}%"

            )

            continue


        # ==================================================
        # FACE BOX ASPECT RATIO
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

                "⚠️ Rejected unusual "
                "face aspect ratio:",

                detection

            )

            print(

                f"   Aspect ratio: "
                f"{aspect_ratio:.2f}"

            )

            continue


        # ==================================================
        # STORE CANDIDATE
        # ==================================================

        candidate = {

            "x":
                x,

            "y":
                y,

            "w":
                w,

            "h":
                h,

            "confidence":
                confidence,

            "area_ratio":
                area_ratio,

            "aspect_ratio":
                aspect_ratio

        }


        candidates.append(
            candidate
        )


    return candidates


# ==========================================================
# SELECT BEST FACE
# ==========================================================

def select_best_face(
    candidates
):

    if not candidates:

        return None


    """
    Candidate scoring:

        1. Detection confidence
        2. Useful portrait size
        3. Avoid excessively large regions
        4. Prefer reasonable face proportions
    """


    def score(
        candidate
    ):

        confidence = candidate[
            "confidence"
        ]


        area_ratio = candidate[
            "area_ratio"
        ]


        aspect_ratio = candidate[
            "aspect_ratio"
        ]


        # ==================================================
        # CONFIDENCE SCORE
        # ==================================================

        confidence_score = confidence


        # ==================================================
        # SIZE SCORE
        # ==================================================
        #
        # Very tiny faces are not useful.
        #
        # But we don't want to automatically prefer the
        # largest possible region.
        #
        # ==================================================

        size_score = min(

            area_ratio * 8,

            1.0

        )


        # ==================================================
        # ASPECT SCORE
        # ==================================================
        #
        # Ideal approximate face-box ratio is around 0.7.
        #
        # This is deliberately soft.
        #
        # ==================================================

        ideal_ratio = 0.70


        aspect_difference = abs(

            aspect_ratio -

            ideal_ratio

        )


        aspect_score = max(

            0.0,

            1.0 -

            aspect_difference

        )


        # ==================================================
        # FINAL SCORE
        # ==================================================

        return (

            confidence_score * 0.70

            +

            size_score * 0.15

            +

            aspect_score * 0.15

        )


    # ======================================================
    # SORT
    # ======================================================

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
        "IDSHIELD AI - DOCUMENT PORTRAIT EXTRACTION"
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
    # STEP 3 - DETECT FACES
    # ======================================================

    detections = detect_faces(

        document_path

    )


    print(

        f"\n🔎 Raw detections: "
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

        f"✅ Valid portrait candidates: "
        f"{len(candidates)}"

    )


    # ======================================================
    # STEP 5 - NO VALID FACE
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
    # STEP 6 - SELECT BEST FACE
    # ======================================================

    best_face = select_best_face(

        candidates

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
        "\n🎯 Selected portrait:"
    )


    print(
        best_face
    )


    # ======================================================
    # STEP 7 - CROP
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
    # STEP 8 - OUTPUT PATH
    # ======================================================

    if output_path is None:

        base_directory = os.path.dirname(

            document_path

        )


        output_path = os.path.join(

            base_directory,

            "document_face_crop.jpg"

        )


    # ======================================================
    # CREATE OUTPUT DIRECTORY
    # ======================================================

    output_directory = os.path.dirname(

        output_path

    )


    if output_directory:

        os.makedirs(

            output_directory,

            exist_ok=True

        )


    # ======================================================
    # STEP 9 - SAVE CROP
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


    print(
        "\n✅ Portrait crop saved:"
    )


    print(
        output_path
    )


    # ======================================================
    # DISPLAY CROP SIZE
    # ======================================================

    try:

        crop_height, crop_width = face_crop.shape[:2]


        print(

            f"📐 Portrait crop size: "
            f"{crop_width} x {crop_height}"

        )

    except Exception:

        pass


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

        "ocr",

        "test_documents",

        "sample_document_with_face.jpg"

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