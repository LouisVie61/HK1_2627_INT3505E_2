from flask import Blueprint, jsonify

from .users_data import get_user


v1_bp = Blueprint("v1", __name__, url_prefix="/users")


@v1_bp.get("/<int:user_id>")
def get_user_v1(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify({"error": "nf"}), 404

    return jsonify(
        {
            "id": user_id,
            "full_name": f"{user['first_name']} {user['last_name']}",
            "email": user["email"],
        }
    )
