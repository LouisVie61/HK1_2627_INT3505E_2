from flask import Flask, jsonify, make_response, request

app = Flask(__name__)
BOOKS = []
_next_id = 1


# ─── tham số phân trang
DEFAULT_SIZE, MAX_SIZE = 20, 100


# ─── list + filter + paginate + links
@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    # Filter: author chính xác, q tìm trong title.
    filtered_books = BOOKS
    author = request.args.get("author")
    if author:
        filtered_books = [
            book for book in filtered_books
            if book["author"].lower() == author.lower()
        ]

    query = (request.args.get("q") or "").lower()
    if query:
        filtered_books = [
            book for book in filtered_books
            if query in book["title"].lower()
        ]

    # Paginate.
    total = len(filtered_books)
    start = (page - 1) * size
    end = start + size
    items = filtered_books[start:end]
    last_page = (total + size - 1) // size

    # HATEOAS links.
    def url(page_number):
        return f"/books?page={page_number}&size={size}"

    links = {
        "self": {"href": url(page)},
        "first": {"href": url(1)},
        "last": {"href": url(max(last_page, 1))},
    }
    if page > 1:
        links["prev"] = {"href": url(page - 1)}
    if end < total:
        links["next"] = {"href": url(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last_page,
        },
        "_links": links,
    }
    response = make_response(jsonify(body), 200)
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


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


# ─── DELETE ─── idempotent, trả 204
@app.delete("/books/<int:bid>")
def delete(bid):
    index = next((key for key, book in enumerate(BOOKS)
                  if book["id"] == bid), None)
    if index is None:
        return jsonify(error="not found"), 404

    BOOKS.pop(index)
    return "", 204

