from flask import Blueprint, jsonify, request

from .users_data import add_user, get_user


v2_bp = Blueprint("v2", __name__, url_prefix="/users")


@v2_bp.get("/<int:user_id>")
def get_user_v2(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify({"error": "nf"}), 404

    return jsonify(
        {
            "id": user_id,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
        }
    )


@v2_bp.post("")
def create_user_v2():
    payload = request.get_json(silent=True)
    required = {"first_name", "last_name", "email"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        return jsonify({"error": "invalid_payload"}), 400

    user_id, user = add_user({field: payload[field] for field in required})
    return jsonify({"id": user_id, **user}), 201
