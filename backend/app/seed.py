"""Idempotent demo data loader: `python -m app.seed` (also used by SEED_DEMO_DATA=true)."""

import logging

from sqlalchemy import func, select

from .db import SessionLocal
from .models import Product, StockMovement, Supplier

logger = logging.getLogger("stockpilot.seed")

SUPPLIERS = [
    {
        "name": "Nimbus Electronics",
        "contact_email": "sales@nimbus.example",
        "phone": "+91 98100 11223",
        "city": "Bengaluru",
    },
    {
        "name": "Harbor Supplies Co.",
        "contact_email": "orders@harbor.example",
        "phone": "+91 99870 44556",
        "city": "Mumbai",
    },
    {
        "name": "GreenLeaf Packaging",
        "contact_email": "hello@greenleaf.example",
        "phone": "+91 97654 77889",
        "city": "Pune",
    },
]

PRODUCTS = [
    {
        "sku": "ELC-1001",
        "name": "USB-C Charging Cable 1m",
        "category": "Electronics",
        "quantity": 240,
        "reorder_level": 50,
        "unit_price": 199.0,
        "supplier": 0,
    },
    {
        "sku": "ELC-1002",
        "name": "Wireless Mouse",
        "category": "Electronics",
        "quantity": 36,
        "reorder_level": 40,
        "unit_price": 749.0,
        "supplier": 0,
    },
    {
        "sku": "ELC-1003",
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "quantity": 0,
        "reorder_level": 10,
        "unit_price": 3499.0,
        "supplier": 0,
    },
    {
        "sku": "OFF-2001",
        "name": "A4 Copier Paper (500 sheets)",
        "category": "Office",
        "quantity": 180,
        "reorder_level": 60,
        "unit_price": 320.0,
        "supplier": 1,
    },
    {
        "sku": "OFF-2002",
        "name": "Gel Pens (box of 12)",
        "category": "Office",
        "quantity": 12,
        "reorder_level": 25,
        "unit_price": 140.0,
        "supplier": 1,
    },
    {
        "sku": "OFF-2003",
        "name": "Ergonomic Office Chair",
        "category": "Furniture",
        "quantity": 8,
        "reorder_level": 5,
        "unit_price": 8999.0,
        "supplier": 1,
    },
    {
        "sku": "PKG-3001",
        "name": "Corrugated Box Medium",
        "category": "Packaging",
        "quantity": 420,
        "reorder_level": 100,
        "unit_price": 28.0,
        "supplier": 2,
    },
    {
        "sku": "PKG-3002",
        "name": "Bubble Wrap Roll 50m",
        "category": "Packaging",
        "quantity": 5,
        "reorder_level": 15,
        "unit_price": 650.0,
        "supplier": 2,
    },
]

MOVEMENTS = [
    ("ELC-1001", "IN", 100, "Purchase order PO-1042 received"),
    ("OFF-2001", "OUT", 20, "Issued to Finance department"),
    ("PKG-3001", "IN", 200, "Monthly packaging restock"),
    ("ELC-1002", "OUT", 4, "Onboarding kit for new hires"),
    ("PKG-3002", "OUT", 10, "Dispatch of customer orders"),
]


def seed() -> None:
    with SessionLocal() as db:
        if (db.scalar(select(func.count(Product.id))) or 0) > 0:
            logger.info("Database already contains products - skipping demo seed")
            return
        suppliers = [Supplier(**s) for s in SUPPLIERS]
        db.add_all(suppliers)
        db.flush()
        products: dict[str, Product] = {}
        for spec in PRODUCTS:
            data = dict(spec)
            supplier = suppliers[data.pop("supplier")]
            product = Product(**data, supplier_id=supplier.id)
            db.add(product)
            products[product.sku] = product
        db.flush()
        for sku, movement_type, qty, note in MOVEMENTS:
            db.add(
                StockMovement(
                    product_id=products[sku].id,
                    movement_type=movement_type,
                    quantity=qty,
                    note=note,
                )
            )
        db.commit()
        logger.info(
            "Seeded %d suppliers, %d products, %d movements",
            len(SUPPLIERS),
            len(PRODUCTS),
            len(MOVEMENTS),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed()
