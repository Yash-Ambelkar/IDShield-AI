import os
import cv2
import numpy as np


# ==========================================================
# IDShield AI - Single Document Tampering Detector
# ==========================================================
#
# This module performs document-level forensic checks.
#
# IMPORTANT:
# It does NOT claim that image analysis alone can prove
# authenticity.
#
# The authenticity registry is the primary authority check.
# This module provides additional suspicious-image signals.
# ==========================================================


# ==========================================================
# LOAD IMAGE
# ==========================================================

def load_document(image_path):

    if not image_path:
        return None

    if not os.path.exists(image_path):
        return None

    try:

        image = cv2.imread(
            image_path,
            cv2.IMREAD_COLOR
        )

        return image

    except Exception:

        return None


# ==========================================================
# IMAGE QUALITY CHECK
# ==========================================================

def calculate_blur_score(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    variance = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return round(
        float(variance),
        2
    )


# ==========================================================
# EDGE ANALYSIS
# ==========================================================

def calculate_edge_density(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_pixels = np.count_nonzero(
        edges
    )

    total_pixels = edges.shape[0] * edges.shape[1]

    if total_pixels == 0:
        return 0

    density = (
        edge_pixels /
        total_pixels
    ) * 100

    return round(
        float(density),
        2
    )


# ==========================================================
# JPEG / COMPRESSION CHECK
# ==========================================================

def compression_check(image_path):

    extension = os.path.splitext(
        image_path
    )[1].lower()

    file_size = os.path.getsize(
        image_path
    )

    # Very small files can indicate that
    # the document was heavily compressed.
    #
    # This is only a signal, NOT proof of fraud.

    if extension in [
        ".jpg",
        ".jpeg"
    ]:

        if file_size < 20 * 1024:

            return {
                "status": "SUSPICIOUS",
                "reason":
                    "Very low image file size."
            }

    return {
        "status": "NORMAL",
        "reason":
            "No obvious compression anomaly detected."
    }


# ==========================================================
# IMAGE DIMENSION CHECK
# ==========================================================

def dimension_check(image):

    height, width = image.shape[:2]

    if width < 400 or height < 250:

        return {
            "status": "SUSPICIOUS",
            "reason":
                "Document image resolution is unusually low.",
            "width":
                width,
            "height":
                height
        }

    return {
        "status": "NORMAL",
        "reason":
            "Document resolution is acceptable.",
        "width":
            width,
        "height":
            height
    }


# ==========================================================
# FORENSIC ANALYSIS
# ==========================================================

def analyze_document(image_path):

    print("\n" + "=" * 60)

    print(
        "IDSHIELD AI - DOCUMENT FORENSIC ANALYSIS"
    )

    print("=" * 60)

    print(
        f"\nDocument: {image_path}"
    )


    # ------------------------------------------------------
    # Check file
    # ------------------------------------------------------

    if not image_path:

        return {

            "status": "ERROR",

            "tampering_score": 100,

            "message":
                "No document was provided."

        }


    if not os.path.exists(
        image_path
    ):

        return {

            "status": "ERROR",

            "tampering_score": 100,

            "message":
                "Document file was not found."

        }


    # ------------------------------------------------------
    # Load image
    # ------------------------------------------------------

    image = load_document(
        image_path
    )

    if image is None:

        return {

            "status": "ERROR",

            "tampering_score": 100,

            "message":
                "Unable to read document image."

        }


    # ------------------------------------------------------
    # Run checks
    # ------------------------------------------------------

    blur_score = calculate_blur_score(
        image
    )

    edge_density = calculate_edge_density(
        image
    )

    compression = compression_check(
        image_path
    )

    dimensions = dimension_check(
        image
    )


    # ------------------------------------------------------
    # Suspicion scoring
    # ------------------------------------------------------

    suspicion_score = 0

    warnings = []


    # ------------------------------------------------------
    # Resolution
    # ------------------------------------------------------

    if dimensions["status"] == "SUSPICIOUS":

        suspicion_score += 25

        warnings.append(
            "Low document image resolution."
        )


    # ------------------------------------------------------
    # Compression
    # ------------------------------------------------------

    if compression["status"] == "SUSPICIOUS":

        suspicion_score += 20

        warnings.append(
            "Unusually small/compressed document image."
        )


    # ------------------------------------------------------
    # Blur
    # ------------------------------------------------------

    if blur_score < 50:

        suspicion_score += 15

        warnings.append(
            "Document image appears heavily blurred."
        )


    # ------------------------------------------------------
    # Extremely high edge density
    # ------------------------------------------------------

    if edge_density > 35:

        suspicion_score += 10

        warnings.append(
            "Unusual edge density detected."
        )


    # ------------------------------------------------------
    # Keep score in range
    # ------------------------------------------------------

    suspicion_score = min(
        100,
        suspicion_score
    )


    # ------------------------------------------------------
    # Determine status
    # ------------------------------------------------------

    if suspicion_score >= 60:

        status = "FLAGGED"

    elif suspicion_score >= 30:

        status = "REVIEW"

    else:

        status = "PASS"


    # ------------------------------------------------------
    # Display
    # ------------------------------------------------------

    print(
        "\nBlur score       :",
        blur_score
    )

    print(
        "Edge density     :",
        edge_density,
        "%"
    )

    print(
        "Image resolution :",
        dimensions["width"],
        "x",
        dimensions["height"]
    )

    print(
        "Compression      :",
        compression["status"]
    )

    print(
        "Tampering score  :",
        suspicion_score
    )

    print(
        "Status           :",
        status
    )


    if warnings:

        print(
            "\nWarnings:"
        )

        for warning in warnings:

            print(
                "⚠️",
                warning
            )

    else:

        print(
            "\n✅ No obvious forensic anomalies detected."
        )


    # ------------------------------------------------------
    # Return
    # ------------------------------------------------------

    return {

        "status":
            status,

        "tampering_score":
            suspicion_score,

        "blur_score":
            blur_score,

        "edge_density":
            edge_density,

        "compression":
            compression,

        "dimensions":
            dimensions,

        "warnings":
            warnings,

        "message":
            (
                "Single-document forensic analysis "
                "completed."
            )

    }


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================
#
# Your pipeline currently calls:
#
# compare_documents(original, submitted)
#
# We keep that function temporarily so the rest of the
# application doesn't immediately break.
#
# Only the submitted document is actually analyzed.
# ==========================================================

def compare_documents(
    original_path,
    submitted_path
):

    print(
        "\n⚠️ Legacy comparison mode detected."
    )

    print(
        "Running single-document forensic analysis."
    )

    return analyze_document(
        submitted_path
    )


# ==========================================================
# OPTIONAL DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    test_document = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "..",
        "ocr",
        "test_documents",
        "sample_document.jpg"
    )

    test_document = os.path.abspath(
        test_document
    )

    result = analyze_document(
        test_document
    )

    print("\n")
    print(
        "=" * 60
    )

    print(
        "FINAL FORENSIC RESULT"
    )

    print(
        "=" * 60
    )

    print(result)