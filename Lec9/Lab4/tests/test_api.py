import hashlib

import pytest

import gateway
from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_beta_cohort_routes_to_v2(client):
    response = client.post(
        "/orders",
        json={"account_id": "ordinary"},
        headers={"X-Cohort": "beta"},
    )
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"


def test_allow_list_account_routes_to_v2(client):
    response = client.post("/orders", json={"account_id": "acct_42"})
    assert response.status_code == 201
    assert response.get_json()["handler"] == "v2"


def test_hash_bucket_is_deterministic(client, monkeypatch):
    account_id = "ordinary"
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    first = client.post("/orders", json={"account_id": account_id})
    second = client.post("/orders", json={"account_id": account_id})
    assert first.headers["X-Order-Handler"] == "v1"
    assert second.headers["X-Order-Handler"] == "v1"

    bucket = int(hashlib.md5(account_id.encode()).hexdigest(), 16) % 100
    monkeypatch.setattr(gateway, "V2_PERCENT", bucket + 1)
    assert client.post("/orders", json={"account_id": account_id}).headers[
        "X-Order-Handler"
    ] == "v2"


def test_flip_to_one_hundred_percent_routes_to_v2(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 100)
    response = client.post("/orders", json={"account_id": "ordinary"})
    assert response.status_code == 201
    assert response.headers["X-Order-Handler"] == "v2"


def test_invalid_json_returns_bad_request(client):
    response = client.post("/orders", data="invalid", content_type="text/plain")
    assert response.status_code == 400
