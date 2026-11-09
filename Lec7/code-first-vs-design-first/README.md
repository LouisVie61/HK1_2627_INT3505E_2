# Demo: Code-First vs Design-First

Hai cách tiếp cận cùng xây dựng Product API đơn giản:

| Cách | Viết trước | Điểm vào |
|---|---|---|
| Code-First | Schema, route và handler | `code_first/app.py` |
| Design-First | OpenAPI contract đã brainstorm/chốt | `design_first/openapi/products.yaml` |

## Chạy demo

```powershell
cd lec7/code-first-vs-design-first
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Code-First: tự sinh OpenAPI theo version

`flask-smorest` đọc schema và route được khai báo trong code rồi sinh OpenAPI.
Kết quả được lưu trong folder version:

```powershell
cd code_first
python generate_openapi.py --version v1
python generate_openapi.py --version v2
```

Các file kết quả nằm tại `code_first/openapi/v1/openapi.yaml` và
`code_first/openapi/v2/openapi.yaml`. Khi thêm hoặc đổi field trong
`ProductSchema`, chạy lại lệnh để cập nhật spec.

Chạy Code-First:

```powershell
flask --app code_first.app run --port 5001
```

Chạy Design-First:

```powershell
python -m design_first.app
```

Thử cả hai:

```powershell
curl http://localhost:5001/products
curl http://localhost:5002/products
curl -X POST http://localhost:5002/products `
  -H "Content-Type: application/json" `
  -d '{"name":"Notebook","price":12.5}'
```

## Cách hiểu Design-First

Design-First không có nghĩa là Connexion tự nghĩ ra API. Team sẽ brainstorm,
review và chốt contract trước: resource, endpoint, method, request/response,
status code, error và schema. Sau đó viết `openapi.yaml`.

Connexion đọc contract đó để tự đăng ký route, validation và nối
`operationId` tới handler. Một số tool có thể sinh code khung từ spec, nhưng
business logic, model database và các quyết định triển khai vẫn cần viết.

Trong demo, Connexion thực hiện việc wire spec vào handler trong
`design_first/api/products.py`.

