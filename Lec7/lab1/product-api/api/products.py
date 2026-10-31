from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from errors import ApiError
from extensions import db
from models import Product
from schemas import ProductIn, ProductOut, ProductPatch, ReserveIn


products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")
product_out = ProductOut()


def body(schema):
    try:
        return schema.load(request.get_json(silent=False) or {})
    except (ValidationError, TypeError, ValueError) as exc:
        messages = exc.messages if isinstance(exc, ValidationError) else {"body": [str(exc)]}
        raise ApiError(422, "Validation failed", messages) from exc


def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        raise ApiError(404, "Product not found")
    return product


@products_bp.get("")
def list_products():
    try:
        page = max(1, int(request.args.get("page", 1)))
        size = min(100, max(1, int(request.args.get("size", 20))))
    except ValueError as exc:
        raise ApiError(422, "page and size must be integers") from exc
    query = select(Product).where(Product.archived.is_(False)).order_by(Product.id)
    total = db.session.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.session.scalars(query.offset((page - 1) * size).limit(size)).all()
    return jsonify({"items": product_out.dump(rows, many=True), "page": page, "size": size, "total": total})


@products_bp.get("/<int:product_id>")
def get_one(product_id):
    return jsonify(product_out.dump(get_product(product_id)))


@products_bp.post("")
def create_product():
    product = Product(**body(ProductIn()))
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "SKU already exists") from exc
    return jsonify(product_out.dump(product)), 201


@products_bp.post("/<int:product_id>/reserve")
def reserve_product(product_id):
    product = get_product(product_id)
    qty = body(ReserveIn())["qty"]
    if product.qty_in_stock < qty:
        raise ApiError(409, "Insufficient stock", {"available": product.qty_in_stock, "requested": qty})
    product.qty_in_stock -= qty
    db.session.commit()
    return jsonify(product_out.dump(product))


@products_bp.patch("/<int:product_id>")
def patch_product(product_id):
    product = get_product(product_id)
    for key, value in body(ProductPatch()).items():
        setattr(product, key, value)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiError(409, "SKU already exists") from exc
    return jsonify(product_out.dump(product))


@products_bp.delete("/<int:product_id>")
def delete_product(product_id):
    product = get_product(product_id)
    product.archived = True
    db.session.commit()
    return "", 204

