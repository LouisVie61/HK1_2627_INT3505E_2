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

## Hai quyết định khó khăn khi thiết kế chức năng Delete BTVN

### 1. Chọn xóa cứng và trả về `204 No Content`

Quyết định đầu tiên là xóa hẳn task khỏi dữ liệu (`del TASKS[task["id"]]`) thay vì dùng xóa mềm, chẳng hạn thêm trường `deletedAt`. Xóa mềm an toàn hơn cho việc khôi phục và audit, nhưng làm mô hình dữ liệu, logic truy vấn và đặc tả API phức tạp hơn. Với phạm vi Lec4, dữ liệu chỉ được lưu trong bộ nhớ và đề bài không yêu cầu khôi phục hay lưu lịch sử, nên xóa cứng là lựa chọn phù hợp và dễ kiểm chứng. Khi xóa thành công, API trả `204 No Content` vì thao tác đã hoàn tất và không cần gửi lại object task trong response.

### 2. Phân biệt task không tồn tại và thao tác xóa thành công

Quyết định thứ hai là không coi việc xóa một `taskId` không tồn tại là thành công. Endpoint phải kiểm tra UUID và tìm task trước khi xóa; nếu ID sai định dạng hoặc không có trong hệ thống, API trả `404 Not Found` theo cùng một cấu trúc lỗi `{ code, message }`. Cách này giúp client phát hiện lỗi nhập ID, tránh tưởng rằng dữ liệu đã bị xóa, đồng thời giữ hành vi nhất quán với `GET /tasks/{taskId}` và `PATCH /tasks/{taskId}`. Chỉ khi task thực sự tồn tại mới trả `204`.
