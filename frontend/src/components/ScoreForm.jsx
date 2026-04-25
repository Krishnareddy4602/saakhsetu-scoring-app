import React, { useState } from "react";

const INCOME_BANDS = ["<2L", "2-5L", "5-10L", ">10L"];

const INITIAL = {
  land_area_acres: "",
  crop_type: "",
  repayment_history_score: "",
  annual_income_band: "2-5L",
};

function validate(form) {
  const errors = {};
  const land = Number(form.land_area_acres);
  if (form.land_area_acres === "" || Number.isNaN(land)) {
    errors.land_area_acres = "Enter a number.";
  } else if (land <= 0) {
    errors.land_area_acres = "Must be greater than 0.";
  }

  if (!form.crop_type.trim()) {
    errors.crop_type = "Crop type is required.";
  }

  const repay = Number(form.repayment_history_score);
  if (form.repayment_history_score === "" || Number.isNaN(repay)) {
    errors.repayment_history_score = "Enter a number.";
  } else if (repay < 0 || repay > 100) {
    errors.repayment_history_score = "Must be between 0 and 100.";
  }

  if (!INCOME_BANDS.includes(form.annual_income_band)) {
    errors.annual_income_band = "Pick a valid band.";
  }

  return errors;
}

export default function ScoreForm({ onSubmit, loading, fieldErrors }) {
  const [form, setForm] = useState(INITIAL);
  const [localErrors, setLocalErrors] = useState({});

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const errors = validate(form);
    setLocalErrors(errors);
    if (Object.keys(errors).length > 0) return;

    onSubmit({
      land_area_acres: Number(form.land_area_acres),
      crop_type: form.crop_type.trim(),
      repayment_history_score: Number(form.repayment_history_score),
      annual_income_band: form.annual_income_band,
    });
  }

  function errorFor(field) {
    return localErrors[field] || (fieldErrors && fieldErrors[field]);
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="land_area_acres">Land area (acres)</label>
        <input
          id="land_area_acres"
          type="number"
          step="0.1"
          min="0"
          value={form.land_area_acres}
          onChange={(e) => update("land_area_acres", e.target.value)}
          disabled={loading}
        />
        {errorFor("land_area_acres") && (
          <span className="error">{errorFor("land_area_acres")}</span>
        )}
      </div>

      <div className="field">
        <label htmlFor="crop_type">Crop type</label>
        <input
          id="crop_type"
          type="text"
          value={form.crop_type}
          onChange={(e) => update("crop_type", e.target.value)}
          disabled={loading}
          placeholder="e.g. paddy, cotton, sugarcane"
        />
        {errorFor("crop_type") && (
          <span className="error">{errorFor("crop_type")}</span>
        )}
      </div>

      <div className="field">
        <label htmlFor="repayment_history_score">
          Repayment history score (0–100)
        </label>
        <input
          id="repayment_history_score"
          type="number"
          step="1"
          min="0"
          max="100"
          value={form.repayment_history_score}
          onChange={(e) => update("repayment_history_score", e.target.value)}
          disabled={loading}
        />
        {errorFor("repayment_history_score") && (
          <span className="error">{errorFor("repayment_history_score")}</span>
        )}
      </div>

      <div className="field">
        <label htmlFor="annual_income_band">Annual income band</label>
        <select
          id="annual_income_band"
          value={form.annual_income_band}
          onChange={(e) => update("annual_income_band", e.target.value)}
          disabled={loading}
        >
          {INCOME_BANDS.map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>
        {errorFor("annual_income_band") && (
          <span className="error">{errorFor("annual_income_band")}</span>
        )}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Scoring…" : "Compute score"}
      </button>
    </form>
  );
}
