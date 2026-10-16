def test_create_and_list_suppliers(client):
    created = client.post(
        "/api/suppliers", json={"name": "Harbor Supplies", "contact_email": "orders@harbor.example"}
    )
    assert created.status_code == 201
    assert created.json()["name"] == "Harbor Supplies"

    listed = client.get("/api/suppliers")
    assert listed.status_code == 200
    assert [s["name"] for s in listed.json()] == ["Harbor Supplies"]


def test_create_supplier_invalid_email(client):
    response = client.post("/api/suppliers", json={"name": "Bad", "contact_email": "not-an-email"})
    assert response.status_code == 422


def test_get_supplier_not_found(client):
    assert client.get("/api/suppliers/404").status_code == 404


def test_update_supplier(client, supplier):
    response = client.put(f"/api/suppliers/{supplier['id']}", json={"city": "Hyderabad"})
    assert response.status_code == 200
    assert response.json()["city"] == "Hyderabad"
    assert response.json()["name"] == "Nimbus Electronics"


def test_delete_supplier_detaches_products(client, supplier, product):
    assert product["supplier_id"] == supplier["id"]
    assert client.delete(f"/api/suppliers/{supplier['id']}").status_code == 204
    assert client.get(f"/api/suppliers/{supplier['id']}").status_code == 404

    detached = client.get(f"/api/products/{product['id']}").json()
    assert detached["supplier_id"] is None
    assert detached["supplier_name"] is None
