import base64
import binascii
import json

from flask import Flask, jsonify, request


app = Flask(__name__)


def make_orders():
    statuses = ["paid", "pending", "cancelled"]
    orders = []
    for order_id in range(1, 31):
        orders.append(
            {
                "id": order_id,
                "total": order_id * 10000,
                "status": statuses[(order_id - 1) % 3],
                "customer_id": (order_id % 5) + 1,
                "created_at": f"2026-01-{((order_id - 1) % 28) + 1:02d}T09:00:00Z",
            }
        )
    return orders


orders = make_orders()


def error(message):
    return jsonify({"error": message}), 400


def encode_cursor(value):
    raw = json.dumps({"id": value}).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def decode_cursor(value):
    try:
        padding = "=" * (-len(value) % 4)
        data = base64.urlsafe_b64decode((value + padding).encode("utf-8"))
        cursor = json.loads(data.decode("utf-8"))
        if not isinstance(cursor.get("id"), int):
            raise ValueError
        return cursor["id"]
    except (ValueError, TypeError, json.JSONDecodeError, binascii.Error):
        raise ValueError("cursor không hợp lệ")


def get_options():
    strategy = request.args.get("pagination", "cursor")
    if strategy not in {"offset", "keyset", "cursor"}:
        raise ValueError("pagination phải là offset, keyset hoặc cursor")

    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        raise ValueError("limit phải là số")
    if limit < 1 or limit > 50:
        raise ValueError("limit phải từ 1 đến 50")

    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    if customer_id is not None:
        try:
            customer_id = int(customer_id)
        except ValueError:
            raise ValueError("customer_id phải là số")

    sort = request.args.get("sort", "id")
    if sort not in {"id", "-id", "created_at", "-created_at"}:
        raise ValueError("sort không được hỗ trợ")

    fields = request.args.get("fields")
    fields = fields.split(",") if fields else None
    allowed_fields = {"id", "total", "status", "customer_id", "created_at"}
    if fields and not set(fields).issubset(allowed_fields):
        raise ValueError("fields không hợp lệ")

    return strategy, limit, status, customer_id, sort, fields


def filter_and_sort_orders(status, customer_id, sort):
    result = orders[:]
    if status:
        result = [order for order in result if order["status"] == status]
    if customer_id is not None:
        result = [order for order in result if order["customer_id"] == customer_id]

    field = sort.lstrip("-")
    result.sort(key=lambda order: order[field], reverse=sort.startswith("-"))
    return result


def select_fields(items, fields):
    if not fields:
        return items
    return [{field: item[field] for field in fields if field in item} for item in items]


@app.get("/orders")
def get_orders():
    try:
        strategy, limit, status, customer_id, sort, fields = get_options()
        result = filter_and_sort_orders(status, customer_id, sort)

        # PHIÊN BẢN 1 - OFFSET-BASED: dễ hiểu, phù hợp màn hình có số trang.
        if strategy == "offset":
            try:
                page = max(int(request.args.get("page", 1)), 1)
            except ValueError:
                raise ValueError("page phải là số")
            start = (page - 1) * limit
            items = result[start : start + limit]
            body = {
                "items": select_fields(items, fields),
                "page": page,
                "limit": limit,
                "total": len(result),
                "has_next": start + limit < len(result),
            }

        # PHIÊN BẢN 2 - KEYSET/SEEK: lấy bản ghi sau một khóa sắp xếp ổn định.
        elif strategy == "keyset":
            if sort not in {"id", "-id"}:
                raise ValueError("keyset demo chỉ hỗ trợ sort=id hoặc sort=-id")
            after_id = request.args.get("after_id")
            if after_id is not None:
                try:
                    after_id = int(after_id)
                except ValueError:
                    raise ValueError("after_id phải là số")
                if sort == "id":
                    result = [order for order in result if order["id"] > after_id]
                else:
                    result = [order for order in result if order["id"] < after_id]
            items = result[:limit]
            next_after_id = items[-1]["id"] if len(items) == limit else None
            body = {
                "items": select_fields(items, fields),
                "limit": limit,
                "next_after_id": next_after_id,
            }

        # PHIÊN BẢN 3 - CURSOR-BASED: bọc khóa phân trang thành token opaque.
        else:
            if sort not in {"id", "-id"}:
                raise ValueError("cursor demo chỉ hỗ trợ sort=id hoặc sort=-id")
            cursor = request.args.get("cursor")
            if cursor:
                after_id = decode_cursor(cursor)
                if sort == "id":
                    result = [order for order in result if order["id"] > after_id]
                else:
                    result = [order for order in result if order["id"] < after_id]
            items = result[:limit]
            next_cursor = encode_cursor(items[-1]["id"]) if len(items) == limit else None
            body = {
                "items": select_fields(items, fields),
                "limit": limit,
                "next_cursor": next_cursor,
            }

        return jsonify(body)
    except ValueError as exc:
        return error(str(exc))


if __name__ == "__main__":
    app.run(debug=True)
