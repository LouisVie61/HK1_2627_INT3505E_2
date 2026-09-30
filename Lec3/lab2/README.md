# Lec 3 - Lab 2

## Bài toán

Tạo error handler thống nhất cho Flask API. Khi có lỗi, API trả về định dạng `problem+json` thay vì HTML mặc định của Flask.

## Cách xử lý lỗi

- `ProblemError` dùng cho lỗi nghiệp vụ của ứng dụng.
- `HTTPException` được xử lý bằng một handler chung, ví dụ lỗi 404 hoặc 405.
- Exception chưa biết được trả về lỗi 500 với nội dung trung tính.
- Chi tiết lỗi server được ghi vào log, không trả stack trace cho client.

## Cấu trúc response lỗi

Response lỗi luôn có các trường:

- `type`: loại lỗi.
- `title`: tên lỗi.
- `detail`: mô tả ngắn.
- `status`: mã HTTP.
- `instance`: endpoint phát sinh lỗi.

Content-Type của response là `application/problem+json`.

## Endpoint kiểm thử

- `GET /resources/1`: trả về resource hợp lệ, status `200`.
- `GET /resources/999`: resource không tồn tại, trả về `404`.
- `GET /missing`: kiểm tra fallback cho HTTP 404.
- `GET /server-error`: kiểm tra lỗi server, trả về `500`.

Các endpoint lỗi đều trả JSON theo cùng một format. API vẫn trả `problem+json` ngay cả khi request không gửi `Accept` hoặc gửi `Accept: text/html`.

## Chạy chương trình

Mở terminal tại thư mục `Lec3/lab2` và chạy:

```bash
pip install flask
python app.py
```

Server chạy tại `http://127.0.0.1:5000`.

## Kết quả mong đợi

Khi gọi `GET /resources/999`, server trả status `404`, Content-Type `application/problem+json`, body có `type`, `title`, `detail`, `status`, `instance` và không có stack trace.
