import os
import json
import sys


# ==========================================================
# IDShield AI - COMPLETE VERIFICATION PIPELINE
# ==========================================================


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ==========================================================
# IMPORT MODULES
# ==========================================================

from ocr.app import extract_fields

from validation.validator import (
    validate_document
)

from tampering.detector import (
    analyze_document
)

from face.verifier import (
    verify_faces
)

from authenticity.authenticity_engine import (
    verify_against_registry
)

from risk_engine.risk_engine import (
    calculate_risk
)

from paddleocr import PaddleOCR


# ==========================================================
# STEP 1 - OCR
# ==========================================================

def run_ocr(document_path):

    print("\n" + "=" * 60)
    print("STEP 1 - OCR DOCUMENT SCANNING")
    print("=" * 60)

    print(
        f"\n📄 Document: {document_path}"
    )

    # ------------------------------------------------------
    # Check document
    # ------------------------------------------------------

    if not document_path:

        return {
            "status": "ERROR",
            "message": "No document was provided."
        }

    if not os.path.exists(document_path):

        return {
            "status": "ERROR",
            "message":
                f"Document not found: {document_path}"
        }

    # ------------------------------------------------------
    # Load OCR model
    # ------------------------------------------------------

    print("\n🔄 Loading OCR model...")

    try:

        ocr = PaddleOCR(
            lang="en"
        )

        print(
            "✅ OCR model loaded!"
        )

    except Exception as e:

        return {
            "status": "ERROR",
            "message":
                f"OCR model error: {str(e)}"
        }

    # ------------------------------------------------------
    # Run OCR
    # ------------------------------------------------------

    print(
        "\n🔍 Scanning document..."
    )

    print(
        "Please wait...\n"
    )

    try:

        result = ocr.predict(
            document_path
        )

    except Exception as e:

        return {
            "status": "ERROR",
            "message":
                f"OCR scanning failed: {str(e)}"
        }

    # ------------------------------------------------------
    # Extract OCR text
    # ------------------------------------------------------

    all_texts = []

    for res in result:

        try:

            if hasattr(
                res,
                "json"
            ):

                data = res.json

                if callable(data):

                    data = data()

                if isinstance(
                    data,
                    dict
                ):

                    ocr_data = data.get(
                        "res",
                        data
                    )

                    if isinstance(
                        ocr_data,
                        dict
                    ):

                        texts = ocr_data.get(
                            "rec_texts",
                            []
                        )

                        if texts:

                            all_texts.extend(
                                texts
                            )

        except Exception as e:

            print(
                f"⚠️ OCR result parsing warning: {e}"
            )

    # ------------------------------------------------------
    # Display raw OCR
    # ------------------------------------------------------

    print("-" * 60)
    print("RAW OCR TEXT")
    print("-" * 60)

    if all_texts:

        for text in all_texts:

            print(
                "•",
                text
            )

    else:

        print(
            "⚠️ No text detected."
        )

    # ------------------------------------------------------
    # Extract structured fields
    # ------------------------------------------------------

    try:

        document_data = extract_fields(
            all_texts
        )

    except Exception as e:

        return {
            "status": "ERROR",

            "raw_text":
                all_texts,

            "message":
                f"Field extraction failed: {str(e)}"
        }

    # ------------------------------------------------------
    # Display extracted data
    # ------------------------------------------------------

    print(
        "\n" + "-" * 60
    )

    print(
        "EXTRACTED DOCUMENT DATA"
    )

    print(
        "-" * 60
    )

    print(
        json.dumps(
            document_data,
            indent=4
        )
    )

    # ------------------------------------------------------
    # Return
    # ------------------------------------------------------

    return {

        "status": "PASS",

        "raw_text":
            all_texts,

        "document_data":
            document_data

    }


# ==========================================================
# STEP 2 - DOCUMENT VALIDATION
# ==========================================================

