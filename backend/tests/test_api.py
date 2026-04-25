"""End-to-end tests for the FastAPI /score endpoint."""

from datetime import datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _valid_payload(**overrides):
    base = {
        "land_area_acres": 2.5,
        "crop_type": "paddy",
        "repayment_history_score": 80,
        "annual_income_band": "2-5L",
    }
    base.update(overrides)
    return base


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_score_happy_path():
    resp = client.post("/score", json=_valid_payload())
    assert resp.status_code == 200

    body = resp.json()
    assert set(body.keys()) == {"request_id", "score", "reason_codes", "timestamp"}

    # request_id is a valid UUID
    UUID(body["request_id"])

    assert 0 <= body["score"] <= 100
    assert isinstance(body["reason_codes"], list)
    assert len(body["reason_codes"]) == 3
    assert all(isinstance(c, str) and c for c in body["reason_codes"])

    # ISO 8601 parseable
    datetime.fromisoformat(body["timestamp"].replace("Z", "+00:00"))


def test_score_rejects_negative_land_area():
    resp = client.post("/score", json=_valid_payload(land_area_acres=-1))
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"] == "Validation failed"
    assert any("land_area_acres" in err["field"] for err in body["errors"])


def test_score_rejects_zero_land_area():
    resp = client.post("/score", json=_valid_payload(land_area_acres=0))
    assert resp.status_code == 422


def test_score_rejects_empty_crop_type():
    resp = client.post("/score", json=_valid_payload(crop_type=""))
    assert resp.status_code == 422


def test_score_rejects_blank_crop_type():
    resp = client.post("/score", json=_valid_payload(crop_type="   "))
    assert resp.status_code == 422


def test_score_rejects_invalid_income_band():
    resp = client.post("/score", json=_valid_payload(annual_income_band="huge"))
    assert resp.status_code == 422
    assert any(
        "annual_income_band" in err["field"] for err in resp.json()["errors"]
    )


def test_score_rejects_repayment_above_100():
    resp = client.post("/score", json=_valid_payload(repayment_history_score=101))
    assert resp.status_code == 422


def test_score_rejects_repayment_below_zero():
    resp = client.post("/score", json=_valid_payload(repayment_history_score=-5))
    assert resp.status_code == 422


def test_score_rejects_missing_field():
    payload = _valid_payload()
    payload.pop("crop_type")
    resp = client.post("/score", json=payload)
    assert resp.status_code == 422


def test_score_rejects_wrong_type():
    resp = client.post(
        "/score", json=_valid_payload(repayment_history_score="not-a-number")
    )
    assert resp.status_code == 422
