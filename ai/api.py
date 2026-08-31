# ==========================================================
# IDShield AI - FASTAPI BACKEND
# ==========================================================
#
# Purpose:
#   Expose the existing IDShield AI pipeline as an HTTP API.
#
# Flow:
#
#   Frontend
#      ↓
#   POST /verify
#      ↓
#   Save uploaded document + selfie
#      ↓
#   pipeline.run_pipeline()
#      ↓
#   OCR
#      ↓
#   Validation
#      ↓
#   Authenticity
#      ↓
#   Tampering
#      ↓
#   Document Portrait
#      ↓
#   Face Verification
#      ↓
#   Risk Engine
#      ↓
#   JSON Response
#
# ==========================================================


import os
import sys
import uuid
import shutil
import traceback


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# Make sure ai/ is available for imports
if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ==========================================================
# UPLOAD DIRECTORY
# ==========================================================

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "api_uploads"
)


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ==========================================================
# FASTAPI IMPORTS
# ==========================================================

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware


# ==========================================================
# IMPORT PIPELINE
# ==========================================================

try:

    from pipeline import run_pipeline

except Exception as e:

    print(
        "\n❌ Unable to import IDShield AI pipeline."
    )

    print(
        str(e)
    )

    raise


# ==========================================================
# CREATE FASTAPI APP
# ==========================================================

app = FastAPI(

    title="IDShield AI",

    description=(
        "AI-powered identity document "
        "verification API."
    ),

    version="1.0.0"

)


# ==========================================================
# CORS
# ==========================================================
#
# Allows:
#
#   Local Vite frontend
#   Vercel frontend
#
# We use "*" temporarily so deployment/testing does not
# fail because of an incorrect frontend domain.
#
# allow_credentials is False because we are not using
# cookie-based authentication for this API request.
#
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]

)


# ==========================================================
# ROOT ENDPOINT
# ==========================================================

@app.get("/")
def root():

    return {

        "success": True,

        "service":
            "IDShield AI",

        "message":
            "IDShield AI API is running.",

        "version":
            "1.0.0"

    }


# ==========================================================
# API HEALTH CHECK
# ==========================================================

@app.get("/api/health")
def health_check():

    return {

        "success": True,

        "status":
            "healthy",

        "service":
            "IDShield AI"

    }


# ==========================================================
# SAVE UPLOADED FILE
# ==========================================================

async def save_uploaded_file(
    uploaded_file: UploadFile,
    destination: str
):

    try:

        with open(
            destination,
            "wb"
        ) as file:

            while True:

                chunk = await uploaded_file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file.write(
                    chunk
                )

    except Exception:

        # Remove partially written file
        if os.path.exists(
            destination
        ):

            try:

                os.remove(
                    destination
                )

            except Exception:

                pass

        raise


# ==========================================================
# CLEANUP FILE
# ==========================================================

def remove_file(
    file_path
):

    if not file_path:
        return

    try:

        if os.path.exists(
            file_path
        ):

            os.remove(
                file_path
            )

    except Exception as e:

        print(
            f"⚠️ Could not remove file: {e}"
        )


# ==========================================================
# CLEANUP DIRECTORY
# ==========================================================

def remove_directory(
    directory
):

    if not directory:
        return

    try:

        if os.path.exists(
            directory
        ):

            shutil.rmtree(
                directory,
                ignore_errors=True
            )

    except Exception as e:

        print(
            f"⚠️ Could not remove upload directory: {e}"
        )


# ==========================================================
# NORMALIZE PIPELINE RESULT
# ==========================================================

def normalize_result(
    result
):

    """
    Make sure the API always returns a dictionary.
    """

    if not isinstance(
        result,
        dict
    ):

        return {

            "status":
                "ERROR",

            "message":
                "Pipeline returned an invalid result.",

            "risk":
                {

                    "risk_score":
                        100,

                    "risk_level":
                        "HIGH",

                    "decision":
                        "DOCUMENT REJECTED"

                }

        }


    return result


# ==========================================================
# MAIN VERIFICATION FUNCTION
# ==========================================================

