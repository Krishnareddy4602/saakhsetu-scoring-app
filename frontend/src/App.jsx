import React, { useState } from "react";
import ScoreForm from "./components/ScoreForm.jsx";
import ScoreResult from "./components/ScoreResult.jsx";
import { postScore } from "./api.js";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  async function handleSubmit(payload) {
    setLoading(true);
    setError(null);
    setFieldErrors({});
    setResult(null);
    try {
      const data = await postScore(payload);
      setResult(data);
    } catch (err) {
      setError(err.message);
      if (err.fieldErrors) setFieldErrors(err.fieldErrors);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>SaakhSetu — Farmer Scoring</h1>
      <p className="subtitle">
        Enter the applicant details below to compute a rule-based score.
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      <ScoreForm
        onSubmit={handleSubmit}
        loading={loading}
        fieldErrors={fieldErrors}
      />

      <ScoreResult result={result} />
    </div>
  );
}
