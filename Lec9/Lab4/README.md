# Lab 4 - Blue-Green Routing

Gateway dùng một URL `POST /orders` và chọn handler theo thứ tự:

1. `X-Cohort: beta` hoặc `X-Cohort: internal` → v2.
2. `account_id` thuộc `acct_42`, `acct_99` → v2.
3. Hash ổn định của `account_id` theo `V2_PERCENT` → v1/v2.

Mặc định `V2_PERCENT = 5`. Có thể đổi thành `100` để mô phỏng hoàn tất
rollout và chuẩn bị sunset v1. Header `X-Order-Handler` cho biết handler đã
được chọn.

## Chạy

```bash
python -m pytest -q
python app.py
```

## Test nhanh

```bash
curl -X POST -H "Content-Type: application/json" -H "X-Cohort: beta" `
  -d '{"account_id":"any"}' http://127.0.0.1:5000/orders
```
