from flask import Blueprint, jsonify, request

from models import Category, db
from routes.common import error, validate

bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")


@bp.get("")
def list_categories():
    return jsonify([c.to_dict() for c in Category.query.order_by(Category.id).all()])


@bp.get("/<int:category_id>")
def get_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return error("not_found", "Category not found", 404)
    return jsonify(category.to_dict())


@bp.post("")
def create_category():
    data = request.get_json(silent=True)
    problem = validate("category.json", data)
    if problem:
        return error("validation_error", problem, 422)
    if Category.query.filter_by(slug=data["slug"]).first() is not None:
        return error("conflict", "slug already exists", 409)
    category = Category(name=data["name"].strip(), slug=data["slug"].strip())
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@bp.patch("/<int:category_id>")
def update_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return error("not_found", "Category not found", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error("validation_error", "Request body must be a non-empty JSON object", 422)
    if "name" in data:
        category.name = data["name"]
    if "slug" in data:
        if Category.query.filter(Category.slug == data["slug"], Category.id != category_id).first() is not None:
            return error("conflict", "slug already exists", 409)
        category.slug = data["slug"]
    db.session.commit()
    return jsonify(category.to_dict())


@bp.delete("/<int:category_id>")
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return error("not_found", "Category not found", 404)
    db.session.delete(category)
    db.session.commit()
    return "", 204
