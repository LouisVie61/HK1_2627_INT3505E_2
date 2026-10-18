import json
from pathlib import Path

from flask import jsonify
from jsonschema import Draft7Validator, FormatChecker

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def load_schema(name):
    with open(SCHEMA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def validate(schema_name, data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"
    validator = Draft7Validator(load_schema(schema_name), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if not errors:
        return None
    first = errors[0]
    field = ".".join(str(p) for p in first.path) or "(root)"
    return f"{field}: {first.message}"


def error(code, message, status):
    return jsonify({"code": code, "message": message}), status
