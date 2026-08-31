import os
import sys
import json
import gc
import cv2


# ==========================================================
# IDShield AI - COMPLETE DOCUMENT VERIFICATION PIPELINE
# ==========================================================
#
# PIPELINE
#
# 1. OCR
# 2. Document Validation
# 3. Authority / Authenticity
# 4. Forensic / Tampering Analysis
# 5. Document Portrait Extraction
# 6. Face Verification
# 7. Risk Engine
# 8. Final Decision
#
#
# FACE FLOW
#
# SELFIE
#    +
# DOCUMENT
#    ↓
# DOCUMENT PORTRAIT EXTRACTION
#    ↓
# PORTRAIT CROP
#    ↓
# NORMALIZATION
#    ↓
# ARCFACE
#    ↓
# MATCH / NO_MATCH
#
#
# IMPORTANT
#
# Face verification compares:
#
#     SELFIE
#       VS
#     DOCUMENT PORTRAIT
#
# NOT:
#
#     SELFIE
#       VS
#     WHOLE DOCUMENT
#
# ==========================================================


# ==========================================================
# PADDLEOCR CONFIGURATION
# ==========================================================

os.environ[
    "PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"
] = "0"


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
# CONFIGURATION
# ==========================================================

# ----------------------------------------------------------
# Face verification
# ----------------------------------------------------------
#
# True  = enable face verification
# False = disable face verification
#
# ----------------------------------------------------------

FACE_VERIFICATION_ENABLED = True


# ----------------------------------------------------------
# Face recognition model
# ----------------------------------------------------------

FACE_MODEL = "ArcFace"


# ----------------------------------------------------------
# Face detector
# ----------------------------------------------------------

FACE_DETECTOR = "retinaface"


# ----------------------------------------------------------
# Minimum document portrait size
# ----------------------------------------------------------

MIN_FACE_IMAGE_SIZE = 160


# ----------------------------------------------------------
# Temporary verification portrait filename
# ----------------------------------------------------------

DOCUMENT_FACE_VERIFICATION_FILENAME = (
    "document_face_verification.jpg"
)


# ==========================================================
# OCR INSTANCE
# ==========================================================

_ocr_instance = None


# ==========================================================
# MEMORY CLEANUP
# ==========================================================

def cleanup_memory():

    try:

        gc.collect()

    except Exception:

        pass


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
# STEP 1 - OCR MODEL
# ==========================================================

def get_ocr():

    global _ocr_instance

    # ------------------------------------------------------
    # Reuse OCR model
    # ------------------------------------------------------

    if _ocr_instance is not None:

        print(
            "♻️ Reusing existing OCR model"
        )

        return _ocr_instance

    # ------------------------------------------------------
    # Initialize PaddleOCR
    # ------------------------------------------------------

    print(
        "\n🔄 Initializing PaddleOCR..."
    )

    try:

        from paddleocr import PaddleOCR

        _ocr_instance = PaddleOCR(

            lang="en",

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
    # VALIDATE PATH
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
            "\n❌ OCR scanning failed:"
        )

        print(
            str(e)
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
    # EXTRACT STRUCTURED FIELDS
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
    # DISPLAY
    # ======================================================

    print_json(
        "EXTRACTED DOCUMENT DATA",
        document_data
    )

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

    status = result.get(
        "status",
        "ERROR"
    )

    if status == "PASS":

        print(
            "\n✅ DOCUMENT VALIDATION PASSED"
        )

    elif status == "FLAGGED":

        print(
            "\n⚠️ DOCUMENT VALIDATION FLAGGED"
        )

    elif status == "FAIL":

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

    status = result.get(
        "status",
        "ERROR"
    )

    if status == "VERIFIED":

        print(
            "\n✅ AUTHORITATIVE RECORD MATCHED"
        )

    elif status == "SUSPICIOUS":

        print(
            "\n❌ DOCUMENT INFORMATION IS SUSPICIOUS"
        )

    elif status == "REVIEW":

        print(
            "\n⚠️ DOCUMENT REQUIRES REVIEW"
        )

    elif status == "NOT_FOUND":

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
# STEP 4 - TAMPERING / FORENSIC ANALYSIS
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
    # VALIDATE PATH
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
    # RUN DETECTOR
    # ======================================================

    print(
        "\n🔍 Running forensic tampering analysis..."
    )

    print(
        "Please wait...\n"
    )

    try:

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
    # VALIDATE RESULT
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
                (
                    "Tampering detector returned "
                    "an invalid result."
                )

        }

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "FORENSIC ANALYSIS RESULT",
        result
    )

    status = result.get(
        "status",
        "ERROR"
    )

    if status == "PASS":

        print(
            "\n✅ NO OBVIOUS FORENSIC ANOMALIES"
        )

    elif status == "REVIEW":

        print(
            "\n⚠️ DOCUMENT REQUIRES FORENSIC REVIEW"
        )

    elif status == "FLAGGED":

        print(
            "\n❌ DOCUMENT FORENSIC CHECK FLAGGED"
        )

    else:

        print(
            "\n⚠️ FORENSIC ANALYSIS FAILED"
        )

    cleanup_memory()

    return result


