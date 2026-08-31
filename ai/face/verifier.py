import os
import gc
import cv2
import numpy as np


# ==========================================================
# IDShield AI - LIGHTWEIGHT FACE VERIFIER
# ==========================================================
#
# Purpose:
#   Compare:
#
#       SELFIE
#          VS
#       DOCUMENT PORTRAIT
#
#
# This version intentionally DOES NOT use:
#
#   ❌ DeepFace
#   ❌ RetinaFace
#   ❌ ArcFace
#
# It uses:
#
#   OpenCV Haar Cascade
#       +
#   lightweight image feature comparison
#
#
# IMPORTANT:
#
# This is a lightweight prototype verifier.
# It is NOT equivalent to a production-grade biometric
# verification system such as ArcFace.
#
# ==========================================================


# ==========================================================
# CONFIGURATION
# ==========================================================

MIN_IMAGE_SIZE = 80

MIN_FACE_SIZE = 30

# Similarity threshold.
#
# Increase this for stricter matching.
# Decrease this if genuine matches are being rejected.
#
SIMILARITY_THRESHOLD = 0.55


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

def cleanup_memory():

    try:

        gc.collect()

    except Exception:

        pass


# ==========================================================
# LOAD FACE DETECTOR
# ==========================================================

def load_face_detector():

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
                "\n❌ OpenCV face detector could not be loaded."
            )

            return None

        return detector

    except Exception as e:

        print(
            "\n❌ Face detector loading failed:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# LOAD IMAGE
# ==========================================================

def load_image(image_path):

    if not image_path:

        return None


    if not os.path.exists(
        image_path
    ):

        print(
            f"\n❌ Image not found: {image_path}"
        )

        return None


    image = cv2.imread(
        image_path
    )


    if image is None:

        print(
            f"\n❌ Unable to read image: {image_path}"
        )

        return None


    height, width = image.shape[:2]


    if (

        width < MIN_IMAGE_SIZE

        or

        height < MIN_IMAGE_SIZE

    ):

        print(
            f"\n⚠️ Image is too small: "
            f"{width} x {height}"
        )

        return None


    return image


# ==========================================================
# DETECT FACE
# ==========================================================

def detect_best_face(
    image
):

    detector = load_face_detector()


    if detector is None:

        return None


    try:

        gray = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )


        gray = cv2.equalizeHist(
            gray
        )


        faces = detector.detectMultiScale(

            gray,

            scaleFactor=1.08,

            minNeighbors=5,

            minSize=(
                MIN_FACE_SIZE,
                MIN_FACE_SIZE
            )

        )


        del gray


        if len(faces) == 0:

            return None


        # --------------------------------------------------
        # Select largest face
        # --------------------------------------------------

        best_face = max(

            faces,

            key=lambda box:
                box[2] * box[3]

        )


        x, y, w, h = best_face


        return {

            "x": int(x),

            "y": int(y),

            "w": int(w),

            "h": int(h)

        }


    except Exception as e:

        print(
            "\n⚠️ Face detection failed:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# CROP FACE
# ==========================================================

def crop_face(
    image,
    face
):

    if face is None:

        return None


    height, width = image.shape[:2]


    x = face["x"]

    y = face["y"]

    w = face["w"]

    h = face["h"]


    # ------------------------------------------------------
    # Padding
    # ------------------------------------------------------

    padding_x = int(
        w * 0.20
    )

    padding_y = int(
        h * 0.20
    )


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
# NORMALIZE FACE
# ==========================================================

def normalize_face(
    face
):

    if face is None:

        return None


    try:

        # --------------------------------------------------
        # Convert to grayscale
        # --------------------------------------------------

        gray = cv2.cvtColor(

            face,

            cv2.COLOR_BGR2GRAY

        )


        # --------------------------------------------------
        # Resize
        # --------------------------------------------------

        gray = cv2.resize(

            gray,

            (128, 128),

            interpolation=cv2.INTER_AREA

        )


        # --------------------------------------------------
        # Histogram equalization
        # --------------------------------------------------

        gray = cv2.equalizeHist(
            gray
        )


        # --------------------------------------------------
        # Blur slightly to reduce noise
        # --------------------------------------------------

        gray = cv2.GaussianBlur(

            gray,

            (3, 3),

            0

        )


        return gray


    except Exception as e:

        print(
            "\n⚠️ Face normalization failed:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# HISTOGRAM SIMILARITY
# ==========================================================

def histogram_similarity(
    image1,
    image2
):

    try:

        hist1 = cv2.calcHist(

            [image1],

            [0],

            None,

            [64],

            [0, 256]

        )


        hist2 = cv2.calcHist(

            [image2],

            [0],

            None,

            [64],

            [0, 256]

        )


        cv2.normalize(

            hist1,

            hist1

        )


        cv2.normalize(

            hist2,

            hist2

        )


        correlation = cv2.compareHist(

            hist1,

            hist2,

            cv2.HISTCMP_CORREL

        )


        # Convert [-1, 1] → [0, 1]

        similarity = (

            correlation + 1
        ) / 2


        return float(
            max(
                0.0,
                min(
                    1.0,
                    similarity
                )
            )
        )


    except Exception:

        return 0.0


# ==========================================================
# STRUCTURAL SIMILARITY
# ==========================================================

def structural_similarity(
    image1,
    image2
):

    try:

        # --------------------------------------------------
        # Normalize pixel values
        # --------------------------------------------------

        a = image1.astype(
            np.float32
        ) / 255.0


        b = image2.astype(
            np.float32
        ) / 255.0


        # --------------------------------------------------
        # Mean squared error
        # --------------------------------------------------

        mse = np.mean(

            (a - b) ** 2

        )


        # --------------------------------------------------
        # Convert MSE to similarity
        # --------------------------------------------------

        similarity = 1.0 - mse


        return float(

            max(

                0.0,

                min(

                    1.0,

                    similarity

                )

            )

        )


    except Exception:

        return 0.0


# ==========================================================
# EDGE SIMILARITY
# ==========================================================

def edge_similarity(
    image1,
    image2
):

    try:

        edges1 = cv2.Canny(

            image1,

            50,

            150

        )


        edges2 = cv2.Canny(

            image2,

            50,

            150

        )


        # --------------------------------------------------
        # Convert to float
        # --------------------------------------------------

        a = edges1.astype(
            np.float32
        ) / 255.0


        b = edges2.astype(
            np.float32
        ) / 255.0


        difference = np.mean(

            np.abs(
                a - b
            )

        )


        similarity = (

            1.0 - difference

        )


        return float(

            max(

                0.0,

                min(

                    1.0,

                    similarity

                )

            )

        )


    except Exception:

        return 0.0


# ==========================================================
# COMPARE FACES
# ==========================================================

def compare_faces(
    reference_face,
    document_face
):

    # ------------------------------------------------------
    # Histogram
    # ------------------------------------------------------

    histogram_score = (
        histogram_similarity(
            reference_face,
            document_face
        )
    )


    # ------------------------------------------------------
    # Structural
    # ------------------------------------------------------

    structural_score = (
        structural_similarity(
            reference_face,
            document_face
        )
    )


    # ------------------------------------------------------
    # Edge
    # ------------------------------------------------------

    edge_score = (
        edge_similarity(
            reference_face,
            document_face
        )
    )


    # ======================================================
    # COMBINED SCORE
    # ======================================================
    #
    # Histogram:
    #     30%
    #
    # Structural:
    #     50%
    #
    # Edge:
    #     20%
    #
    # ======================================================

    similarity = (

        histogram_score * 0.30

        +

        structural_score * 0.50

        +

        edge_score * 0.20

    )


    similarity = max(

        0.0,

        min(

            1.0,

            similarity

        )

    )


    return {

        "similarity_score":
            round(
                similarity,
                4
            ),

        "histogram_score":
            round(
                histogram_score,
                4
            ),

        "structural_score":
            round(
                structural_score,
                4
            ),

        "edge_score":
            round(
                edge_score,
                4
            )

    }


# ==========================================================
# VERIFY FACES
# ==========================================================

def verify_faces(
    reference_image_path,
    document_image_path
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "IDSHIELD AI - LIGHTWEIGHT FACE VERIFICATION"
    )

    print(
        "=" * 60
    )


    # ======================================================
    # VALIDATE REFERENCE
    # ======================================================

    if not reference_image_path:

        return {

            "status":
                "NO_REFERENCE_FACE",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "No reference selfie was provided."

        }


    if not os.path.exists(
        reference_image_path
    ):

        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Reference selfie was not found."

        }


    # ======================================================
    # VALIDATE DOCUMENT PORTRAIT
    # ======================================================

    if not document_image_path:

        return {

            "status":
                "NO_DOCUMENT_FACE",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Document portrait was not provided."

        }


    if not os.path.exists(
        document_image_path
    ):

        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Document portrait was not found."

        }


    # ======================================================
    # LOAD IMAGES
    # ======================================================

    print(
        "\n📷 Loading selfie..."
    )


    reference_image = load_image(

        reference_image_path

    )


    if reference_image is None:

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Unable to load selfie."

        }


    print(
        "📄 Loading document portrait..."
    )


    document_image = load_image(

        document_image_path

    )


    if document_image is None:

        del reference_image

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Unable to load document portrait."

        }


    # ======================================================
    # DETECT SELFIE FACE
    # ======================================================

    print(
        "\n🔎 Detecting face in selfie..."
    )


    reference_detection = (
        detect_best_face(
            reference_image
        )
    )


    if reference_detection is None:

        del reference_image
        del document_image

        cleanup_memory()


        return {

            "status":
                "NO_REFERENCE_FACE",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "No face detected in selfie."

        }


    # ======================================================
    # DETECT DOCUMENT FACE
    # ======================================================

    print(
        "🔎 Detecting face in document portrait..."
    )


    document_detection = (
        detect_best_face(
            document_image
        )
    )


    # ------------------------------------------------------
    # Important:
    #
    # The document portrait was already cropped by
    # document_face.py.
    #
    # Therefore, if Haar cannot find another face inside
    # the crop, use the entire portrait crop.
    #
    # ------------------------------------------------------

    if document_detection is None:

        document_face_crop = (
            document_image
        )

        print(
            "ℹ️ No secondary face detection "
            "inside document crop."
        )

        print(
            "Using extracted document portrait directly."
        )

    else:

        document_face_crop = crop_face(

            document_image,

            document_detection

        )


    # ======================================================
    # CROP SELFIE
    # ======================================================

    reference_face_crop = crop_face(

        reference_image,

        reference_detection

    )


    if reference_face_crop is None:

        del reference_image
        del document_image

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Unable to crop selfie face."

        }


    if document_face_crop is None:

        del reference_image
        del document_image
        del reference_face_crop

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Unable to prepare document portrait."

        }


    # ======================================================
    # NORMALIZE
    # ======================================================

    print(
        "\n🧠 Preparing face features..."
    )


    normalized_reference = normalize_face(

        reference_face_crop

    )


    normalized_document = normalize_face(

        document_face_crop

    )


    if (

        normalized_reference is None

        or

        normalized_document is None

    ):

        del reference_image
        del document_image
        del reference_face_crop
        del document_face_crop

        cleanup_memory()


        return {

            "status":
                "ERROR",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                SIMILARITY_THRESHOLD,

            "message":
                "Unable to normalize face images."

        }


    # ======================================================
    # COMPARE
    # ======================================================

    print(
        "\n🔬 Comparing:"
    )

    print(
        "   SELFIE"
    )

    print(
        "     ↕"
    )

    print(
        "   DOCUMENT PORTRAIT"
    )


    scores = compare_faces(

        normalized_reference,

        normalized_document

    )


    similarity_score = scores[
        "similarity_score"
    ]


    # ======================================================
    # DISTANCE
    # ======================================================

    distance = (

        1.0 -

        similarity_score

    )


    # ======================================================
    # DECISION
    # ======================================================

    verified = (

        similarity_score >=
        SIMILARITY_THRESHOLD

    )


    # ======================================================
    # STATUS
    # ======================================================

    if verified:

        status = "VERIFIED"

        message = (
            "Selfie and document portrait "
            "passed lightweight face comparison."
        )

    else:

        status = "NO_MATCH"

        message = (
            "Selfie and document portrait "
            "did not meet the similarity threshold."
        )


    # ======================================================
    # DISPLAY
    # ======================================================

    print(
        "\nSimilarity score:",
        round(
            similarity_score,
            4
        )
    )


    print(
        "Threshold:",
        SIMILARITY_THRESHOLD
    )


    print(
        "Distance:",
        round(
            distance,
            4
        )
    )


    if verified:

        print(
            "\n✅ FACE MATCH"
        )

    else:

        print(
            "\n❌ FACE DOES NOT MATCH"
        )


    # ======================================================
    # CLEANUP
    # ======================================================

    del reference_image
    del document_image
    del reference_face_crop
    del document_face_crop
    del normalized_reference
    del normalized_document

    cleanup_memory()


    # ======================================================
    # RESULT
    # ======================================================

    return {

        "status":
            status,

        "verified":
            verified,

        "similarity_score":
            round(
                similarity_score,
                4
            ),

        "distance":
            round(
                distance,
                4
            ),

        "threshold":
            SIMILARITY_THRESHOLD,

        "features": {

            "histogram_score":
                scores[
                    "histogram_score"
                ],

            "structural_score":
                scores[
                    "structural_score"
                ],

            "edge_score":
                scores[
                    "edge_score"
                ]

        },

        "message":
            message

    }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "IDSHIELD AI - FACE VERIFIER TEST"
    )

    print(
        "=" * 60
    )


    # ------------------------------------------------------
    # Test images
    # ------------------------------------------------------

    BASE_DIR = os.path.dirname(

        os.path.abspath(
            __file__
        )

    )


    reference_face = os.path.join(

        BASE_DIR,

        "test_images",

        "person1.jpg"

    )


    document_face = os.path.join(

        BASE_DIR,

        "test_images",

        "document_face_crop.jpg"

    )


    print(
        "\nSelfie:"
    )

    print(
        reference_face
    )


    print(
        "\nDocument portrait:"
    )

    print(
        document_face
    )


    if not os.path.exists(
        reference_face
    ):

        print(
            "\n❌ Selfie test image not found."
        )

    elif not os.path.exists(
        document_face
    ):

        print(
            "\n❌ Document portrait test image not found."
        )

    else:

        result = verify_faces(

            reference_face,

            document_face

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