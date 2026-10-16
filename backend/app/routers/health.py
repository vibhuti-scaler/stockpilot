from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics",
    }


@router.get("/health", response_model=HealthOut, summary="Liveness probe")
def health() -> HealthOut:
    """Cheap liveness check: the process is up and can answer HTTP."""
    return HealthOut(status="UP", service=settings.app_name, version=settings.app_version)


@router.get("/ready", response_model=HealthOut, summary="Readiness probe")
def ready(db: Session = Depends(get_db)) -> HealthOut:
    """Readiness check: the application can reach PostgreSQL and is able to serve traffic."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:  # pragma: no cover - exercised only when the DB is down
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database unavailable"
        ) from exc
    return HealthOut(status="READY", service=settings.app_name, version=settings.app_version)
