# Security Audit - Social Network API (Lec6)

Phạm vi: `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`. Dưới đây là các điểm có thể bị lộ/khai thác, kèm trạng thái trong code hiện tại.

| # | Điểm có thể lộ | Kịch bản tấn công | Giảm thiểu | Trạng thái |
|---|----------------|-------------------|------------|------------|
| 1 | **Brute-force / credential stuffing** ở `/auth/login` | Thử hàng loạt mật khẩu cho 1 username | Khóa tài khoản 15 phút sau 5 lần sai (429 + `Retry-After`); nên thêm rate limit theo IP | Đã làm (khóa theo username); thiếu limit theo IP |
| 2 | **User enumeration** | Phân biệt "user không tồn tại" với "sai mật khẩu" qua thông báo hoặc thời gian phản hồi | Cùng 1 thông báo 401 `invalid_credentials`; luôn chạy so khớp hash kể cả khi user không tồn tại | Đã làm |
| 3 | **Đánh cắp / dùng lại refresh token** | Kẻ cắp có refresh token sống 7 ngày, sinh access token mãi mãi | Rotation: mỗi refresh token dùng 1 lần, token cũ vào danh sách thu hồi (401 `token_revoked`); nên thu hồi cả "family" khi phát hiện reuse | Đã làm (rotation); chưa thu hồi cả family |
| 4 | **JWT bị giả mạo** (đổi `alg` thành `none`, đổi claim `scope`, ký bằng secret yếu) | Sửa payload thành scope cao hơn | Ép `algorithms=["HS256"]`, kiểm `iss`, `exp`, `jti`, `type`; secret đọc từ biến môi trường `JWT_SECRET`, dài >= 32 ký tự | Đã làm; secret mặc định chỉ để dev, **bắt buộc đổi khi deploy** |
| 5 | **Nhầm loại token** | Dùng refresh token (sống lâu) làm access token, hoặc ngược lại | Claim `type` được kiểm ở từng endpoint | Đã làm |
| 6 | **IDOR / BOLA ở `GET /posts/{id}`** | Duyệt ID 1,2,3... để đọc bài private của người khác | Kiểm quyền sở hữu theo từng object; bài private của người khác trả 404 (không lộ sự tồn tại thay vì 403) | Đã làm |
| 7 | **Thiếu scope / leo thang đặc quyền** | Tài khoản `profile:read` đọc bài viết | Mỗi endpoint khai báo scope; thiếu scope trả 403 `insufficient_scope`; scope của token mới lấy lại từ hệ thống khi refresh, không sao chép từ token cũ | Đã làm |
| 8 | **Lộ token qua cache/log/đường truyền** | Proxy cache response chứa token; token nằm trong URL/log; sniff HTTP | `Cache-Control: no-store` trên response token; token chỉ trong header/body, không trong URL; bắt buộc HTTPS ở production (HSTS) | `no-store` đã làm; **HTTPS chưa** (Flask dev chạy HTTP) |
| 9 | **Lưu trữ phía client** | XSS đọc token trong localStorage | Access token để trong bộ nhớ, refresh token trong cookie `HttpOnly; Secure; SameSite` | Ngoài phạm vi API (khuyến nghị cho client) |
| 10 | **Lộ thông tin qua lỗi / debug** | `debug=True` lộ Werkzeug debugger (RCE); stack trace | Tắt debug ở production; lỗi trả JSON chuẩn `{error:{code,message}}` không kèm chi tiết nội bộ | Lỗi JSON chuẩn đã làm; **`debug=True` chỉ để dev** |
| 11 | **Dữ liệu in-memory, mật khẩu seed trong code** | Mất trạng thái thu hồi khi restart (refresh token cũ dùng lại được); mật khẩu demo bị lộ qua repo | Dùng Redis/DB cho danh sách thu hồi và bộ đếm khóa; không commit mật khẩu thật | Giới hạn của bài lab |
| 12 | **Thiếu CORS/security header** | Trang web lạ gọi API bằng trình duyệt của nạn nhân | Cấu hình CORS whitelist, thêm `X-Content-Type-Options: nosniff` | Chưa làm |

## Kết luận

Đã phủ 8/12 điểm ở mức code. Việc cần làm trước khi production: HTTPS + HSTS, secret thật từ môi trường, lưu trạng thái thu hồi/khóa ngoài bộ nhớ (Redis), rate limit theo IP, thu hồi cả family khi phát hiện reuse, tắt debug, cấu hình CORS.
