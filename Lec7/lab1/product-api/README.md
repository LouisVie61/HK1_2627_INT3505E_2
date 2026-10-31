# Product API

## Chạy ứng dụng

```bash
cd Lec7/lab1/product-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Test nhanh

```bash
curl "localhost:5000/api/v1/products?page=1&size=20"
curl -X POST localhost:5000/api/v1/products -H "Content-Type: application/json" -d "{\"sku\":\"SKU-001\",\"name\":\"Keyboard\",\"price_cents\":250000,\"qty_in_stock\":5}"
curl -X POST localhost:5000/api/v1/products/1/reserve -H "Content-Type: application/json" -d "{\"qty\":1}"
curl -X PATCH localhost:5000/api/v1/products/1 -H "Content-Type: application/json" -d "{\"price_cents\":230000}"
curl -X DELETE localhost:5000/api/v1/products/1
```

`DATABASE_URL` mặc định là SQLite. Có thể trỏ sang PostgreSQL bằng biến môi trường tương ứng.

## Bổ sung bài tập về nhà

- `Order` và `OrderItem` dùng blueprint riêng tại `/api/v1/orders`. Một Product
  chỉ được xuất hiện một lần trong cùng Order nhờ unique constraint
  `uq_order_product`.
- `/healthz` chỉ kiểm tra service còn hoạt động; `/ready` kiểm tra kết nối database.
- Chạy test: `pytest -q`.
- Chạy bằng Docker: `docker compose up --build`.

Ví dụ OrderItem:

```bash
curl -X POST localhost:5000/api/v1/orders
curl -X POST localhost:5000/api/v1/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"qty":2}'
curl localhost:5000/api/v1/orders/1
```

GET Order dùng `joinedload(Order.items).joinedload(OrderItem.product)` để nạp
OrderItem và Product trong một truy vấn, tránh N+1 khi dựng response.

