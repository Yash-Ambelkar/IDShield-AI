import os
import gc
import cv2


# ==========================================================
# IDSHIELD AI
# LIGHTWEIGHT FACE VERIFICATION
# YuNet + SFace
# ==========================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

YUNET_MODEL = os.path.join(
    BASE_DIR,
    "models",
    "face_detection_yunet.onnx"
)

SFACE_MODEL = os.path.join(
    BASE_DIR,
    "models",
    "face_recognition_sface.onnx"
)


# ==========================================================
# SETTINGS
# ==========================================================

FACE_CONFIDENCE = 0.75

NMS_THRESHOLD = 0.3

TOP_K = 50

# SFace cosine similarity threshold.
#
# This is intentionally configurable.
# We will tune it using your real test images.
#
COSINE_THRESHOLD = 0.363


_detector = None
_recognizer = None


# ==========================================================
# LOAD YUNET
# ==========================================================

def get_detector():

    global _detector

    if _detector is None:

        if not os.path.exists(
            YUNET_MODEL
        ):

            raise FileNotFoundError(
                f"YuNet model not found: {YUNET_MODEL}"
            )

        print(
            "\n🧠 Loading YuNet..."
        )

        _detector = cv2.FaceDetectorYN.create(

            YUNET_MODEL,

            "",

            (320, 320),

            FACE_CONFIDENCE,

            NMS_THRESHOLD,

            TOP_K

        )

        print(
            "✅ YuNet loaded."
        )

    return _detector


# ==========================================================
# LOAD SFACE
# ==========================================================

def get_recognizer():

    global _recognizer

    if _recognizer is None:

        if not os.path.exists(
            SFACE_MODEL
        ):

            raise FileNotFoundError(
                f"SFace model not found: {SFACE_MODEL}"
            )

        print(
            "\n🧠 Loading SFace..."
        )

        _recognizer = cv2.FaceRecognizerSF.create(

            SFACE_MODEL,

            ""

        )

        print(
            "✅ SFace loaded."
        )

    return _recognizer


# ==========================================================
# DETECT BEST FACE
# ==========================================================

def detect_best_face(
    image
):

    if image is None:

        return None

    height, width = image.shape[:2]

    detector = get_detector()

    detector.setInputSize(
        (width, height)
    )

    _, faces = detector.detect(
        image
    )

    if faces is None:

        return None

    if len(faces) == 0:

        return None

    # ------------------------------------------------------
    # Choose largest/highest-confidence face
    # ------------------------------------------------------

    best = None
    best_score = -1

    for face in faces:

        x = float(face[0])
        y = float(face[1])
        w = float(face[2])
        h = float(face[3])

        confidence = float(
            face[14]
        )

        area = w * h

        score = (
            confidence * 0.7
            +
            (
                area /
                max(
                    width * height,
                    1
                )
            )
            * 0.3
        )

        if score > best_score:

            best_score = score

            best = face

    return best


# ==========================================================
# VERIFY FACES
# ==========================================================

def verify_faces(
    reference_face,
    document_portrait
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

    print(
        "\nReference face:"
    )

    print(
        reference_face
    )

    print(
        "\nDocument portrait:"
    )

    print(
        document_portrait
    )

    # ------------------------------------------------------
    # Validate paths
    # ------------------------------------------------------

    if not reference_face:

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
                COSINE_THRESHOLD,

            "message":
                "Reference selfie path is empty."

        }

    if not document_portrait:

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
                COSINE_THRESHOLD,

            "message":
                "Document portrait path is empty."

        }

    if not os.path.exists(
        reference_face
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
                COSINE_THRESHOLD,

            "message":
                "Reference selfie file does not exist."

        }

    if not os.path.exists(
        document_portrait
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
                COSINE_THRESHOLD,

            "message":
                "Document portrait file does not exist."

        }

    # ------------------------------------------------------
    # Load images
    # ------------------------------------------------------

    reference = cv2.imread(
        reference_face
    )

    document = cv2.imread(
        document_portrait
    )

    if reference is None:

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
                COSINE_THRESHOLD,

            "message":
                "Unable to read selfie image."

        }

    if document is None:

        del reference
        gc.collect()

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
                COSINE_THRESHOLD,

            "message":
                "Unable to read document portrait."

        }

    # ------------------------------------------------------
    # Detect faces
    # ------------------------------------------------------

    try:

        reference_face_data = detect_best_face(
            reference
        )

        document_face_data = detect_best_face(
            document
        )

    except Exception as e:

        del reference
        del document

        gc.collect()

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
                COSINE_THRESHOLD,

            "message":
                f"Face detection failed: {str(e)}"

        }

    # ------------------------------------------------------
    # Selfie face missing
    # ------------------------------------------------------

    if reference_face_data is None:

        del reference
        del document

        gc.collect()

        return {

            "status":
                "NO_FACE",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                COSINE_THRESHOLD,

            "message":
                "No face detected in selfie."

        }

    # ------------------------------------------------------
    # Document face missing
    # ------------------------------------------------------

    if document_face_data is None:

        del reference
        del document

        gc.collect()

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
                COSINE_THRESHOLD,

            "message":
                "No face detected in document portrait."

        }

    print(
        "\n✅ Face detected in both images."
    )

    # ------------------------------------------------------
    # Load SFace
    # ------------------------------------------------------

    try:

        recognizer = get_recognizer()

        # --------------------------------------------------
        # Align faces
        # --------------------------------------------------

        aligned_reference = recognizer.alignCrop(

            reference,

            reference_face_data

        )

        aligned_document = recognizer.alignCrop(

            document,

            document_face_data

        )

        # --------------------------------------------------
        # Extract features
        # --------------------------------------------------

        feature_reference = recognizer.feature(

            aligned_reference

        )

        feature_document = recognizer.feature(

            aligned_document

        )

        # --------------------------------------------------
        # Cosine similarity
        # --------------------------------------------------

        cosine_score = float(

            recognizer.match(

                feature_reference,

                feature_document,

                cv2.FaceRecognizerSF_FR_COSINE

            )

        )

    except Exception as e:

        del reference
        del document

        gc.collect()

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
                COSINE_THRESHOLD,

            "message":
                f"SFace verification failed: {str(e)}"

        }

    # ------------------------------------------------------
    # Convert similarity to distance-like value
    # ------------------------------------------------------

    distance = 1.0 - cosine_score

    verified = (
        cosine_score >= COSINE_THRESHOLD
    )

    # ------------------------------------------------------
    # Cleanup image memory
    # ------------------------------------------------------

    del reference
    del document

    del aligned_reference
    del aligned_document

    del feature_reference
    del feature_document

    gc.collect()

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    if verified:

        status = "MATCH"

        message = (
            "Reference face matches "
            "the document portrait."
        )

        print(
            "\n✅ FACE MATCH"
        )

    else:

        status = "NO_MATCH"

        message = (
            "Reference face does not match "
            "the document portrait."
        )

        print(
            "\n❌ FACE DOES NOT MATCH"
        )

    print(
        f"\nCosine similarity: {cosine_score:.4f}"
    )

    print(
        f"Threshold: {COSINE_THRESHOLD:.4f}"
    )

    return {

        "status":
            status,

        "verified":
            verified,

        "similarity_score":
            round(
                cosine_score,
                4
            ),

        "distance":
            round(
                distance,
                4
            ),

        "threshold":
            COSINE_THRESHOLD,

        "model":
            "SFace",

        "detector":
            "YuNet",

        "message":
            message

    }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "SFace + YuNet verifier loaded successfully."
    )