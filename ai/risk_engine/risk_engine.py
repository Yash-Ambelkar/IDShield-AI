# ==========================================================
# IDShield AI - Risk Engine
# Multi-Layer Document Risk Analysis
# ==========================================================


def calculate_risk(
    validation_result,
    authenticity_result,
    tampering_result,
    face_result
):

    # ======================================================
    # INITIAL VALUES
    # ======================================================

    risk_score = 0

    warnings = []

    checks = {}


    # ======================================================
    # 1. DOCUMENT VALIDATION
    # ======================================================

    validation_status = validation_result.get(
        "status",
        "ERROR"
    )

    checks["validation"] = validation_status


    if validation_status == "PASS":

        validation_risk = 0

    elif validation_status == "FLAGGED":

        validation_risk = 15

        warnings.append(
            "Document validation detected inconsistencies."
        )

    elif validation_status == "FAIL":

        validation_risk = 30

        warnings.append(
            "Document validation failed."
        )

    else:

        validation_risk = 25

        warnings.append(
            "Document validation could not be completed."
        )


    risk_score += validation_risk


    # ======================================================
    # 2. AUTHORITATIVE REGISTRY VERIFICATION
    # ======================================================

    authenticity_status = authenticity_result.get(
        "status",
        "ERROR"
    )

    checks["authenticity"] = authenticity_status


    authority_match_score = authenticity_result.get(
        "match_score",
        0
    )

    record_found = authenticity_result.get(
        "record_found",
        False
    )


    # ------------------------------------------------------
    # VERIFIED
    # ------------------------------------------------------

    if authenticity_status == "VERIFIED":

        authenticity_risk = 0


    # ------------------------------------------------------
    # REVIEW
    # ------------------------------------------------------

    elif authenticity_status == "REVIEW":

        authenticity_risk = 25

        warnings.append(
            authenticity_result.get(
                "message",
                "Authority verification requires review."
            )
        )


    # ------------------------------------------------------
    # SUSPICIOUS
    # ------------------------------------------------------

    elif authenticity_status == "SUSPICIOUS":

        authenticity_risk = 60

        warnings.append(
            authenticity_result.get(
                "message",
                "Document information is suspicious."
            )
        )


    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------

    else:

        authenticity_risk = 20

        warnings.append(
            "Authority verification could not be completed."
        )


    # ------------------------------------------------------
    # Extra penalty if record doesn't exist
    # ------------------------------------------------------

    if not record_found:

        authenticity_risk = max(
            authenticity_risk,
            25
        )


    risk_score += authenticity_risk


    # ======================================================
    # 3. TAMPERING DETECTION
    # ======================================================

    tampering_status = tampering_result.get(
        "status",
        "ERROR"
    )

    checks["tampering"] = tampering_status


    tampering_score = tampering_result.get(
        "tampering_score",
        0
    )


    # ------------------------------------------------------
    # PASS
    # ------------------------------------------------------

    if tampering_status == "PASS":

        tampering_risk = 0


    # ------------------------------------------------------
    # REVIEW
    # ------------------------------------------------------

    elif tampering_status == "REVIEW":

        tampering_risk = 25

        warnings.append(
            "Possible document modifications detected."
        )


    # ------------------------------------------------------
    # FLAGGED
    # ------------------------------------------------------

    elif tampering_status == "FLAGGED":

        tampering_risk = 50

        warnings.append(
            "Significant document modification indicators detected."
        )


    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------

    else:

        tampering_risk = 15

        warnings.append(
            "Tampering analysis could not be completed."
        )


    # ------------------------------------------------------
    # Use detector score if available
    # ------------------------------------------------------

    if isinstance(
        tampering_score,
        (int, float)
    ):

        if tampering_score >= 90:

            tampering_risk = max(
                tampering_risk,
                50
            )

        elif tampering_score >= 60:

            tampering_risk = max(
                tampering_risk,
                30
            )

        elif tampering_score >= 25:

            tampering_risk = max(
                tampering_risk,
                15
            )


    risk_score += tampering_risk


    # ======================================================
    # 4. FACE VERIFICATION
    # ======================================================

    face_status = face_result.get(
        "status",
        "NOT_AVAILABLE"
    )

    checks["face_verification"] = face_status


    face_similarity = face_result.get(
        "similarity_score"
    )


    # ------------------------------------------------------
    # MATCH
    # ------------------------------------------------------

    if face_status == "MATCH":

        face_risk = 0


    # ------------------------------------------------------
    # NO MATCH
    # ------------------------------------------------------

    elif face_status == "NO_MATCH":

        face_risk = 40

        warnings.append(
            "Submitted face does not match the reference."
        )


    # ------------------------------------------------------
    # NO FACE
    # ------------------------------------------------------

    elif face_status == "NO_FACE":

        face_risk = 0

        warnings.append(
            "No document portrait was available for face verification."
        )


    # ------------------------------------------------------
    # NOT AVAILABLE
    # ------------------------------------------------------

    elif face_status == "NOT_AVAILABLE":

        face_risk = 0


    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------

    else:

        face_risk = 10

        warnings.append(
            "Face verification could not be completed."
        )


    risk_score += face_risk


    # ======================================================
    # CAP SCORE
    # ======================================================

    risk_score = min(
        100,
        max(
            0,
            risk_score
        )
    )


    # ======================================================
    # DETERMINE RISK LEVEL
    # ======================================================

    if risk_score <= 30:

        risk_level = "LOW"

    elif risk_score <= 60:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    # ======================================================
    # FINAL DECISION
    # ======================================================

    # ------------------------------------------------------
    # Strong authority mismatch
    # ------------------------------------------------------

    if authenticity_status == "SUSPICIOUS":

        decision = "DOCUMENT REJECTED"


    # ------------------------------------------------------
    # Strong tampering detection
    # ------------------------------------------------------

    elif tampering_status == "FLAGGED":

        decision = "DOCUMENT REJECTED"


    # ------------------------------------------------------
    # Face mismatch
    # ------------------------------------------------------

    elif face_status == "NO_MATCH":

        decision = "DOCUMENT REJECTED"


    # ------------------------------------------------------
    # High overall risk
    # ------------------------------------------------------

    elif risk_score > 60:

        decision = "DOCUMENT REJECTED"


    # ------------------------------------------------------
    # Medium risk
    # ------------------------------------------------------

    elif risk_score > 30:

        decision = "DOCUMENT REQUIRES REVIEW"


    # ------------------------------------------------------
    # Low risk
    # ------------------------------------------------------

    else:

        decision = "DOCUMENT APPROVED"


    # ======================================================
    # AUTHORITY INFORMATION
    # ======================================================

    authority_information = {

        "status":
            authenticity_status,

        "record_found":
            record_found,

        "match_score":
            authority_match_score,

        "message":
            authenticity_result.get(
                "message",
                ""
            )

    }


    # ======================================================
    # FINAL RESULT
    # ======================================================

    return {

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "decision":
            decision,

        "checks":
            checks,

        "scores": {

            "validation":
                validation_risk,

            "authenticity":
                authenticity_risk,

            "tampering":
                tampering_risk,

            "face":
                face_risk

        },

        "authority":
            authority_information,

        "face_similarity":
            face_similarity,

        "warnings":
            warnings

    }