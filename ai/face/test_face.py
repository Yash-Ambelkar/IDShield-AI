import json

from verifier import verify_faces


# ==========================================
# IDShield AI - FACE VERIFICATION TEST
# ==========================================


IMAGE_1 = "test_images/person1.jpg"
IMAGE_2 = "test_images/person2.jpg"


# ==========================================
# Run verification
# ==========================================

result = verify_faces(
    IMAGE_1,
    IMAGE_2
)


# ==========================================
# Display result
# ==========================================

print("=" * 60)
print("        IDSHIELD AI - FACE VERIFICATION")
print("=" * 60)

print()

print(
    json.dumps(
        result,
        indent=4
    )
)

print()

print("=" * 60)

if result["status"] == "MATCH":

    print("✅ FACE MATCH")

elif result["status"] == "NO_MATCH":

    print("❌ FACE DOES NOT MATCH")

else:

    print("⚠️ FACE VERIFICATION ERROR")

print("=" * 60)