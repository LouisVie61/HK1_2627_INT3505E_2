from flask import Flask, jsonify, request

app = Flask(__name__)

_next = 2
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "R. Martin"},
]


def find(bid):
    return next((book for book in BOOKS if book["id"] == bid), None)


@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:n]), 200


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
    title, author = body.get("title"), body.get("author")

    if not title or not author:
        return {"error": "need title+author"}, 400

    book = {"id": _next, "title": title, "author": author}
    _next += 1
    BOOKS.append(book)

    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}


@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return {"error": "not found"}, 404

    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200

    BOOKS.remove(book)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
