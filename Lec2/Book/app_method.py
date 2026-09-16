from flask import Flask, jsonify, make_response, request


app = Flask(__name__)
BOOKS = []
_next_id = 1


@app.get("/books")
def list_books():
    return jsonify({"data": BOOKS, "total": len(BOOKS)}), 200


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

    book = {"id": _next_id, "title": title, "author": author}
    BOOKS.append(book)
    _next_id += 1

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books/{book['id']}"
    return response


# ─── GET /books/<id> ─── cache 60s
@app.get("/books/<int:bid>")
def fetch(bid):
    index = next((key for key, book in enumerate(BOOKS)
                  if book["id"] == bid), None)
    if index is None:
        return jsonify(error="not found"), 404

    response = make_response(jsonify(BOOKS[index]), 200)
    response.headers["Cache-Control"] = "max-age=60"
    return response


# ─── PUT ─── thay toàn bộ, title+author bắt buộc
@app.put("/books/<int:bid>")
def put(bid):
    index = next((key for key, book in enumerate(BOOKS)
                  if book["id"] == bid), None)
    if index is None:
        return jsonify(error="not found"), 404

    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    author = payload.get("author")
    if not title or not author:
        return jsonify(error="need title+author"), 422

    BOOKS[index] = {
        "id": bid,
        "title": title.strip(),
        "author": author.strip(),
        "isbn": payload.get("isbn"),
        "price": payload.get("price"),
    }
    return jsonify(BOOKS[index]), 200


# ─── PATCH ─── chỉ cập nhật field có trong body
@app.patch("/books/<int:bid>")
def patch(bid):
    index = next((key for key, book in enumerate(BOOKS)
                  if book["id"] == bid), None)
    if index is None:
        return jsonify(error="not found"), 404

    payload = request.get_json(silent=True) or {}
    if payload.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422

    for key in "title author isbn price".split():
        if key in payload:
            BOOKS[index][key] = payload[key]
    return jsonify(BOOKS[index]), 200


# ─── DELETE ─── xoá, trả 204
@app.delete("/books/<int:bid>")
def delete(bid):
    index = next((key for key, book in enumerate(BOOKS)
                  if book["id"] == bid), None)
    if index is None:
        return jsonify(error="not found"), 404

    BOOKS.pop(index)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
