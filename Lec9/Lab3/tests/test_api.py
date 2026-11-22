import hashlib

import pytest

import gateway
from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_beta_cohort_has_highest_priority(client):
    response = client.post(
        "/orders", json={"account_id": "ordinary"}, headers={"X-Cohort": " BeTa "}
    )
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"


def test_force_account_uses_v2(client):
    response = client.post("/orders", json={"account_id": "acct_42"})
    assert response.status_code == 201
    assert response.get_json()["handler"] == "v2"


def test_percentage_bucket_is_stable(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    account_id = "ordinary"
    response = client.post("/orders", json={"account_id": account_id})
    assert response.status_code == 200
    assert response.headers["X-Order-Handler"] == "v1"

    expected_bucket = int(
        hashlib.md5(account_id.encode("utf-8")).hexdigest(), 16
    ) % 100
    monkeypatch.setattr(gateway, "V2_PERCENT", expected_bucket + 1)
    response = client.post("/orders", json={"account_id": account_id})
    assert response.headers["X-Order-Handler"] == "v2"


def test_full_rollout_uses_v2(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 100)
    response = client.post("/orders", json={"account_id": "ordinary"})
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"


def test_invalid_body_is_rejected(client):
    response = client.post("/orders", data="not-json", content_type="text/plain")
    assert response.status_code == 400
