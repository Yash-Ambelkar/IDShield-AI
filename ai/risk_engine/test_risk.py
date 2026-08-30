import json

from risk_engine import calculate_risk


# ==========================================
# IDShield AI - HIGH RISK TEST
# ==========================================


validation_result = {

    "status": "FLAGGED",

    "validation_score": 40

}


tampering_result = {

    "status": "FLAGGED",

    "tampering_score": 70

}


face_result = {

    "status": "NO_MATCH",

    "verified": False,

    "similarity_score": 25

}


# ==========================================
# Calculate Risk
# ==========================================

result = calculate_risk(

    validation_result,

    tampering_result,

    face_result

)


# ==========================================
# Display Result
# ==========================================

print("=" * 60)

print("        IDSHIELD AI - HIGH RISK TEST")

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

print("FINAL DECISION:", result["decision"])

print("RISK LEVEL:", result["risk_level"])

print("RISK SCORE:", result["risk_score"])

print("=" * 60)