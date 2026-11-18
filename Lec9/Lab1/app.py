from flask import Flask

from blueprints.v1 import v1_bp
from blueprints.v2 import v2_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(v1_bp, url_prefix="/api/v1/users")
    app.register_blueprint(v2_bp, url_prefix="/api/v2/users")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
