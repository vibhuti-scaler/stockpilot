from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..metrics import INVENTORY_VALUE, LOW_STOCK_PRODUCTS, PRODUCTS_TOTAL
from ..models import Product, StockMovement, Supplier
from ..schemas import InventoryStats, ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


def _get_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def _validate_supplier(db: Session, supplier_id: int | None) -> None:
    if supplier_id is not None and db.get(Supplier, supplier_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Supplier {supplier_id} does not exist",
        )


@router.get("", response_model=list[ProductOut], summary="List products")
def list_products(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Search by name or SKU"),
    category: str | None = Query(default=None),
    stock_status: str | None = Query(default=None, pattern="^(IN_STOCK|LOW_STOCK|OUT_OF_STOCK)$"),
) -> list[Product]:
    stmt = select(Product).order_by(Product.id.desc())
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(func.lower(Product.name).like(pattern), func.lower(Product.sku).like(pattern))
        )
    if category:
        stmt = stmt.where(Product.category == category)
    if stock_status == "OUT_OF_STOCK":
        stmt = stmt.where(Product.quantity <= 0)
    elif stock_status == "LOW_STOCK":
        stmt = stmt.where(Product.quantity > 0, Product.quantity <= Product.reorder_level)
    elif stock_status == "IN_STOCK":
        stmt = stmt.where(Product.quantity > Product.reorder_level)
    return list(db.scalars(stmt).unique())


@router.get("/stats", response_model=InventoryStats, summary="Inventory KPIs")
def inventory_stats(db: Session = Depends(get_db)) -> InventoryStats:
    total_products = db.scalar(select(func.count(Product.id))) or 0
    total_units = db.scalar(select(func.coalesce(func.sum(Product.quantity), 0))) or 0
    low_stock = (
        db.scalar(
            select(func.count(Product.id)).where(
                Product.quantity > 0, Product.quantity <= Product.reorder_level
            )
        )
        or 0
    )
    out_of_stock = db.scalar(select(func.count(Product.id)).where(Product.quantity <= 0)) or 0
    inventory_value = (
        db.scalar(select(func.coalesce(func.sum(Product.quantity * Product.unit_price), 0))) or 0
    )
    suppliers = db.scalar(select(func.count(Supplier.id))) or 0
    since = datetime.now(UTC) - timedelta(days=1)
    movements_today = (
        db.scalar(select(func.count(StockMovement.id)).where(StockMovement.created_at >= since))
        or 0
    )

    PRODUCTS_TOTAL.set(total_products)
    LOW_STOCK_PRODUCTS.set(low_stock + out_of_stock)
    INVENTORY_VALUE.set(float(inventory_value))

    return InventoryStats(
        totalProducts=total_products,
        totalUnits=int(total_units),
        lowStock=low_stock,
        outOfStock=out_of_stock,
        inventoryValue=round(float(inventory_value), 2),
        suppliers=suppliers,
        movementsToday=movements_today,
    )


@router.get("/low-stock", response_model=list[ProductOut], summary="Products needing reorder")
def low_stock_products(db: Session = Depends(get_db)) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.quantity <= Product.reorder_level)
        .order_by(Product.quantity.asc(), Product.name)
    )
    return list(db.scalars(stmt).unique())


@router.get("/{product_id}", response_model=ProductOut, summary="Get product")
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    return _get_or_404(db, product_id)


@router.post(
    "", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="Create product"
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    _validate_supplier(db, payload.supplier_id)
    product = Product(**payload.model_dump())
    product.sku = product.sku.upper()
    db.add(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"SKU {product.sku} already exists"
        ) from exc
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut, summary="Update product")
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
) -> Product:
    product = _get_or_404(db, product_id)
    changes = payload.model_dump(exclude_unset=True)
    if "supplier_id" in changes:
        _validate_supplier(db, changes["supplier_id"])
    if "sku" in changes and changes["sku"]:
        changes["sku"] = changes["sku"].upper()
    for key, value in changes.items():
        setattr(product, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="SKU already exists"
        ) from exc
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete product")
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = _get_or_404(db, product_id)
    db.delete(product)
    db.commit()
