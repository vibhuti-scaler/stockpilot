#!/bin/sh
# Container entrypoint: wait for PostgreSQL, apply Alembic migrations, optionally seed, then serve.
set -e

ATTEMPTS="${DB_WAIT_ATTEMPTS:-30}"
i=1
until alembic upgrade head; do
  if [ "$i" -ge "$ATTEMPTS" ]; then
    echo "Database not reachable after $ATTEMPTS attempts - giving up" >&2
    exit 1
  fi
  echo "Database not ready (attempt $i/$ATTEMPTS) - retrying in 2s..."
  i=$((i + 1))
  sleep 2
done

if [ "$SEED_DEMO_DATA" = "true" ]; then
  python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
