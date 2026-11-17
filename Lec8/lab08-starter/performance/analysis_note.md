# Analysis note — Load test `GET /books`

## Phạm vi và cách đo

Endpoint chính được chọn là `GET /books`, vì đây là thao tác đọc danh sách
sách được gọi thường xuyên nhất trong Books API. Kịch bản dùng
`performance/locustfile_main_endpoint.py`, chỉ tạo request tới endpoint này;
Locust chờ ngẫu nhiên 1–3 giây giữa hai request của cùng một user. API chạy
bằng Flask development server với SQLite cục bộ trên cùng máy.

Lệnh chạy và report:

```powershell
New-Item -ItemType Directory -Path instance,reports -Force
python -m app --port 5000
python -m locust -f performance/locustfile_main_endpoint.py `
  --headless -H http://127.0.0.1:5000 -u 10 -r 2 -t 30s `
  --html reports/main-endpoint.html
```

## Kết quả quan sát

| Endpoint | Users | Spawn rate | Duration | Requests | p95 | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `GET /books` | 10 | 2/s | 30s | 143 | 11 ms | 0.00% | 4.93 |

Kết quả lần chạy này là 143 requests, p95 11 ms, không có failure và throughput
4,93 requests/giây. Không nên suy ra số liệu từ máy hoặc lần chạy khác. Report HTML được lưu tại
`reports/main-endpoint.html` để đối chiếu.

## SLO đề xuất

SLO ban đầu cho `GET /books` là **p95 latency < 300 ms** trong một cửa sổ đo
30 giây ở mức 10 users, đồng thời **availability ≥ 99,9%** (tối đa 0,1% request
trả lỗi). p95 phù hợp hơn average vì phản ánh nhóm request chậm ở đuôi phân
phối; availability cần tính từ HTTP response thật, không tính các lỗi mô
phỏng do client Locust tự đánh dấu.

Đây chỉ là baseline để làm CI gate hoặc phát hiện regression. Flask development
server, SQLite, dữ liệu nhỏ, localhost và một máy đo không đại diện cho môi
trường production. Trước khi cam kết SLO chính thức cần lặp lại nhiều lần,
tăng kích thước dữ liệu, dùng deployment gần production và theo dõi p99,
throughput, lỗi HTTP 5xx cùng tài nguyên CPU/RAM/DB.
