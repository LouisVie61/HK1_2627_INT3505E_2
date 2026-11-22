# Lab 3 - Blue-green routing

`POST /orders` dùng cùng một URL nhưng gateway chọn handler `v1` hoặc `v2`
theo thứ tự ưu tiên:

1. Header `X-Cohort: beta` hoặc `X-Cohort: internal`.
2. Account `acct_42` hoặc `acct_99`.
3. Hash ổn định của `account_id` rơi vào bucket nhỏ hơn `V2_PERCENT`.

`V2_PERCENT` mặc định là `5`, có thể thay đổi trong `gateway.py` để mô phỏng
rollout từ 5% lên 100%. Response luôn có header `X-Order-Handler`; v2 trả
status `201`, còn v1 trả `200`.

Chạy test:

```bash
python -m pytest -q
```

Chạy server:

```bash
python app.py
```

Ví dụ:

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "X-Cohort: beta" -d '{"account_id":"any"}' \
  http://127.0.0.1:5000/orders
```
