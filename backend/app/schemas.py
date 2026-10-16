from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

StockStatus = Literal["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]
MovementType = Literal["IN", "OUT"]


# ---------- Suppliers ----------
class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    contact_email: EmailStr | Literal[""] = ""
    phone: str = Field(default="", max_length=40)
    city: str = Field(default="", max_length=80)


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    contact_email: EmailStr | Literal[""] | None = None
    phone: str | None = Field(default=None, max_length=40)
    city: str | None = Field(default=None, max_length=80)


class SupplierOut(SupplierCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Products ----------
class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9\-]+$")
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(default="General", min_length=1, max_length=60)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    unit_price: float = Field(default=0, ge=0)
    supplier_id: int | None = None


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=40, pattern=r"^[A-Za-z0-9\-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=60)
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    unit_price: float | None = Field(default=None, ge=0)
    supplier_id: int | None = None


class ProductOut(ProductCreate):
    id: int
    supplier_name: str | None = None
    stock_status: StockStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InventoryStats(BaseModel):
    totalProducts: int
    totalUnits: int
    lowStock: int
    outOfStock: int
    inventoryValue: float
    suppliers: int
    movementsToday: int


# ---------- Stock movements ----------
class MovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int = Field(gt=0, le=1_000_000)
    note: str = Field(default="", max_length=500)


class MovementOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    movement_type: MovementType
    quantity: int
    note: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Misc ----------
class HealthOut(BaseModel):
    status: str
    service: str
    version: str


class MessageOut(BaseModel):
    detail: str
