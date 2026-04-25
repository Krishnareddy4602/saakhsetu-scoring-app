"""Rule-based scoring logic for SaakhSetu.

The scoring is intentionally simple and explainable. It returns a score in
[0, 100] and exactly three reason codes that explain the main drivers.

Weights (out of 100):
    - Repayment history       : 50
    - Annual income band      : 30
    - Land holding size       : 20

Reason codes are picked from the three input dimensions so the explanation
mirrors the inputs that actually moved the score.
"""

from typing import List, Tuple

from .schemas import ScoreRequest

INCOME_BAND_POINTS = {
    "<2L": 10,
    "2-5L": 18,
    "5-10L": 25,
    ">10L": 30,
}


def _land_component(land_area_acres: float) -> Tuple[float, str]:
    """Score the land holding (max 20) and return a reason code."""
    if land_area_acres < 1:
        return 6.0, "marginal_landholding"
    if land_area_acres < 2.5:
        return 12.0, "small_landholding"
    if land_area_acres < 10:
        return 17.0, "mid_landholding"
    return 20.0, "large_landholding"


def _repayment_component(repayment: float) -> Tuple[float, str]:
    """Scale repayment history (0-100) onto a 0-50 scale."""
    points = (repayment / 100.0) * 50.0
    if repayment >= 80:
        code = "good_repayment"
    elif repayment >= 50:
        code = "average_repayment"
    else:
        code = "weak_repayment"
    return points, code


def _income_component(band: str) -> Tuple[float, str]:
    """Score the income band and return a matching reason code."""
    points = INCOME_BAND_POINTS[band]
    code_map = {
        "<2L": "low_income_band",
        "2-5L": "lower_mid_income_band",
        "5-10L": "mid_income_band",
        ">10L": "high_income_band",
    }
    return float(points), code_map[band]


def compute_score(req: ScoreRequest) -> Tuple[float, List[str]]:
    """Compute the score and reason codes for a validated request.

    Returns a (score, reason_codes) tuple where reason_codes has exactly 3
    entries — one each for repayment, income, and land holding (in that
    order, since repayment carries the largest weight).
    """
    repay_pts, repay_code = _repayment_component(req.repayment_history_score)
    income_pts, income_code = _income_component(req.annual_income_band)
    land_pts, land_code = _land_component(req.land_area_acres)

    raw_score = repay_pts + income_pts + land_pts
    score = round(max(0.0, min(100.0, raw_score)), 2)

    reason_codes = [repay_code, income_code, land_code]
    return score, reason_codes
