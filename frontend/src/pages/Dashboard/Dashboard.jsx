import { Link } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-page">

      {/* HERO */}

      <section className="dashboard-hero">

        <div className="dashboard-hero-content">

          <div className="eyebrow">
            <span>✦</span>
            AI-POWERED IDENTITY SECURITY
          </div>

          <h1>
            Secure identity
            <br />
            verification,
            <span> reimagined.</span>
          </h1>

          <p>
            IDShield AI combines document intelligence,
            tampering detection and biometric verification
            to help security teams identify suspicious
            identities faster.
          </p>

          <Link
            to="/verification"
            className="primary-button"
          >
            Start Verification
            <span>→</span>
          </Link>

        </div>


        {/* SECURITY VISUAL */}

        <div className="security-visual">

          <div className="visual-glow"></div>

          <div className="shield-large">

            <div className="shield-inner">
              ✓
            </div>

            <div className="scan-line"></div>

          </div>

          <div className="visual-label">
            ✓ AI ENGINE ONLINE
          </div>

        </div>

      </section>


      {/* STATS */}

      <section className="stats-grid">

        <div className="stat-card">

          <div className="stat-icon">
            ✓
          </div>

          <div>
            <strong>4</strong>
            <span>AI Security Layers</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ⚡
          </div>

          <div>
            <strong>Seconds</strong>
            <span>Automated Screening</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            ◇
          </div>

          <div>
            <strong>AI</strong>
            <span>Risk Assessment</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">
            🔒
          </div>

          <div>
            <strong>Secure</strong>
            <span>Verification Processing</span>
          </div>

        </div>

      </section>


      {/* HOW IT WORKS */}

      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <span className="mini-label">
              HOW IT WORKS
            </span>

            <h2>
              One verification. Multiple checks.
            </h2>

          </div>

          <p>
            IDShield analyzes identity information through
            multiple independent security layers.
          </p>

        </div>


        <div className="workflow">

          <Workflow
            number="01"
            icon="▤"
            title="Upload"
            text="Submit the identity document and face photo."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="02"
            icon="⌕"
            title="Analyze"
            text="AI extracts and analyzes identity information."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="03"
            icon="✓"
            title="Verify"
            text="Multiple security checks verify the identity."
          />

          <div className="workflow-line"></div>

          <Workflow
            number="04"
            icon="◆"
            title="Decide"
            text="Risk engine produces the final decision."
          />

        </div>

      </section>


      {/* CAPABILITIES */}

      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <span className="mini-label">
              VERIFICATION ENGINE
            </span>

            <h2>
              Four layers of protection
            </h2>

          </div>

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
            text="Check required fields, dates and document information."
          />

          <Capability
            number="03"
            icon="⌁"
            title="Tampering Detection"
            text="Detect suspicious visual modifications in documents."
          />

          <Capability
            number="04"
            icon="◉"
            title="Face Verification"
            text="Compare the submitted face against the identity document."
          />

        </div>

      </section>


      {/* CTA */}

      <section className="dashboard-cta">

        <div>

          <span className="mini-label">
            READY TO VERIFY?
          </span>

          <h2>
            Start a secure identity verification.
          </h2>

          <p>
            Upload your documents and let IDShield AI analyze them.
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


/* WORKFLOW COMPONENT */

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


/* CAPABILITY COMPONENT */

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

    </div>
  );
}


export default Dashboard;