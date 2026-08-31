import React, {
    useEffect,
    useRef,
    useState
} from "react";

import { useNavigate } from "react-router-dom";

import "./Verification.css";


// ==========================================================
// IDShield AI - VERIFICATION PAGE
// ==========================================================

function Verification() {

    const navigate = useNavigate();


    // ======================================================
    // STATE
    // ======================================================

    const [document, setDocument] = useState(null);

    const [selfie, setSelfie] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    // ======================================================
    // CAMERA STATE
    // ======================================================

    const [cameraOpen, setCameraOpen] =
        useState(false);

    const [cameraType, setCameraType] =
        useState(null);


    // ======================================================
    // CAMERA REFERENCES
    // ======================================================

    const videoRef = useRef(null);

    const streamRef = useRef(null);


    // ======================================================
    // FILE INPUT REFERENCES
    // ======================================================

    const documentInputRef =
        useRef(null);

    const selfieInputRef =
        useRef(null);



    // ======================================================
    // FILE UPLOAD - DOCUMENT
    // ======================================================

    const handleDocumentChange = (event) => {

        const file =
            event.target.files?.[0];


        if (!file) {
            return;
        }


        setDocument(file);

        setError("");


        // Allow selecting the same file again
        event.target.value = "";
    };



    // ======================================================
    // FILE UPLOAD - SELFIE
    // ======================================================

    const handleSelfieChange = (event) => {

        const file =
            event.target.files?.[0];


        if (!file) {
            return;
        }


        setSelfie(file);

        setError("");


        // Allow selecting the same file again
        event.target.value = "";
    };



    // ======================================================
    // OPEN CAMERA
    // ======================================================

    const openCamera = async (type) => {

        setError("");


        // --------------------------------------------------
        // Check browser support
        // --------------------------------------------------

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            setError(
                "Camera is not supported by this browser. Please use Upload File."
            );

            return;
        }


        // --------------------------------------------------
        // Stop previous stream if any
        // --------------------------------------------------

        if (streamRef.current) {

            streamRef.current
                .getTracks()
                .forEach((track) => {
                    track.stop();
                });

            streamRef.current = null;
        }


        try {

            // ------------------------------------------------
            // Camera configuration
            // ------------------------------------------------

            const stream =
                await navigator.mediaDevices.getUserMedia({

                    video: {

                        facingMode:
                            type === "selfie"
                                ? "user"
                                : "environment",

                        width: {
                            ideal: 1280
                        },

                        height: {
                            ideal: 720
                        }

                    },

                    audio: false

                });


            // ------------------------------------------------
            // Save stream
            // ------------------------------------------------

            streamRef.current = stream;


            // ------------------------------------------------
            // Set camera state
            // ------------------------------------------------

            setCameraType(type);

            setCameraOpen(true);


        } catch (err) {

            console.error(
                "Camera access error:",
                err
            );


            setError(
                "Unable to access camera. Please allow camera permission or use Upload File."
            );

        }

    };



    // ======================================================
    // CONNECT CAMERA STREAM TO VIDEO
    // ======================================================

    useEffect(() => {

        if (
            cameraOpen &&
            videoRef.current &&
            streamRef.current
        ) {

            videoRef.current.srcObject =
                streamRef.current;


            videoRef.current
                .play()
                .catch(() => {});

        }

    }, [cameraOpen]);



    // ======================================================
    // STOP CAMERA
    // ======================================================

    const stopCamera = () => {

        // --------------------------------------------------
        // Stop all camera tracks
        // --------------------------------------------------

        if (streamRef.current) {

            streamRef.current
                .getTracks()
                .forEach((track) => {

                    track.stop();

                });


            streamRef.current = null;
        }


        // --------------------------------------------------
        // Remove video stream
        // --------------------------------------------------

        if (videoRef.current) {

            videoRef.current.srcObject =
                null;

        }


        // --------------------------------------------------
        // Reset state
        // --------------------------------------------------

        setCameraOpen(false);

        setCameraType(null);

    };



    // ======================================================
    // CAPTURE PHOTO
    // ======================================================

    const capturePhoto = () => {

        // --------------------------------------------------
        // Check video
        // --------------------------------------------------

        if (!videoRef.current) {

            setError(
                "Camera is not ready."
            );

            return;
        }


        const video =
            videoRef.current;


        // --------------------------------------------------
        // Check video dimensions
        // --------------------------------------------------

        if (
            video.videoWidth === 0 ||
            video.videoHeight === 0
        ) {

            setError(
                "Camera image is not ready. Please try again."
            );

            return;
        }


        // --------------------------------------------------
        // Create canvas
        // --------------------------------------------------

        const canvas =
            document.createElement(
                "canvas"
            );


        canvas.width =
            video.videoWidth;


        canvas.height =
            video.videoHeight;


        const context =
            canvas.getContext("2d");


        if (!context) {

            setError(
                "Unable to capture camera image."
            );

            return;
        }


        // --------------------------------------------------
        // Draw selfie normally
        //
        // We don't mirror the actual uploaded image.
        // The document/selfie should be stored naturally.
        // --------------------------------------------------

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );


        // --------------------------------------------------
        // Convert canvas to JPEG
        // --------------------------------------------------

        canvas.toBlob(

            (blob) => {

                if (!blob) {

                    setError(
                        "Unable to create captured image."
                    );

                    return;
                }


                // --------------------------------------------
                // File name
                // --------------------------------------------

                const fileName =
                    cameraType === "selfie"
                        ? "selfie-camera.jpg"
                        : "identity-document-camera.jpg";


                // --------------------------------------------
                // Create File
                // --------------------------------------------

                const file =
                    new File(
                        [blob],
                        fileName,
                        {
                            type: "image/jpeg"
                        }
                    );


                // --------------------------------------------
                // Save document
                // --------------------------------------------

                if (
                    cameraType ===
                    "document"
                ) {

                    setDocument(file);

                }


                // --------------------------------------------
                // Save selfie
                // --------------------------------------------

                if (
                    cameraType ===
                    "selfie"
                ) {

                    setSelfie(file);

                }


                setError("");


                // --------------------------------------------
                // Close camera
                // --------------------------------------------

                stopCamera();

            },

            "image/jpeg",

            0.92

        );

    };



    // ======================================================
    // CLEAN CAMERA WHEN COMPONENT UNMOUNTS
    // ======================================================

    useEffect(() => {

        return () => {

            if (streamRef.current) {

                streamRef.current
                    .getTracks()
                    .forEach((track) => {

                        track.stop();

                    });

                streamRef.current = null;

            }

        };

    }, []);



    // ======================================================
    // VERIFY DOCUMENT
    // ======================================================

    const handleVerification =
        async () => {

            setError("");


            // ------------------------------------------------
            // Validate document
            // ------------------------------------------------

            if (!document) {

                setError(
                    "Please upload or capture your identity document."
                );

                return;
            }


            // ------------------------------------------------
            // Validate selfie
            // ------------------------------------------------

            if (!selfie) {

                setError(
                    "Please upload or capture your selfie."
                );

                return;
            }


            // ------------------------------------------------
            // Start loading
            // ------------------------------------------------

            setLoading(true);


            try {

                // ==================================================
                // CREATE FORM DATA
                // ==================================================

                const formData =
                    new FormData();


                formData.append(
                    "document",
                    document
                );


                formData.append(
                    "selfie",
                    selfie
                );


                // ==================================================
                // RAILWAY BACKEND
                // ==================================================
                //
                // Vite environment variable can be used in
                // production.
                //
                // Railway URL is used as fallback.
                //
                // ==================================================

                const API_URL =
                    import.meta.env.VITE_API_URL ||
                    "https://idshield-ai-production-617a.up.railway.app";


                console.log(
                    "IDShield API:",
                    API_URL
                );


                // ==================================================
                // SEND REQUEST
                // ==================================================

                const response = await fetch(
    `${API_URL}/verify`,
    {
        method: "POST",
        body: formData
    }
);


                // ==================================================
                // READ RESPONSE
                // ==================================================

                let data;


                try {

                    data =
                        await response.json();

                } catch (jsonError) {

                    console.error(
                        "Response JSON error:",
                        jsonError
                    );


                    throw new Error(
                        "Invalid response received from IDShield AI."
                    );

                }


                // ==================================================
                // DISPLAY BACKEND RESPONSE
                // ==================================================

                console.log(
                    "IDShield AI backend response:",
                    data
                );


                // ==================================================
                // HTTP ERROR
                // ==================================================

                if (!response.ok) {

                    const message =
                        data?.detail ||
                        data?.message ||
                        "Verification request failed.";


                    throw new Error(

                        typeof message ===
                        "string"

                            ? message

                            : "Verification request failed."

                    );

                }


                // ==================================================
                // EMPTY RESPONSE
                // ==================================================

                if (!data) {

                    throw new Error(
                        "Empty response received from IDShield AI."
                    );

                }


                // ==================================================
                // DETERMINE PIPELINE RESULT
                // ==================================================
                //
                // Depending on the backend response structure,
                // the result may be inside:
                //
                // data.result
                // data.data
                // or directly inside data.
                //
                // ==================================================

                const pipelineResult =
                    data.result ||
                    data.data ||
                    data;


                // ==================================================
                // VALIDATE PIPELINE RESULT
                // ==================================================

                if (
                    typeof pipelineResult !==
                        "object" ||
                    pipelineResult === null
                ) {

                    throw new Error(
                        "Invalid response received from IDShield AI."
                    );

                }


                // ==================================================
                // CHECK EXPLICIT BACKEND FAILURE
                // ==================================================

                if (
                    data.success === false &&
                    data.status !== "COMPLETED" &&
                    !pipelineResult.risk
                ) {

                    throw new Error(
                        data.message ||
                        "Document verification failed."
                    );

                }


                // ==================================================
                // STORE COMPLETE RESULT
                // ==================================================

                sessionStorage.setItem(

                    "verificationResult",

                    JSON.stringify(
                        pipelineResult
                    )

                );


                // ==================================================
                // STORE FILE NAMES
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
                        URL.createObjectURL(
                            document
                        );


                    const selfiePreview =
                        URL.createObjectURL(
                            selfie
                        );


                    sessionStorage.setItem(

                        "uploadedDocument",

                        documentPreview

                    );


                    sessionStorage.setItem(

                        "uploadedSelfie",

                        selfiePreview

                    );

                } catch (
                    previewError
                ) {

                    console.warn(
                        "Preview creation failed:",
                        previewError
                    );

                }


                // ==================================================
                // NAVIGATE TO RESULT
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
    // RENDER UPLOAD BOX
    // ======================================================

    const renderUploadBox =
        (type) => {

            const isDocument =
                type === "document";


            const selectedFile =
                isDocument
                    ? document
                    : selfie;


            return (

                <div className="upload-box">


                    {/* ==================================================
                        HIDDEN FILE INPUT
                    ================================================== */}

                    <input

                        ref={
                            isDocument
                                ? documentInputRef
                                : selfieInputRef
                        }

                        type="file"

                        accept="image/*"

                        className="hidden-file-input"

                        onChange={
                            isDocument
                                ? handleDocumentChange
                                : handleSelfieChange
                        }

                    />


                    {/* ==================================================
                        ICON
                    ================================================== */}

                    <div className="upload-icon">

                        {isDocument
                            ? "📄"
                            : "👤"}

                    </div>


                    {/* ==================================================
                        TITLE
                    ================================================== */}

                    <h3>

                        {isDocument
                            ? "Identity Document"
                            : "Selfie"}

                    </h3>


                    {/* ==================================================
                        SELECTED FILE / DESCRIPTION
                    ================================================== */}

                    {selectedFile ? (

                        <div className="file-selected">

                            ✓ {selectedFile.name}

                        </div>

                    ) : (

                        <p>

                            {isDocument

                                ? "Use your camera or upload a clear photo of your identity document."

                                : "Take a clear front-facing selfie or upload an existing photo."

                            }

                        </p>

                    )}


                    {/* ==================================================
                        OPTIONS
                    ================================================== */}

                    <div className="upload-options">


                        {/* ==================================================
                            CAMERA BUTTON
                        ================================================== */}

                        <button

                            type="button"

                            className="camera-button"

                            onClick={() =>
                                openCamera(type)
                            }

                            disabled={loading}

                        >

                            <span>
                                📷
                            </span>

                            <span>
                                Take Photo
                            </span>

                        </button>


                        {/* ==================================================
                            UPLOAD BUTTON
                        ================================================== */}

                        <button

                            type="button"

                            className="upload-button"

                            onClick={() => {

                                if (
                                    isDocument
                                ) {

                                    documentInputRef
                                        .current
                                        ?.click();

                                } else {

                                    selfieInputRef
                                        .current
                                        ?.click();

                                }

                            }}

                            disabled={loading}

                        >

                            <span>
                                📁
                            </span>

                            <span>
                                Upload File
                            </span>

                        </button>


                    </div>


                    {/* ==================================================
                        REPLACE MESSAGE
                    ================================================== */}

                    {selectedFile && (

                        <small
                            className="replace-text"
                        >

                            Choose another option to replace

                        </small>

                    )}

                </div>

            );

        };



    // ======================================================
    // UI
    // ======================================================

    return (

        <div className="verification-page">


            <div className="verification-container">


                {/* ==================================================
                    HEADER
                ================================================== */}

                <div className="verification-header">

                    <h1>
                        Identity Verification
                    </h1>

                    <p>
                        Verify your identity securely
                        using your identity document
                        and selfie.
                    </p>

                </div>


                {/* ==================================================
                    MAIN CARD
                ================================================== */}

                <div className="verification-card">


                    {/* ==================================================
                        UPLOAD SECTION
                    ================================================== */}

                    <div className="verification-section">

                        <h2>
                            Verification Documents
                        </h2>

                        <p>
                            You can take a photo using
                            your camera or upload an
                            existing image.
                        </p>


                        <div className="upload-grid">

                            {renderUploadBox(
                                "document"
                            )}

                            {renderUploadBox(
                                "selfie"
                            )}

                        </div>

                    </div>


                    {/* ==================================================
                        ERROR
                    ================================================== */}

                    {error && (

                        <div
                            className="verification-error"
                        >

                            ⚠️ {error}

                        </div>

                    )}


                    {/* ==================================================
                        LOADING
                    ================================================== */}

                    {loading && (

                        <div
                            className="verification-loading"
                        >

                            <div
                                className="loading-spinner"
                            >
                            </div>


                            <div>

                                IDShield AI is
                                verifying your
                                documents...

                            </div>

                        </div>

                    )}


                    {/* ==================================================
                        VERIFY BUTTON
                    ================================================== */}

                    <button

                        type="button"

                        className="verify-button"

                        onClick={
                            handleVerification
                        }

                        disabled={loading}

                    >

                        {loading

                            ? "Verifying..."

                            : "Verify Identity"

                        }

                    </button>


                    {/* ==================================================
                        INFO
                    ================================================== */}

                    <div
                        className="verification-info"
                    >

                        <div
                            className="verification-info-icon"
                        >

                            🔒

                        </div>


                        <p>

                            Your document and selfie
                            are securely processed for
                            identity verification.
                            Make sure both images are
                            clear and readable.

                        </p>

                    </div>


                    {/* ==================================================
                        SECURITY POINTS
                    ================================================== */}

                    <div
                        className="security-points"
                    >


                        <div
                            className="security-point"
                        >

                            <strong>
                                🔍 AI Analysis
                            </strong>

                            <span>

                                Automated document
                                and face verification.

                            </span>

                        </div>


                        <div
                            className="security-point"
                        >

                            <strong>
                                🛡️ Fraud Detection
                            </strong>

                            <span>

                                Forensic checks help
                                identify suspicious
                                documents.

                            </span>

                        </div>


                        <div
                            className="security-point"
                        >

                            <strong>
                                🔐 Secure Processing
                            </strong>

                            <span>

                                Your files are processed
                                securely during
                                verification.

                            </span>

                        </div>


                    </div>

                </div>

            </div>


            {/* ======================================================
                CAMERA MODAL
            ====================================================== */}

            {cameraOpen && (

                <div
                    className="camera-overlay"
                >

                    <div
                        className="camera-modal"
                    >


                        {/* ==================================================
                            CAMERA HEADER
                        ================================================== */}

                        <div
                            className="camera-header"
                        >

                            <div>

                                <h2>

                                    {cameraType ===
                                    "selfie"

                                        ? "Take Selfie"

                                        : "Capture Document"

                                    }

                                </h2>


                                <p>

                                    Position the image
                                    clearly inside
                                    the frame.

                                </p>

                            </div>


                            <button

                                type="button"

                                className="camera-close"

                                onClick={
                                    stopCamera
                                }

                            >

                                ✕

                            </button>

                        </div>


                        {/* ==================================================
                            CAMERA VIEW
                        ================================================== */}

                        <div

                            className={

                                `camera-view ${
                                    cameraType ===
                                    "selfie"
                                        ? "selfie-camera"
                                        : ""
                                }`

                            }

                        >

                            <video

                                ref={videoRef}

                                autoPlay

                                playsInline

                                muted

                            />


                            <div
                                className="camera-frame"
                            >
                            </div>

                        </div>


                        {/* ==================================================
                            CAMERA CONTROLS
                        ================================================== */}

                        <div
                            className="camera-controls"
                        >

                            <button

                                type="button"

                                className="camera-cancel"

                                onClick={
                                    stopCamera
                                }

                            >

                                Cancel

                            </button>


                            <button

                                type="button"

                                className="capture-button"

                                onClick={
                                    capturePhoto
                                }

                            >

                                📷 Capture

                            </button>

                        </div>

                    </div>

                </div>

            )}

        </div>

    );

}


export default Verification;