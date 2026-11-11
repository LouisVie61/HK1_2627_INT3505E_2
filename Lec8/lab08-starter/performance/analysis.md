# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 20 | 0.00% | 4.91 |
| B | 50 | 5 | 60s | 23 | 0.07% | 23.39 |
| C | 200 | 50 | 30s | 97 | 0.18% | 96.61 |

1. Kịch bản C có p95 cao nhất (97 ms), tăng từ 20 ms ở A và 23 ms ở B. Khi tăng lên 200 users, SQLite và Flask development server phải xử lý nhiều request đồng thời hơn; p95 tăng rõ dù chưa vượt 300 ms.

2. Failure chỉ xuất hiện ở `GET /books?year={year}`: B có 1/1.393 request (0,07%), C có 5/2.837 request (0,18%). Đây không phải HTTP 500 từ server. Trong `search_by_year`, server vẫn trả HTTP 200 và `response.failure("Simulated 1% client-side failure")` đánh dấu request thất bại ở Locust; tỷ lệ quan sát dao động vì số mẫu hữu hạn. Các endpoint khác không có failure.

3. Cả A, B và C đều đạt SLO giả định p95 < 300 ms theo lần chạy này. Đây chỉ là baseline thực hành trên Flask development server và SQLite cục bộ, một máy và một lần chạy; không đại diện cho production, chưa bao gồm network thực, nhiều process/worker, dữ liệu lớn hoặc traffic dài hạn.

4. Để kiểm chứng pool tối đa 5, cấu hình SQLAlchemy với `pool_size=5`, `max_overflow=0` và `pool_timeout` ngắn, sau đó chạy lại A/B/C (đặc biệt C). So sánh p95, RPS và failure rate với bảng trên; đồng thời ghi nhận log `TimeoutError`/HTTP 500 và số connection đang checkout. Nếu 200 users tranh chấp 5 connection, p95 và timeout/failure sẽ tăng; cần phân biệt timeout pool thật với `response.failure` nhân tạo của Locust.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.
