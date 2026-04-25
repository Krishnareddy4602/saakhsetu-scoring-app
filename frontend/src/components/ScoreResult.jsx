import React from "react";

export default function ScoreResult({ result }) {
  if (!result) return null;
  return (
    <div className="card">
      <div className="score-row">
        <span className="score-value">{result.score}</span>
        <span className="score-label">/ 100</span>
      </div>
      <div className="reasons">
        {result.reason_codes.map((code) => (
          <span key={code} className="reason-chip">
            {code}
          </span>
        ))}
      </div>
      <div className="meta">
        <div>Request ID: {result.request_id}</div>
        <div>Timestamp: {result.timestamp}</div>
      </div>
    </div>
  );
}
