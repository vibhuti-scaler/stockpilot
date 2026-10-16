# ---- Stage 1: build a virtualenv with the pinned dependencies ----
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt \
    # the runtime never installs packages: drop the installers to shrink the attack surface
    && /opt/venv/bin/pip uninstall -y pip setuptools wheel

# ---- Stage 2: minimal runtime image ----
FROM python:3.12-slim

LABEL org.opencontainers.image.title="stockpilot-backend" \
      org.opencontainers.image.description="StockPilot inventory management API (FastAPI + PostgreSQL)" \
      org.opencontainers.image.authors="Vibhuti Bhatnagar (24bcs10288)" \
      org.opencontainers.image.source="https://github.com/vibhuti-scaler/stockpilot"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Remove the interpreter's bundled pip/setuptools as well (not needed at runtime, flagged by scanners)
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/lib/python3.12/site-packages/setuptools* \
           /usr/local/lib/python3.12/site-packages/_distutils_hack \
           /usr/local/lib/python3.12/site-packages/distutils-precedence.pth \
           /usr/local/bin/pip* \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app alembic.ini entrypoint.sh ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app

USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

# Apply Alembic migrations (with DB wait/retry), optionally seed demo data, then start Uvicorn
ENTRYPOINT ["./entrypoint.sh"]
