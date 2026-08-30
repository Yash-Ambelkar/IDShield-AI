import { NavLink } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">

      <NavLink to="/" className="brand">

        <div className="brand-icon">
          ID
        </div>

        <div className="brand-text">
          <h2>IDShield</h2>
          <span>AI Verification</span>
        </div>

      </NavLink>


      <div className="nav-links">

        <NavLink to="/">
          Dashboard
        </NavLink>

        <NavLink to="/verification">
          Verification
        </NavLink>

        <NavLink to="/history">
          History
        </NavLink>

      </div>


      <div className="security-status">

        <span className="status-dot"></span>

        System Secure

      </div>

    </nav>
  );
}

export default Navbar;