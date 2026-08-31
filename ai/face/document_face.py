import os
import gc
import cv2
import numpy as np


# ==========================================================
# IDSHIELD AI
# LIGHTWEIGHT DOCUMENT FACE EXTRACTION
# YuNet + OpenCV
# ==========================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "face_detection_yunet.onnx"
)


# ----------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------

CONFIDENCE_THRESHOLD = 0.75
NMS_THRESHOLD = 0.3
TOP_K = 50

PADDING_RATIO = 0.25

MIN_FACE_SIZE = 20


# ==========================================================
# LOAD DETECTOR
# ==========================================================

_detector = None


def get_detector():

    global _detector

    if _detector is None:

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                f"YuNet model not found: {MODEL_PATH}"
            )

        print(
            "\n🧠 Loading lightweight YuNet face detector..."
        )

        _detector = cv2.FaceDetectorYN.create(
            MODEL_PATH,
            "",
            (320, 320),
            CONFIDENCE_THRESHOLD,
            NMS_THRESHOLD,
            TOP_K
        )

        print(
            "✅ YuNet detector loaded."
        )

    return _detector


# ==========================================================
# VALIDATE IMAGE
# ==========================================================

def validate_document_image(
    document_path
):

    if not document_path:

        return {
            "valid": False,
            "message": "Document path is empty."
        }

    if not os.path.exists(
        document_path
    ):

        return {
            "valid": False,
            "message": "Document image does not exist."
        }

    image = cv2.imread(
        document_path
    )

    if image is None:

        return {
            "valid": False,
            "message": "Unable to read document image."
        }

    height, width = image.shape[:2]

    if width < 100 or height < 100:

        return {
            "valid": False,
            "message": "Document image resolution is too small."
        }

    return {
        "valid": True,
        "message": "Document image is valid."
    }


# ==========================================================
# DETECT FACES
# ==========================================================

def detect_faces(
    document_path
):

    image = cv2.imread(
        document_path
    )

    if image is None:

        return []

    height, width = image.shape[:2]

    detector = get_detector()

    detector.setInputSize(
        (width, height)
    )

    _, faces = detector.detect(
        image
    )

    if faces is None:

        return []

    results = []

    for face in faces:

        x = int(
            face[0]
        )

        y = int(
            face[1]
        )

        w = int(
            face[2]
        )

        h = int(
            face[3]
        )

        confidence = float(
            face[14]
        )

        if w < MIN_FACE_SIZE:
            continue

        if h < MIN_FACE_SIZE:
            continue

        results.append({

            "x": x,

            "y": y,

            "w": w,

            "h": h,

            "confidence": confidence

        })

    del image

    return results


# ==========================================================
# FILTER FACE CANDIDATES
# ==========================================================

def filter_face_candidates(
    detections,
    width,
    height
):

    candidates = []

    for face in detections:

        x = face["x"]
        y = face["y"]
        w = face["w"]
        h = face["h"]

        area = w * h

        relative_area = (
            area /
            float(width * height)
        )

        center_x = (
            x + w / 2
        )

        center_y = (
            y + h / 2
        )

        # --------------------------------------------------
        # Ignore extremely tiny faces
        # --------------------------------------------------

        if relative_area < 0.0005:

            continue

        # --------------------------------------------------
        # Ignore faces touching image boundary
        # --------------------------------------------------

        if x < 0 or y < 0:

            continue

        if x + w > width:

            continue

        if y + h > height:

            continue

        # --------------------------------------------------
        # Score
        # --------------------------------------------------

        score = (
            face["confidence"] * 0.7
            +
            min(
                relative_area * 10,
                1.0
            ) * 0.3
        )

        candidates.append({

            **face,

            "score": score,

            "center_x": center_x,

            "center_y": center_y,

            "relative_area": relative_area

        })

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return candidates


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

    padding_x = int(
        w * PADDING_RATIO
    )

    padding_y = int(
        h * PADDING_RATIO
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
# EXTRACT DOCUMENT FACE
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
        "IDSHIELD AI - LIGHTWEIGHT DOCUMENT FACE EXTRACTION"
    )

    print(
        "=" * 60
    )

    print(
        "\n🧑 Searching for portrait inside document..."
    )

    # ------------------------------------------------------
    # Validate
    # ------------------------------------------------------

    validation = validate_document_image(
        document_path
    )

    if not validation["valid"]:

        return {

            "status": "ERROR",

            "face_found": False,

            "face_path": None,

            "confidence": None,

            "facial_area": None,

            "message":
                validation["message"]

        }

    # ------------------------------------------------------
    # Load image
    # ------------------------------------------------------

    image = cv2.imread(
        document_path
    )

    if image is None:

        return {

            "status": "ERROR",

            "face_found": False,

            "face_path": None,

            "confidence": None,

            "facial_area": None,

            "message":
                "Unable to load document image."

        }

    height, width = image.shape[:2]

    print(
        f"\n📄 Document size: {width} x {height}"
    )

    # ------------------------------------------------------
    # Detect
    # ------------------------------------------------------

    try:

        detections = detect_faces(
            document_path
        )

    except Exception as e:

        del image
        gc.collect()

        return {

            "status": "ERROR",

            "face_found": False,

            "face_path": None,

            "confidence": None,

            "facial_area": None,

            "message":
                f"Face detection failed: {str(e)}"

        }

    print(
        f"\n🔎 Raw detections: {len(detections)}"
    )

    # ------------------------------------------------------
    # Filter
    # ------------------------------------------------------

    candidates = filter_face_candidates(
        detections,
        width,
        height
    )

    print(
        f"✅ Valid portrait candidates: {len(candidates)}"
    )

    # ------------------------------------------------------
    # No face
    # ------------------------------------------------------

    if not candidates:

        del image
        gc.collect()

        return {

            "status": "REVIEW",

            "face_found": False,

            "face_path": None,

            "confidence": None,

            "facial_area": None,

            "message":
                "No reliable portrait found in document."

        }

    # ------------------------------------------------------
    # Select best face
    # ------------------------------------------------------

    best_face = candidates[0]

    print(
        "\n🏆 Selected document portrait:"
    )

    print(
        f"Confidence: {best_face['confidence']:.4f}"
    )

    print(
        f"Face area: {best_face['w']} x {best_face['h']}"
    )

    # ------------------------------------------------------
    # Crop
    # ------------------------------------------------------

    crop = crop_face(
        image,
        best_face
    )

    if crop is None:

        del image
        gc.collect()

        return {

            "status": "ERROR",

            "face_found": False,

            "face_path": None,

            "confidence":
                best_face["confidence"],

            "facial_area": best_face,

            "message":
                "Unable to crop detected portrait."

        }

    # ------------------------------------------------------
    # Output path
    # ------------------------------------------------------

    if not output_path:

        output_path = os.path.join(

            os.path.dirname(
                document_path
            ),

            "document_face_crop.jpg"

        )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    success = cv2.imwrite(
        output_path,
        crop,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            95
        ]
    )

    del crop
    del image

    gc.collect()

    if not success:

        return {

            "status": "ERROR",

            "face_found": False,

            "face_path": None,

            "confidence":
                best_face["confidence"],

            "facial_area":
                best_face,

            "message":
                "Unable to save document portrait."

        }

    print(
        "\n✅ DOCUMENT PORTRAIT EXTRACTED"
    )

    print(
        "Portrait:",
        output_path
    )

    return {

        "status": "PASS",

        "face_found": True,

        "face_path":
            output_path,

        "confidence":
            best_face["confidence"],

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
            "Document portrait extracted successfully."

    }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "YuNet document face extractor loaded."
    )