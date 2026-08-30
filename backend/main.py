import os
import sys
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# ==========================================================
# IDShield AI - BACKEND API
# ==========================================================


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AI_DIR = os.path.join(
    PROJECT_DIR,
    "ai"
)

TEMP_DIR = os.path.join(
    PROJECT_DIR,
    "backend",
    "temp"
)


# ==========================================================
# CREATE TEMP DIRECTORY
# ==========================================================

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)


# ==========================================================
# ADD AI DIRECTORY TO PYTHON PATH
# ==========================================================

if AI_DIR not in sys.path:

    sys.path.insert(
        0,
        AI_DIR
    )


# ==========================================================
# IMPORT IDSHIELD PIPELINE
# ==========================================================

from pipeline import run_pipeline


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(

    title="IDShield AI API",

    description=(
        "AI-powered identity verification "
        "and document authenticity platform"
    ),

    version="1.0.0"
)


# ==========================================================
# SERVE UPLOADED FILES
# ==========================================================
#
# This allows the frontend to display the uploaded
# document and selfie using a normal image URL.
#
# Example:
#
# http://127.0.0.1:8000/files/ID-ABC12345/xxxxx.png
#
# ==========================================================

app.mount(
    "/files",
    StaticFiles(
        directory=TEMP_DIR
    ),
    name="files"
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173",

        "http://127.0.0.1:5173"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {

        "success": True,

        "message":
            "IDShield AI backend is running",

        "version":
            "1.0.0"

    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():

    return {

        "success": True,

        "status":
            "online",

        "service":
            "IDShield AI"

    }


# ==========================================================
# SAVE UPLOADED FILE
# ==========================================================

async def save_upload(

    upload_file: UploadFile,

    folder: str

):

    # ------------------------------------------------------
    # Get original filename
    # ------------------------------------------------------

    original_filename = (

        upload_file.filename

        or ""

    )


    # ------------------------------------------------------
    # Get file extension
    # ------------------------------------------------------

    extension = os.path.splitext(

        original_filename

    )[1].lower()


    # ------------------------------------------------------
    # Generate unique filename
    # ------------------------------------------------------

    filename = (

        f"{uuid.uuid4().hex}"

        f"{extension}"

    )


    # ------------------------------------------------------
    # Create file path
    # ------------------------------------------------------

    file_path = os.path.join(

        folder,

        filename

    )


    # ------------------------------------------------------
    # Save file
    # ------------------------------------------------------

    with open(

        file_path,

        "wb"

    ) as buffer:

        shutil.copyfileobj(

            upload_file.file,

            buffer

        )


    return file_path


# ==========================================================
# VERIFICATION API
# ==========================================================

@app.post("/verify")
async def verify_document(

    # ------------------------------------------------------
    # DOCUMENT REQUIRED
    # ------------------------------------------------------

    document: UploadFile = File(...),

    # ------------------------------------------------------
    # SELFIE OPTIONAL
    # ------------------------------------------------------

    selfie: UploadFile = File(None)

):

    # ======================================================
    # CREATE VERIFICATION ID
    # ======================================================

    verification_id = (

        f"ID-"

        f"{uuid.uuid4().hex[:8].upper()}"

    )


    # ======================================================
    # CREATE VERIFICATION DIRECTORY
    # ======================================================

    verification_dir = os.path.join(

        TEMP_DIR,

        verification_id

    )


    os.makedirs(

        verification_dir,

        exist_ok=True

    )


    try:

        # ==================================================
        # VALIDATE DOCUMENT
        # ==================================================

        if not document:

            return {

                "success": False,

                "verification_id":
                    verification_id,

                "message":
                    "Identity document is required."

            }


        # ==================================================
        # SAVE DOCUMENT
        # ==================================================

        document_path = await save_upload(

            document,

            verification_dir

        )


        # ==================================================
        # SAVE SELFIE IF PROVIDED
        # ==================================================

        selfie_path = None


        if selfie:

            selfie_path = await save_upload(

                selfie,

                verification_dir

            )


        # ==================================================
        # DISPLAY VERIFICATION INFORMATION
        # ==================================================

        print("\n")

        print("=" * 60)

        print(
            "IDSHIELD AI - NEW VERIFICATION"
        )

        print("=" * 60)


        print(

            f"Verification ID : "
            f"{verification_id}"

        )


        print(

            f"Document        : "
            f"{document.filename}"

        )


        if selfie:

            print(

                f"Selfie          : "
                f"{selfie.filename}"

            )

        else:

            print(

                "Selfie          : "
                "Not provided"

            )


        print(

            f"Document saved  : "
            f"{document_path}"

        )


        if selfie_path:

            print(

                f"Selfie saved    : "
                f"{selfie_path}"

            )


        # ==================================================
        # RUN COMPLETE AI PIPELINE
        # ==================================================

        print("\n")

        print(
            "🚀 Starting IDShield AI pipeline..."
        )


        # --------------------------------------------------
        # Current pipeline accepts:
        #
        # run_pipeline(
        #     document_path,
        #     reference_face_path
        # )
        #
        # --------------------------------------------------

        result = run_pipeline(

            document_path,

            selfie_path

        )


        # ==================================================
        # PIPELINE RETURN CHECK
        # ==================================================

        if result is None:

            print(

                "\n❌ Pipeline returned "
                "no result."

            )


            return {

                "success": False,

                "verification_id":
                    verification_id,

                "message":
                    "Verification pipeline failed."

            }


        # ==================================================
        # PIPELINE ERROR
        # ==================================================

        if isinstance(

            result,

            dict

        ):

            if result.get(
                "status"
            ) == "ERROR":

                return {

                    "success": False,

                    "verification_id":
                        verification_id,

                    "result":
                        result,

                    "message":
                        result.get(

                            "message",

                            "Pipeline error."

                        )

                }


        # ==================================================
        # CREATE FILE URLS
        # ==================================================
        #
        # These URLs are returned to the frontend.
        #
        # The frontend can use them directly inside:
        #
        # <img src={...} />
        #
        # ==================================================

        document_filename = os.path.basename(

            document_path

        )


        document_url = (

            f"/files/"
            f"{verification_id}/"
            f"{document_filename}"

        )


        selfie_url = None


        if selfie_path:

            selfie_filename = os.path.basename(

                selfie_path

            )

            selfie_url = (

                f"/files/"
                f"{verification_id}/"
                f"{selfie_filename}"

            )


        # ==================================================
        # VERIFICATION COMPLETED
        # ==================================================

        print("\n")

        print("=" * 60)

        print(
            "✅ VERIFICATION COMPLETED"
        )

        print("=" * 60)


        print(

            f"Document URL : "
            f"{document_url}"

        )


        if selfie_url:

            print(

                f"Selfie URL   : "
                f"{selfie_url}"

            )


        # ==================================================
        # RETURN RESULT TO FRONTEND
        # ==================================================

        return {

            "success": True,

            "verification_id":
                verification_id,

            "result":
                result,

            "files": {

                # Original filenames
                "document":
                    document.filename,

                "selfie":
                    selfie.filename
                    if selfie
                    else None,

                # Browser-accessible URLs
                "document_url":
                    document_url,

                "selfie_url":
                    selfie_url

            }

        }


    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except Exception as e:

        print("\n")

        print("=" * 60)

        print(
            "❌ VERIFICATION ERROR"
        )

        print("=" * 60)


        print(
            str(e)
        )


        return {

            "success": False,

            "verification_id":
                verification_id,

            "message":
                str(e)

        }


# ==========================================================
# STARTUP MESSAGE
# ==========================================================

print("=" * 60)

print(
    "IDSHIELD AI BACKEND"
)

print("=" * 60)

print(
    "API ready"
)

print(
    "Endpoint: POST /verify"
)

print(
    "Document: REQUIRED"
)

print(
    "Selfie: OPTIONAL"
)

print(
    "File preview: ENABLED"
)

print("=" * 60)