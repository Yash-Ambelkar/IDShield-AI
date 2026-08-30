import json

from detector import compare_documents


# ==========================================
# IDShield AI - TAMPERING TEST
# ==========================================

ORIGINAL_DOCUMENT = "../ocr/test_documents/sample_document.jpg"

TAMPERED_DOCUMENT = "tampered_document.jpg"


# ==========================================
# Run comparison
# ==========================================

result = compare_documents(
    ORIGINAL_DOCUMENT,
    TAMPERED_DOCUMENT
)


# ==========================================
# Display result
# ==========================================

print("=" * 60)
print("          IDSHIELD AI - TAMPERING TEST")
print("=" * 60)

print()

print("Original document:")
print(ORIGINAL_DOCUMENT)

print()

print("Submitted document:")
print(TAMPERED_DOCUMENT)

print()

print("=" * 60)
print("                  RESULT")
print("=" * 60)

print(
    json.dumps(
        result,
        indent=4
    )
)

print()

print("=" * 60)
print("              FINAL DECISION")
print("=" * 60)

if result.get("status") == "PASS":

    print("✅ DOCUMENT APPEARS AUTHENTIC")

elif result.get("status") == "REVIEW":

    print("⚠️ DOCUMENT REQUIRES REVIEW")

elif result.get("status") == "FLAGGED":

    print("🚨 DOCUMENT TAMPERING DETECTED")

else:

    print("❌ ERROR")

print()

print("=" * 60)