def run_validation(
    document_data
):

    print("\n" + "=" * 60)

    print(
        "STEP 2 - DOCUMENT VALIDATION"
    )

    print("=" * 60)

    try:

        result = validate_document(
            document_data
        )

    except Exception as e:

        result = {

            "status":
                "ERROR",

            "message":
                str(e)

        }

    # ------------------------------------------------------
    # Display
    # ------------------------------------------------------

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ------------------------------------------------------
    # Decision
    # ------------------------------------------------------

    if result.get(
        "status"
    ) == "PASS":

        print(
            "\n✅ DOCUMENT VALIDATION PASSED"
        )

    elif result.get(
        "status"
    ) == "FLAGGED":

        print(
            "\n⚠️ DOCUMENT VALIDATION FLAGGED"
        )

    elif result.get(
        "status"
    ) == "FAIL":

        print(
            "\n❌ DOCUMENT VALIDATION FAILED"
        )

    else:

        print(
            "\n⚠️ DOCUMENT VALIDATION ERROR"
        )

    return result


# ==========================================================
# STEP 3 - AUTHORITY / AUTHENTICITY VERIFICATION
# ==========================================================

def run_authenticity(
    document_data
):

    print("\n" + "=" * 60)

    print(
        "STEP 3 - AUTHORITY / AUTHENTICITY VERIFICATION"
    )

    print("=" * 60)

    print(
        "\n🔎 Checking authoritative identity registry..."
    )

    try:

        result = verify_against_registry(
            document_data
        )

    except Exception as e:

        result = {

            "status":
                "ERROR",

            "record_found":
                False,

            "registry_match":
                False,

            "match_score":
                0,

            "message":
                (
                    "Authority verification error: "
                    f"{str(e)}"
                ),

            "comparison":
                {}

        }

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ------------------------------------------------------
    # Decision
    # ------------------------------------------------------

    if result.get(
        "status"
    ) == "VERIFIED":

        print(
            "\n✅ AUTHORITATIVE RECORD MATCHED"
        )

    elif result.get(
        "status"
    ) == "SUSPICIOUS":

        print(
            "\n❌ DOCUMENT INFORMATION IS SUSPICIOUS"
        )

    elif result.get(
        "status"
    ) == "REVIEW":

        print(
            "\n⚠️ DOCUMENT REQUIRES REVIEW"
        )

    elif result.get(
        "status"
    ) == "NOT_FOUND":

        print(
            "\n⚠️ NO AUTHORITATIVE RECORD FOUND"
        )

    else:

        print(
            "\n⚠️ AUTHORITY VERIFICATION ERROR"
        )

    return result


# ==========================================================
# STEP 4 - DOCUMENT FORENSIC ANALYSIS
# ==========================================================

def run_tampering(
    submitted_path
):

    print("\n" + "=" * 60)

    print(
        "STEP 4 - DOCUMENT FORENSIC ANALYSIS"
    )

    print("=" * 60)

    print(
        f"\nSubmitted document: {submitted_path}"
    )

    # ------------------------------------------------------
    # Check document path
    # ------------------------------------------------------

    if not submitted_path:

        return {

            "status":
                "ERROR",

            "tampering_score":
                100,

            "message":
                "No submitted document was provided."

        }

    # ------------------------------------------------------
    # Check file
    # ------------------------------------------------------

    if not os.path.exists(
        submitted_path
    ):

        return {

            "status":
                "ERROR",

            "tampering_score":
                100,

            "message":
                "Submitted document was not found."

        }

    # ------------------------------------------------------
    # Run forensic detector
    # ------------------------------------------------------

    print(
        "\n🔍 Running document forensic analysis..."
    )

    print(
        "Please wait...\n"
    )

    try:

        result = analyze_document(
            submitted_path
        )

    except Exception as e:

        result = {

            "status":
                "ERROR",

            "tampering_score":
                100,

            "message":
                str(e)

        }

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    print("-" * 60)

    print(
        "FORENSIC ANALYSIS RESULT"
    )

    print("-" * 60)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ------------------------------------------------------
    # Decision
    # ------------------------------------------------------

    if result.get(
        "status"
    ) == "PASS":

        print(
            "\n✅ NO OBVIOUS FORENSIC ANOMALIES"
        )

    elif result.get(
        "status"
    ) == "REVIEW":

        print(
            "\n⚠️ DOCUMENT REQUIRES FORENSIC REVIEW"
        )

    elif result.get(
        "status"
    ) == "FLAGGED":

        print(
            "\n❌ DOCUMENT FORENSIC CHECK FLAGGED"
        )

    else:

        print(
            "\n❌ FORENSIC ANALYSIS ERROR"
        )

        print(
            result.get(
                "message",
                "Unknown forensic error"
            )
        )

    return result


