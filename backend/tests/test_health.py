def test_root_lists_operational_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "StockPilot API"
    assert body["docs"] == "/docs"


def test_health_returns_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "READY"


def test_metrics_exposes_prometheus_format(client):
    client.get("/api/products")  # generate at least one request sample
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
    assert "stockpilot_products_total" in response.text


def test_openapi_docs_available(client):
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert "/api/products" in schema["paths"]
    assert "/api/suppliers/{supplier_id}" in schema["paths"]
