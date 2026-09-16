from flask import Flask, jsonify, make_response, request


app = Flask(__name__)
BOOKS = []
_next_id = 1

DEFAULT_SIZE, MAX_SIZE = 20, 100


# ─── GET /books nâng cấp: filter + pagination + HATEOAS + cache
@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

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

    total = len(filtered_books)
    start = (page - 1) * size
    end = start + size
    items = filtered_books[start:end]
    total_pages = (total + size - 1) // size

    def url(page_number):
        params = [f"page={page_number}", f"size={size}"]
        if author:
            params.append(f"author={author}")
        if query:
            params.append(f"q={query}")
        return "/books?" + "&".join(params)

    links = {
        "self": {"href": url(page)},
        "first": {"href": url(1)},
        "last": {"href": url(max(total_pages, 1))},
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
            "total_pages": total_pages,
        },
        "_links": links,
    }
    response = make_response(jsonify(body), 200)
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


# ─── POST /books để tạo dữ liệu thử nghiệm
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
