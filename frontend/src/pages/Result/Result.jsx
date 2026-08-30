import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Result.css";

function Result() {
  const navigate = useNavigate();

  const [result, setResult] = useState(null);

  const [documentPreview, setDocumentPreview] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState(null);

  const [documentName, setDocumentName] = useState("");
  const [selfieName, setSelfieName] = useState("");

  // ======================================================
  // LOAD VERIFICATION RESULT + FILE PREVIEWS
  // ======================================================

  useEffect(() => {
    const storedResult =
      sessionStorage.getItem("verificationResult");

    if (!storedResult) {
      navigate("/verification");
      return;
    }

    try {
      // ==================================================
      // LOAD BACKEND RESULT
      // ==================================================

      const parsedResult = JSON.parse(storedResult);

      setResult(parsedResult);

      // ==================================================
      // LOAD UPLOADED FILES
      // ==================================================

      const storedFiles =
        sessionStorage.getItem("verificationFiles");

      if (storedFiles) {
        const files = JSON.parse(storedFiles);

        // ------------------------------------------------
        // DOCUMENT PREVIEW
        // ------------------------------------------------

        if (files.document) {
          setDocumentPreview(files.document);
        }

        // ------------------------------------------------
        // SELFIE PREVIEW
        // ------------------------------------------------

        if (files.selfie) {
          setSelfiePreview(files.selfie);
        }

        // ------------------------------------------------
        // DOCUMENT NAME
        // ------------------------------------------------

        if (files.documentName) {
          setDocumentName(files.documentName);
        }

        // ------------------------------------------------
        // SELFIE NAME
        // ------------------------------------------------

        if (files.selfieName) {
          setSelfieName(files.selfieName);
        }
      }

    } catch (error) {
      console.error(
        "Unable to read verification result:",
        error
      );

      navigate("/verification");
    }

  }, [navigate]);


  // ======================================================
  // LOADING
  // ======================================================

  if (!result) {
    return (
      <div className="result-loading">

        <div className="loading-spinner"></div>

        <h2>
          Loading verification result...
        </h2>

        <p>
          Please wait while the verification result is loaded.
        </p>

      </div>
    );
  }


  // ======================================================
  // BACKEND DATA
  // ======================================================

  const ocrData =
    result.ocr?.document_data || {};

  const validation =
    result.validation || {};

  const tampering =
    result.tampering || {};

  const face =
    result.face_verification || {};

  const risk =
    result.risk || {};


  // ======================================================
  // BASIC VALUES
  // ======================================================

  const decision =
    risk.decision || "UNKNOWN";

  const riskLevel =
    risk.risk_level || "UNKNOWN";

  const riskScore =
    risk.risk_score ?? 0;

  const validationScore =
    validation.validation_score ?? 0;

  const tamperingScore =
    tampering.tampering_score ?? 0;

  const faceSimilarity =
    face.similarity_score;


  // ======================================================
  // FINAL DECISION STATES
  // ======================================================

  const isApproved =
    decision === "DOCUMENT APPROVED";

  const isRejected =
    decision === "DOCUMENT REJECTED";


  const faceMatched =
    face.status === "MATCH";


  // ======================================================
  // OCR FIELD COUNT
  // ======================================================

  const extractedFields =
    [
      ocrData.document_type,
      ocrData.document_number,
      ocrData.name,
      ocrData.nationality,
      ocrData.date_of_birth,
      ocrData.date_of_expiry,
      ocrData.gender
    ].filter(
      (value) =>
        value !== null &&
        value !== undefined &&
        value !== ""
    ).length;


  // ======================================================
  // NEW VERIFICATION
  // ======================================================

  const newVerification = () => {

    sessionStorage.removeItem(
      "verificationResult"
    );

    sessionStorage.removeItem(
      "verificationFiles"
    );

    sessionStorage.removeItem(
      "uploadedDocument"
    );

    sessionStorage.removeItem(
      "uploadedSelfie"
    );

    sessionStorage.removeItem(
      "documentName"
    );

    sessionStorage.removeItem(
      "selfieName"
    );

    navigate("/verification");

  };


  // ======================================================
  // DOCUMENT TYPE
  // ======================================================

  const documentType =
    ocrData.document_type ||
    "Not detected";


  // ======================================================
  // PDF DETECTION
  // ======================================================

  const isPDF =
    documentName &&
    documentName
      .toLowerCase()
      .endsWith(".pdf");


  // ======================================================
  // RENDER
  // ======================================================

  return (

    <div className="result-page">


      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="result-header">

        <div>

          <div className="eyebrow">

            <span>
              ✦
            </span>

            VERIFICATION RESULT

          </div>


          <h1>

            Verification

            <br />

            <span>
              result.
            </span>

          </h1>


          <p className="result-intro">

            AI analysis has completed the identity
            verification process.

          </p>

        </div>


        <button
          className="new-verification"
          onClick={newVerification}
        >

          + New Verification

        </button>

      </div>



      {/* ==================================================
          SUBMITTED FILES
      ================================================== */}

      <section className="submitted-section">


        <div className="section-heading">

          <div>

            <span className="mini-label">
              SUBMITTED FILES
            </span>

            <h2>
              Your uploaded documents
            </h2>

          </div>


          <p>
            These are the files analyzed by IDShield AI.
          </p>

        </div>



        <div className="submitted-grid">


          {/* ==================================================
              IDENTITY DOCUMENT
          ================================================== */}

          <div className="submitted-card">


            <div className="submitted-card-header">


              <div className="submitted-title">

                <div className="submitted-icon">
                  ▣
                </div>


                <div>

                  <h3>
                    Identity Document
                  </h3>

                  <span>
                    Document submitted for verification
                  </span>

                </div>

              </div>


              <span className="uploaded-badge">

                ✓ UPLOADED

              </span>

            </div>



            {/* ==================================================
                DOCUMENT PREVIEW
            ================================================== */}

            <div className="document-preview">

              {documentPreview ? (

                isPDF ? (

                  <div className="pdf-result-preview">

                    <div className="pdf-result-icon">
                      PDF
                    </div>

                    <strong>
                      {documentName || "PDF document"}
                    </strong>

                    <span>
                      PDF document uploaded successfully
                    </span>

                  </div>

                ) : (

                  <img
                    src={documentPreview}
                    alt="Uploaded identity document"
                  />

                )

              ) : (

                <div className="preview-empty">

                  <div className="preview-empty-icon">
                    ▣
                  </div>

                  <strong>
                    Document preview unavailable
                  </strong>

                  <span>
                    The document was submitted successfully.
                  </span>

                </div>

              )}

            </div>



            {/* ==================================================
                DOCUMENT FILE INFORMATION
            ================================================== */}

            <div className="file-information">

              <span>
                FILE NAME
              </span>


              <strong>
                {documentName || "Uploaded document"}
              </strong>

            </div>


          </div>



          {/* ==================================================
              FACE PHOTO
          ================================================== */}

          <div className="submitted-card">


            <div className="submitted-card-header">


              <div className="submitted-title">

                <div className="submitted-icon face">
                  ◉
                </div>


                <div>

                  <h3>
                    Face Photo
                  </h3>

                  <span>
                    Photo submitted for face verification
                  </span>

                </div>

              </div>


              <span className="uploaded-badge">

                ✓ UPLOADED

              </span>

            </div>



            {/* ==================================================
                SELFIE PREVIEW
            ================================================== */}

            <div className="face-preview">

              {selfiePreview ? (

                <img
                  src={selfiePreview}
                  alt="Uploaded face"
                />

              ) : (

                <div className="preview-empty">

                  <div className="preview-empty-icon">
                    ◉
                  </div>

                  <strong>
                    Face preview unavailable
                  </strong>

                  <span>
                    The face image was submitted successfully.
                  </span>

                </div>

              )}

            </div>



            {/* ==================================================
                SELFIE FILE INFORMATION
            ================================================== */}

            <div className="file-information">

              <span>
                FILE NAME
              </span>


              <strong>
                {selfieName || "Uploaded face photo"}
              </strong>

            </div>


          </div>


        </div>

      </section>



      {/* ==================================================
          FINAL DECISION
      ================================================== */}

      <div
        className={`result-summary ${
          isApproved
            ? "approved"
            : isRejected
            ? "rejected"
            : "review"
        }`}
      >


        <div className="result-status">


          <div className="result-check">

            {isApproved
              ? "✓"
              : isRejected
              ? "×"
              : "!"}

          </div>


          <div>

            <span className="result-label">
              FINAL DECISION
            </span>


            <h2>
              {decision}
            </h2>


            <p>

              {isApproved

                ? "All required verification checks passed successfully."

                : isRejected

                ? "One or more verification checks failed."

                : "The document requires additional review."

              }

            </p>

          </div>


        </div>



        <div className="risk-score">

          <span>
            RISK SCORE
          </span>


          <strong>
            {String(riskScore).padStart(2, "0")}
          </strong>


          <small>
            {riskLevel} RISK
          </small>

        </div>


      </div>



      {/* ==================================================
          VERIFICATION CHECKS
      ================================================== */}

      <div className="result-grid">


        {/* ==================================================
            OCR
        ================================================== */}

        <div className="result-card">


          <div className="result-card-top">


            <div className="result-icon">
              ▤
            </div>


            <span
              className={
                result.ocr?.status === "PASS"
                  ? "passed"
                  : result.ocr?.status === "FAIL"
                  ? "failed"
                  : "unknown"
              }
            >

              {result.ocr?.status || "UNKNOWN"}

            </span>


          </div>


          <h3>
            Document OCR
          </h3>


          <p>
            Identity information extracted from
            the submitted document.
          </p>


          <div className="result-line">

            <span>
              Fields extracted
            </span>


            <strong>
              {extractedFields} / 7
            </strong>

          </div>


        </div>



        {/* ==================================================
            VALIDATION
        ================================================== */}

        <div className="result-card">


          <div className="result-card-top">


            <div className="result-icon">
              ✓
            </div>


            <span
              className={
                validation.status === "PASS"
                  ? "passed"
                  : validation.status === "FAIL"
                  ? "failed"
                  : "unknown"
              }
            >

              {validation.status || "UNKNOWN"}

            </span>


          </div>


          <h3>
            Document Validation
          </h3>


          <p>
            Required fields, dates and document
            information were checked.
          </p>


          <div className="result-line">

            <span>
              Validation score
            </span>


            <strong>
              {validationScore}%
            </strong>

          </div>


        </div>



        {/* ==================================================
            TAMPERING
        ================================================== */}

        <div className="result-card">


          <div className="result-card-top">


            <div className="result-icon">
              ⌁
            </div>


            <span
              className={
                tampering.status === "PASS"
                  ? "passed"
                  : tampering.status === "FAIL"
                  ? "failed"
                  : tampering.status === "FLAGGED"
                  ? "failed"
                  : "unknown"
              }
            >

              {tampering.status || "UNKNOWN"}

            </span>


          </div>


          <h3>
            Tampering Detection
          </h3>


          <p>
            The submitted document was checked for
            suspicious visual modifications.
          </p>


          <div className="result-line">

            <span>
              Tampering score
            </span>


            <strong>
              {tamperingScore}
            </strong>

          </div>


        </div>



        {/* ==================================================
            FACE
        ================================================== */}

        <div className="result-card">


          <div className="result-card-top">


            <div className="result-icon">
              ◉
            </div>


            <span
              className={
                faceMatched
                  ? "passed"
                  : face.status === "NO_MATCH"
                  ? "failed"
                  : "unknown"
              }
            >

              {face.status || "UNKNOWN"}

            </span>


          </div>


          <h3>
            Face Verification
          </h3>


          <p>

            {face.status === "NO_FACE"

              ? "No face was detected in the identity document."

              : face.status === "MATCH"

              ? "The submitted face matches the document identity."

              : face.status === "NO_MATCH"

              ? "The submitted face does not match the document."

              : face.message ||
                "Face verification could not be completed."

            }

          </p>


          <div className="result-line">

            <span>
              Similarity
            </span>


            <strong>

              {faceSimilarity !== null &&
              faceSimilarity !== undefined

                ? `${faceSimilarity}%`

                : "N/A"}

            </strong>

          </div>


        </div>


      </div>



      {/* ==================================================
          DOCUMENT DETAILS
      ================================================== */}

      <div className="details-card">


        <div className="details-heading">


          <div>

            <span className="mini-label">
              EXTRACTED INFORMATION
            </span>


            <h2>
              Document Details
            </h2>

          </div>


          <span
            className={
              validation.status === "PASS"
                ? "verified-badge"
                : "review-badge"
            }
          >

            {validation.status === "PASS"
              ? "✓ VERIFIED"
              : "⚠ REVIEW"}

          </span>


        </div>



        <div className="details-grid">


          {/* ==================================================
              DOCUMENT TYPE
          ================================================== */}

          <div>

            <span>
              Document Type
            </span>


            <strong>
              {documentType}
            </strong>

          </div>



          {/* ==================================================
              NAME
          ================================================== */}

          <div>

            <span>
              Full Name
            </span>


            <strong>
              {ocrData.name ||
                "Not detected"}
            </strong>

          </div>



          {/* ==================================================
              DOCUMENT NUMBER
          ================================================== */}

          <div>

            <span>
              Document Number
            </span>


            <strong>
              {ocrData.document_number ||
                "Not detected"}
            </strong>

          </div>



          {/* ==================================================
              NATIONALITY
          ================================================== */}

          <div>

            <span>
              Nationality
            </span>


            <strong>
              {ocrData.nationality ||
                "Not detected"}
            </strong>

          </div>



          {/* ==================================================
              DATE OF BIRTH
          ================================================== */}

          <div>

            <span>
              Date of Birth
            </span>


            <strong>
              {ocrData.date_of_birth ||
                "Not detected"}
            </strong>

          </div>



          {/* ==================================================
              DATE OF EXPIRY
          ================================================== */}

          <div>

            <span>
              Date of Expiry
            </span>


            <strong>
              {ocrData.date_of_expiry ||
                "Not detected"}
            </strong>

          </div>



          {/* ==================================================
              GENDER
          ================================================== */}

          <div>

            <span>
              Gender
            </span>


            <strong>
              {ocrData.gender ||
                "Not detected"}
            </strong>

          </div>


        </div>

      </div>



      {/* ==================================================
          WARNINGS
      ================================================== */}

      {risk.warnings &&
        risk.warnings.length > 0 && (

        <div className="warnings-card">


          <div className="warnings-icon">
            !
          </div>


          <div>

            <strong>
              Verification Warnings
            </strong>


            {risk.warnings.map(
              (warning, index) => (

                <p key={index}>
                  {warning}
                </p>

              )
            )}

          </div>


        </div>

      )}



      {/* ==================================================
          AUDIT
      ================================================== */}

      <div className="audit-card">


        <div className="audit-icon">
          ✓
        </div>


        <div>

          <strong>
            Verification completed
          </strong>


          <p>
            Results were generated by the IDShield AI
            verification pipeline using the submitted files.
          </p>

        </div>


        <div className="audit-id">

          <span>
            VERIFICATION ID
          </span>


          <strong>
            {result.verification_id ||
              "N/A"}
          </strong>

        </div>


      </div>


    </div>

  );
}

export default Result;