# ==========================================================
# STEP 5 - FACE VERIFICATION
# ==========================================================

def run_face_verification(
    reference_face,
    document_image
):

    print("\n" + "=" * 60)

    print(
        "STEP 5 - FACE VERIFICATION"
    )

    print("=" * 60)

    # ======================================================
    # NO SELFIE
    # ======================================================

    if not reference_face:

        print(
            "\nℹ️ No selfie/reference face provided."
        )

        print(
            "Face verification will be skipped."
        )

        return {

            "status":
                "NOT_AVAILABLE",

            "similarity_score":
                None,

            "message":
                "No reference face was provided."

        }

    # ======================================================
    # CHECK REFERENCE FACE
    # ======================================================

    if not os.path.exists(
        reference_face
    ):

        print(
            "\n⚠️ Reference face not found."
        )

        return {

            "status":
                "NOT_AVAILABLE",

            "similarity_score":
                None,

            "message":
                "Reference face was not found."

        }

    # ======================================================
    # CHECK DOCUMENT
    # ======================================================

    if not document_image:

        return {

            "status":
                "ERROR",

            "similarity_score":
                None,

            "message":
                "Document image was not provided."

        }

    if not os.path.exists(
        document_image
    ):

        return {

            "status":
                "ERROR",

            "similarity_score":
                None,

            "message":
                (
                    "Document image not found: "
                    f"{document_image}"
                )

        }

    # ======================================================
    # DISPLAY
    # ======================================================

    print(
        f"\nReference face : {reference_face}"
    )

    print(
        f"Document image : {document_image}"
    )

    print(
        "\n🔄 Running face verification..."
    )

    print(
        "Please wait...\n"
    )

    # ======================================================
    # RUN FACE VERIFICATION
    # ======================================================

    try:

        result = verify_faces(

            reference_face,

            document_image

        )

    except Exception as e:

        result = {

            "status":
                "ERROR",

            "similarity_score":
                None,

            "message":
                str(e)

        }

    # ======================================================
    # DISPLAY RESULT
    # ======================================================

    print("-" * 60)

    print(
        "FACE VERIFICATION RESULT"
    )

    print("-" * 60)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ======================================================
    # DECISION
    # ======================================================

    if result.get(
        "status"
    ) == "MATCH":

        print(
            "\n✅ FACE MATCH"
        )

    elif result.get(
        "status"
    ) == "NO_MATCH":

        print(
            "\n❌ FACE DOES NOT MATCH"
        )

    elif result.get(
        "status"
    ) == "NO_FACE":

        print(
            "\n⚠️ NO FACE FOUND"
        )

    elif result.get(
        "status"
    ) == "NOT_AVAILABLE":

        print(
            "\nℹ️ FACE VERIFICATION NOT AVAILABLE"
        )

    else:

        print(
            "\n⚠️ FACE VERIFICATION ERROR"
        )

        print(
            result.get(
                "message",
                "Unknown face verification error"
            )
        )

    return result


# ==========================================================
# STEP 6 - RISK ENGINE
# ==========================================================

