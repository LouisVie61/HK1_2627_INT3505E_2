# Design-First

Ở phần này, API contract được viết trước trong
[`openapi/products.yaml`](openapi/products.yaml). Connexion đọc file này để
đăng ký route, validate request và nối `operationId` tới handler trong
[`api/products.py`](api/products.py).

## Cài đặt

Chạy từ thư mục `code-first-vs-design-first`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Lệnh trên cài cả `uvicorn`, server ASGI mà Connexion 3 sử dụng khi chạy app.

## Chạy Design-First (Connexion 3)

Chạy từ thư mục `code-first-vs-design-first`:

```powershell
python -m design_first.app
```

Connexion 3 chạy thông qua middleware của `FlaskApp`. Vì vậy hãy dùng lệnh
`python -m design_first.app`; không dùng `flask --app design_first.app run`.

Nếu đang đứng trong thư mục `design_first`, dùng:

```powershell
python app.py
```

## Thử API

Mở danh sách sản phẩm:

```text
http://127.0.0.1:5002/products
```

Hoặc dùng PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:5002/products
```

Tạo sản phẩm:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:5002/products `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"Notebook","price":12.5}'
```

Connexion tự tạo route từ `openapi.yaml`; phần xử lý dữ liệu nằm trong các
handler được khai báo bằng `operationId`.

Sau khi chỉnh sửa `openapi.yaml` hoặc handler, dừng server bằng `Ctrl+C` rồi
chạy lại lệnh trên.

