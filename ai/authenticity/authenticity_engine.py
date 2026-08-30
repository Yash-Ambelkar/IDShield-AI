import os
import json
from datetime import datetime


# ==========================================================
# IDShield AI
# Generic Document Authenticity Engine
# ==========================================================


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

AI_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROJECT_DIR = os.path.dirname(
    AI_DIR
)

DATABASE_PATH = os.path.join(
    PROJECT_DIR,
    "database",
    "document_registry.json"
)


# ==========================================================
# SUPPORTED DOCUMENT TYPES
# ==========================================================

SUPPORTED_DOCUMENT_TYPES = [

    "PASSPORT",

    "DRIVING LICENSE",

    "PAN",

    "VOTER ID",

    "NATIONAL ID"

]


# ==========================================================
# DOCUMENT-SPECIFIC FIELDS
# ==========================================================

DOCUMENT_FIELDS = {

    "PASSPORT": [
        "document_type",
        "document_number",
        "name",
        "nationality",
        "date_of_birth",
        "date_of_expiry",
        "gender"
    ],

    "DRIVING LICENSE": [
        "document_type",
        "document_number",
        "name",
        "date_of_birth",
        "date_of_expiry",
        "gender"
    ],

    "PAN": [
        "document_type",
        "document_number",
        "name",
        "date_of_birth"
    ],

    "VOTER ID": [
        "document_type",
        "document_number",
        "name",
        "date_of_birth",
        "gender"
    ],

    "NATIONAL ID": [
        "document_type",
        "document_number",
        "name",
        "date_of_birth",
        "gender"
    ]

}


# ==========================================================
# LOAD DATABASE
# ==========================================================

