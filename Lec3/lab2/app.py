import logging

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException, NotFound


app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

resources = {
    1: {"id": 1, "name": "Resource 1"},
    2: {"id": 2, "name": "Resource 2"},
}


class ProblemError(Exception):
    def __init__(self, status, title, detail):
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail


def problem_response(status, title, detail):
    body = {
        "type": "https://example.com/problems/api-error",
        "title": title,
        "detail": detail,
        "status": status,
        "instance": request.path,
    }
    response = jsonify(body)
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return problem_response(error.status, error.title, error.detail)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return problem_response(
        error.code,
        error.name,
        error.description,
    )


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unexpected server error: %s", error)
    return problem_response(
        500,
        "Internal Server Error",
        "Đã xảy ra lỗi phía máy chủ.",
    )


@app.get("/resources/<int:resource_id>")
def get_resource(resource_id):
    resource = resources.get(resource_id)

    if resource is None:
        raise ProblemError(
            404,
            "Resource Not Found",
            "Không tìm thấy resource.",
        )

    return jsonify(resource)


@app.get("/http-error")
def http_error():
    raise NotFound(description="Đường dẫn này chỉ dùng để kiểm tra lỗi HTTP.")


@app.get("/server-error")
def server_error():
    raise RuntimeError("Lỗi thử nghiệm phía server")


if __name__ == "__main__":
    app.run(debug=False)
