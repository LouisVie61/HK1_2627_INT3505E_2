import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy.exc import IntegrityError

from api.products import products_bp
from errors import ApiError, error_response
from extensions import db


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///products.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    app.register_blueprint(products_bp)
    app.register_error_handler(ApiError, error_response)

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(IntegrityError)
    def integrity_error(_):
        db.session.rollback()
        return jsonify({"error": "Database constraint violated"}), 409

    with app.app_context():
        from models import Product  # noqa: F401
        db.create_all()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")

