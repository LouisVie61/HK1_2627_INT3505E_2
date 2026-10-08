# Lec 4 - OpenAPI: đọc, viết và kiểm tra spec

## Nội dung

Thư mục này chứa OpenAPI specification cho **Tasks API quản lý task nội bộ**:

- [`openapi.yaml`](openapi.yaml): OpenAPI 3.1.0.
- 5 endpoint chính: `GET /tasks`, `GET /tasks/{taskId}`, `POST /tasks`, `PATCH /tasks/{taskId}`, `DELETE /tasks/{taskId}`.
- Task gồm các trường chính: `title`, `status`, `priority`, `dueDate`.
- Có `operationId` duy nhất, schema dùng lại bằng `$ref`, pagination, response lỗi và Bearer JWT security.

## Mở bằng Swagger Editor

1. Mở <https://editor.swagger.io/>.
2. Chọn **File → Import File**.
3. Chọn file `openapi.yaml` trong thư mục `Lec4`.
4. Kiểm tra phần preview bên phải và danh sách lỗi ở phía dưới editor.

Cũng có thể kéo thả file `openapi.yaml` trực tiếp vào Swagger Editor.

## Kiểm tra nhanh

- Mỗi operation có `operationId` riêng.
- Các endpoint yêu cầu Bearer token theo cấu hình `bearerAuth` ở cấp root.
- `TaskCreate` dùng cho tạo mới; `TaskPatch` dùng cho cập nhật một phần.
- Response danh sách trả về `{ data, pagination }`.
- Lỗi trả về thống nhất theo `{ code, message, details }`.

## Lưu ý chạy thử

Spec chỉ mô tả hợp đồng API; server thực tế cần chạy tại `http://localhost:5000/v1` hoặc chỉnh lại mục `servers` trong `openapi.yaml`.
