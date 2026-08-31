import os
import gc


# ==========================================================
# IDShield AI - FACE VERIFICATION
# ==========================================================
#
# Purpose:
#
#   Compare:
#
#       SELFIE / REFERENCE FACE
#                 ↕
#             ArcFace
#                 ↕
#       DOCUMENT PORTRAIT
#
#
# IMPORTANT:
#
# This module expects the second image to already contain
# the portrait extracted from the identity document.
#
# Document portrait extraction is handled separately by:
#
#     face/document_face.py
#
# This prevents the detector from incorrectly rejecting a
# small portrait crop as a "full document".
#
# ==========================================================


# ==========================================================
# CONFIGURATION
# ==========================================================

FACE_MODEL = "ArcFace"

FACE_DETECTOR = "retinaface"


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

def validate_image(
    image_path,
    image_label
):

    # ------------------------------------------------------
    # Path check
    # ------------------------------------------------------

    if not image_path:

        return {

            "valid": False,

            "message":
                f"{image_label} was not provided."

        }

    # ------------------------------------------------------
    # File existence
    # ------------------------------------------------------

    if not os.path.exists(image_path):

        return {

            "valid": False,

            "message":
                (
                    f"{image_label} was not found: "
                    f"{image_path}"
                )

        }

    # ------------------------------------------------------
    # OpenCV validation
    # ------------------------------------------------------

    try:

        import cv2

        image = cv2.imread(
            image_path
        )

        if image is None:

            return {

                "valid": False,

                "message":
                    (
                        f"{image_label} could not "
                        "be read as an image."
                    )

            }

        height, width = image.shape[:2]

        del image

        cleanup_memory()

        # --------------------------------------------------
        # Minimum image size
        # --------------------------------------------------

        if width < 50 or height < 50:

            return {

                "valid": False,

                "message":
                    (
                        f"{image_label} is too small "
                        "for face verification."
                    )

            }

        return {

            "valid": True,

            "width": width,

            "height": height,

            "message":
                "Image is valid."

        }

    except Exception as e:

        return {

            "valid": False,

            "message":
                (
                    f"{image_label} validation failed: "
                    f"{str(e)}"
                )

        }


# ==========================================================
# LIGHTWEIGHT FACE CHECK
# ==========================================================

def contains_face(
    image_path
):

    """
    Lightweight OpenCV face existence check.

    This is used only as a basic sanity check.

    IMPORTANT:
    We do NOT apply the full-document area rejection here.

    A document portrait crop can legitimately contain a face
    occupying a large percentage of the image.
    """

    try:

        import cv2

        image = cv2.imread(
            image_path
        )

        if image is None:

            return False

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        cascade_path = (

            cv2.data.haarcascades
            +
            "haarcascade_frontalface_default.xml"

        )

        detector = cv2.CascadeClassifier(
            cascade_path
        )

        if detector.empty():

            del gray
            del image

            cleanup_memory()

            return False

        faces = detector.detectMultiScale(

            gray,

            scaleFactor=1.1,

            minNeighbors=4,

            minSize=(30, 30)

        )

        del gray
        del image

        cleanup_memory()

        return len(faces) > 0

    except Exception:

        cleanup_memory()

        return False


# ==========================================================
# LOAD DEEPFACE
# ==========================================================

def load_deepface():

    print(
        "\n🔄 Loading DeepFace..."
    )

    try:

        from deepface import DeepFace

        print(
            "✅ DeepFace loaded."
        )

        return DeepFace

    except Exception as e:

        print(
            "\n❌ DeepFace import failed:"
        )

        print(
            str(e)
        )

        return None


# ==========================================================
# CALCULATE PRESENTATION SIMILARITY
# ==========================================================

