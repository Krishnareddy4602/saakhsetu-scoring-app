from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

IncomeBand = Literal["<2L", "2-5L", "5-10L", ">10L"]


class ScoreRequest(BaseModel):
    land_area_acres: float = Field(
        ...,
        gt=0,
        description="Land area in acres. Must be strictly greater than 0.",
    )
    crop_type: str = Field(
        ...,
        min_length=1,
        description="Free-form crop label, e.g. 'paddy', 'cotton'.",
    )
    repayment_history_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Past repayment score from 0 to 100 (inclusive).",
    )
    annual_income_band: IncomeBand = Field(
        ...,
        description="Annual income band. One of '<2L', '2-5L', '5-10L', '>10L'.",
    )

    @field_validator("crop_type")
    @classmethod
    def crop_type_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("crop_type must be a non-empty string")
        return v.strip()


class ScoreResponse(BaseModel):

    request_id: UUID
    score: float = Field(..., ge=0, le=100)
    reason_codes: List[str] = Field(..., min_length=3, max_length=3)
    timestamp: datetime
