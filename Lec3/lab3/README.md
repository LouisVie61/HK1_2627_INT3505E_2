# Lec 3 - Lab 3

## Bài toán

Xây dựng API `GET /orders` cho danh sách nhiều đơn hàng. API hỗ trợ ba cách phân trang: offset-based, keyset/seek và cursor-based.

Ngoài phân trang, API có lọc theo `status`, `customer_id`, sắp xếp bằng `sort` và chỉ lấy một số trường bằng `fields`.

## 1. Offset-based pagination

### Định nghĩa

Phân trang bằng cách chỉ định **số trang** (hoặc số bản ghi cần bỏ qua) và số lượng bản ghi lấy ra, tương tự `LIMIT`/`OFFSET` trong SQL.

### Cơ chế

Server tính `start = (page - 1) * limit` rồi cắt mảng kết quả `result[start : start + limit]` (xem [app.py:109-122](app.py#L109-L122)). Về bản chất SQL tương đương:

```sql
SELECT * FROM orders ORDER BY id LIMIT 5 OFFSET 5;
```

Database phải **duyệt/đếm qua toàn bộ `offset` dòng phía trước** rồi mới bắt đầu lấy dữ liệu trả về — dù những dòng đó không hề được dùng. Vì vậy chi phí tăng tuyến tính theo `offset`: offset càng lớn (trang càng xa) thì càng chậm, không phụ thuộc index.

Hệ quả thứ hai: trang được tính theo **vị trí tuyệt đối**, không neo vào dữ liệu cụ thể. Nếu giữa hai lần gọi có bản ghi mới chèn vào trước vị trí đang đọc, toàn bộ các dòng phía sau dịch chuyển → trang sau có thể lặp lại hoặc bỏ sót bản ghi.

### Ví dụ

```
GET /orders?pagination=offset&page=2&limit=5
```

Bỏ qua 5 bản ghi đầu (trang 1), lấy tiếp 5 bản ghi kế. Response trả kèm `page`, `total`, `has_next` để dựng UI dạng số trang `1 2 3 4 ...` — phù hợp màn hình quản trị, nơi người dùng cần nhảy thẳng đến một trang bất kỳ.

## 2. Keyset / seek pagination

### Định nghĩa

Phân trang bằng cách lấy các bản ghi **đứng sau một giá trị khóa (key) đã biết**, thay vì đếm vị trí. Không có khái niệm "trang số mấy", chỉ có "bản ghi sau giá trị X".

### Cơ chế

Client gửi lên giá trị khóa cuối cùng đã nhận (`after_id`), server lọc theo điều kiện so sánh trên chính khóa đó (xem [app.py:125-144](app.py#L125-L144)):

```python
if after_id is not None:
    result = [order for order in result if order["id"] > after_id]
items = result[:limit]
next_after_id = items[-1]["id"] if len(items) == limit else None
```

Tương đương SQL:

```sql
SELECT * FROM orders WHERE id > 5 ORDER BY id LIMIT 5;
```

Vì `id` có index (B-tree, thường là primary key), database **seek thẳng** tới vị trí `id = 5` rồi đọc tiếp — không phải duyệt qua các dòng trước đó. Độ phức tạp gần như O(log n + limit), không phụ thuộc "đang ở trang bao nhiêu xa".

Vì trang được neo vào **giá trị dữ liệu cụ thể** (`id > 5`) chứ không phải vị trí tuyệt đối, việc chèn/xóa bản ghi ở nơi khác trong bảng không làm lệch kết quả — khác hẳn offset.

**Ràng buộc quan trọng**: khóa dùng để seek phải **duy nhất và có thứ tự ổn định**. Code giới hạn `sort` chỉ còn `id`/`-id` khi dùng keyset ([app.py:126-127](app.py#L126-L127)) vì nếu sort theo cột có giá trị trùng nhau (ví dụ nhiều đơn cùng `created_at`), điều kiện `created_at > X` có thể bỏ sót hoặc lặp các bản ghi có cùng giá trị X. Trong thực tế, người ta thường dùng **composite keyset** `WHERE (created_at, id) > (X, Y)` để đảm bảo khóa luôn duy nhất.

### Ví dụ

```
GET /orders?pagination=keyset&limit=5&sort=id&after_id=5
```

Lấy 5 đơn hàng có `id` lớn hơn 5. Lần gọi tiếp theo dùng `next_after_id` vừa nhận được làm `after_id` mới — tiến dần về cuối danh sách, không bao giờ quay lại trang trước đó bằng cách đổi số trang.

## 3. Cursor-based pagination

### Định nghĩa

Về cơ chế lọc, cursor-based **chính là keyset** — cùng dùng điều kiện so sánh trên khóa sắp xếp. Khác biệt duy nhất: giá trị khóa đó được server **gói lại thành một chuỗi "mờ" (tiếng Anh: opaque — nghĩa là không nhìn xuyên qua được) mà client chỉ được cầm và gửi lại, không được phép đọc hiểu nội dung bên trong**, thay vì để client thấy trực tiếp con số thật.

> Hình dung cursor như một **tấm vé giữ xe**: bạn không cần biết tấm vé ghi mã số gì — chỉ cần cầm nó và đưa lại lúc lấy xe, nơi giữ xe tự biết phải làm gì với nó.

### Cơ chế

So sánh hai nhánh xử lý trong code sẽ thấy chúng gần như giống hệt nhau, chỉ khác bước encode/decode:

```python
# keyset: client tự cầm con số thật
after_id = int(request.args.get("after_id"))

# cursor: client cầm một chuỗi không đọc hiểu được
after_id = decode_cursor(request.args.get("cursor"))
```

`encode_cursor`/`decode_cursor` ([app.py:34-48](app.py#L34-L48)) gói `{"id": value}` thành JSON rồi base64:

```python
def encode_cursor(value):
    raw = json.dumps({"id": value}).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
```

Client không parse, không suy luận cursor chứa gì — chỉ giữ và gửi lại y nguyên. Lợi ích:

1. **Tự do đổi khóa phân trang nội bộ** mà không phá hợp đồng API — ví dụ sau này đổi từ `id` sang composite `(created_at, id)`, client vẫn gọi `?cursor=...` y như cũ.
2. **Giấu chi tiết triển khai** khỏi client bên thứ ba (mobile app, SDK công khai).

Lưu ý: bản demo chỉ **encode** (base64), không **ký/mã hóa** thật sự — ai cũng decode ngược lại được giá trị bên trong (`base64.urlsafe_b64decode`), nên về bảo mật nó chỉ "làm mờ" chứ chưa chống giả mạo. Production thường ký cursor bằng HMAC để server tin tưởng cursor đến từ chính mình.

### Ví dụ

```
GET /orders?limit=5
→ { "items": [...], "next_cursor": "eyJpZCI6IDV9" }

GET /orders?limit=5&cursor=eyJpZCI6IDV9
→ { "items": [...], "next_cursor": "eyJpZCI6IDEwfQ" }
```

Client không cần biết `eyJpZCI6IDV9` giải mã ra `{"id": 5}` — chỉ cần dán nguyên cursor vào request sau. Phù hợp infinite scroll, feed, lịch sử giao dịch — nơi người dùng chỉ kéo tiếp chứ không nhảy trang.

## So sánh

| Tiêu chí | Offset | Keyset / Seek | Cursor-based |
|---|---|---|---|
| Vị trí trang được xác định bằng | Số thứ tự tuyệt đối (`OFFSET`) | Giá trị khóa sắp xếp (`id > X`) | Khóa sắp xếp, nhưng được gói trong chuỗi "mờ" client không đọc được |
| Tốc độ khi dữ liệu lớn | Chậm dần theo offset (phải duyệt qua các dòng bị bỏ) | Nhanh, dùng index seek, không phụ thuộc độ sâu trang | Giống keyset (cùng cơ chế lọc bên dưới) |
| Ổn định khi dữ liệu thay đổi đồng thời | Dễ lệch (trùng/bỏ sót) khi có insert/delete | Ổn định vì neo vào giá trị dữ liệu | Ổn định như keyset |
| Nhảy thẳng đến trang N bất kỳ | Có | Không | Không |
| Client có thấy/suy luận được khóa phân trang không | Có (số trang) | Có (`after_id` là số thật) | Không (cursor "mờ", chỉ cầm và gửi lại) |
| Ràng buộc dữ liệu | Không cần khóa đặc biệt | Cần cột sort duy nhất, có index | Giống keyset |
| Trường hợp dùng điển hình | Màn hình quản trị có nút số trang | API nội bộ, service-to-service cần tốc độ | Infinite scroll, mobile app, API public |

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
