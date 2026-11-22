"""Small stand-in handlers representing the two order implementations."""


def _create_order(body, version):
    order = dict(body)
    order.setdefault("status", "created")
    order["handler"] = version
    return order


def v1_create_order(body):
    return _create_order(body, "v1")


def v2_create_order(body):
    return _create_order(body, "v2")
