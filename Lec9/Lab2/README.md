# Lab 2 - Sunset decorator

Chạy test:

```bash
python -m pytest -q
```

Chạy server:

```bash
python app.py
```

API v1 dùng endpoint `GET /api/v1/users/<id>` và được đánh dấu deprecated.

- Trước `2026-12-31 23:59:59 UTC`: trả dữ liệu cùng các header `Sunset`, `Deprecation` và `Link`.
- Sau thời điểm sunset: trả `410 Gone`.
- File `sunset.py` chứa decorator `deprecate_at` dùng lại cho các endpoint cũ.