# ==========================================================
# STEP 5A - DOCUMENT PORTRAIT EXTRACTION
# ==========================================================

def prepare_document_face(
    document_path
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 5A - DOCUMENT PORTRAIT EXTRACTION"
    )

    print(
        "=" * 60
    )

    print(
        "\n🧑 Searching for portrait inside document..."
    )

    # ======================================================
    # LOAD DOCUMENT FACE MODULE
    # ======================================================

    try:

        from face.document_face import (
            extract_document_face
        )

    except Exception as e:

        print(
            "\n❌ Unable to load document-face module:"
        )

        print(
            str(e)
        )

        return {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                (
                    "Document portrait module failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # OUTPUT PATH
    # ======================================================

    output_path = os.path.join(

        os.path.dirname(
            document_path
        ),

        "document_face_crop.jpg"

    )

    # ======================================================
    # EXTRACT
    # ======================================================

    try:

        result = extract_document_face(

            document_path,

            output_path

        )

    except Exception as e:

        print(
            "\n❌ Document portrait extraction failed:"
        )

        print(
            str(e)
        )

        result = {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                (
                    "Document portrait extraction failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # VALIDATE RESULT
    # ======================================================

    if not isinstance(
        result,
        dict
    ):

        result = {

            "status":
                "ERROR",

            "face_found":
                False,

            "face_path":
                None,

            "confidence":
                None,

            "facial_area":
                None,

            "message":
                "Invalid portrait extraction result."

        }

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "DOCUMENT PORTRAIT RESULT",
        result
    )

    # ======================================================
    # CHECK RESULT
    # ======================================================

    if result.get(
        "face_found",
        False
    ):

        print(
            "\n✅ DOCUMENT PORTRAIT FOUND"
        )

        print(
            "Portrait:",
            result.get(
                "face_path"
            )
        )

        print(
            "Confidence:",
            result.get(
                "confidence"
            )
        )

    else:

        print(
            "\n⚠️ NO RELIABLE DOCUMENT PORTRAIT FOUND"
        )

    cleanup_memory()

    return result


# ==========================================================
# STEP 5B - NORMALIZE DOCUMENT PORTRAIT
# ==========================================================

def normalize_document_face(
    face_path
):

    """
    Enlarges a small document portrait crop before sending
    it to the face verification model.

    Original crop is not modified.
    """

    if not face_path:

        return None

    if not os.path.exists(
        face_path
    ):

        return None

    image = cv2.imread(
        face_path
    )

    if image is None:

        return None

    try:

        height, width = image.shape[:2]

        print(
            f"\n📐 Original document portrait: "
            f"{width} x {height}"
        )

        # --------------------------------------------------
        # Calculate scale
        # --------------------------------------------------

        scale = max(

            MIN_FACE_IMAGE_SIZE / width,

            MIN_FACE_IMAGE_SIZE / height,

            1.0

        )

        # --------------------------------------------------
        # Already large enough
        # --------------------------------------------------

        if scale <= 1.0:

            del image

            cleanup_memory()

            return face_path

        # --------------------------------------------------
        # New dimensions
        # --------------------------------------------------

        new_width = int(
            width * scale
        )

        new_height = int(
            height * scale
        )

        print(
            f"🔍 Enlarging portrait to "
            f"{new_width} x {new_height}"
        )

        # --------------------------------------------------
        # Resize
        # --------------------------------------------------

        enlarged = cv2.resize(

            image,

            (
                new_width,
                new_height
            ),

            interpolation=cv2.INTER_CUBIC

        )

        # --------------------------------------------------
        # Save verification image
        # --------------------------------------------------

        directory = os.path.dirname(
            face_path
        )

        verification_path = os.path.join(

            directory,

            DOCUMENT_FACE_VERIFICATION_FILENAME

        )

        success = cv2.imwrite(

            verification_path,

            enlarged

        )

        del enlarged

        del image

        cleanup_memory()

        if not success:

            print(
                "⚠️ Could not create verification portrait."
            )

            return face_path

        print(
            "\n✅ Verification portrait created:"
        )

        print(
            verification_path
        )

        return verification_path

    except Exception as e:

        print(
            "\n⚠️ Portrait normalization failed:"
        )

        print(
            str(e)
        )

        try:

            del image

        except Exception:

            pass

        cleanup_memory()

        return face_path


# ==========================================================
# STEP 5C - FACE VERIFICATION
# ==========================================================

def run_face_verification(
    reference_face,
    document_image
):

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 5C - FACE VERIFICATION"
    )

    print(
        "=" * 60
    )

    # ======================================================
    # CHECK ENABLED
    # ======================================================

    if not FACE_VERIFICATION_ENABLED:

        print(
            "\nℹ️ Face verification is disabled."
        )

        return {

            "status":
                "NOT_AVAILABLE",

            "verified":
                False,

            "similarity_score":
                None,

            "distance":
                None,

            "threshold":
                None,

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                "Face verification is disabled."

        }

    # ======================================================
    # CHECK SELFIE
    # ======================================================

    if not reference_face:

        print(
            "\n⚠️ No selfie/reference face supplied."
        )

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
                None,

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                "No selfie/reference face was provided."

        }

    if not os.path.exists(
        reference_face
    ):

        print(
            "\n❌ Reference face not found:"
        )

        print(
            reference_face
        )

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

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                (
                    "Reference face was not found: "
                    f"{reference_face}"
                )

        }

    # ======================================================
    # CHECK DOCUMENT
    # ======================================================

    if not document_image:

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

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                "No document image was provided."

        }

    if not os.path.exists(
        document_image
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
                None,

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                (
                    "Document image was not found: "
                    f"{document_image}"
                )

        }

    # ======================================================
    # EXTRACT DOCUMENT PORTRAIT
    # ======================================================

    portrait_result = prepare_document_face(

        document_image

    )

    # ======================================================
    # VALIDATE RESULT
    # ======================================================

    if not isinstance(
        portrait_result,
        dict
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
                None,

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                "Invalid document portrait result."

        }

    # ======================================================
    # NO DOCUMENT PORTRAIT
    # ======================================================

    if not portrait_result.get(
        "face_found",
        False
    ):

        print(
            "\n⚠️ No reliable document portrait found."
        )

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
                None,

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                (
                    "No reliable portrait could be "
                    "detected in the identity document."
                )

        }

    # ======================================================
    # DOCUMENT PORTRAIT PATH
    # ======================================================

    document_face_path = portrait_result.get(
        "face_path"
    )

    if not document_face_path:

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

            "document_face_found":
                False,

            "document_face_path":
                None,

            "message":
                "Portrait extraction returned no file path."

        }

    # ======================================================
    # NORMALIZE PORTRAIT
    # ======================================================

    verification_face_path = normalize_document_face(

        document_face_path

    )

    if not verification_face_path:

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

            "document_face_found":
                True,

            "document_face_path":
                document_face_path,

            "message":
                "Unable to prepare document portrait."

        }

    # ======================================================
    # LOAD FACE VERIFIER
    # ======================================================

    try:

        from face.verifier import (
            verify_faces
        )

    except Exception as e:

        print(
            "\n❌ Unable to load face verifier:"
        )

        print(
            str(e)
        )

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

            "document_face_found":
                True,

            "document_face_path":
                verification_face_path,

            "message":
                (
                    "Face verifier could not be loaded: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # DISPLAY COMPARISON
    # ======================================================

    print(
        "\n🧠 Preparing face verification..."
    )

    print(
        "\nComparing:"
    )

    print(
        "  SELFIE"
    )

    print(
        "    ↕"
    )

    print(
        "  DOCUMENT PORTRAIT"
    )

    print(
        "\nModel:",
        FACE_MODEL
    )

    print(
        "Detector:",
        FACE_DETECTOR
    )

    # ======================================================
    # RUN FACE VERIFICATION
    # ======================================================

    try:

        result = verify_faces(

            reference_face,

            verification_face_path

        )

    except Exception as e:

        print(
            "\n❌ Face verification failed:"
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

            "document_face_found":
                True,

            "document_face_path":
                verification_face_path,

            "message":
                (
                    "Face verification failed: "
                    f"{str(e)}"
                )

        }

    # ======================================================
    # VALIDATE RESULT
    # ======================================================

    if not isinstance(
        result,
        dict
    ):

        result = {

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

            "message":
                "Face verifier returned an invalid result."

        }

    # ======================================================
    # NORMALIZE STATUS
    # ======================================================

    if result.get(
        "verified",
        False
    ):

        result["status"] = "MATCH"

    elif result.get(
        "status"
    ) not in [

        "ERROR",

        "NO_FACE",

        "NO_MATCH",

        "NO_DOCUMENT_FACE"

    ]:

        result["status"] = "NO_MATCH"

    # ======================================================
    # ADD DOCUMENT PORTRAIT INFORMATION
    # ======================================================

    result[
        "document_face_found"
    ] = True

    result[
        "document_face_path"
    ] = verification_face_path

    # ======================================================
    # DISPLAY
    # ======================================================

    print_json(
        "FACE VERIFICATION RESULT",
        result
    )

    if result.get(
        "verified",
        False
    ):

        print(
            "\n✅ FACE MATCH"
        )

    else:

        print(
            "\n❌ FACE DOES NOT MATCH"
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

    # ======================================================
    # LOAD RISK ENGINE
    # ======================================================

    try:

        from risk_engine.risk_engine import (
            calculate_risk
        )

    except Exception as e:

        print(
            "\n❌ Unable to load risk engine:"
        )

        print(
            str(e)
        )

        return {

            "risk_score":
                100,

            "risk_level":
                "HIGH",

            "decision":
                "DOCUMENT REJECTED",

            "warnings": [

                (
                    "Risk engine could not be loaded: "
                    f"{str(e)}"
                )

            ],

            "authenticity":
                authenticity_result,

            "tampering":
                tampering_result,

            "face_verification":
                face_result

        }

    # ======================================================
    # RUN CURRENT RISK ENGINE
    # ======================================================

    try:

        result = calculate_risk(

            validation_result,

            authenticity_result,

            tampering_result,

            face_result

        )

    except TypeError:

        # --------------------------------------------------
        # Legacy compatibility
        # --------------------------------------------------

        try:

            print(
                "\nℹ️ Trying legacy risk engine signature..."
            )

            result = calculate_risk(

                validation_result,

                tampering_result,

                face_result

            )

        except Exception as e:

            print(
                "\n❌ Risk engine failed:"
            )

            print(
                str(e)
            )

            result = {

                "risk_score":
                    100,

                "risk_level":
                    "HIGH",

                "decision":
                    "DOCUMENT REJECTED",

                "warnings": [

                    (
                        "Risk engine failed: "
                        f"{str(e)}"
                    )

                ]

            }

    except Exception as e:

        print(
            "\n❌ Risk engine failed:"
        )

        print(
            str(e)
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
    # BASIC RESULT
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
    # VALIDATION
    # ======================================================

    checks = result.get(
        "checks",
        {}
    )

    if checks:

        print()

        print(
            "DOCUMENT CHECKS"
        )

        print(
            "-" * 60
        )

        print(
            "Validation      :",
            checks.get(
                "validation",
                "UNKNOWN"
            )
        )

        print(
            "Authenticity    :",
            checks.get(
                "authenticity",
                "UNKNOWN"
            )
        )

        print(
            "Tampering       :",
            checks.get(
                "tampering",
                "UNKNOWN"
            )
        )

        print(
            "Face Verification:",
            checks.get(
                "face_verification",
                "UNKNOWN"
            )
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
    # TAMPERING
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
    # FACE
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

    if face.get(
        "distance"
    ) is not None:

        print(
            "FACE DISTANCE    :",
            face.get(
                "distance"
            )
        )

    if face.get(
        "threshold"
    ) is not None:

        print(
            "FACE THRESHOLD   :",
            face.get(
                "threshold"
            )
        )

    if face.get(
        "document_face_found"
    ) is not None:

        print(
            "DOCUMENT PORTRAIT:",
            face.get(
                "document_face_found"
            )
        )

    if face.get(
        "document_face_path"
    ):

        print(
            "PORTRAIT PATH    :",
            face.get(
                "document_face_path"
            )
        )

    # ======================================================
    # FINAL DECISION MESSAGE
    # ======================================================

    print()

    print(
        "-" * 60
    )

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
        "       IDSHIELD AI - COMPLETE PIPELINE"
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
        "\n🚀 STARTING DOCUMENT VALIDATION"
    )

    validation_result = run_validation(

        document_data

    )

    # ======================================================
    # STEP 3 - AUTHENTICITY
    # ======================================================

    print(
        "\n🚀 STARTING AUTHENTICITY VERIFICATION"
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
    # STEP 5 - FACE VERIFICATION
    # ======================================================

    print(
        "\n🚀 STARTING DOCUMENT FACE VERIFICATION"
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
    # CLEANUP
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

        "sample_document_with_face.jpg"

    )

    # ======================================================
    # TEST SELFIE
    # ======================================================

    REFERENCE_FACE = os.path.join(

        BASE_DIR,

        "face",

        "test_images",

        "person1.jpg"

    )

    # ======================================================
    # DISPLAY TEST FILES
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
            "Face verification will not be possible."
        )

        REFERENCE_FACE = None

    # ======================================================
    # RUN COMPLETE PIPELINE
    # ======================================================

    final_result = run_pipeline(

        DOCUMENT,

        REFERENCE_FACE

    )

    # ======================================================
    # FINAL STATUS
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