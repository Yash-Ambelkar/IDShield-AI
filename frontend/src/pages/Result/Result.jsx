import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Result.css";


// ==========================================================
// IDShield AI - RESULT PAGE
// ==========================================================

function Result() {

    const navigate = useNavigate();

    const [result, setResult] = useState(null);

    const [error, setError] = useState("");


    // ======================================================
    // LOAD RESULT
    // ======================================================

    useEffect(() => {

        try {

            const storedResult =
                sessionStorage.getItem(
                    "verificationResult"
                );


            if (!storedResult) {

                setError(
                    "No verification result was found."
                );

                return;
            }


            const parsedResult =
                JSON.parse(
                    storedResult
                );


            setResult(
                parsedResult
            );


        } catch (err) {

            console.error(
                "Unable to load verification result:",
                err
            );


            setError(
                "Unable to load verification result."
            );

        }

    }, []);


    // ======================================================
    // START NEW VERIFICATION
    // ======================================================

    const handleNewVerification = () => {

        sessionStorage.removeItem(
            "verificationResult"
        );

        sessionStorage.removeItem(
            "documentName"
        );

        sessionStorage.removeItem(
            "selfieName"
        );


        navigate(
            "/verification"
        );

    };


    // ======================================================
    // LOADING
    // ======================================================

    if (!result && !error) {

        return (

            <div className="result-page">

                <div className="result-card">

                    <h2>
                        Loading verification result...
                    </h2>

                </div>

            </div>

        );

    }


    // ======================================================
    // ERROR
    // ======================================================

    if (error) {

        return (

            <div className="result-page">

                <div className="result-card">

                    <h2>
                        Verification Result
                    </h2>


                    <p className="result-error">

                        {error}

                    </p>


                    <button
                        onClick={
                            handleNewVerification
                        }
                    >
                        Start New Verification
                    </button>

                </div>

            </div>

        );

    }


    // ======================================================
    // EXTRACT RESULTS
    // ======================================================

    const risk =
        result?.risk || {};


    const validation =
        result?.validation || {};


    const authenticity =
        result?.authenticity || {};


    const tampering =
        result?.tampering || {};


    const face =
        result?.face_verification || {};


    // ======================================================
    // BASIC VALUES
    // ======================================================

    const decision =
        risk?.decision ||
        "UNKNOWN";


    const riskLevel =
        risk?.risk_level ||
        "UNKNOWN";


    const riskScore =
        risk?.risk_score ??
        "N/A";


    const validationStatus =
        validation?.status ||
        risk?.checks?.validation ||
        "UNKNOWN";


    const authenticityStatus =
        authenticity?.status ||
        risk?.checks?.authenticity ||
        "UNKNOWN";


    const tamperingStatus =
        tampering?.status ||
        risk?.checks?.tampering ||
        "UNKNOWN";


    const faceStatus =
        face?.status ||
        risk?.checks?.face_verification ||
        "UNKNOWN";


    const faceSimilarity =
        face?.similarity_score;


    const authorityMatch =
        authenticity?.match_score;


    const recordFound =
        authenticity?.record_found;


    const tamperingScore =
        tampering?.tampering_score;


    const warnings =
        Array.isArray(
            risk?.warnings
        )
            ? risk.warnings
            : [];


    // ======================================================
    // DECISION CLASS
    // ======================================================

    let decisionClass =
        "decision-review";


    if (
        decision ===
        "DOCUMENT APPROVED"
    ) {

        decisionClass =
            "decision-approved";

    }


    else if (
        decision ===
        "DOCUMENT REJECTED"
    ) {

        decisionClass =
            "decision-rejected";

    }


    // ======================================================
    // RISK CLASS
    // ======================================================

    let riskClass =
        "risk-medium";


    if (
        riskLevel === "LOW"
    ) {

        riskClass =
            "risk-low";

    }


    else if (
        riskLevel === "HIGH"
    ) {

        riskClass =
            "risk-high";

    }


    // ======================================================
    // STATUS CLASS HELPER
    // ======================================================

    const getStatusClass = (
        status
    ) => {

        if (
            status === "PASS" ||
            status === "VERIFIED" ||
            status === "MATCH"
        ) {

            return "status-pass";

        }


        if (
            status === "FAIL" ||
            status === "SUSPICIOUS" ||
            status === "NO_MATCH" ||
            status === "FLAGGED"
        ) {

            return "status-fail";

        }


        return "status-review";

    };


    // ======================================================
    // FORMAT VALUE
    // ======================================================

    const formatValue = (
        value
    ) => {

        if (
            value === null ||
            value === undefined
        ) {

            return "N/A";

        }


        return String(
            value
        );

    };


    // ======================================================
    // RENDER
    // ======================================================

    return (

        <div className="result-page">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="result-header">

                <h1>
                    IDShield AI
                </h1>


                <p>
                    Document Verification Result
                </p>

            </div>


            {/* ==================================================
                FINAL DECISION
            ================================================== */}

            <div
                className={
                    `result-decision ${decisionClass}`
                }
            >

                <div className="decision-icon">

                    {decision ===
                    "DOCUMENT APPROVED"
                        ? "✓"
                        : decision ===
                          "DOCUMENT REJECTED"
                            ? "✕"
                            : "!"}

                </div>


                <div>

                    <p className="decision-label">
                        FINAL DECISION
                    </p>


                    <h2>
                        {decision}
                    </h2>

                </div>

            </div>


            {/* ==================================================
                RISK SUMMARY
            ================================================== */}

            <div className="risk-summary">

                <div className="risk-box">

                    <span>
                        Risk Score
                    </span>


                    <strong
                        className={riskClass}
                    >
                        {formatValue(
                            riskScore
                        )}
                    </strong>

                </div>


                <div className="risk-box">

                    <span>
                        Risk Level
                    </span>


                    <strong
                        className={riskClass}
                    >
                        {riskLevel}
                    </strong>

                </div>

            </div>


            {/* ==================================================
                VERIFICATION CHECKS
            ================================================== */}

            <div className="verification-card">

                <h2>
                    Verification Checks
                </h2>


                <div className="checks-grid">


                    {/* ------------------------------------------
                        DOCUMENT VALIDATION
                    ------------------------------------------ */}

                    <div className="check-item">

                        <div>

                            <h3>
                                Document Validation
                            </h3>

                            <p>
                                Structure and field validation
                            </p>

                        </div>


                        <span
                            className={
                                `status-badge ${
                                    getStatusClass(
                                        validationStatus
                                    )
                                }`
                            }
                        >

                            {validationStatus}

                        </span>

                    </div>


                    {/* ------------------------------------------
                        AUTHENTICITY
                    ------------------------------------------ */}

                    <div className="check-item">

                        <div>

                            <h3>
                                Authority Verification
                            </h3>

                            <p>
                                Authoritative record verification
                            </p>

                        </div>


                        <span
                            className={
                                `status-badge ${
                                    getStatusClass(
                                        authenticityStatus
                                    )
                                }`
                            }
                        >

                            {authenticityStatus}

                        </span>

                    </div>


                    {/* ------------------------------------------
                        FORENSIC
                    ------------------------------------------ */}

                    <div className="check-item">

                        <div>

                            <h3>
                                Forensic Analysis
                            </h3>

                            <p>
                                Document tampering analysis
                            </p>

                        </div>


                        <span
                            className={
                                `status-badge ${
                                    getStatusClass(
                                        tamperingStatus
                                    )
                                }`
                            }
                        >

                            {tamperingStatus}

                        </span>

                    </div>


                    {/* ------------------------------------------
                        FACE
                    ------------------------------------------ */}

                    <div className="check-item">

                        <div>

                            <h3>
                                Face Verification
                            </h3>

                            <p>
                                Selfie vs document portrait
                            </p>

                        </div>


                        <span
                            className={
                                `status-badge ${
                                    getStatusClass(
                                        faceStatus
                                    )
                                }`
                            }
                        >

                            {faceStatus}

                        </span>

                    </div>

                </div>

            </div>


            {/* ==================================================
                DETAILED RESULTS
            ================================================== */}

            <div className="details-grid">


                {/* ==================================================
                    AUTHORITY
                ================================================== */}

                <div className="detail-card">

                    <h2>
                        Authority Verification
                    </h2>


                    <div className="detail-row">

                        <span>
                            Status
                        </span>

                        <strong>
                            {formatValue(
                                authenticityStatus
                            )}
                        </strong>

                    </div>


                    <div className="detail-row">

                        <span>
                            Record Found
                        </span>

                        <strong>
                            {recordFound === true
                                ? "Yes"
                                : recordFound === false
                                    ? "No"
                                    : "N/A"}
                        </strong>

                    </div>


                    <div className="detail-row">

                        <span>
                            Match Score
                        </span>

                        <strong>
                            {authorityMatch !==
                            undefined &&
                            authorityMatch !==
                            null
                                ? `${authorityMatch}%`
                                : "N/A"}
                        </strong>

                    </div>

                </div>


                {/* ==================================================
                    FORENSIC
                ================================================== */}

                <div className="detail-card">

                    <h2>
                        Forensic Analysis
                    </h2>


                    <div className="detail-row">

                        <span>
                            Status
                        </span>

                        <strong>
                            {formatValue(
                                tamperingStatus
                            )}
                        </strong>

                    </div>


                    <div className="detail-row">

                        <span>
                            Tampering Score
                        </span>

                        <strong>
                            {formatValue(
                                tamperingScore
                            )}
                        </strong>

                    </div>

                </div>


                {/* ==================================================
                    FACE
                ================================================== */}

                <div className="detail-card">

                    <h2>
                        Face Verification
                    </h2>


                    <div className="detail-row">

                        <span>
                            Status
                        </span>

                        <strong>
                            {formatValue(
                                faceStatus
                            )}
                        </strong>

                    </div>


                    <div className="detail-row">

                        <span>
                            Similarity
                        </span>

                        <strong>
                            {faceSimilarity !==
                            undefined &&
                            faceSimilarity !==
                            null
                                ? `${faceSimilarity}`
                                : "N/A"}
                        </strong>

                    </div>


                    <div className="detail-row">

                        <span>
                            Document Portrait
                        </span>

                        <strong>
                            {face?.document_face_found
                                ? "Found"
                                : "Not Found"}
                        </strong>

                    </div>

                </div>

            </div>


            {/* ==================================================
                WARNINGS
            ================================================== */}

            {warnings.length > 0 && (

                <div className="warnings-card">

                    <h2>
                        Warnings
                    </h2>


                    <div>

                        {warnings.map(
                            (
                                warning,
                                index
                            ) => (

                                <div
                                    className="warning-item"
                                    key={index}
                                >

                                    <span>
                                        !
                                    </span>


                                    <p>
                                        {warning}
                                    </p>

                                </div>

                            )
                        )}

                    </div>

                </div>

            )}


            {/* ==================================================
                REQUEST INFORMATION
            ================================================== */}

            {result?.request_id && (

                <div className="request-information">

                    <span>
                        Verification ID
                    </span>


                    <code>
                        {result.request_id}
                    </code>

                </div>

            )}


            {/* ==================================================
                ACTIONS
            ================================================== */}

            <div className="result-actions">

                <button
                    type="button"
                    onClick={
                        handleNewVerification
                    }
                >
                    Verify Another Document
                </button>

            </div>


        </div>

    );

}


export default Result;