def load_registry():

    if not os.path.exists(DATABASE_PATH):

        print(
            "⚠️ Document registry not found:"
        )

        print(
            DATABASE_PATH
        )

        return {}

    try:

        with open(
            DATABASE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        print(
            f"❌ Registry loading error: {e}"
        )

        return {}


# ==========================================================
# NORMALIZE VALUE
# ==========================================================

def normalize(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .upper()
        .replace(" ", "")
    )


# ==========================================================
# NORMALIZE DOCUMENT TYPE
# ==========================================================

def normalize_document_type(
    document_type
):

    if not document_type:

        return None

    value = (
        str(document_type)
        .strip()
        .upper()
    )

    aliases = {

        "DRIVING LICENSE":
            "DRIVING LICENSE",

        "DRIVING LICENCE":
            "DRIVING LICENSE",

        "DRIVER LICENSE":
            "DRIVING LICENSE",

        "DRIVER LICENCE":
            "DRIVING LICENSE",

        "VOTER":
            "VOTER ID",

        "VOTER CARD":
            "VOTER ID",

        "NATIONAL ID CARD":
            "NATIONAL ID"

    }

    return aliases.get(
        value,
        value
    )


# ==========================================================
# FIND RECORD
# ==========================================================

def find_record(
    document_type,
    document_number
):

    registry = load_registry()

    document_type = normalize_document_type(
        document_type
    )

    document_number = normalize(
        document_number
    )

    if not document_type:

        return None

    if not document_number:

        return None

    document_records = registry.get(
        document_type,
        {}
    )

    for key, record in document_records.items():

        if normalize(key) == document_number:

            return record

    return None


# ==========================================================
# DATE VALIDATION
# ==========================================================

def is_expired(expiry_date):

    if not expiry_date:

        return False

    try:

        expiry = datetime.strptime(
            expiry_date,
            "%d-%m-%Y"
        )

        return expiry < datetime.now()

    except ValueError:

        return False


# ==========================================================
# COMPARE FIELDS
# ==========================================================

def compare_fields(
    document,
    official_record,
    document_type
):

    fields = DOCUMENT_FIELDS.get(
        document_type,
        []
    )

    comparison = {}

    matched = 0
    checked = 0

    for field in fields:

        submitted_value = document.get(
            field
        )

        official_value = official_record.get(
            field
        )

        submitted_normalized = normalize(
            submitted_value
        )

        official_normalized = normalize(
            official_value
        )

        # --------------------------------------------------
        # Missing submitted field
        # --------------------------------------------------

        if not submitted_normalized:

            comparison[field] = {

                "status": "MISSING",

                "submitted": submitted_value,

                "official": official_value

            }

            continue

        # --------------------------------------------------
        # Official field unavailable
        # --------------------------------------------------

        if not official_normalized:

            comparison[field] = {

                "status": "NOT_AVAILABLE",

                "submitted": submitted_value,

                "official": None

            }

            continue

        checked += 1

        # --------------------------------------------------
        # Match
        # --------------------------------------------------

        if (
            submitted_normalized ==
            official_normalized
        ):

            matched += 1

            comparison[field] = {

                "status": "MATCH",

                "submitted": submitted_value,

                "official": official_value

            }

        # --------------------------------------------------
        # Mismatch
        # --------------------------------------------------

        else:

            comparison[field] = {

                "status": "MISMATCH",

                "submitted": submitted_value,

                "official": official_value

            }

    if checked > 0:

        match_score = round(
            (matched / checked) * 100
        )

    else:

        match_score = 0

    return {

        "match_score": match_score,

        "matched_fields": matched,

        "checked_fields": checked,

        "comparison": comparison

    }


# ==========================================================
# AUTHENTICITY VERIFICATION
# ==========================================================

def verify_against_registry(
    document
):

    document_type = normalize_document_type(
        document.get("document_type")
    )

    document_number = document.get(
        "document_number"
    )

    # ======================================================
    # DOCUMENT TYPE CHECK
    # ======================================================

    if not document_type:

        return {

            "status": "REVIEW",

            "record_found": False,

            "registry_match": False,

            "match_score": 0,

            "message":
                "Document type could not be determined.",

            "comparison": {}

        }


    # ======================================================
    # SUPPORTED TYPE CHECK
    # ======================================================

    if (
        document_type
        not in SUPPORTED_DOCUMENT_TYPES
    ):

        return {

            "status": "REVIEW",

            "record_found": False,

            "registry_match": False,

            "match_score": 0,

            "message":
                f"Document type '{document_type}' "
                "is not currently supported.",

            "comparison": {}

        }


    # ======================================================
    # DOCUMENT NUMBER CHECK
    # ======================================================

    if not document_number:

        return {

            "status": "REVIEW",

            "record_found": False,

            "registry_match": False,

            "match_score": 0,

            "message":
                "Document number could not be extracted.",

            "comparison": {}

        }


    # ======================================================
    # FIND AUTHORITATIVE RECORD
    # ======================================================

    official_record = find_record(

        document_type,

        document_number

    )


    # ======================================================
    # RECORD NOT FOUND
    # ======================================================

    if official_record is None:

        return {

            "status": "REVIEW",

            "record_found": False,

            "registry_match": False,

            "match_score": 0,

            "message":
                "No authoritative record was found "
                "for this document.",

            "comparison": {}

        }


    # ======================================================
    # COMPARE
    # ======================================================

    comparison_result = compare_fields(

        document,

        official_record,

        document_type

    )

    match_score = comparison_result[
        "match_score"
    ]


    # ======================================================
    # OFFICIAL STATUS
    # ======================================================

    official_status = str(
        official_record.get(
            "status",
            "UNKNOWN"
        )
    ).upper()


    # ======================================================
    # EXPIRY
    # ======================================================

    expiry_date = official_record.get(
        "date_of_expiry"
    )

    expired = is_expired(
        expiry_date
    )


    # ======================================================
    # FINAL DECISION
    # ======================================================

    if official_status != "ACTIVE":

        status = "SUSPICIOUS"

        message = (
            "An authoritative record exists, "
            "but the document status is not active."
        )

    elif expired:

        status = "SUSPICIOUS"

        message = (
            "The authoritative document record "
            "has expired."
        )

    elif match_score == 100:

        status = "VERIFIED"

        message = (
            "All available identity fields match "
            "the authoritative record."
        )

    elif match_score >= 70:

        status = "REVIEW"

        message = (
            "The authoritative record was found, "
            "but some fields do not match."
        )

    else:

        status = "SUSPICIOUS"

        message = (
            "Significant differences were found "
            "between the submitted document and "
            "the authoritative record."
        )


    # ======================================================
    # RETURN
    # ======================================================

    return {

        "status": status,

        "record_found": True,

        "registry_match": (
            status == "VERIFIED"
        ),

        "document_type":
            document_type,

        "document_number":
            document_number,

        "match_score":
            match_score,

        "matched_fields":
            comparison_result[
                "matched_fields"
            ],

        "checked_fields":
            comparison_result[
                "checked_fields"
            ],

        "official_status":
            official_status,

        "expiry_date":
            expiry_date,

        "message":
            message,

        "comparison":
            comparison_result[
                "comparison"
            ]

    }