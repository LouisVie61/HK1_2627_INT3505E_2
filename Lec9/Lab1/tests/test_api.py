import pytest

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_same_user_has_different_v1_and_v2_schemas(client):
    v1 = client.get("/api/v1/users/1")
    v2 = client.get("/api/v2/users/1")

    assert v1.status_code == 200
    assert v1.get_json() == {
        "id": 1,
        "full_name": "Văn Nguyễn",
        "email": "a@vnu.vn",
    }
    assert v2.status_code == 200
    assert v2.get_json() == {
        "id": 1,
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn",
    }


def test_missing_user_returns_404_in_both_versions(client):
    assert client.get("/api/v1/users/999").get_json() == {"error": "nf"}
    assert client.get("/api/v2/users/999").get_json() == {"error": "nf"}


def test_v2_can_create_user(client):
    response = client.post(
        "/api/v2/users",
        json={"first_name": "An", "last_name": "Lê", "email": "an@vnu.vn"},
    )

    assert response.status_code == 201
    assert response.get_json()["first_name"] == "An"
