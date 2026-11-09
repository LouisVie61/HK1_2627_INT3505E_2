PRODUCTS = [
    {"id": 1, "name": "Coffee", "price": 4.5},
    {"id": 2, "name": "Tea", "price": 3.0},
]


def list_products():
    """Handler được OpenAPI operationId products.list_products gọi."""
    return PRODUCTS


def create_product(body):
    """Handler được OpenAPI operationId products.create_product gọi."""
    product = {
        "id": len(PRODUCTS) + 1,
        "name": body["name"],
        "price": body["price"],
    }
    PRODUCTS.append(product)
    return product, 201

