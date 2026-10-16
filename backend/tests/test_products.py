def test_list_products_empty(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client, supplier):
    response = client.post(
        "/api/products",
        json={
            "sku": "off-2001",
            "name": "A4 Copier Paper",
            "category": "Office",
            "quantity": 50,
            "reorder_level": 10,
            "unit_price": 320,
            "supplier_id": supplier["id"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "OFF-2001"  # SKUs are normalised to upper-case
    assert body["supplier_name"] == "Nimbus Electronics"
    assert body["stock_status"] == "IN_STOCK"
    assert body["id"] > 0


def test_create_product_validation_error(client):
    response = client.post("/api/products", json={"sku": "x", "name": "", "quantity": -5})
    assert response.status_code == 422
    fields = {err["loc"][-1] for err in response.json()["detail"]}
    assert {"sku", "name", "quantity"} <= fields


def test_create_product_duplicate_sku_conflict(client, product):
    response = client.post("/api/products", json={"sku": product["sku"], "name": "Duplicate"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_product_unknown_supplier(client):
    response = client.post("/api/products", json={"sku": "AB-1", "name": "X", "supplier_id": 999})
    assert response.status_code == 422


def test_get_product(client, product):
    response = client.get(f"/api/products/{product['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "USB-C Charging Cable"


def test_get_product_not_found(client):
    response = client.get("/api/products/12345")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client, product):
    response = client.put(
        f"/api/products/{product['id']}", json={"quantity": 5, "unit_price": 249.5}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == 5
    assert body["unit_price"] == 249.5
    assert body["stock_status"] == "LOW_STOCK"


def test_update_product_not_found(client):
    response = client.put("/api/products/999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_product(client, product):
    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404
    assert client.delete(f"/api/products/{product['id']}").status_code == 404


def test_search_and_filter_products(client, supplier):
    for sku, name, qty, reorder, category in [
        ("A-1", "Alpha Widget", 100, 10, "Hardware"),
        ("B-2", "Beta Gadget", 5, 10, "Hardware"),
        ("C-3", "Gamma Gizmo", 0, 10, "Software"),
    ]:
        client.post(
            "/api/products",
            json={
                "sku": sku,
                "name": name,
                "quantity": qty,
                "reorder_level": reorder,
                "category": category,
            },
        )

    assert len(client.get("/api/products").json()) == 3
    assert [p["name"] for p in client.get("/api/products?q=beta").json()] == ["Beta Gadget"]
    assert len(client.get("/api/products?category=Hardware").json()) == 2
    assert [p["sku"] for p in client.get("/api/products?stock_status=LOW_STOCK").json()] == ["B-2"]
    assert [p["sku"] for p in client.get("/api/products?stock_status=OUT_OF_STOCK").json()] == [
        "C-3"
    ]
    assert [p["sku"] for p in client.get("/api/products?stock_status=IN_STOCK").json()] == ["A-1"]
    assert client.get("/api/products?stock_status=BOGUS").status_code == 422

    low = client.get("/api/products/low-stock").json()
    assert [p["sku"] for p in low] == ["C-3", "B-2"]


def test_inventory_stats(client, supplier):
    client.post(
        "/api/products",
        json={"sku": "S-1", "name": "One", "quantity": 10, "reorder_level": 2, "unit_price": 2.5},
    )
    client.post(
        "/api/products",
        json={"sku": "S-2", "name": "Two", "quantity": 1, "reorder_level": 5, "unit_price": 100},
    )
    client.post(
        "/api/products",
        json={"sku": "S-3", "name": "Three", "quantity": 0, "reorder_level": 5, "unit_price": 7},
    )

    stats = client.get("/api/products/stats").json()
    assert stats == {
        "totalProducts": 3,
        "totalUnits": 11,
        "lowStock": 1,
        "outOfStock": 1,
        "inventoryValue": 125.0,
        "suppliers": 1,
        "movementsToday": 0,
    }