def calculate_similarity(
    distance,
    threshold
):

    if distance is None:

        return None

    if threshold is None:

        return None

    try:

        distance = float(
            distance
        )

        threshold = float(
            threshold
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    if threshold <= 0:

        return None

    # ------------------------------------------------------
    # IMPORTANT
    #
    # This is only a presentation score.
    #
    # It is NOT a probability.
    # ------------------------------------------------------

    similarity = (

        1
        -
        (
            distance / threshold
        )

    ) * 100

    similarity = max(

        0,

        min(
            100,
            similarity
        )

    )

    return round(
        similarity,
        2
    )


# ==========================================================
# FACE VERIFICATION
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
        "IDSHIELD AI - FACE VERIFICATION"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # STEP 1 - VALIDATE SELFIE
    # ======================================================

    print(
        "\n🔎 Checking reference/selfie image..."
    )

    reference_check = validate_image(

        reference_face,

        "Reference face"

    )

    if not reference_check["valid"]:

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                False,

            "document_face_path":
                document_portrait,

            "message":
                reference_check["message"]

        }

    print(
        "✅ Reference image is valid."
    )

    # ======================================================
    # STEP 2 - VALIDATE DOCUMENT PORTRAIT
    # ======================================================

    print(
        "\n🔎 Checking document portrait..."
    )

    portrait_check = validate_image(

        document_portrait,

        "Document portrait"

    )

    if not portrait_check["valid"]:

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                False,

            "document_face_path":
                document_portrait,

            "message":
                portrait_check["message"]

        }

    print(
        "✅ Document portrait is valid."
    )

    print(
        "\n📐 Reference image size:"
        f" {reference_check['width']} x "
        f"{reference_check['height']}"
    )

    print(
        "📐 Document portrait size:"
        f" {portrait_check['width']} x "
        f"{portrait_check['height']}"
    )

    # ======================================================
    # STEP 3 - BASIC FACE CHECK
    # ======================================================

    print(
        "\n🔎 Checking face in reference image..."
    )

    reference_has_face = contains_face(
        reference_face
    )

    if not reference_has_face:

        print(
            "❌ No face detected in reference image."
        )

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                False,

            "document_face_path":
                document_portrait,

            "message":
                (
                    "No face detected in "
                    "reference/selfie image."
                )

        }

    print(
        "✅ Face detected in reference image."
    )

    # ======================================================
    # DOCUMENT PORTRAIT
    # ======================================================
    #
    # IMPORTANT:
    #
    # We DO NOT use the old full-document filtering logic.
    #
    # The document portrait has already been extracted by:
    #
    #     document_face.py
    #
    # Therefore the face is allowed to occupy a large
    # percentage of this image.
    #
    # ======================================================

    print(
        "\n🖼️ Using previously extracted document portrait..."
    )

    print(
        "Portrait:"
    )

    print(
        document_portrait
    )

    # ======================================================
    # STEP 4 - LOAD DEEPFACE
    # ======================================================

    DeepFace = load_deepface()

    if DeepFace is None:

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                True,

            "document_face_path":
                document_portrait,

            "message":
                "DeepFace could not be loaded."

        }

    # ======================================================
    # STEP 5 - ARCface VERIFICATION
    # ======================================================

    print(
        "\n🧠 Running ArcFace verification..."
    )

    print(
        "\nComparing:"
    )

    print(
        "    SELFIE"
    )

    print(
        "      ↕"
    )

    print(
        "    DOCUMENT PORTRAIT"
    )

    try:

        result = DeepFace.verify(

            img1_path=reference_face,

            img2_path=document_portrait,

            model_name=FACE_MODEL,

            detector_backend=FACE_DETECTOR,

            enforce_detection=True

        )

    except Exception as e:

        print(
            "\n❌ ArcFace verification failed:"
        )

        print(
            str(e)
        )

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                True,

            "document_face_path":
                document_portrait,

            "message":
                (
                    "Face verification failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # STEP 6 - READ RESULT
    # ======================================================

    try:

        verified = bool(

            result.get(
                "verified",
                False
            )

        )

        distance = result.get(
            "distance"
        )

        threshold = result.get(
            "threshold"
        )

        similarity = calculate_similarity(

            distance,

            threshold

        )

    except Exception as e:

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
                None,

            "model":
                FACE_MODEL,

            "detector":
                FACE_DETECTOR,

            "document_face_found":
                True,

            "document_face_path":
                document_portrait,

            "message":
                (
                    "Unable to process "
                    f"face verification result: {str(e)}"
                )

        }

    # ======================================================
    # STEP 7 - DETERMINE STATUS
    # ======================================================

    if verified:

        status = "MATCH"

        print(
            "\n✅ FACE MATCH"
        )

    else:

        status = "NO_MATCH"

        print(
            "\n❌ FACE DOES NOT MATCH"
        )

    # ======================================================
    # DISPLAY RESULT
    # ======================================================

    print(
        "\n"
        + "-" * 60
    )

    print(
        "FACE VERIFICATION RESULT"
    )

    print(
        "-" * 60
    )

    print(
        "Status          :",
        status
    )

    print(
        "Verified        :",
        verified
    )

    print(
        "Similarity      :",
        similarity
    )

    print(
        "Distance        :",
        distance
    )

    print(
        "Threshold       :",
        threshold
    )

    print(
        "Model           :",
        FACE_MODEL
    )

    print(
        "Detector        :",
        FACE_DETECTOR
    )

    print(
        "Document Face   :",
        document_portrait
    )

    print(
        "-" * 60
    )

    # ======================================================
    # CLEANUP
    # ======================================================

    cleanup_memory()

    # ======================================================
    # FINAL RESULT
    # ======================================================

    return {

        "status":
            status,

        "verified":
            verified,

        "similarity_score":
            similarity,

        "distance":
            distance,

        "threshold":
            threshold,

        "model":
            FACE_MODEL,

        "detector":
            FACE_DETECTOR,

        "document_face_found":
            True,

        "document_face_path":
            document_portrait,

        "message":
            (
                "Face verification completed successfully."
                if verified
                else
                "Reference face does not match "
                "the document portrait."
            )

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
        "IDSHIELD AI - FACE VERIFICATION TEST"
    )

    print(
        "=" * 60
    )

    REFERENCE_FACE = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        "test_images",

        "person1.jpg"

    )

    DOCUMENT_PORTRAIT = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        "..",

        "ocr",

        "test_documents",

        "document_face_verification.jpg"

    )

    DOCUMENT_PORTRAIT = os.path.abspath(
        DOCUMENT_PORTRAIT
    )

    print(
        "\nReference:"
    )

    print(
        REFERENCE_FACE
    )

    print(
        "\nDocument portrait:"
    )

    print(
        DOCUMENT_PORTRAIT
    )

    if not os.path.exists(
        REFERENCE_FACE
    ):

        print(
            "\n❌ Reference image not found."
        )

        raise SystemExit(1)

    if not os.path.exists(
        DOCUMENT_PORTRAIT
    ):

        print(
            "\n❌ Document portrait not found."
        )

        raise SystemExit(1)

    result = verify_faces(

        REFERENCE_FACE,

        DOCUMENT_PORTRAIT

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