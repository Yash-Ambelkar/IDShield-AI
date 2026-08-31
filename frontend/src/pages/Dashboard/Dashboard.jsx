import { Link } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-page">

      {/* =====================================================
          HERO
      ===================================================== */}

      <section className="dashboard-hero">

        <div className="dashboard-hero-content">

          <div className="eyebrow">
            <span className="eyebrow-dot"></span>
            AI-POWERED IDENTITY SECURITY
          </div>

          <h1>
            Verify identities
            <br />
            with <span>confidence.</span>
          </h1>

          <p>
            IDShield AI analyzes identity documents through
            document intelligence, fraud detection and
            biometric verification — all in one verification flow.
          </p>

          <div className="hero-actions">

            <Link
              to="/verification"
              className="primary-button"
            >
              Start Verification
              <span>→</span>
            </Link>

            <a
              href="#how-it-works"
              className="secondary-button"
            >
              How it works
            </a>

          </div>

          <div className="hero-trust">

            <div className="trust-item">
              <span>✓</span>
              AI Analysis
            </div>

            <div className="trust-item">
              <span>✓</span>
              Fraud Detection
            </div>

            <div className="trust-item">
              <span>✓</span>
              Face Verification
            </div>

          </div>

        </div>


        {/* =================================================
            SECURITY VISUAL
        ================================================= */}

        <div className="security-visual">

          <div className="visual-glow"></div>

          <div className="security-orbit orbit-one"></div>
          <div className="security-orbit orbit-two"></div>

          <div className="shield-large">

            <div className="shield-inner">
              ✓
            </div>

            <div className="scan-line"></div>

          </div>

          <div className="visual-status">

            <span className="status-dot"></span>

            <span>
              AI ENGINE
            </span>

            <strong>
              ONLINE
            </strong>

          </div>

          <div className="floating-card floating-card-top">

            <span className="floating-icon">
              ◉
            </span>

            <div>
              <strong>
                Face Match
              </strong>

              <small>
                Ready
              </small>
            </div>

            <span className="floating-check">
              ✓
            </span>

          </div>

          <div className="floating-card floating-card-bottom">

            <span className="floating-icon">
              ◇
            </span>

            <div>
              <strong>
                Risk Engine
              </strong>

              <small>
                Active
              </small>
            </div>

            <span className="floating-check">
              ✓
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          QUICK STATS
      ===================================================== */}

      <section className="stats-grid">

        <StatCard
          icon="✓"
          value="4"
          label="Security Layers"
        />

        <StatCard
          icon="⚡"
          value="Fast"
          label="Automated Analysis"
        />

        <StatCard
          icon="◈"
          value="AI"
          label="Risk Assessment"
        />

        <StatCard
          icon="🔒"
          value="Secure"
          label="Document Processing"
        />

      </section>


      {/* =====================================================
          HOW IT WORKS
      ===================================================== */}

      <section
        className="dashboard-section"
        id="how-it-works"
      >

        <div className="section-heading">

          <div>

            <span className="mini-label">
              VERIFICATION FLOW
            </span>

            <h2>
              From document to decision.
            </h2>

          </div>

          <p>
            A simple verification process powered by
            multiple AI-driven security checks.
          </p>

        </div>


        <div className="workflow">

          <Workflow
            number="01"
            icon="▤"
            title="Submit"
            text="Upload your identity document and selfie."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="02"
            icon="⌕"
            title="Analyze"
            text="AI extracts and analyzes the submitted information."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="03"
            icon="✓"
            title="Verify"
            text="Identity, authenticity and document signals are checked."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="04"
            icon="◆"
            title="Decide"
            text="The risk engine generates the final verification decision."
          />

        </div>

      </section>


      {/* =====================================================
          SECURITY LAYERS
      ===================================================== */}

      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <span className="mini-label">
              IDSHIELD AI ENGINE
            </span>

            <h2>
              Multiple layers. One decision.
            </h2>

          </div>

          <p>
            Each layer contributes signals that help
            build a stronger verification result.
          </p>

        </div>


        <div className="capabilities-grid">

          <Capability
            number="01"
            icon="▤"
            title="Document OCR"
            text="Extract identity information automatically from submitted documents."
          />

          <Capability
            number="02"
            icon="✓"
            title="Validation"
            text="Check document fields, formats and required identity information."
          />

          <Capability
            number="03"
            icon="⌁"
            title="Tampering Detection"
            text="Analyze documents for suspicious visual or forensic anomalies."
          />

          <Capability
            number="04"
            icon="◉"
            title="Face Verification"
            text="Compare the submitted selfie with the document portrait."
          />

        </div>

      </section>


      {/* =====================================================
          CTA
      ===================================================== */}

      <section className="dashboard-cta">

        <div className="cta-content">

          <span className="mini-label">
            READY TO VERIFY?
          </span>

          <h2>
            Verify an identity in a few simple steps.
          </h2>

          <p>
            Upload your document and selfie,
            then let IDShield AI handle the analysis.
          </p>

        </div>


        <Link
          to="/verification"
          className="primary-button"
        >
          Start Verification
          <span>→</span>
        </Link>

      </section>

    </div>
  );
}


/* ==========================================================
   STAT CARD
========================================================== */

function StatCard({
  icon,
  value,
  label
}) {

  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div className="stat-content">

        <strong>
          {value}
        </strong>

        <span>
          {label}
        </span>

      </div>

    </div>
  );
}


/* ==========================================================
   WORKFLOW
========================================================== */

function Workflow({
  number,
  icon,
  title,
  text
}) {

  return (
    <div className="workflow-item">

      <span className="workflow-number">
        {number}
      </span>

      <div className="workflow-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}


/* ==========================================================
   CAPABILITY
========================================================== */

function Capability({
  number,
  icon,
  title,
  text
}) {

  return (
    <div className="capability-card">

      <span className="capability-number">
        {number}
      </span>

      <div className="capability-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

      <div className="capability-arrow">
        →
      </div>

    </div>
  );
}


export default Dashboard;