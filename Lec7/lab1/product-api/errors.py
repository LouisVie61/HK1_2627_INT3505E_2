from flask import jsonify


class ApiError(Exception):
    def __init__(self, status, message, detail=None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.detail = detail


def error_response(error):
    payload = {"error": error.message}
    if error.detail is not None:
        payload["detail"] = error.detail
    return jsonify(payload), error.status

