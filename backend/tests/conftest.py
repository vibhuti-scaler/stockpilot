"""Shared pytest fixtures.

Tests never touch the real PostgreSQL database: an isolated in-memory SQLite database is
created for every test function and injected through FastAPI's dependency override.
"""

import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest  # noqa: E402
from app import models  # noqa: E402, F401
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def supplier(client):
    response = client.post(
        "/api/suppliers",
        json={
            "name": "Nimbus Electronics",
            "contact_email": "sales@nimbus.example",
            "phone": "+91 98100 11223",
            "city": "Bengaluru",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def product(client, supplier):
    response = client.post(
        "/api/products",
        json={
            "sku": "ELC-1001",
            "name": "USB-C Charging Cable",
            "category": "Electronics",
            "quantity": 100,
            "reorder_level": 20,
            "unit_price": 199.0,
            "supplier_id": supplier["id"],
        },
    )
    assert response.status_code == 201
    return response.json()
