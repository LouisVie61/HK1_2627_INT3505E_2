from flask import Blueprint, jsonify, request

from models import User, db
from routes.common import error, validate

bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@bp.get("")
def list_users():
    return jsonify([u.to_dict() for u in User.query.order_by(User.id).all()])


@bp.get("/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return error("not_found", "User not found", 404)
    return jsonify(user.to_dict())


@bp.post("")
def create_user():
    data = request.get_json(silent=True)
    problem = validate("user.json", data)
    if problem:
        return error("validation_error", problem, 422)
    if User.query.filter_by(email=data["email"]).first() is not None:
        return error("conflict", "email already registered", 409)
    user = User(email=data["email"].strip(), display_name=data["display_name"].strip())
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.patch("/<int:user_id>")
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return error("not_found", "User not found", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error("validation_error", "Request body must be a non-empty JSON object", 422)
    if "email" in data:
        if User.query.filter(User.email == data["email"], User.id != user_id).first() is not None:
            return error("conflict", "email already registered", 409)
        user.email = data["email"]
    if "display_name" in data:
        user.display_name = data["display_name"]
    db.session.commit()
    return jsonify(user.to_dict())


@bp.delete("/<int:user_id>")
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return error("not_found", "User not found", 404)
    db.session.delete(user)
    db.session.commit()
    return "", 204
