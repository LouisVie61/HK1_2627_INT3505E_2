from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from api.products import body
from errors import ApiError
from extensions import db
from models import Order, OrderItem, Product
from schemas import OrderItemIn, OrderItemOut, OrderOut


orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")
order_out = OrderOut()
item_out = OrderItemOut()


def get_order(order_id):
    result = db.session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
    )
    order = result.unique().scalar_one_or_none()
    if order is None:
        raise ApiError(404, "Order not found")
    return order


@orders_bp.post("")
def create_order():
    order = Order()
    db.session.add(order)
    db.session.commit()
    return jsonify(order_out.dump(order)), 201


@orders_bp.get("/<int:order_id>")
def get_one_order(order_id):
    return jsonify(order_out.dump(get_order(order_id)))


@orders_bp.post("/<int:order_id>/items")
def add_item(order_id):
    order = get_order(order_id)
    data = body(OrderItemIn())
    product = db.session.get(Product, data["product_id"])
    if product is None or product.archived:
        raise ApiError(404, "Product not found")
    item = OrderItem(order=order, product=product, qty=data["qty"])
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "A product can only appear once in an order") from exc
    return jsonify(item_out.dump(item)), 201


@orders_bp.get("/<int:order_id>/items")
def list_items(order_id):
    order = get_order(order_id)
    return jsonify(item_out.dump(order.items, many=True))