def run_risk_engine(
    validation_result,
    authenticity_result,
    tampering_result,
    face_result
):

    print("\n" + "=" * 60)

    print(
        "STEP 6 - RISK ENGINE"
    )

    print("=" * 60)

    try:

        result = calculate_risk(

            validation_result,

            authenticity_result,

            tampering_result,

            face_result

        )

    except TypeError:

        # --------------------------------------------------
        # Compatibility with older risk engine
        # --------------------------------------------------

        try:

            result = calculate_risk(

                validation_result,

                tampering_result,

                face_result

            )

        except Exception as e:

            result = {

                "risk_score":
                    100,

                "risk_level":
                    "HIGH",

                "decision":
                    "DOCUMENT REJECTED",

                "checks": {

                    "validation":
                        validation_result.get(
                            "status",
                            "ERROR"
                        ),

                    "authenticity":
                        authenticity_result.get(
                            "status",
                            "ERROR"
                        ),

                    "tampering":
                        tampering_result.get(
                            "status",
                            "ERROR"
                        ),

                    "face_verification":
                        face_result.get(
                            "status",
                            "ERROR"
                        )

                },

                "warnings": [

                    f"Risk engine error: {str(e)}"

                ]

            }

    except Exception as e:

        result = {

            "risk_score":
                100,

            "risk_level":
                "HIGH",

            "decision":
                "DOCUMENT REJECTED",

            "checks": {

                "validation":
                    validation_result.get(
                        "status",
                        "ERROR"
                    ),

                "authenticity":
                    authenticity_result.get(
                        "status",
                        "ERROR"
                    ),

                "tampering":
                    tampering_result.get(
                        "status",
                        "ERROR"
                    ),

                "face_verification":
                    face_result.get(
                        "status",
                        "ERROR"
                    )

            },

            "warnings": [

                f"Risk engine error: {str(e)}"

            ]

        }

    # ======================================================
    # Always expose authenticity
    # ======================================================

    if "authenticity" not in result:

        result[
            "authenticity"
        ] = authenticity_result

    # ======================================================
    # Always expose forensic result
    # ======================================================

    if "tampering" not in result:

        result[
            "tampering"
        ] = tampering_result

    # ======================================================
    # Display
    # ======================================================

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    return result


# ==========================================================
# FINAL DECISION
# ==========================================================

def display_final_decision(
    result
):

    print("\n")

    print("=" * 60)

    print(
        "             IDSHIELD AI"
    )

    print(
        "          FINAL DECISION"
    )

    print("=" * 60)

    # ------------------------------------------------------
    # Basic values
    # ------------------------------------------------------

    decision = result.get(
        "decision",
        "UNKNOWN"
    )

    risk_level = result.get(
        "risk_level",
        "UNKNOWN"
    )

    risk_score = result.get(
        "risk_score",
        0
    )

    print()

    print(
        "FINAL DECISION :",
        decision
    )

    print(
        "RISK LEVEL     :",
        risk_level
    )

    print(
        "RISK SCORE     :",
        risk_score
    )

    # ======================================================
    # AUTHENTICITY
    # ======================================================

    authenticity = result.get(
        "authenticity",
        {}
    )

    print()

    print(
        "AUTHORITY STATUS:",
        authenticity.get(
            "status",
            "UNKNOWN"
        )
    )

    if authenticity.get(
        "record_found"
    ) is not None:

        print(
            "RECORD FOUND     :",
            authenticity.get(
                "record_found"
            )
        )

    if authenticity.get(
        "match_score"
    ) is not None:

        print(
            "AUTHORITY MATCH  :",
            authenticity.get(
                "match_score"
            ),
            "%"
        )

    # ======================================================
    # FORENSIC RESULT
    # ======================================================

    tampering = result.get(
        "tampering",
        {}
    )

    print()

    print(
        "FORENSIC STATUS  :",
        tampering.get(
            "status",
            "UNKNOWN"
        )
    )

    if tampering.get(
        "tampering_score"
    ) is not None:

        print(
            "TAMPERING SCORE  :",
            tampering.get(
                "tampering_score"
            )
        )

    # ======================================================
    # FINAL MESSAGE
    # ======================================================

    print()

    if decision == "DOCUMENT APPROVED":

        print(
            "✅ DOCUMENT APPROVED"
        )

    elif decision == "DOCUMENT REJECTED":

        print(
            "❌ DOCUMENT REJECTED"
        )

    else:

        print(
            "⚠️ DOCUMENT REQUIRES REVIEW"
        )

    # ======================================================
    # WARNINGS
    # ======================================================

    warnings = result.get(
        "warnings",
        []
    )

    if warnings:

        print()

        print("-" * 60)

        print(
            "WARNINGS"
        )

        print("-" * 60)

        for warning in warnings:

            print(
                "⚠️",
                warning
            )

    print()

    print("=" * 60)


