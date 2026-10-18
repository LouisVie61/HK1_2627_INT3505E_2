from flask import Blueprint, jsonify, request

from models import Author, Book, Category, db
from routes.common import error, validate

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")


def resolve_authors(author_ids):
    if not author_ids:
        return []
    authors = Author.query.filter(Author.id.in_(author_ids)).all()
    if len(authors) != len(set(author_ids)):
        return None
    return authors


@bp.get("")
def list_books():
    query = Book.query
    category_id = request.args.get("category_id", type=int)
    if category_id is not None:
        query = query.filter(Book.category_id == category_id)
    books = query.order_by(Book.id).all()
    return jsonify([book.to_dict() for book in books])


@bp.get("/<int:book_id>")
def get_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return error("not_found", "Book not found", 404)
    return jsonify(book.to_dict())


@bp.post("")
def create_book():
    data = request.get_json(silent=True)
    problem = validate("book.json", data)
    if problem:
        return error("validation_error", problem, 422)
    if data.get("category_id") is not None and Category.query.get(data["category_id"]) is None:
        return error("validation_error", "category_id does not reference an existing category", 422)
    authors = resolve_authors(data.get("author_ids"))
    if authors is None:
        return error("validation_error", "author_ids contains an unknown author", 422)
    if Book.query.filter_by(isbn=data["isbn"]).first() is not None:
        return error("conflict", "isbn already exists", 409)
    book = Book(
        title=data["title"].strip(),
        isbn=data["isbn"].strip(),
        price_vnd=data["price_vnd"],
        stock=data.get("stock", 0),
        category_id=data.get("category_id"),
    )
    book.authors = authors
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@bp.patch("/<int:book_id>")
def update_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return error("not_found", "Book not found", 404)
    data = request.get_json(silent=True)
    problem = validate("book_patch.json", data)
    if problem:
        return error("validation_error", problem, 422)
    if "category_id" in data and data["category_id"] is not None and Category.query.get(data["category_id"]) is None:
        return error("validation_error", "category_id does not reference an existing category", 422)
    if "author_ids" in data:
        authors = resolve_authors(data["author_ids"])
        if authors is None:
            return error("validation_error", "author_ids contains an unknown author", 422)
        book.authors = authors
    if "isbn" in data and data["isbn"] != book.isbn and Book.query.filter_by(isbn=data["isbn"]).first() is not None:
        return error("conflict", "isbn already exists", 409)
    for field in ("title", "isbn", "price_vnd", "stock", "category_id"):
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    return jsonify(book.to_dict())


@bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return error("not_found", "Book not found", 404)
    db.session.delete(book)
    db.session.commit()
    return "", 204
