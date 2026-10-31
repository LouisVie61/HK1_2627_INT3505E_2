# Lab 1 - xây dựng Product API CRUD hoàn chỉnh

Lab triển khai 6 endpoint quản lý sản phẩm:

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/v1/products` | Danh sách, phân trang bằng `page` và `size` |
| GET | `/api/v1/products/<id>` | Lấy một sản phẩm |
| POST | `/api/v1/products` | Tạo sản phẩm |
| POST | `/api/v1/products/<id>/reserve` | Giảm tồn kho |
| PATCH | `/api/v1/products/<id>` | Cập nhật một phần |
| DELETE | `/api/v1/products/<id>` | Soft delete |

Chi tiết triển khai nằm trong thư mục [`product-api`](product-api/).

