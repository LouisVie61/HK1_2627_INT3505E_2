from flask import Flask, jsonify, request

from gateway import dispatch


def create_app():
    app = Flask(__name__)

    @app.post("/orders")
    def create_order():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify({"error": "request body must be a JSON object"}), 400

        version, result = dispatch(body)
        response = jsonify(result)
        response.status_code = 201 if version == "v2" else 200
        response.headers["X-Order-Handler"] = version
        return response

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
