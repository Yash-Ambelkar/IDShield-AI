import cv2
import os


# ==========================================
# IDShield AI
# Create Tampered Test Document
# ==========================================

SOURCE_IMAGE = "../ocr/test_documents/sample_document.jpg"
OUTPUT_IMAGE = "tampered_document.jpg"


def create_tampered_document():

    # --------------------------------------
    # Check source image
    # --------------------------------------

    if not os.path.exists(SOURCE_IMAGE):
        print("❌ Source document not found!")
        print(f"Expected: {SOURCE_IMAGE}")
        return

    # --------------------------------------
    # Load original document
    # --------------------------------------

    image = cv2.imread(SOURCE_IMAGE)

    if image is None:
        print("❌ Could not read source image.")
        return

    # --------------------------------------
    # Create intentional tampering
    #
    # We cover part of the document and
    # replace it with modified information.
    # --------------------------------------

    cv2.rectangle(
        image,
        (520, 330),
        (760, 390),
        (255, 255, 255),
        -1
    )

    cv2.putText(
        image,
        "ARJUN VERMA",
        (520, 375),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    # --------------------------------------
    # Add another suspicious modification
    # --------------------------------------

    cv2.rectangle(
        image,
        (510, 590),
        (760, 650),
        (255, 255, 255),
        -1
    )

    cv2.putText(
        image,
        "14-08-2040",
        (510, 630),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    # --------------------------------------
    # Save tampered document
    # --------------------------------------

    success = cv2.imwrite(
        OUTPUT_IMAGE,
        image
    )

    if success:

        print("=" * 60)
        print("       IDSHIELD AI - TAMPER TEST")
        print("=" * 60)

        print("\n✅ Tampered document created!")

        print(f"\nOriginal:")
        print(SOURCE_IMAGE)

        print(f"\nTampered:")
        print(OUTPUT_IMAGE)

        print("\nModifications:")
        print("1. Name changed")
        print("2. Expiry date changed")

        print("=" * 60)

    else:

        print("❌ Failed to create tampered document.")


# ==========================================
# Start
# ==========================================

if __name__ == "__main__":
    create_tampered_document()