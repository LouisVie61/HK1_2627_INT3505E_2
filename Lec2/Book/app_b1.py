from flask import Flask, jsonify, make_response, request


app = Flask(__name__)
BOOKS = []
_next_id = 1


# ─── GET /books —— trả danh sách
@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS),
    }), 200


# ─── POST /books —— tạo mới
@app.post("/books")
def create_book():
    global _next_id

    if not request.is_json:
        return jsonify(error="expected JSON"), 415

    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    author = (payload.get("author") or "").strip()

    if not title or not author:
        return jsonify(error="title and author required"), 422

    book = {
        "id": _next_id,
        "title": title,
        "author": author,
    }
    BOOKS.append(book)
    _next_id += 1

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books/{book['id']}"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
