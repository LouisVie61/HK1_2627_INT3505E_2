# Lab 1 - URI Path Versioning

Chạy ứng dụng:

```bash
python app.py
```

Các endpoint chính:

- `GET /api/v1/users/1` trả về `full_name`.
- `GET /api/v2/users/1` trả về `first_name` và `last_name`.
- `POST /api/v2/users` tạo user mới với JSON gồm `first_name`, `last_name`, `email`.

Chạy test:

```bash
pytest -q
```
