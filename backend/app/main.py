"""StockPilot API - FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .routers import health, movements, products, suppliers

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger("stockpilot")

DESCRIPTION = """
StockPilot is an inventory management service.

* **Products** - catalogue items with SKU, quantity, reorder level and unit price
* **Suppliers** - vendors that provide products
* **Stock movements** - an append-only ledger of goods received (IN) and issued (OUT)

Operational endpoints: `/health` (liveness), `/ready` (readiness), `/metrics` (Prometheus).
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("%s %s starting", settings.app_name, settings.app_version)
    yield
    logger.info("%s shutting down", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=DESCRIPTION,
    lifespan=lifespan,
    contact={"name": "Vibhuti Bhatnagar (24bcs10288)"},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics", "/health", "/ready"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(movements.router)
