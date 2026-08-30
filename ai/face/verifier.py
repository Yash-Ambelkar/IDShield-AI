import os
import cv2
from deepface import DeepFace


# ==========================================================
# IDShield AI - Face Verification
# ==========================================================


def contains_face(image_path):
    """
    Quickly checks whether an image contains a face.
    This prevents DeepFace from running unnecessarily
    on documents that do not contain a face.
    """

    if not os.path.exists(image_path):
        return False

    image = cv2.imread(image_path)

    if image is None:
        return False

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    cascade_path = cv2.data.haarcascades + (
        "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(
        cascade_path
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    return len(faces) > 0


def verify_faces(image1, image2):

    # ------------------------------------------------------
    # Check files
    # ------------------------------------------------------

    if not os.path.exists(image1):
        return {
            "status": "ERROR",
            "message": f"Image not found: {image1}"
        }

    if not os.path.exists(image2):
        return {
            "status": "ERROR",
            "message": f"Image not found: {image2}"
        }

    # ------------------------------------------------------
    # Check reference face
    # ------------------------------------------------------

    if not contains_face(image1):

        return {
            "status": "ERROR",
            "verified": False,
            "similarity_score": None,
            "distance": None,
            "threshold": None,
            "message": "No face detected in reference image."
        }

    # ------------------------------------------------------
    # Check document face
    # ------------------------------------------------------

    if not contains_face(image2):

        return {
            "status": "NO_FACE",
            "verified": False,
            "similarity_score": None,
            "distance": None,
            "threshold": None,
            "message": (
                "No face detected in the identity document."
            )
        }

    # ------------------------------------------------------
    # DeepFace verification
    # ------------------------------------------------------

    try:

        print("\n🔍 Running face verification...")

        result = DeepFace.verify(
            img1_path=image1,
            img2_path=image2,
            model_name="ArcFace",
            detector_backend="opencv",
            enforce_detection=True
        )

        verified = result.get(
            "verified",
            False
        )

        distance = result.get(
            "distance"
        )

        threshold = result.get(
            "threshold"
        )

        # --------------------------------------------------
        # Similarity
        # --------------------------------------------------

        similarity = None

        if (
            distance is not None
            and threshold is not None
            and threshold > 0
        ):

            similarity = max(
                0,
                min(
                    100,
                    (1 - (distance / threshold)) * 100
                )
            )

        # --------------------------------------------------
        # Final status
        # --------------------------------------------------

        if verified:
            status = "MATCH"
        else:
            status = "NO_MATCH"

        return {

            "status": status,

            "verified": verified,

            "similarity_score": (
                round(similarity, 2)
                if similarity is not None
                else None
            ),

            "distance": distance,

            "threshold": threshold

        }

    except Exception as e:

        return {

            "status": "ERROR",

            "verified": False,

            "similarity_score": None,

            "distance": None,

            "threshold": None,

            "message": str(e)

        }