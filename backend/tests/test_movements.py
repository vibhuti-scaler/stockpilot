def test_receive_stock_increases_quantity(client, product):
    response = client.post(
        "/api/movements",
        json={"product_id": product["id"], "movement_type": "IN", "quantity": 25, "note": "PO-1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["movement_type"] == "IN"
    assert body["product_sku"] == "ELC-1001"
    assert client.get(f"/api/products/{product['id']}").json()["quantity"] == 125


def test_issue_stock_decreases_quantity(client, product):
    response = client.post(
        "/api/movements", json={"product_id": product["id"], "movement_type": "OUT", "quantity": 90}
    )
    assert response.status_code == 201
    updated = client.get(f"/api/products/{product['id']}").json()
    assert updated["quantity"] == 10
    assert updated["stock_status"] == "LOW_STOCK"


def test_issue_more_than_available_is_rejected(client, product):
    response = client.post(
        "/api/movements",
        json={"product_id": product["id"], "movement_type": "OUT", "quantity": 101},
    )
    assert response.status_code == 409
    assert "Insufficient stock" in response.json()["detail"]
    assert client.get(f"/api/products/{product['id']}").json()["quantity"] == 100


def test_movement_for_unknown_product(client):
    response = client.post(
        "/api/movements", json={"product_id": 999, "movement_type": "IN", "quantity": 1}
    )
    assert response.status_code == 404


def test_movement_validation(client, product):
    bad_type = client.post(
        "/api/movements", json={"product_id": product["id"], "movement_type": "LOST", "quantity": 1}
    )
    assert bad_type.status_code == 422
    zero_qty = client.post(
        "/api/movements", json={"product_id": product["id"], "movement_type": "IN", "quantity": 0}
    )
    assert zero_qty.status_code == 422


def test_ledger_lists_latest_first_and_filters(client, product):
    for qty in (1, 2, 3):
        client.post(
            "/api/movements",
            json={"product_id": product["id"], "movement_type": "IN", "quantity": qty},
        )
    ledger = client.get("/api/movements").json()
    assert [m["quantity"] for m in ledger] == [3, 2, 1]
    assert len(client.get("/api/movements?limit=2").json()) == 2
    assert client.get("/api/movements?product_id=999").json() == []
    assert client.get("/api/products/stats").json()["movementsToday"] == 3
