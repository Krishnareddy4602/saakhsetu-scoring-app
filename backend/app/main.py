"""SaakhSetu scoring API — FastAPI application."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import log_scoring_event
from .schemas import ScoreRequest, ScoreResponse
from .scoring import compute_score

app = FastAPI(
    title="SaakhSetu Scoring API",
    version="0.1.0",
    description="Rule-based credit-style scoring for smallholder farmers.",
)

# In a real deployment we'd lock this down to known frontend origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """Return clean 422s with a flat list of field-level error messages."""
    errors = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", []) if p != "body")
        errors.append(
            {
                "field": loc or "body",
                "message": err.get("msg", "invalid value"),
                "type": err.get("type", "invalid"),
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest) -> ScoreResponse:
    request_id = uuid4()
    score_value, reason_codes = compute_score(payload)
    timestamp = datetime.now(timezone.utc)

    log_scoring_event(
        request_id=str(request_id),
        inputs={
            "land_area_acres": payload.land_area_acres,
            "crop_type": payload.crop_type,
            "repayment_history_score": payload.repayment_history_score,
            "annual_income_band": payload.annual_income_band,
        },
        score=score_value,
        reason_codes=reason_codes,
    )

    return ScoreResponse(
        request_id=request_id,
        score=score_value,
        reason_codes=reason_codes,
        timestamp=timestamp,
    )
