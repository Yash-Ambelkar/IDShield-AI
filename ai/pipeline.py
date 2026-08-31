import os
import sys
import json
import gc


# ==========================================================
# IDShield AI - HOSTED VERIFICATION PIPELINE
# ==========================================================
#
# Pipeline:
#
# 1. OCR
# 2. Document Validation
# 3. Authority / Authenticity
# 4. Forensic / Tampering Analysis
# 5. Face Verification
# 6. Risk Engine
# 7. Final Decision
#
# Hosted configuration:
#
# OCR             -> ENABLED
# Validation      -> ENABLED
# Authenticity    -> ENABLED
# Tampering       -> ENABLED
# Face            -> DISABLED
#
# Face verification is temporarily disabled because the
# current hosted instance has limited RAM.
#
# ==========================================================


# ==========================================================
# PADDLEOCR CONFIGURATION
# ==========================================================
#
# IMPORTANT:
# This must be configured BEFORE PaddleOCR/PaddlePaddle
# is imported.
#
# This prevents oneDNN / MKLDNN related errors such as:
#
# ConvertPirAttribute2RuntimeAttribute not support
# [pir::ArrayAttribute<pir::DoubleAttribute>]
#
# ==========================================================

os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:

    sys.path.insert(
        0,
        BASE_DIR
    )


# ==========================================================
# OCR MODEL
# ==========================================================

_ocr_instance = None


def get_ocr():
    """
    Initialize PaddleOCR only when required.

    The OCR model is loaded lazily and reused between
    requests to reduce memory usage.
    """

    global _ocr_instance

    # ------------------------------------------------------
    # Reuse existing OCR instance
    # ------------------------------------------------------

    if _ocr_instance is not None:

        print(
            "♻️ Reusing existing OCR model"
        )

        return _ocr_instance

    # ------------------------------------------------------
    # Initialize OCR
    # ------------------------------------------------------

    print(
        "\n🔄 Initializing PaddleOCR..."
    )

    try:

        from paddleocr import PaddleOCR

        _ocr_instance = PaddleOCR(

            lang="en",

            # Disable oneDNN / MKLDNN
            enable_mkldnn=False

        )

        print(
            "✅ PaddleOCR initialized"
        )

        return _ocr_instance

    except Exception as e:

        print(
            "\n❌ PaddleOCR initialization failed:"
        )

        print(
            str(e)
        )

        raise


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

def cleanup_memory():

    print(
        "🧹 Cleaning unused memory..."
    )

    try:

        gc.collect()

    except Exception as e:

        print(
            f"⚠️ Memory cleanup warning: {e}"
        )

    print(
        "✅ Memory cleanup completed"
    )


# ==========================================================
# SAFE JSON DISPLAY
# ==========================================================

def print_json(
    title,
    data
):

    print(
        "\n" + "-" * 60
    )

    print(
        title
    )

    print(
        "-" * 60
    )

    try:

        print(
            json.dumps(
                data,
                indent=4,
                default=str
            )
        )

    except Exception:

        print(
            data
        )


# ==========================================================
# STEP 1 - OCR
# ==========================================================

