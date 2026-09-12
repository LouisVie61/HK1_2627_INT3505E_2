from flask import Flask, jsonify, request

app = Flask(__name__)

_next = 2
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "R. Martin", "year": 2008},
]


@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    query = request.args.get("q", "").strip().lower()
    sort_by = request.args.get("sort", "").strip().lower()
    items = _filter_and_sort_books(BOOKS, query, sort_by)

    return jsonify(items[:n]), 200


@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book:
        return {"error": "not found"}, 404
    return jsonify(book), 200


@app.route("/books", methods=["POST"])
def create_book():
    global _next

    body = request.get_json(silent=True) or {}
    title, author, year = body.get("title"), body.get("author"), body.get("year")

    if not title or not author or year is None:
        return {"error": "need title+author+year"}, 400

    if not _is_valid_year(year):
        return {"error": "year must be a number >= 1900"}, 400

    book = {"id": _next, "title": title, "author": author, "year": year}
    _next += 1
    BOOKS.append(book)

    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}


@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return {"error": "not found"}, 404

    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        if "year" in body and not _is_valid_year(body["year"]):
            return {"error": "year must be a number >= 1900"}, 400

        book.update(body)
        return jsonify(book), 200

    BOOKS.remove(book)
    return "", 204


def find(bid):
    return next((book for book in BOOKS if book["id"] == bid), None)


def _is_valid_year(year):
    if isinstance(year, bool):
        return False

    if not isinstance(year, (int, float)):
        return False

    if year < 1900:
        return False

    return True


def _book_matches_query(book, query):
    title = book["title"].lower()
    author = book["author"].lower()

    if query in title:
        return True

    if query in author:
        return True

    return False


def _get_book_title_for_sort(book):
    title = book["title"]
    normalized_title = title.lower()
    return normalized_title


def _filter_and_sort_books(books, query="", sort_by=""):
    items = books

    if query:
        matched_books = []
        for book in items:
            if _book_matches_query(book, query):
                matched_books.append(book)

        items = matched_books

    if sort_by == "title":
        items = sorted(items, key=_get_book_title_for_sort)

    return items


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
