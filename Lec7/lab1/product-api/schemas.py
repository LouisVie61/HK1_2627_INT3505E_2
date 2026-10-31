from marshmallow import Schema, fields, validate


class ProductOut(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, load_default=None)
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))


class ProductPatch(Schema):
    sku = fields.Str(validate=validate.Length(min=3, max=32))
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    price_cents = fields.Int(validate=validate.Range(min=0))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))


class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class OrderItemIn(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class OrderItemOut(Schema):
    id = fields.Int(dump_only=True)
    order_id = fields.Int()
    product_id = fields.Int()
    qty = fields.Int()
    product = fields.Nested(ProductOut, only=("id", "sku", "name", "price_cents"))


class OrderOut(Schema):
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    items = fields.Nested(OrderItemOut, many=True)

