import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Verification.css";


// ==========================================================
// IDShield AI - VERIFICATION PAGE
// ==========================================================

function Verification() {

    const navigate = useNavigate();

    // ------------------------------------------------------
    // STATE
    // ------------------------------------------------------

    const [document, setDocument] = useState(null);

    const [selfie, setSelfie] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    // ======================================================
    // DOCUMENT SELECTION
    // ======================================================

    const handleDocumentChange = (event) => {

        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        setDocument(file);

        setError("");
    };


    // ======================================================
    // SELFIE SELECTION
    // ======================================================

    const handleSelfieChange = (event) => {

        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        setSelfie(file);

        setError("");
    };


    // ======================================================
    // SUBMIT VERIFICATION
    // ======================================================

    const handleVerification = async () => {

        setError("");


        // --------------------------------------------------
        // Validate document
        // --------------------------------------------------

        if (!document) {

            setError(
                "Please upload your identity document."
            );

            return;
        }


        // --------------------------------------------------
        // Validate selfie
        // --------------------------------------------------

        if (!selfie) {

            setError(
                "Please upload your selfie."
            );

            return;
        }


        // --------------------------------------------------
        // Start loading
        // --------------------------------------------------

        setLoading(true);


        try {

            // ==================================================
            // CREATE FORM DATA
            // ==================================================

            const formData = new FormData();


            formData.append(
                "document",
                document
            );


            formData.append(
                "selfie",
                selfie
            );


            // ==================================================
            // SEND REQUEST TO FASTAPI
            // ==================================================

            const response = await fetch(

                "http://127.0.0.1:8000/api/verify",

                {
                    method: "POST",

                    body: formData
                }

            );


            // ==================================================
            // READ RESPONSE
            // ==================================================

            const data = await response.json();


            // ==================================================
            // HANDLE HTTP ERROR
            // ==================================================

            if (!response.ok) {

                const message =
                    data?.detail ||
                    data?.message ||
                    "Verification request failed.";

                throw new Error(
                    typeof message === "string"
                        ? message
                        : "Verification request failed."
                );
            }


            // ==================================================
            // VALIDATE API RESPONSE
            // ==================================================

            if (!data) {

                throw new Error(
                    "Empty response received from IDShield AI."
                );
            }


            if (
                data.success === false &&
                !data.risk
            ) {

                throw new Error(
                    data.message ||
                    "Document verification failed."
                );
            }


            // ==================================================
            // STORE COMPLETE RESULT
            // ==================================================
            //
            // Result.jsx already expects:
            //
            // verificationResult
            //
            // containing:
            //
            // ocr
            // validation
            // tampering
            // face_verification
            // risk
            //
            // ==================================================

            sessionStorage.setItem(

                "verificationResult",

                JSON.stringify(data)

            );


            // ==================================================
            // STORE UPLOADED FILE INFORMATION
            // ==================================================

            sessionStorage.setItem(

                "documentName",

                document.name

            );


            sessionStorage.setItem(

                "selfieName",

                selfie.name

            );


            // ==================================================
            // CREATE LOCAL PREVIEWS
            // ==================================================

            try {

                const documentPreview =
                    URL.createObjectURL(document);

                const selfiePreview =
                    URL.createObjectURL(selfie);


                sessionStorage.setItem(

                    "uploadedDocument",

                    documentPreview

                );


                sessionStorage.setItem(

                    "uploadedSelfie",

                    selfiePreview

                );

            } catch (previewError) {

                console.warn(
                    "Preview creation failed:",
                    previewError
                );

            }


            // ==================================================
            // GO TO RESULT PAGE
            // ==================================================

            navigate(
                "/result"
            );


        } catch (err) {

            console.error(
                "IDShield verification error:",
                err
            );


            setError(

                err?.message ||
                "Unable to connect to IDShield AI."

            );

        } finally {

            setLoading(false);

        }

    };


    // ======================================================
    // UI
    // ======================================================

    return (

        <div className="verification-page">


            {/* ==================================================
                DOCUMENT UPLOAD
            ================================================== */}

            <div className="upload-section">

                <h2>
                    Identity Document
                </h2>


                <input

                    type="file"

                    accept="image/*"

                    onChange={
                        handleDocumentChange
                    }

                />


                {document && (

                    <p>
                        Selected: {document.name}
                    </p>

                )}

            </div>


            {/* ==================================================
                SELFIE UPLOAD
            ================================================== */}

            <div className="upload-section">

                <h2>
                    Selfie
                </h2>


                <input

                    type="file"

                    accept="image/*"

                    onChange={
                        handleSelfieChange
                    }

                />


                {selfie && (

                    <p>
                        Selected: {selfie.name}
                    </p>

                )}

            </div>


            {/* ==================================================
                ERROR
            ================================================== */}

            {error && (

                <div className="verification-error">

                    {error}

                </div>

            )}


            {/* ==================================================
                VERIFY BUTTON
            ================================================== */}

            <button

                type="button"

                onClick={
                    handleVerification
                }

                disabled={loading}

            >

                {loading
                    ? "Verifying..."
                    : "Verify Document"
                }

            </button>


        </div>

    );

}


export default Verification;