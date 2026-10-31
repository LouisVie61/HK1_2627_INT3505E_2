def make_product(client, sku="SKU-001"):
    response = client.post(
        "/api/v1/products",
        json={"sku": sku, "name": "Keyboard", "price_cents": 250000, "qty_in_stock": 5},
    )
    assert response.status_code == 201
    return response.get_json()


def test_product_post_and_get(client):
    product = make_product(client)
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    assert response.get_json()["sku"] == product["sku"]


def test_order_item_does_not_duplicate_product(client):
    product = make_product(client)
    order = client.post("/api/v1/orders").get_json()
    item = client.post(
        f"/api/v1/orders/{order['id']}/items",
        json={"product_id": product["id"], "qty": 2},
    )
    assert item.status_code == 201
    order_response = client.get(f"/api/v1/orders/{order['id']}")
    assert order_response.status_code == 200
    assert order_response.get_json()["items"][0]["product"]["sku"] == "SKU-001"
    duplicate = client.post(
        f"/api/v1/orders/{order['id']}/items",
        json={"product_id": product["id"], "qty": 1},
    )
    assert duplicate.status_code == 409

