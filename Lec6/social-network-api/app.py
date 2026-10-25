import os
import time
import uuid
from functools import wraps
from pathlib import Path

import jwt
from flask import Flask, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-only-secret-change-me-0123456789abcdef")
ACCESS_TTL = 15 * 60
REFRESH_TTL = 7 * 24 * 3600
MAX_FAILS = 5
LOCK_SECONDS = 15 * 60
ISSUER = "social-network-api"

# --- dữ liệu giả lập (in-memory) -------------------------------------------
USERS = {
    "alice": {
        "id": 1,
        "password_hash": generate_password_hash("alice123"),
        "scopes": ["posts:read", "posts:write"],
    },
    "bob": {  # tài khoản bị hạn chế: không có scope posts:read
        "id": 2,
        "password_hash": generate_password_hash("bob12345"),
        "scopes": ["profile:read"],
    },
}
POSTS = {
    1: {"id": 1, "author_id": 1, "content": "Hello social network!", "visibility": "public",
        "created_at": "2026-10-01T08:00:00Z"},
    2: {"id": 2, "author_id": 1, "content": "Nhật ký riêng của Alice", "visibility": "private",
        "created_at": "2026-10-02T09:30:00Z"},
}
REVOKED_JTI = set()        # refresh token đã dùng/bị thu hồi
FAILED = {}                # username -> (số lần sai, thời điểm bị khóa đến)
USER_BY_ID = {u["id"]: name for name, u in USERS.items()}


def error(status, code, message, headers=None):
    resp = jsonify({"error": {"code": code, "message": message}})
    resp.status_code = status
    for k, v in (headers or {}).items():
        resp.headers[k] = v
    return resp


def issue_token(user_id, scopes, kind, ttl, family=None):
    now = int(time.time())
    payload = {
        "iss": ISSUER, "sub": str(user_id), "type": kind, "scope": " ".join(scopes),
        "iat": now, "exp": now + ttl, "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256"), payload


def decode_token(token, kind):
    claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], issuer=ISSUER,
                        options={"require": ["exp", "iat", "sub", "jti"]})
    if claims.get("type") != kind:
        raise jwt.InvalidTokenError("wrong token type")
    return claims


def token_pair(user_id, scopes):
    access, _ = issue_token(user_id, scopes, "access", ACCESS_TTL)
    refresh, _ = issue_token(user_id, scopes, "refresh", REFRESH_TTL)
    return {"access_token": access, "refresh_token": refresh,
            "token_type": "Bearer", "expires_in": ACCESS_TTL}


def require_scope(scope):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return error(401, "missing_token", "Thiếu header Authorization: Bearer <access_token>",
                             {"WWW-Authenticate": "Bearer"})
            try:
                claims = decode_token(header[7:], "access")
            except jwt.ExpiredSignatureError:
                return error(401, "token_expired", "Access token đã hết hạn, hãy gọi /auth/refresh",
                             {"WWW-Authenticate": 'Bearer error="invalid_token"'})
            except jwt.InvalidTokenError:
                return error(401, "invalid_token", "Access token không hợp lệ",
                             {"WWW-Authenticate": 'Bearer error="invalid_token"'})
            if scope not in claims["scope"].split():
                return error(403, "insufficient_scope", f"Cần scope '{scope}'",
                             {"WWW-Authenticate": f'Bearer error="insufficient_scope", scope="{scope}"'})
            g.user_id = int(claims["sub"])
            return fn(*a, **kw)
        return wrapper
    return deco


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False

    @app.post("/auth/login")
    def login():
        body = request.get_json(silent=True)
        if (not isinstance(body, dict) or not isinstance(body.get("username"), str)
                or not isinstance(body.get("password"), str)
                or not body["username"] or not body["password"]):
            return error(400, "invalid_request", "Cần JSON {username, password} dạng chuỗi không rỗng")
        username = body["username"]
        fails, locked_until = FAILED.get(username, (0, 0))
        now = time.time()
        if locked_until > now:
            retry = int(locked_until - now) + 1
            return error(429, "account_locked", "Quá nhiều lần đăng nhập sai, thử lại sau",
                         {"Retry-After": str(retry)})
        user = USERS.get(username)
        # luôn so khớp hash để thời gian phản hồi không lộ username tồn tại
        hash_ = user["password_hash"] if user else generate_password_hash("dummy")
        if not (check_password_hash(hash_, body["password"]) and user):
            fails += 1
            FAILED[username] = (fails, now + LOCK_SECONDS if fails >= MAX_FAILS else 0)
            return error(401, "invalid_credentials", "Sai tên đăng nhập hoặc mật khẩu")
        FAILED.pop(username, None)
        resp = jsonify(token_pair(user["id"], user["scopes"]))
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.post("/auth/refresh")
    def refresh():
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("refresh_token"), str):
            return error(400, "invalid_request", "Cần JSON {refresh_token} dạng chuỗi")
        try:
            claims = decode_token(body["refresh_token"], "refresh")
        except jwt.ExpiredSignatureError:
            return error(401, "token_expired", "Refresh token đã hết hạn, hãy đăng nhập lại")
        except jwt.InvalidTokenError:
            return error(401, "invalid_token", "Refresh token không hợp lệ")
        if claims["jti"] in REVOKED_JTI:
            # token đã dùng rồi mà bị dùng lại -> nghi bị đánh cắp
            return error(401, "token_revoked", "Refresh token đã bị thu hồi/đã sử dụng")
        user_id = int(claims["sub"])
        name = USER_BY_ID.get(user_id)
        if name is None:
            return error(401, "invalid_token", "Refresh token không hợp lệ")
        REVOKED_JTI.add(claims["jti"])  # rotation: mỗi refresh token chỉ dùng 1 lần
        # scope lấy lại từ DB, không tin scope trong token cũ
        resp = jsonify(token_pair(user_id, USERS[name]["scopes"]))
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/posts/<int:post_id>")
    @require_scope("posts:read")
    def get_post(post_id):
        post = POSTS.get(post_id)
        # bài private của người khác trả 404 giống bài không tồn tại (chống dò ID)
        if post is None or (post["visibility"] == "private" and post["author_id"] != g.user_id):
            return error(404, "post_not_found", "Không tìm thấy bài viết")
        return jsonify(post)

    @app.get("/openapi.yaml")
    def spec():
        text = Path(__file__).with_name("openapi.yaml").read_text(encoding="utf-8")
        return app.response_class(text, mimetype="application/yaml")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
