from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock database
BOOKS = [
    {"id": "abc-1234", "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": "py-101", "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": "flask-1", "title": "Flask Web Development", "author": "Miguel Grinberg"},
]


def find_book_by_id(book_id):
    return next((book for book in BOOKS if book["id"] == book_id), None)


@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book_by_id(book_id)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return jsonify({"id": item_id}), 200


@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    query = request.args.get("q", "").strip().lower()

    items = BOOKS
    if query:
        items = [book for book in items if query in book["title"].lower()]

    return jsonify({"items": items[:limit]}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
