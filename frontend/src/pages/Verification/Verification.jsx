import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Verification.css";

function Verification() {
  const navigate = useNavigate();

  const [document, setDocument] = useState(null);
  const [selfie, setSelfie] = useState(null);

  const [documentPreview, setDocumentPreview] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState(null);

  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraType, setCameraType] = useState(null);

  const [stream, setStream] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState("");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // ======================================================
  // FILE PREVIEW
  // ======================================================

  const createPreview = (file, type) => {
    if (!file) return;

    const reader = new FileReader();

    reader.onload = () => {
      if (type === "document") {
        setDocumentPreview(reader.result);
      }

      if (type === "selfie") {
        setSelfiePreview(reader.result);
      }
    };

    reader.readAsDataURL(file);
  };

  // ======================================================
  // DOCUMENT UPLOAD
  // ======================================================

  const handleDocument = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setError("");

    if (file.size > 10 * 1024 * 1024) {
      setError("Document must be smaller than 10MB.");
      return;
    }

    setDocument(file);
    createPreview(file, "document");
  };

  // ======================================================
  // SELFIE UPLOAD
  // ======================================================

  const handleSelfie = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setError("");

    if (file.size > 10 * 1024 * 1024) {
      setError("Photo must be smaller than 10MB.");
      return;
    }

    setSelfie(file);
    createPreview(file, "selfie");
  };

  // ======================================================
  // OPEN CAMERA
  // ======================================================

  const openCamera = async (type) => {
    setError("");
    setCameraType(type);

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: type === "selfie" ? "user" : "environment"
        },
        audio: false
      });

      setStream(mediaStream);
      setCameraOpen(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      }, 100);

    } catch (err) {
      console.error("Camera error:", err);

      setError(
        "Camera access was blocked. Please allow camera permission or upload an image instead."
      );

      setCameraOpen(false);
    }
  };

  // ======================================================
  // CLOSE CAMERA
  // ======================================================

  const closeCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }

    setStream(null);
    setCameraOpen(false);
    setCameraType(null);
  };

  // ======================================================
  // CAPTURE PHOTO
  // ======================================================

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    canvas.toBlob(
      (blob) => {
        if (!blob) return;

        const fileName =
          cameraType === "document"
            ? "captured-document.jpg"
            : "captured-selfie.jpg";

        const file = new File(
          [blob],
          fileName,
          {
            type: "image/jpeg"
          }
        );

        const previewUrl =
          URL.createObjectURL(blob);

        if (cameraType === "document") {
          setDocument(file);
          setDocumentPreview(previewUrl);
        }

        if (cameraType === "selfie") {
          setSelfie(file);
          setSelfiePreview(previewUrl);
        }

        closeCamera();
      },
      "image/jpeg",
      0.9
    );
  };

  // ======================================================
  // SAVE FILE AS DATA URL
  // ======================================================

  const fileToDataURL = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;

      reader.readAsDataURL(file);
    });
  };

  // ======================================================
  // START REAL VERIFICATION
  // ======================================================

  const startVerification = async () => {
    setError("");

    if (!document) {
      setError("Please upload or capture an identity document.");
      return;
    }

    if (!selfie) {
      setError("Please upload or capture a face photo.");
      return;
    }

    setIsVerifying(true);

    try {
      // --------------------------------------------------
      // CREATE FORM DATA
      // --------------------------------------------------

      const formData = new FormData();

      formData.append(
        "document",
        document
      );

      formData.append(
        "selfie",
        selfie
      );

      // --------------------------------------------------
      // SEND TO FASTAPI
      // --------------------------------------------------

      const response = await fetch(
    "https://idshield-ai-backend.onrender.com/verify",
    {
        method: "POST",
        body: formData
    }
);

      // --------------------------------------------------
      // READ RESPONSE
      // --------------------------------------------------

      const data = await response.json();

      console.log(
        "IDShield API response:",
        data
      );

      // --------------------------------------------------
      // API ERROR
      // --------------------------------------------------

      if (!response.ok || !data.success) {
        throw new Error(
          data.message ||
          "Verification failed."
        );
      }

      // --------------------------------------------------
      // SAVE ACTUAL BACKEND RESULT
      // --------------------------------------------------

      sessionStorage.setItem(
        "verificationResult",
        JSON.stringify({
          ...data.result,
          verification_id:
            data.verification_id
        })
      );

      // --------------------------------------------------
      // SAVE UPLOADED FILE PREVIEWS
      // --------------------------------------------------

      const documentDataURL =
        await fileToDataURL(document);

      const selfieDataURL =
        await fileToDataURL(selfie);

      sessionStorage.setItem(
        "verificationFiles",
        JSON.stringify({
          document: documentDataURL,
          selfie: selfieDataURL,

          documentName:
            document.name,

          selfieName:
            selfie.name
        })
      );

      // --------------------------------------------------
      // SAVE HISTORY
      // --------------------------------------------------

      const history =
        JSON.parse(
          sessionStorage.getItem(
            "verificationHistory"
          ) || "[]"
        );

      const risk =
        data.result?.risk || {};

      const ocr =
        data.result?.ocr?.document_data || {};

      const historyItem = {
        id:
          data.verification_id,

        date:
          new Date().toISOString(),

        decision:
          risk.decision || "UNKNOWN",

        risk_level:
          risk.risk_level || "UNKNOWN",

        risk_score:
          risk.risk_score ?? 0,

        name:
          ocr.name || "Unknown",

        document_type:
          ocr.document_type ||
          "Unknown"
      };

      history.unshift(historyItem);

      sessionStorage.setItem(
        "verificationHistory",
        JSON.stringify(history)
      );

      // --------------------------------------------------
      // GO TO RESULT
      // --------------------------------------------------

      navigate("/result");

    } catch (err) {
      console.error(
        "Verification error:",
        err
      );

      setError(
        err.message ||
        "Unable to connect to IDShield AI backend."
      );

      setIsVerifying(false);
    }
  };

  // ======================================================
  // UI
  // ======================================================

  return (
    <div className="verification-page">

      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="verification-header">

        <div>

          <div className="eyebrow">
            <span>✦</span>
            IDENTITY VERIFICATION
          </div>

          <h1>
            Start your
            <br />
            <span>verification.</span>
          </h1>

          <p>
            Upload your identity document and a clear
            face photo to begin the verification process.
          </p>

        </div>

      </div>


      {/* ==================================================
          CARD
      ================================================== */}

      <div className="verification-card">

        <div className="card-header">

          <div>
            <h2>
              Upload Documents
            </h2>

            <p>
              Upload files or capture them using your camera.
            </p>
          </div>

          <div className="step">
            01 / 01
          </div>

        </div>


        {/* ==================================================
            ERROR
        ================================================== */}

        {error && (
          <div className="verification-error">
            <span>!</span>
            <p>{error}</p>
          </div>
        )}


        {/* ==================================================
            UPLOAD GRID
        ================================================== */}

        <div className="upload-grid">


          {/* ==================================================
              DOCUMENT
          ================================================== */}

          <div className="upload-box">

            <div className="upload-top">

              <div className="upload-icon">
                ▣
              </div>

              <div>

                <h3>
                  Identity Document
                </h3>

                <p>
                  Government-issued identification
                </p>

              </div>

            </div>


            {!document ? (

              <div className="upload-options">

                <label className="upload-button">

                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={handleDocument}
                  />

                  <span>↑</span>
                  Upload Document

                </label>


                <button
                  type="button"
                  className="camera-button"
                  onClick={() =>
                    openCamera("document")
                  }
                >
                  <span>▣</span>
                  Take Photo
                </button>


                <small>
                  JPG, PNG or PDF • Max 10MB
                </small>

              </div>

            ) : (

              <div className="file-preview">

                {documentPreview &&
                document.type.startsWith("image/") ? (

                  <img
                    src={documentPreview}
                    alt="Uploaded document"
                  />

                ) : (

                  <div className="pdf-preview">
                    <span>PDF</span>
                    <strong>
                      Document uploaded
                    </strong>
                  </div>

                )}

                <div className="file-info">

                  <div>

                    <strong>
                      {document.name}
                    </strong>

                    <span>
                      {(document.size / 1024 / 1024).toFixed(2)}
                      {" "}MB
                    </span>

                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setDocument(null);
                      setDocumentPreview(null);
                    }}
                  >
                    Change
                  </button>

                </div>

              </div>

            )}

          </div>


          {/* ==================================================
              SELFIE
          ================================================== */}

          <div className="upload-box">

            <div className="upload-top">

              <div className="upload-icon">
                ◉
              </div>

              <div>

                <h3>
                  Face Photo
                </h3>

                <p>
                  Clear photo for face verification
                </p>

              </div>

            </div>


            {!selfie ? (

              <div className="upload-options">

                <label className="upload-button">

                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png"
                    capture="user"
                    onChange={handleSelfie}
                  />

                  <span>↑</span>
                  Upload Photo

                </label>


                <button
                  type="button"
                  className="camera-button"
                  onClick={() =>
                    openCamera("selfie")
                  }
                >
                  <span>◎</span>
                  Take Selfie

                </button>


                <small>
                  JPG or PNG • Max 10MB
                </small>

              </div>

            ) : (

              <div className="file-preview selfie-preview">

                {selfiePreview && (

                  <img
                    src={selfiePreview}
                    alt="Uploaded selfie"
                  />

                )}

                <div className="file-info">

                  <div>

                    <strong>
                      {selfie.name}
                    </strong>

                    <span>
                      {(selfie.size / 1024 / 1024).toFixed(2)}
                      {" "}MB
                    </span>

                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setSelfie(null);
                      setSelfiePreview(null);
                    }}
                  >
                    Change
                  </button>

                </div>

              </div>

            )}

          </div>

        </div>


        {/* ==================================================
            PRIVACY + BUTTON
        ================================================== */}

        <div className="verification-action">

          <div className="privacy-note">

            <span>🔒</span>

            <div>

              <strong>
                Your data is protected
              </strong>

              <p>
                Files are processed securely for verification.
              </p>

            </div>

          </div>


          <button
            className="verify-button"
            disabled={
              !document ||
              !selfie ||
              isVerifying
            }
            onClick={startVerification}
          >

            {isVerifying ? (
              <>
                <span className="button-spinner"></span>
                Verifying...
              </>
            ) : (
              <>
                Start Verification
                <span>→</span>
              </>
            )}

          </button>

        </div>

      </div>


      {/* ==================================================
          CAMERA MODAL
      ================================================== */}

      {cameraOpen && (

        <div className="camera-overlay">

          <div className="camera-modal">

            <div className="camera-header">

              <div>

                <span>
                  DOCUMENT CAPTURE
                </span>

                <h2>
                  {cameraType === "selfie"
                    ? "Take your selfie"
                    : "Capture your document"}
                </h2>

              </div>

              <button
                type="button"
                onClick={closeCamera}
              >
                ×
              </button>

            </div>


            <div className="camera-view">

              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
              />

              <div
                className={
                  cameraType === "selfie"
                    ? "face-frame"
                    : "document-frame"
                }
              >

                <span>
                  {cameraType === "selfie"
                    ? "Position your face inside the frame"
                    : "Place the complete document inside the frame"}
                </span>

              </div>

            </div>


            <div className="camera-controls">

              <button
                type="button"
                className="capture-button"
                onClick={capturePhoto}
              >
                <span></span>
                Capture Photo
              </button>

              <button
                type="button"
                className="cancel-camera"
                onClick={closeCamera}
              >
                Cancel
              </button>

            </div>

          </div>

        </div>

      )}


      {/* Hidden canvas used to capture camera image */}

      <canvas
        ref={canvasRef}
        style={{ display: "none" }}
      />

    </div>
  );
}

export default Verification;