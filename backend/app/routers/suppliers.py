from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Supplier
from ..schemas import SupplierCreate, SupplierOut, SupplierUpdate

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


def _get_or_404(db: Session, supplier_id: int) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.get("", response_model=list[SupplierOut], summary="List suppliers")
def list_suppliers(db: Session = Depends(get_db)) -> list[Supplier]:
    return list(db.scalars(select(Supplier).order_by(Supplier.name)))


@router.post(
    "", response_model=SupplierOut, status_code=status.HTTP_201_CREATED, summary="Create supplier"
)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)) -> Supplier:
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierOut, summary="Get supplier")
def get_supplier(supplier_id: int, db: Session = Depends(get_db)) -> Supplier:
    return _get_or_404(db, supplier_id)


@router.put("/{supplier_id}", response_model=SupplierOut, summary="Update supplier")
def update_supplier(
    supplier_id: int, payload: SupplierUpdate, db: Session = Depends(get_db)
) -> Supplier:
    supplier = _get_or_404(db, supplier_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete supplier")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)) -> None:
    supplier = _get_or_404(db, supplier_id)
    for product in supplier.products:
        product.supplier_id = None
    db.delete(supplier)
    db.commit()
