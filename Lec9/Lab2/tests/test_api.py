from datetime import datetime, timezone

import pytest

from app import app
from sunset import deprecate_at, http_date


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_v1_has_sunset_headers(client):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "full_name": "Nguyễn Văn A"}
    assert response.headers["Sunset"] == http_date(
        datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    )
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Link"] == '</api/v2/users>; rel="successor-version"'


def test_expired_endpoint_returns_410():
    @deprecate_at(
        datetime(2000, 1, 1, tzinfo=timezone.utc), replacement="/api/v2/users"
    )
    def expired():
        return {"message": "should not be called"}

    with app.test_request_context("/api/v1/users/1"):
        response, status = expired()

    assert status == 410
    assert response.get_json() == {
        "error": "gone",
        "sunset": "Sat, 01 Jan 2000 00:00:00 GMT",
        "use_instead": "/api/v2/users",
    }
