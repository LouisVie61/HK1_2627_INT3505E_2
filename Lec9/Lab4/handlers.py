"""Example implementations behind the gateway."""


def _create_order(body, version):
    result = dict(body)
    result.setdefault("status", "created")
    result["handler"] = version
    return result


def v1_create_order(body):
    return _create_order(body, "v1")


def v2_create_order(body):
    return _create_order(body, "v2")
