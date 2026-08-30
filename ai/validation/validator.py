from datetime import datetime


# ==========================================
# IDShield AI
# Document Validation Module
# ==========================================


# ------------------------------------------
# Required fields for identity documents
# ------------------------------------------

REQUIRED_FIELDS = [
    "document_type",
    "name",
    "document_number",
    "nationality",
    "date_of_birth",
    "date_of_expiry",
    "gender"
]


# ------------------------------------------
# Date parser
# ------------------------------------------

def parse_date(date_string):

    try:
        return datetime.strptime(
            date_string,
            "%d-%m-%Y"
        )

    except (ValueError, TypeError):
        return None


# ------------------------------------------
# Validate required fields
# ------------------------------------------

def validate_required_fields(document):

    missing_fields = []

    for field in REQUIRED_FIELDS:

        value = document.get(field)

        if value is None or str(value).strip() == "":
            missing_fields.append(field)

    if missing_fields:

        return {
            "status": "FAIL",
            "missing_fields": missing_fields
        }

    return {
        "status": "PASS",
        "missing_fields": []
    }


# ------------------------------------------
# Validate date of birth
# ------------------------------------------

def validate_date_of_birth(document):

    dob = parse_date(
        document.get("date_of_birth")
    )

    if dob is None:

        return {
            "status": "FAIL",
            "message": "Invalid date of birth"
        }

    today = datetime.now()

    if dob >= today:

        return {
            "status": "FAIL",
            "message": "Date of birth cannot be in the future"
        }

    return {
        "status": "PASS",
        "message": "Date of birth is valid"
    }


# ------------------------------------------
# Validate document expiry
# ------------------------------------------

def validate_expiry(document):

    expiry = parse_date(
        document.get("date_of_expiry")
    )

    if expiry is None:

        return {
            "status": "FAIL",
            "message": "Invalid expiry date"
        }

    today = datetime.now()

    if expiry < today:

        return {
            "status": "FAIL",
            "message": "Document has expired"
        }

    return {
        "status": "PASS",
        "message": "Document is not expired"
    }


# ------------------------------------------
# Validate DOB and expiry relationship
# ------------------------------------------

def validate_date_relationship(document):

    dob = parse_date(
        document.get("date_of_birth")
    )

    expiry = parse_date(
        document.get("date_of_expiry")
    )

    if dob is None or expiry is None:

        return {
            "status": "FAIL",
            "message": "Unable to compare dates"
        }

    if expiry <= dob:

        return {
            "status": "FAIL",
            "message": "Expiry date must be after date of birth"
        }

    return {
        "status": "PASS",
        "message": "Date relationship is valid"
    }


# ------------------------------------------
# Validate document number
# ------------------------------------------

def validate_document_number(document):

    document_number = document.get(
        "document_number"
    )

    if not document_number:

        return {
            "status": "FAIL",
            "message": "Document number is missing"
        }

    # Basic sanity check
    # Real document formats will be added later
    if len(document_number) < 5:

        return {
            "status": "FAIL",
            "message": "Document number is too short"
        }

    return {
        "status": "PASS",
        "message": "Document number format looks valid"
    }


# ------------------------------------------
# Validate gender
# ------------------------------------------

def validate_gender(document):

    gender = document.get("gender")

    if not gender:

        return {
            "status": "FAIL",
            "message": "Gender is missing"
        }

    gender = gender.upper().strip()

    allowed_values = [
        "M",
        "F",
        "X",
        "MALE",
        "FEMALE"
    ]

    if gender not in allowed_values:

        return {
            "status": "FAIL",
            "message": "Invalid gender value"
        }

    return {
        "status": "PASS",
        "message": "Gender value is valid"
    }


# ------------------------------------------
# Main validation function
# ------------------------------------------

def validate_document(document):

    results = {}

    # Required fields
    results["required_fields"] = (
        validate_required_fields(document)
    )

    # Date of birth
    results["date_of_birth"] = (
        validate_date_of_birth(document)
    )

    # Expiry
    results["document_expiry"] = (
        validate_expiry(document)
    )

    # Date relationship
    results["date_relationship"] = (
        validate_date_relationship(document)
    )

    # Document number
    results["document_number"] = (
        validate_document_number(document)
    )

    # Gender
    results["gender"] = (
        validate_gender(document)
    )

    # --------------------------------------
    # Calculate validation score
    # --------------------------------------

    total_checks = len(results)

    passed_checks = 0

    for check in results.values():

        if check["status"] == "PASS":
            passed_checks += 1

    score = round(
        (passed_checks / total_checks) * 100
    )

    # --------------------------------------
    # Overall status
    # --------------------------------------

    if score == 100:

        overall_status = "PASS"

    elif score >= 60:

        overall_status = "FLAGGED"

    else:

        overall_status = "FAIL"

    # --------------------------------------
    # Collect warnings
    # --------------------------------------

    warnings = []

    for check_name, check_result in results.items():

        if check_result["status"] == "FAIL":

            warnings.append(
                check_result["message"]
                if "message" in check_result
                else f"{check_name} validation failed"
            )

    return {
        "status": overall_status,
        "validation_score": score,
        "checks": results,
        "warnings": warnings
    }