# ==========================================================
# COMPLETE PIPELINE
# ==========================================================

def run_pipeline(
    document_path,
    reference_face_path=None
):

    print("\n")

    print("=" * 60)

    print(
        "       IDSHIELD AI - COMPLETE PIPELINE"
    )

    print("=" * 60)

    # ======================================================
    # STEP 1 - OCR
    # ======================================================

    ocr_result = run_ocr(
        document_path
    )

    if ocr_result.get(
        "status"
    ) == "ERROR":

        print(
            "\n❌ PIPELINE STOPPED AT OCR"
        )

        print(
            ocr_result.get(
                "message",
                "OCR error"
            )
        )

        return {

            "status":
                "ERROR",

            "stage":
                "OCR",

            "message":
                ocr_result.get(
                    "message",
                    "OCR error"
                )

        }

    document_data = ocr_result.get(
        "document_data",
        {}
    )

    # ======================================================
    # STEP 2 - VALIDATION
    # ======================================================

    validation_result = run_validation(

        document_data

    )

    # ======================================================
    # STEP 3 - AUTHORITY / AUTHENTICITY
    # ======================================================

    authenticity_result = run_authenticity(

        document_data

    )

    # ======================================================
    # STEP 4 - FORENSIC ANALYSIS
    # ======================================================

    tampering_result = run_tampering(

        document_path

    )

    # ======================================================
    # STEP 5 - FACE VERIFICATION
    # ======================================================

    face_result = run_face_verification(

        reference_face_path,

        document_path

    )

    # ======================================================
    # STEP 6 - RISK ENGINE
    # ======================================================

    risk_result = run_risk_engine(

        validation_result,

        authenticity_result,

        tampering_result,

        face_result

    )

    # ======================================================
    # FINAL DECISION
    # ======================================================

    display_final_decision(

        risk_result

    )

    # ======================================================
    # COMPLETE RESULT
    # ======================================================

    return {

        "status":
            "COMPLETED",

        "ocr":
            ocr_result,

        "validation":
            validation_result,

        "authenticity":
            authenticity_result,

        "tampering":
            tampering_result,

        "face_verification":
            face_result,

        "risk":
            risk_result

    }


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    # ------------------------------------------------------
    # TEST DOCUMENT
    # ------------------------------------------------------

    DOCUMENT = os.path.join(

        BASE_DIR,

        "ocr",

        "test_documents",

        "sample_document.jpg"

    )

    # ------------------------------------------------------
    # TEST REFERENCE FACE
    # ------------------------------------------------------

    REFERENCE_FACE = os.path.join(

        BASE_DIR,

        "face",

        "test_images",

        "person1.jpg"

    )

    # ======================================================
    # DISPLAY FILES
    # ======================================================

    print(
        "\nChecking test files...\n"
    )

    print(
        "Document       :",
        DOCUMENT
    )

    print(
        "Reference face :",
        REFERENCE_FACE
    )

    # ======================================================
    # DOCUMENT CHECK
    # ======================================================

    if not os.path.exists(
        DOCUMENT
    ):

        print(
            "\n❌ Document file not found!"
        )

        print(
            DOCUMENT
        )

        sys.exit(1)

    # ======================================================
    # REFERENCE FACE CHECK
    # ======================================================

    if not os.path.exists(
        REFERENCE_FACE
    ):

        print(
            "\n⚠️ Reference face not found."
        )

        print(
            "Face verification will be skipped."
        )

        REFERENCE_FACE = None

    # ======================================================
    # RUN PIPELINE
    # ======================================================

    final_result = run_pipeline(

        DOCUMENT,

        REFERENCE_FACE

    )

    # ======================================================
    # COMPLETED
    # ======================================================

    print("\n")

    print("=" * 60)

    print(
        "       IDSHIELD AI - PIPELINE COMPLETED"
    )

    print("=" * 60)

    if isinstance(
        final_result,
        dict
    ):

        if final_result.get(
            "status"
        ) == "ERROR":

            print(
                "\n❌ Pipeline completed with an error."
            )

        else:

            print(
                "\n✅ Pipeline result generated successfully."
            )

    print("=" * 60)