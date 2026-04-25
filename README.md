# SaakhSetu Scoring App

A small end-to-end credit-style scoring app for the Arbix AI / SaakhSetu
practical exercise. A Python (FastAPI) backend exposes a `/score` endpoint
that runs a simple, explainable, rule-based score over four input fields,
and a minimal React (Vite) frontend lets you submit the form and see the
score and reason codes.

## Time-box (required disclosure)

- **Start time (IST):** 25 April 2026, 11:00 IST
- **End time (IST):**   25 April 2026, 12:30 IST
- **Approximate total time spent:** ~90 minutes

### What I completed

- `POST /score` endpoint with full input validation (FastAPI + Pydantic v2)
- Rule-based, explainable scoring (repayment 50 pts, income 30 pts, land 20 pts)
- Exactly 3 reason codes per response, plus `request_id`, `score`, `timestamp`
- Useful 422 error responses with per-field messages
- Structured audit logging (JSON line per request) to stdout and `audit.log`
- Unit tests for scoring logic + API tests covering happy path and several
  validation error paths (well above the 2-test minimum)
- Minimal React frontend with form, loading state, field-level errors, and
  graceful handling of backend errors / network failures
- `/health` endpoint for quick sanity checks

## Project structure

```
saakhsetu-scoring-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + routes + error handler
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── scoring.py           # Pure rule-based scoring logic
│   │   └── logging_config.py    # Structured audit logging setup
│   ├── tests/
│   │   ├── test_scoring.py      # Unit tests for scoring logic
│   │   └── test_api.py          # API tests (happy path + validation)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── components/ScoreForm.jsx
│   │   └── components/ScoreResult.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
└── LLM_NOTES.md
```

## Run steps

### Backend (Python 3.10+)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now served at `http://localhost:8000`.

- `GET  /health` → `{ "status": "ok" }`
- `POST /score`  → see contract below

Run the tests:

```bash
cd backend
pytest -v
```

### Frontend (Node 18+)

```bash
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173` and proxies `/score` and `/health`
to the backend at `http://localhost:8000` (see `vite.config.js`), so you
don't need to set any environment variables for local dev.

## API contract

`POST /score`

Request:

```json
{
  "land_area_acres": 2.5,
  "crop_type": "paddy",
  "repayment_history_score": 80,
  "annual_income_band": "2-5L"
}
```

Response (`200 OK`):

```json
{
  "request_id": "f1c4f3c0-6f4b-4a3c-9e36-2d4f9a7e1b22",
  "score": 71.0,
  "reason_codes": ["good_repayment", "lower_mid_income_band", "mid_landholding"],
  "timestamp": "2026-04-25T05:32:11.123456+00:00"
}
```

Validation errors return `422` with a flat error list:

```json
{
  "detail": "Validation failed",
  "errors": [
    {"field": "land_area_acres", "message": "Input should be greater than 0", "type": "greater_than"}
  ]
}
```

### Field rules

| Field                     | Rule                                       |
|---------------------------|--------------------------------------------|
| `land_area_acres`         | number, strictly `> 0`                     |
| `crop_type`               | non-empty, non-whitespace string           |
| `repayment_history_score` | number in `[0, 100]` (inclusive)           |
| `annual_income_band`      | one of `<2L`, `2-5L`, `5-10L`, `>10L`      |

## Scoring logic (rule-based)

Total score is the sum of three components, clamped to `[0, 100]`:

| Component             | Max points | How                                      |
|-----------------------|------------|------------------------------------------|
| Repayment history     | 50         | `(repayment / 100) * 50`                 |
| Annual income band    | 30         | `<2L=10`, `2-5L=18`, `5-10L=25`, `>10L=30` |
| Land holding          | 20         | `<1 → 6`, `<2.5 → 12`, `<10 → 17`, else 20 |

Reason codes (always exactly 3, in order: repayment, income, land):

- Repayment: `good_repayment` (≥80), `average_repayment` (≥50), `weak_repayment`
- Income:    `low_income_band`, `lower_mid_income_band`, `mid_income_band`, `high_income_band`
- Land:      `marginal_landholding`, `small_landholding`, `mid_landholding`, `large_landholding`

The logic is intentionally simple, deterministic, and easy to explain to a
reviewer.

## Audit logging

Every successful scoring request writes one JSON line to **stdout** and to
`backend/audit.log`. Example:

```json
{"event": "score_computed", "request_id": "...", "timestamp": "...", "inputs": {"land_area_acres": 2.5, "crop_type": "paddy", "repayment_history_score": 80, "annual_income_band": "2-5L"}, "score": 71.0, "reason_codes": ["good_repayment", "lower_mid_income_band", "mid_landholding"]}
```

We log only the four input fields used for scoring plus the score and
reason codes — nothing that could be considered sensitive (no PII).

## Design choices and tradeoffs

- **FastAPI + Pydantic v2** — gets validation, OpenAPI docs (`/docs`), and
  clean 4xx error responses essentially for free.
- **Pure scoring function** — `compute_score()` takes a validated request
  and returns `(score, reason_codes)`. Keeping it pure makes it trivially
  unit-testable without spinning up the HTTP layer.
- **Custom validation error handler** — FastAPI's default 422 shape is
  noisy; the override flattens it into `{field, message, type}` so the
  frontend can map errors directly onto fields.
- **JSON line audit logging** — easy to grep, easy to ship to a log
  aggregator later. Writing to both stdout and a file means containerised
  setups still get logs without losing the local file for quick inspection.
- **Vite dev proxy** — the frontend talks to `/score` directly and Vite
  proxies it to `localhost:8000`, so there's no CORS dance during local dev
  and no API base URL hardcoded into the frontend.
- **No database** — the exercise calls persistence optional. The audit log
  serves as the auditable trail inside the time-box.

## LLM / tool usage disclosure

See [`LLM_NOTES.md`](./LLM_NOTES.md) for tools used, example prompts, and
what I personally checked and corrected.
