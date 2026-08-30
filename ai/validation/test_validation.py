import json

from validator import validate_document


# ==========================================
# Test Document
# ==========================================

document = {

    "document_type": "IDENTITY DOCUMENT",

    "name": "ARJUN SHARMA",

    "document_number": "TEST123456",

    "nationality": "INDIAN",

    "date_of_birth": "15-08-2004",

    "date_of_expiry": "14-08-2034",

    "gender": "M"
}


# ==========================================
# Run validation
# ==========================================

result = validate_document(document)


# ==========================================
# Display result
# ==========================================

print("=" * 60)
print("        IDSHIELD AI - DOCUMENT VALIDATION")
print("=" * 60)

print(
    json.dumps(
        result,
        indent=4
    )
)

print("=" * 60)