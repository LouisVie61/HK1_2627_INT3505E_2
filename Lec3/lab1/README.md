# Lec 3 - Lab 1

## Bài toán

Thiết kế resource cho một Blog API đơn giản.

Blog có người dùng, bài viết, bình luận và thẻ. Trong phần này tập trung minh họa resource `posts`.

## Phân loại resource

- **Collection:** `posts`, `users` là các tập hợp tài nguyên.
- **Item:** `posts/{post_id}` và `users/{user_id}` là một tài nguyên cụ thể.
- **Sub-resource:** `posts/{post_id}/comments`, `posts/{post_id}/tags` và `users/{user_id}/following` là tài nguyên phụ thuộc vào tài nguyên cha.

## Cây endpoint

```text
/api/v1                              (API version 1)
├── /posts                           (collection bài viết)
│   ├── /{post_id}                   (item: một bài viết)
│   ├── /{post_id}/comments          (sub-resource: bình luận)
│   └── /{post_id}/tags              (sub-resource: thẻ)
└── /users                           (collection người dùng)
    ├── /{user_id}                   (item: một người dùng)
    └── /{user_id}/following         (sub-resource: danh sách đang theo dõi)
```

## Quyết định version

Chọn version segment `/api/v1` và đặt ở đầu URL. Cách này giúp nhận biết phiên bản API ngay từ endpoint. Nếu sau này thay đổi lớn về cấu trúc hoặc dữ liệu, có thể tạo `/api/v2` và vẫn giữ `/api/v1` cho client cũ.

## Method sử dụng

- `GET /api/v1/posts`: xem danh sách bài viết.
- `POST /api/v1/posts`: thêm bài viết mới.
- `GET /api/v1/posts/{post_id}`: xem một bài viết.

## Chạy chương trình

Mở terminal tại thư mục `Lec3/lab1` và chạy:

```bash
pip install flask
python app.py
```

Server chạy tại `http://127.0.0.1:5000`.

Có thể kiểm tra nhanh bằng trình duyệt:

```text
http://127.0.0.1:5000/api/v1/posts
http://127.0.0.1:5000/api/v1/posts/1
```

Kết quả trả về ở dạng JSON. `GET` dùng để đọc dữ liệu, `POST` dùng để tạo bài viết mới. Nếu thiếu `title` hoặc `content`, API trả về lỗi `400`.
