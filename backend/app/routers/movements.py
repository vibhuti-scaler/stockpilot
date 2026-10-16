from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..metrics import STOCK_MOVEMENTS
from ..models import Product, StockMovement
from ..schemas import MovementCreate, MovementOut

router = APIRouter(prefix="/api/movements", tags=["stock movements"])


@router.get("", response_model=list[MovementOut], summary="Stock movement ledger")
def list_movements(
    db: Session = Depends(get_db),
    product_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
) -> list[StockMovement]:
    stmt = select(StockMovement).order_by(StockMovement.id.desc()).limit(limit)
    if product_id is not None:
        stmt = stmt.where(StockMovement.product_id == product_id)
    return list(db.scalars(stmt).unique())


@router.post(
    "",
    response_model=MovementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Receive (IN) or issue (OUT) stock",
)
def create_movement(payload: MovementCreate, db: Session = Depends(get_db)) -> StockMovement:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if payload.movement_type == "OUT":
        if product.quantity < payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for {product.sku}: "
                    f"{product.quantity} available, {payload.quantity} requested"
                ),
            )
        product.quantity -= payload.quantity
    else:
        product.quantity += payload.quantity

    movement = StockMovement(**payload.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    STOCK_MOVEMENTS.labels(movement_type=payload.movement_type).inc()
    return movement
