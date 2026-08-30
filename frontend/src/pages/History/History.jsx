import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./History.css";

function History() {

  const navigate = useNavigate();

  const [history, setHistory] = useState([]);


  // ======================================================
  // LOAD HISTORY
  // ======================================================

  useEffect(() => {

    loadHistory();

  }, []);


  const loadHistory = () => {

    const storedHistory =
      JSON.parse(
        localStorage.getItem(
          "verificationHistory"
        ) || "[]"
      );

    setHistory(storedHistory);

  };


  // ======================================================
  // OPEN RESULT
  // ======================================================

  const openResult = (item) => {

    sessionStorage.setItem(
      "verificationResult",
      JSON.stringify(item.result)
    );

    sessionStorage.setItem(
      "verificationId",
      item.id
    );

    sessionStorage.setItem(
      "documentName",
      item.documentName
    );

    sessionStorage.setItem(
      "selfieName",
      item.selfieName
    );

    navigate("/result");

  };


  // ======================================================
  // DELETE ONE
  // ======================================================

  const deleteRecord = (id) => {

    const updatedHistory =
      history.filter(
        item => item.id !== id
      );

    localStorage.setItem(
      "verificationHistory",
      JSON.stringify(updatedHistory)
    );

    setHistory(updatedHistory);

  };


  // ======================================================
  // CLEAR ALL
  // ======================================================

  const clearHistory = () => {

    const confirmed =
      window.confirm(
        "Are you sure you want to clear verification history?"
      );

    if (!confirmed) {
      return;
    }

    localStorage.removeItem(
      "verificationHistory"
    );

    setHistory([]);

  };


  // ======================================================
  // FORMAT DATE
  // ======================================================

  const formatDate = (date) => {

    try {

      return new Date(date).toLocaleString(
        "en-IN",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }
      );

    } catch {

      return "Unknown date";

    }

  };


  // ======================================================
  // GET DECISION
  // ======================================================

  const getDecision = (item) => {

    return (
      item.result?.risk?.decision ||
      "UNKNOWN"
    );

  };


  // ======================================================
  // GET RISK
  // ======================================================

  const getRisk = (item) => {

    return (
      item.result?.risk?.risk_level ||
      "UNKNOWN"
    );

  };


  // ======================================================
  // GET SCORE
  // ======================================================

  const getScore = (item) => {

    return (
      item.result?.risk?.risk_score ??
      0
    );

  };


  // ======================================================
  // STATUS CLASS
  // ======================================================

  const getStatusClass = (item) => {

    const decision =
      getDecision(item);

    if (
      decision ===
      "DOCUMENT APPROVED"
    ) {
      return "approved";
    }

    if (
      decision ===
      "DOCUMENT REJECTED"
    ) {
      return "rejected";
    }

    return "review";

  };


  // ======================================================
  // PAGE
  // ======================================================

  return (

    <div className="history-page">


      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="history-header">


        <div>

          <div className="eyebrow">

            <span>✦</span>

            VERIFICATION HISTORY

          </div>


          <h1>

            Verification

            <br />

            <span>
              history.
            </span>

          </h1>


          <p>

            Review previously processed identity
            verification requests.

          </p>

        </div>



        <div className="history-actions">

          <button
            className="new-verification"
            onClick={() =>
              navigate("/verification")
            }
          >

            + New Verification

          </button>


          {history.length > 0 && (

            <button
              className="clear-history"
              onClick={clearHistory}
            >

              Clear History

            </button>

          )}

        </div>


      </div>



      {/* ==================================================
          STATS
      ================================================== */}

      <div className="history-stats">


        <div className="history-stat">

          <span>
            TOTAL VERIFICATIONS
          </span>

          <strong>
            {history.length}
          </strong>

        </div>


        <div className="history-stat">

          <span>
            APPROVED
          </span>

          <strong>

            {
              history.filter(
                item =>
                  getDecision(item) ===
                  "DOCUMENT APPROVED"
              ).length
            }

          </strong>

        </div>


        <div className="history-stat">

          <span>
            REJECTED
          </span>

          <strong>

            {
              history.filter(
                item =>
                  getDecision(item) ===
                  "DOCUMENT REJECTED"
              ).length
            }

          </strong>

        </div>


        <div className="history-stat">

          <span>
            REVIEW
          </span>

          <strong>

            {
              history.filter(
                item =>
                  ![
                    "DOCUMENT APPROVED",
                    "DOCUMENT REJECTED"
                  ].includes(
                    getDecision(item)
                  )
              ).length
            }

          </strong>

        </div>


      </div>



      {/* ==================================================
          EMPTY STATE
      ================================================== */}

      {history.length === 0 ? (

        <div className="history-empty">


          <div className="empty-icon">
            ◫
          </div>


          <h2>
            No verification history
          </h2>


          <p>
            Completed verification requests will
            appear here automatically.
          </p>


          <button
            onClick={() =>
              navigate("/verification")
            }
          >

            Start Verification →

          </button>


        </div>

      ) : (


        /* ==================================================
           HISTORY LIST
        ================================================== */

        <div className="history-list">


          {history.map((item) => {


            const decision =
              getDecision(item);

            const risk =
              getRisk(item);

            const score =
              getScore(item);

            const statusClass =
              getStatusClass(item);


            return (

              <div
                className={`history-item ${statusClass}`}
                key={item.id}
              >


                {/* ICON */}

                <div className="history-document-icon">

                  ▣

                </div>



                {/* MAIN */}

                <div className="history-main">


                  <div className="history-main-top">

                    <h3>
                      {item.documentName ||
                        "Identity Document"}
                    </h3>


                    <span
                      className={`history-status ${statusClass}`}
                    >

                      {decision ===
                      "DOCUMENT APPROVED"

                        ? "✓ APPROVED"

                        : decision ===
                          "DOCUMENT REJECTED"

                        ? "× REJECTED"

                        : "! REVIEW"}

                    </span>

                  </div>


                  <p>

                    Verification ID:

                    <strong>
                      {item.id}
                    </strong>

                  </p>


                  <span className="history-date">

                    {formatDate(item.date)}

                  </span>


                </div>



                {/* RISK */}

                <div className="history-risk">

                  <span>
                    RISK SCORE
                  </span>


                  <strong>
                    {String(score).padStart(
                      2,
                      "0"
                    )}
                  </strong>


                  <small>
                    {risk}
                  </small>

                </div>



                {/* OPEN */}

                <button
                  className="view-history"
                  onClick={() =>
                    openResult(item)
                  }
                >

                  View

                  <span>
                    →
                  </span>

                </button>



                {/* DELETE */}

                <button
                  className="delete-history"
                  onClick={() =>
                    deleteRecord(item.id)
                  }
                  title="Delete verification"
                >

                  ×

                </button>


              </div>

            );

          })}


        </div>

      )}


    </div>

  );

}

export default History;