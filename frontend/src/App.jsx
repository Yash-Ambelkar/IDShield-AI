import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar/Navbar";
import Footer from "./components/Footer/Footer";

import Dashboard from "./pages/Dashboard/Dashboard";
import Verification from "./pages/Verification/Verification";
import Result from "./pages/Result/Result";
import History from "./pages/History/History";

import "./App.css";

function App() {
  return (
    <div className="app">

      <Navbar />

      <main className="main">

        <Routes>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/verification"
            element={<Verification />}
          />

          <Route
            path="/result"
            element={<Result />}
          />

          <Route
            path="/history"
            element={<History />}
          />

        </Routes>

      </main>

      <Footer />

    </div>
  );
}

export default App;