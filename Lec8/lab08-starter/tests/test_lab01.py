"""LAB 1 — functional tests for the Books API.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

The tests are intentionally independent; fixtures provide a fresh database for
each test.
"""

from jsonschema import ValidationError, validate

from tools import get_book_schema


def test_list_books_empty_database_returns_empty_array(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_missing_book_returns_not_found(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_without_title_returns_validation_error(client):
    response = client.post("/books", json={"author": "An Author"})
    payload = response.get_json()

    assert response.status_code == 400
    assert any(item["field"] == "title" for item in payload["errors"])


def test_deleted_book_cannot_be_fetched(client):
    created = client.post(
        "/books", json={"title": "A Book", "author": "An Author"}
    )
    book_id = created.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    fetched = client.get(f"/books/{book_id}")

    assert deleted.status_code == 204
    assert fetched.status_code == 404


def test_book_response_rejects_unexpected_fields(client):
    response = client.post(
        "/books",
        json={
            "title": "Schema Book",
            "author": "Schema Author",
            "year": 2021,
            "isbn": "1234567890123",
        },
    )
    book = response.get_json()

    validate(book, get_book_schema())
    invalid_book = {**book, "password_hash": "should-not-leak"}

    try:
        validate(invalid_book, get_book_schema())
    except ValidationError:
        pass
    else:
        raise AssertionError("Book schema accepted an unexpected field")