def run_ocr(
    document_path
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 1 - OCR DOCUMENT SCANNING"
    )

    print(
        "=" * 60
    )

    print(
        f"\n📄 Document: {document_path}"
    )

    # ======================================================
    # VALIDATE DOCUMENT
    # ======================================================

    if not document_path:

        return {

            "status":
                "ERROR",

            "message":
                "No document was provided."

        }

    if not os.path.exists(
        document_path
    ):

        return {

            "status":
                "ERROR",

            "message":
                (
                    "Document not found: "
                    f"{document_path}"
                )

        }

    # ======================================================
    # LOAD OCR
    # ======================================================

    try:

        ocr = get_ocr()

    except Exception as e:

        return {

            "status":
                "ERROR",

            "message":
                (
                    "OCR model initialization failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # RUN OCR
    # ======================================================

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

        print(
            f"\n❌ OCR scanning failed: {e}"
        )

        return {

            "status":
                "ERROR",

            "message":
                (
                    "OCR scanning failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # EXTRACT OCR TEXT
    # ======================================================

    all_texts = []

    try:

        for res in result:

            try:

                if not hasattr(
                    res,
                    "json"
                ):

                    continue

                data = res.json

                # Some PaddleOCR versions expose
                # json as a callable.
                if callable(data):

                    data = data()

                if not isinstance(
                    data,
                    dict
                ):

                    continue

                ocr_data = data.get(
                    "res",
                    data
                )

                if not isinstance(
                    ocr_data,
                    dict
                ):

                    continue

                texts = ocr_data.get(
                    "rec_texts",
                    []
                )

                if isinstance(
                    texts,
                    list
                ):

                    all_texts.extend(
                        texts
                    )

            except Exception as e:

                print(
                    f"⚠️ OCR parsing warning: {e}"
                )

    except Exception as e:

        return {

            "status":
                "ERROR",

            "message":
                (
                    "OCR result processing failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # DISPLAY RAW OCR
    # ======================================================

    print(
        "\n" + "-" * 60
    )

    print(
        "RAW OCR TEXT"
    )

    print(
        "-" * 60
    )

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

    # ======================================================
    # STRUCTURED FIELD EXTRACTION
    # ======================================================

    try:

        from ocr.app import extract_fields

        document_data = extract_fields(
            all_texts
        )

    except Exception as e:

        return {

            "status":
                "ERROR",

            "raw_text":
                all_texts,

            "message":
                (
                    "Field extraction failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # DISPLAY EXTRACTED DATA
    # ======================================================

    print_json(
        "EXTRACTED DOCUMENT DATA",
        document_data
    )

    # ======================================================
    # MEMORY CLEANUP
    # ======================================================

    cleanup_memory()

    # ======================================================
    # RETURN
    # ======================================================

    return {

        "status":
            "PASS",

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

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 2 - DOCUMENT VALIDATION"
    )

    print(
        "=" * 60
    )

    try:

        from validation.validator import (
            validate_document
        )

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

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "DOCUMENT VALIDATION RESULT",
        result
    )

    # ======================================================
    # DECISION
    # ======================================================

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

    cleanup_memory()

    return result


# ==========================================================
# STEP 3 - AUTHORITY / AUTHENTICITY
# ==========================================================

def run_authenticity(
    document_data
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 3 - AUTHORITY / AUTHENTICITY VERIFICATION"
    )

    print(
        "=" * 60
    )

    print(
        "\n🔎 Checking authoritative identity registry..."
    )

    try:

        from authenticity.authenticity_engine import (
            verify_against_registry
        )

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

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "AUTHORITY / AUTHENTICITY RESULT",
        result
    )

    # ======================================================
    # DECISION
    # ======================================================

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

    cleanup_memory()

    return result


# ==========================================================
# STEP 4 - DOCUMENT FORENSIC / TAMPERING ANALYSIS
# ==========================================================

def run_tampering(
    submitted_path
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 4 - DOCUMENT FORENSIC ANALYSIS"
    )

    print(
        "=" * 60
    )

    print(
        f"\nSubmitted document: {submitted_path}"
    )

    # ======================================================
    # CHECK DOCUMENT
    # ======================================================

    if not submitted_path:

        return {

            "status":
                "ERROR",

            "tampering_score":
                100,

            "message":
                "No submitted document was provided."

        }

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

    # ======================================================
    # RUN FORENSIC DETECTOR
    # ======================================================

    print(
        "\n🔍 Running forensic tampering analysis..."
    )

    print(
        "Please wait...\n"
    )

    try:

        # Lazy import to avoid loading the detector
        # until it is actually required.

        from tampering.detector import (
            analyze_document
        )

        result = analyze_document(
            submitted_path
        )

    except Exception as e:

        print(
            "\n⚠️ Tampering detector failed:"
        )

        print(
            str(e)
        )

        result = {

            "status":
                "ERROR",

            "tampering_score":
                None,

            "message":
                (
                    "Forensic analysis failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # MAKE SURE RESULT IS A DICTIONARY
    # ======================================================

    if not isinstance(
        result,
        dict
    ):

        result = {

            "status":
                "ERROR",

            "tampering_score":
                None,

            "message":
                "Tampering detector returned an invalid result."

        }

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "FORENSIC ANALYSIS RESULT",
        result
    )

    # ======================================================
    # DECISION
    # ======================================================

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

    elif result.get(
        "status"
    ) == "ERROR":

        print(
            "\n⚠️ FORENSIC ANALYSIS FAILED"
        )

    else:

        print(
            "\n⚠️ UNKNOWN FORENSIC RESULT"
        )

    cleanup_memory()

    return result


# ==========================================================
# STEP 5 - FACE VERIFICATION
# ==========================================================

def run_face_verification(
    reference_face,
    document_image
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 5 - FACE VERIFICATION"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # TEMPORARILY DISABLED
    # ======================================================
    #
    # We keep this disabled on the current low-memory
    # hosted instance.
    #
    # The function remains in the pipeline so that face
    # verification can be enabled later without changing
    # the API structure.
    #
    # ======================================================

    if not reference_face:

        print(
            "\nℹ️ No selfie/reference face provided."
        )

    else:

        print(
            "\nℹ️ Face verification is temporarily "
            "disabled on the hosted instance."
        )

    result = {

        "status":
            "NOT_AVAILABLE",

        "similarity_score":
            None,

        "message":
            (
                "Face verification is temporarily "
                "unavailable on the current hosted instance."
            )

    }

    print_json(
        "FACE VERIFICATION RESULT",
        result
    )

    cleanup_memory()

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

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 6 - RISK ENGINE"
    )

    print(
        "=" * 60
    )

    try:

        from risk_engine.risk_engine import (
            calculate_risk
        )

        # ==================================================
        # TRY CURRENT RISK ENGINE
        # ==================================================

        try:

            result = calculate_risk(

                validation_result,

                authenticity_result,

                tampering_result,

                face_result

            )

        # ==================================================
        # LEGACY RISK ENGINE
        # ==================================================

        except TypeError:

            print(
                "\nℹ️ Using legacy risk engine signature..."
            )

            result = calculate_risk(

                validation_result,

                tampering_result,

                face_result

            )

    except Exception as e:

        print(
            f"\n❌ Risk engine failed: {e}"
        )

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

                (
                    "Risk engine error: "
                    f"{str(e)}"
                )

            ]

        }

    # ======================================================
    # VALIDATE RESULT
    # ======================================================

    if not isinstance(
        result,
        dict
    ):

        result = {

            "risk_score":
                100,

            "risk_level":
                "HIGH",

            "decision":
                "DOCUMENT REJECTED",

            "warnings": [

                "Risk engine returned an invalid result."

            ]

        }

    # ======================================================
    # ALWAYS EXPOSE AUTHENTICITY
    # ======================================================

    if "authenticity" not in result:

        result[
            "authenticity"
        ] = authenticity_result

    # ======================================================
    # ALWAYS EXPOSE TAMPERING
    # ======================================================

    if "tampering" not in result:

        result[
            "tampering"
        ] = tampering_result

    # ======================================================
    # ALWAYS EXPOSE FACE
    # ======================================================

    if "face_verification" not in result:

        result[
            "face_verification"
        ] = face_result

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "RISK ENGINE RESULT",
        result
    )

    cleanup_memory()

    return result


# ==========================================================
# FINAL DECISION DISPLAY
# ==========================================================

def display_final_decision(
    result
):

    print(
        "\n"
    )

    print(
        "=" * 60
    )

    print(
        "             IDSHIELD AI"
    )

    print(
        "          FINAL DECISION"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # BASIC VALUES
    # ======================================================

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
    # FACE RESULT
    # ======================================================

    face = result.get(
        "face_verification",
        {}
    )

    print()

    print(
        "FACE STATUS      :",
        face.get(
            "status",
            "UNKNOWN"
        )
    )

    if face.get(
        "similarity_score"
    ) is not None:

        print(
            "FACE SIMILARITY  :",
            face.get(
                "similarity_score"
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

        print(
            "-" * 60
        )

        print(
            "WARNINGS"
        )

        print(
            "-" * 60
        )

        for warning in warnings:

            print(
                "⚠️",
                warning
            )

    print()

    print(
        "=" * 60
    )


# ==========================================================
# COMPLETE PIPELINE
# ==========================================================

def run_pipeline(
    document_path,
    reference_face_path=None
):

    print(
        "\n"
    )

    print(
        "=" * 60
    )

    print(
        "       IDSHIELD AI - HOSTED PIPELINE"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # INPUT VALIDATION
    # ======================================================

    if not document_path:

        return {

            "status":
                "ERROR",

            "stage":
                "INPUT",

            "message":
                "No document was provided."

        }

    if not os.path.exists(
        document_path
    ):

        return {

            "status":
                "ERROR",

            "stage":
                "INPUT",

            "message":
                (
                    "Document not found: "
                    f"{document_path}"
                )

        }

    # ======================================================
    # STEP 1 - OCR
    # ======================================================

    print(
        "\n🚀 STARTING OCR"
    )

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

        cleanup_memory()

        return {

            "status":
                "ERROR",

            "stage":
                "OCR",

            "message":
                ocr_result.get(
                    "message",
                    "OCR error"
                ),

            "ocr":
                ocr_result

        }

    # ======================================================
    # DOCUMENT DATA
    # ======================================================

    document_data = ocr_result.get(
        "document_data",
        {}
    )

    # ======================================================
    # STEP 2 - VALIDATION
    # ======================================================

    print(
        "\n🚀 STARTING VALIDATION"
    )

    validation_result = run_validation(
        document_data
    )

    # ======================================================
    # STEP 3 - AUTHENTICITY
    # ======================================================

    print(
        "\n🚀 STARTING AUTHENTICITY"
    )

    authenticity_result = run_authenticity(
        document_data
    )

    # ======================================================
    # STEP 4 - TAMPERING
    # ======================================================

    print(
        "\n🚀 STARTING TAMPERING DETECTION"
    )

    tampering_result = run_tampering(
        document_path
    )

    # ======================================================
    # STEP 5 - FACE
    # ======================================================

    print(
        "\n🚀 STARTING FACE VERIFICATION"
    )

    face_result = run_face_verification(

        reference_face_path,

        document_path

    )

    # ======================================================
    # STEP 6 - RISK ENGINE
    # ======================================================

    print(
        "\n🚀 STARTING RISK ENGINE"
    )

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
    # FINAL CLEANUP
    # ======================================================

    cleanup_memory()

    # ======================================================
    # COMPLETE RESULT
    # ======================================================

    final_result = {

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

    print(
        "\n✅ IDShield AI pipeline completed."
    )

    return final_result


# ==========================================================
# LOCAL TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "\n"
    )

    print(
        "=" * 60
    )

    print(
        "IDSHIELD AI - LOCAL PIPELINE TEST"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # TEST DOCUMENT
    # ======================================================

    DOCUMENT = os.path.join(

        BASE_DIR,

        "ocr",

        "test_documents",

        "sample_document.jpg"

    )

    # ======================================================
    # TEST REFERENCE FACE
    # ======================================================

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

    print(
        "\n"
    )

    print(
        "=" * 60
    )

    print(
        "       IDSHIELD AI - PIPELINE COMPLETED"
    )

    print(
        "=" * 60
    )

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

            print(
                "Stage:",
                final_result.get(
                    "stage",
                    "UNKNOWN"
                )
            )

            print(
                "Message:",
                final_result.get(
                    "message",
                    "Unknown error"
                )
            )

        else:

            print(
                "\n✅ Pipeline result generated successfully."
            )

    print(
        "=" * 60
    )