async def process_verification(

    document: UploadFile,

    selfie: UploadFile

):

    print(
        "\n"
        + "=" * 70
    )

    print(
        "IDSHIELD AI - API VERIFICATION REQUEST"
    )

    print(
        "=" * 70
    )


    # ======================================================
    # VALIDATE DOCUMENT
    # ======================================================

    if not document:

        raise HTTPException(

            status_code=400,

            detail="Document file is required."

        )


    # ======================================================
    # VALIDATE SELFIE
    # ======================================================

    if not selfie:

        raise HTTPException(

            status_code=400,

            detail="Selfie file is required."

        )


    # ======================================================
    # FILE NAMES
    # ======================================================

    document_name = (
        document.filename
        or "document.jpg"
    )


    selfie_name = (
        selfie.filename
        or "selfie.jpg"
    )


    print(
        "\n📄 Document:"
    )

    print(
        document_name
    )


    print(
        "\n🤳 Selfie:"
    )

    print(
        selfie_name
    )


    # ======================================================
    # CREATE UNIQUE REQUEST DIRECTORY
    # ======================================================

    request_id = str(
        uuid.uuid4()
    )


    request_directory = os.path.join(

        UPLOAD_DIR,

        request_id

    )


    os.makedirs(

        request_directory,

        exist_ok=True

    )


    # ======================================================
    # FILE EXTENSIONS
    # ======================================================

    document_extension = os.path.splitext(
        document_name
    )[1].lower()


    selfie_extension = os.path.splitext(
        selfie_name
    )[1].lower()


    # Default extensions

    if not document_extension:

        document_extension = ".jpg"


    if not selfie_extension:

        selfie_extension = ".jpg"


    # ======================================================
    # FILE PATHS
    # ======================================================

    document_path = os.path.join(

        request_directory,

        "document" + document_extension

    )


    selfie_path = os.path.join(

        request_directory,

        "selfie" + selfie_extension

    )


    # ======================================================
    # SAVE DOCUMENT
    # ======================================================

    try:

        print(
            "\n💾 Saving uploaded document..."
        )


        await save_uploaded_file(

            document,

            document_path

        )


        print(
            "✅ Document saved:"
        )

        print(
            document_path
        )


    except Exception as e:

        remove_directory(
            request_directory
        )


        print(
            "\n❌ Failed to save document:"
        )

        print(
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "Failed to save document: "
                f"{str(e)}"
            )

        )


    # ======================================================
    # SAVE SELFIE
    # ======================================================

    try:

        print(
            "\n💾 Saving uploaded selfie..."
        )


        await save_uploaded_file(

            selfie,

            selfie_path

        )


        print(
            "✅ Selfie saved:"
        )

        print(
            selfie_path
        )


    except Exception as e:

        remove_directory(
            request_directory
        )


        print(
            "\n❌ Failed to save selfie:"
        )

        print(
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "Failed to save selfie: "
                f"{str(e)}"
            )

        )


    # ======================================================
    # RUN IDSHIELD AI PIPELINE
    # ======================================================

    print(
        "\n🚀 Starting IDShield AI pipeline..."
    )


    print(
        "\nDocument:"
    )

    print(
        document_path
    )


    print(
        "\nReference face:"
    )

    print(
        selfie_path
    )


    try:

        result = run_pipeline(

            document_path,

            selfie_path

        )


    except Exception as e:

        print(
            "\n❌ IDShield AI pipeline failed:"
        )

        print(
            str(e)
        )


        traceback.print_exc()


        remove_directory(
            request_directory
        )


        raise HTTPException(

            status_code=500,

            detail={
                "success":
                    False,

                "message":
                    "IDShield AI pipeline failed.",

                "error":
                    str(e)

            }

        )


    # ======================================================
    # NORMALIZE RESULT
    # ======================================================

    result = normalize_result(
        result
    )


    # ======================================================
    # ADD REQUEST INFORMATION
    # ======================================================

    result[
        "request_id"
    ] = request_id


    # ======================================================
    # API SUCCESS FLAG
    # ======================================================

    result[
        "success"
    ] = (

        result.get(
            "status"
        ) == "COMPLETED"

    )


    # ======================================================
    # DISPLAY FINAL RESULT
    # ======================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "IDSHIELD AI - API REQUEST COMPLETED"
    )

    print(
        "=" * 70
    )


    print(
        "\nRequest ID:"
    )

    print(
        request_id
    )


    if isinstance(
        result.get("risk"),
        dict
    ):

        print(
            "\nRisk score:"
        )

        print(
            result["risk"].get(
                "risk_score"
            )
        )


        print(
            "\nRisk level:"
        )

        print(
            result["risk"].get(
                "risk_level"
            )
        )


        print(
            "\nDecision:"
        )

        print(
            result["risk"].get(
                "decision"
            )
        )


    print(
        "\n✅ API verification completed."
    )


    # ======================================================
    # RETURN RESULT
    # ======================================================

    return result


# ==========================================================
# VERIFICATION ENDPOINT
# ==========================================================
#
# Primary production endpoint:
#
# POST /verify
#
# ==========================================================

@app.post("/verify")
async def verify_document(

    document: UploadFile = File(...),

    selfie: UploadFile = File(...)

):

    return await process_verification(
        document,
        selfie
    )


# ==========================================================
# BACKWARD COMPATIBILITY ENDPOINT
# ==========================================================
#
# Also support:
#
# POST /api/verify
#
# This prevents older frontend versions from breaking.
#
# ==========================================================

@app.post("/api/verify")
async def verify_document_api(

    document: UploadFile = File(...),

    selfie: UploadFile = File(...)

):

    return await process_verification(
        document,
        selfie
    )


# ==========================================================
# API INFORMATION
# ==========================================================

@app.get("/api")
def api_info():

    return {

        "name":
            "IDShield AI API",

        "version":
            "1.0.0",

        "endpoints": {

            "health":
                "/api/health",

            "verify":
                "/verify",

            "verify_legacy":
                "/api/verify"

        }

    }


# ==========================================================
# LOCAL SERVER
# ==========================================================

if __name__ == "__main__":

    import uvicorn


    # Railway provides PORT through environment variable.
    # Locally it defaults to 8000.

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )


    print(
        "\n"
    )

    print(
        "=" * 70
    )

    print(
        "       IDSHIELD AI - API SERVER"
    )

    print(
        "=" * 70
    )


    print(
        "\nStarting server..."
    )


    print(
        "\nAPI:"
    )

    print(
        f"http://127.0.0.1:{port}"
    )


    print(
        "\nSwagger documentation:"
    )

    print(
        f"http://127.0.0.1:{port}/docs"
    )


    print(
        "\nHealth check:"
    )

    print(
        f"http://127.0.0.1:{port}/api/health"
    )


    print(
        "\nVerification:"
    )

    print(
        f"http://127.0.0.1:{port}/verify"
    )


    print(
        "\nPress CTRL+C to stop."
    )


    uvicorn.run(

        app,

        host="0.0.0.0",

        port=port

    )