# Lec 3 - Lab 3

## Bài toán

Xây dựng API `GET /orders` cho danh sách nhiều đơn hàng. API hỗ trợ ba cách phân trang: offset-based, keyset/seek và cursor-based.

Ngoài phân trang, API có lọc theo `status`, `customer_id`, sắp xếp bằng `sort` và chỉ lấy một số trường bằng `fields`.

## 1. Offset-based pagination

Offset-based dùng số trang hoặc số bản ghi cần bỏ qua. Ví dụ:

`/orders?pagination=offset&page=2&limit=5`

API bỏ qua 5 bản ghi đầu rồi lấy 5 bản ghi tiếp theo.

Ưu điểm là dễ hiểu, dễ làm nút số trang và phù hợp với màn hình quản trị. Nhược điểm là khi dữ liệu rất lớn, database phải bỏ qua nhiều dòng; nếu có đơn hàng mới chèn vào thì các trang sau có thể bị lệch.

Ví dụ thực tế: trang danh sách đơn hàng của admin có các nút `1, 2, 3, 4` thường dùng offset-based.

## 2. Keyset / seek pagination

Keyset không dùng số trang. API lấy các bản ghi sau một giá trị khóa đã biết.

`/orders?pagination=keyset&limit=5&after_id=5&sort=id`

Request này lấy các đơn hàng có `id` lớn hơn 5. Khóa `id` phải được sắp xếp ổn định và có index.

Ưu điểm là nhanh hơn offset khi bảng có nhiều dữ liệu và ít bị trùng hoặc bỏ sót khi có bản ghi mới. Nhược điểm là không nhảy trực tiếp đến trang số 10 và cần một khóa sắp xếp phù hợp.

Ví dụ thực tế: đọc tiếp danh sách sự kiện hoặc lịch sử giao dịch theo thời gian, chỉ cần lấy phần sau bản ghi cuối cùng.

## 3. Cursor-based pagination

Cursor-based cũng dựa trên khóa sắp xếp, nhưng server mã hóa khóa đó thành một cursor opaque. Client không cần biết cursor chứa `id` hay thông tin gì bên trong.

Request đầu tiên:

`/orders?limit=5`

Response trả về `next_cursor`. Request tiếp theo truyền cursor đó:

`/orders?limit=5&cursor=...`

Ưu điểm là phù hợp cho infinite scroll, mobile app và dữ liệu liên tục thay đổi. Client chỉ cần giữ cursor, không phụ thuộc vào số trang. Nhược điểm là không phù hợp khi cần nhảy đến một trang bất kỳ và cursor không nên tự phân tích ở phía client.

Ví dụ thực tế: kéo tiếp danh sách tin nhắn, feed mạng xã hội hoặc lịch sử thanh toán.

## So sánh nhanh

- Offset: dễ hiểu, có số trang, nhưng chậm khi offset lớn.
- Keyset: nhanh và ổn định hơn, nhưng cần khóa sắp xếp.
- Cursor: che giấu trạng thái phân trang, phù hợp infinite scroll, nhưng không có khái niệm trang số N.

## Filter, sort và sparse fieldsets

- `status=paid`: chỉ lấy đơn hàng đã thanh toán.
- `customer_id=5`: chỉ lấy đơn hàng của khách hàng 5.
- `sort=id` hoặc `sort=-id`: sắp xếp tăng hoặc giảm theo id.
- `fields=id,total`: chỉ trả về `id` và `total`, giúp response nhỏ hơn.

Ví dụ kết hợp:

`/orders?status=paid&limit=5&fields=id,total`

Cursor sai định dạng hoặc tham số không hợp lệ sẽ trả về `400`.

## Chạy chương trình

Mở terminal tại thư mục `Lec3/lab3`:

```bash
pip install flask
python app.py
```

Server chạy tại `http://127.0.0.1:5000`.
