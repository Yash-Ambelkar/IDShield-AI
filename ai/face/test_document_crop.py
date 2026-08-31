import cv2
import os

from deepface import DeepFace


DOCUMENT = os.path.join(
    "ocr",
    "test_documents",
    "sample_document.jpg"
)

OUTPUT = os.path.join(
    "face",
    "test_images",
    "manual_portrait_crop.jpg"
)


image = cv2.imread(DOCUMENT)

if image is None:
    print("❌ Could not load document")
    raise SystemExit(1)


height, width = image.shape[:2]

print("Document size:", width, "x", height)


# ==========================================================
# TEMPORARY MANUAL CROP
# ==========================================================
#
# We are testing the portrait area.
#
# Adjust these four values after looking at your ID image.
#
# ==========================================================

x1 = int(width * 0.55)
y1 = int(height * 0.10)

x2 = int(width * 0.95)
y2 = int(height * 0.70)


crop = image[
    y1:y2,
    x1:x2
]


os.makedirs(
    os.path.dirname(OUTPUT),
    exist_ok=True
)


cv2.imwrite(
    OUTPUT,
    crop
)


print()
print("✅ Manual crop saved:")
print(OUTPUT)

print()
print("Crop size:", crop.shape[1], "x", crop.shape[0])


# ==========================================================
# TEST RETINAFACE
# ==========================================================

print()
print("🔍 Testing RetinaFace on manual portrait crop...")


try:

    result = DeepFace.extract_faces(

        img_path=OUTPUT,

        detector_backend="retinaface",

        enforce_detection=False

    )

    print()
    print("RESULT:")
    print(result)

    print()
    print("Number of detections:", len(result))

    for i, face in enumerate(result):

        print()
        print("Detection", i + 1)

        print(
            "Confidence:",
            face.get("confidence")
        )

        print(
            "Facial area:",
            face.get("facial_area")
        )


except Exception as e:

    print()
    print("❌ RetinaFace failed:")
    print(e)