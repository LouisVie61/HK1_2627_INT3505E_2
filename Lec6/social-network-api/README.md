# Lec 6: Social Network API (Flask + OpenAPI)

Bài tập về nhà: OpenAPI spec cho 3 endpoint, kèm bản cài đặt Flask và `SecurityAudit.md`.

| Endpoint | Scope cần | Lỗi có thể xảy ra |
|---|---|---|
| `POST /auth/login` | không (công khai) | 400, 401, 429 |
| `POST /auth/refresh` | không; cần refresh token hợp lệ | 400, 401 |
| `GET /posts/{id}` | `posts:read` | 401, 403, 404 |

Chi tiết từng mã lỗi + `error.code` nằm trong [openapi.yaml](social-network-api/openapi.yaml) (xem thêm tại `GET /openapi.yaml` khi server chạy hoặc dán vào editor.swagger.io).

## Chạy

```
cd social-network-api
pip install -r requirements.txt
python app.py
```

Tài khoản mẫu: `alice / alice123` (scope `posts:read posts:write`), `bob / bob12345` (chỉ `profile:read`, gọi `GET /posts/1` sẽ nhận 403).

```
curl -X POST localhost:5000/auth/login -H "Content-Type: application/json" -d '{"username":"alice","password":"alice123"}'
curl localhost:5000/posts/1 -H "Authorization: Bearer <access_token>"
curl -X POST localhost:5000/auth/refresh -H "Content-Type: application/json" -d '{"refresh_token":"<refresh_token>"}'
```

Phân tích bảo mật: [SecurityAudit.md](social-network-api/SecurityAudit.md).
