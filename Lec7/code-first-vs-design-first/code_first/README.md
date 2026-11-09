# Code-First

Trong phần này, schema và route được viết trước trong `app.py`. Sau đó
`flask-smorest` tự sinh OpenAPI từ các khai báo đó.

## Cài đặt

Chạy từ thư mục `code-first-vs-design-first`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Sinh OpenAPI theo version

Chạy từ thư mục `code_first`:

```powershell
python generate_openapi.py --version v1
python generate_openapi.py --version v2
```

Kết quả được lưu tại:

```text
openapi/v1/openapi.yaml
openapi/v2/openapi.yaml
```

Khi thay đổi `ProductSchema`, chạy lại lệnh tương ứng để sinh lại spec.

## Chạy API

Chạy từ thư mục `code-first-vs-design-first`:

```powershell
flask --app code_first.app run --port 5001
```

Thử API:

```powershell
curl http://localhost:5001/products/
```

## Mở Swagger UI theo version

Sau khi đã sinh spec, mở các URL sau trên trình duyệt:

```text
http://127.0.0.1:5001/swagger/v1
http://127.0.0.1:5001/swagger/v2
```

Swagger UI sẽ đọc lần lượt các file:

```text
http://127.0.0.1:5001/openapi/v1/openapi.yaml
http://127.0.0.1:5001/openapi/v2/openapi.yaml
```

Nếu sửa code rồi muốn xem version mới, sinh file trước:

```powershell
python generate_openapi.py --version v3
```

Sau đó mở `http://127.0.0.1:5001/swagger/v3`.

