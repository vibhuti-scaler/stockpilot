#!/usr/bin/env bash
# Generates sustained CPU load on the backend so the HPA scales it out.
# Usage: URL=http://stockpilot.local/api/products ./scripts/load-test.sh [concurrency] [seconds]
set -euo pipefail

URL="${URL:-http://stockpilot.local/api/products}"
CONCURRENCY="${1:-20}"
DURATION="${2:-120}"

echo "Hammering $URL with $CONCURRENCY workers for ${DURATION}s ..."
end=$((SECONDS + DURATION))
for _ in $(seq 1 "$CONCURRENCY"); do
  (
    while [ $SECONDS -lt $end ]; do
      curl -s -o /dev/null "$URL" || true
      curl -s -o /dev/null "${URL%/products}/products/stats" || true
    done
  ) &
done
wait
echo "Load test completed. Watch: kubectl get hpa -n stockpilot -w"
