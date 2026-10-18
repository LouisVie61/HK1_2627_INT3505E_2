from flask import Blueprint, jsonify, request

from models import Author, db
from routes.common import error, validate

bp = Blueprint("authors", __name__, url_prefix="/api/v1/authors")


@bp.get("")
def list_authors():
    return jsonify([a.to_dict() for a in Author.query.order_by(Author.id).all()])


@bp.get("/<int:author_id>")
def get_author(author_id):
    author = Author.query.get(author_id)
    if author is None:
        return error("not_found", "Author not found", 404)
    return jsonify(author.to_dict())


@bp.post("")
def create_author():
    data = request.get_json(silent=True)
    problem = validate("author.json", data)
    if problem:
        return error("validation_error", problem, 422)
    author = Author(name=data["name"].strip(), bio=data.get("bio"))
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201


@bp.patch("/<int:author_id>")
def update_author(author_id):
    author = Author.query.get(author_id)
    if author is None:
        return error("not_found", "Author not found", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error("validation_error", "Request body must be a non-empty JSON object", 422)
    if "name" in data:
        author.name = data["name"]
    if "bio" in data:
        author.bio = data["bio"]
    db.session.commit()
    return jsonify(author.to_dict())


@bp.delete("/<int:author_id>")
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author is None:
        return error("not_found", "Author not found", 404)
    db.session.delete(author)
    db.session.commit()
    return "", 204
