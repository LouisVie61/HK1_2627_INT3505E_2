from flask import Flask, jsonify, request

from gateway import dispatch


app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400

    which, result = dispatch(body)
    response = jsonify(result)
    response.headers["X-Order-Handler"] = which
    response.status_code = 201 if which == "v2" else 200
    return response


if __name__ == "__main__":
    app.run(debug=True)
