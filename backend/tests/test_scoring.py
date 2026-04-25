"""Unit tests for the rule-based scoring logic."""

from app.schemas import ScoreRequest
from app.scoring import compute_score


def _req(**overrides):
    base = dict(
        land_area_acres=2.0,
        crop_type="paddy",
        repayment_history_score=85,
        annual_income_band="2-5L",
    )
    base.update(overrides)
    return ScoreRequest(**base)


def test_compute_score_strong_profile():
    score, reasons = compute_score(
        _req(
            land_area_acres=12,
            repayment_history_score=95,
            annual_income_band=">10L",
        )
    )
    # 47.5 (repayment) + 30 (income) + 20 (land) = 97.5
    assert score == 97.5
    assert reasons == ["good_repayment", "high_income_band", "large_landholding"]


def test_compute_score_weak_profile():
    score, reasons = compute_score(
        _req(
            land_area_acres=0.5,
            repayment_history_score=20,
            annual_income_band="<2L",
        )
    )
    # 10 (repayment) + 10 (income) + 6 (land) = 26
    assert score == 26.0
    assert reasons == ["weak_repayment", "low_income_band", "marginal_landholding"]


def test_score_is_clamped_between_0_and_100():
    score, _ = compute_score(_req())
    assert 0 <= score <= 100


def test_reason_codes_always_three():
    _, reasons = compute_score(_req())
    assert len(reasons) == 3
