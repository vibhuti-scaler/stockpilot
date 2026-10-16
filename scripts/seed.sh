#!/usr/bin/env bash
# Seeds a running StockPilot API with a few suppliers/products through the public REST API.
# Usage: API=http://localhost:8000 ./scripts/seed.sh
set -euo pipefail
API="${API:-http://localhost:8000}"

post() { curl -s -o /dev/null -w "%{http_code} $1 $2\n" -X POST "$API$1" -H 'Content-Type: application/json' -d "$2"; }

post /api/suppliers '{"name":"Nimbus Electronics","contact_email":"sales@nimbus.example","city":"Bengaluru"}'
post /api/suppliers '{"name":"Harbor Supplies Co.","contact_email":"orders@harbor.example","city":"Mumbai"}'
post /api/products  '{"sku":"ELC-1001","name":"USB-C Charging Cable 1m","category":"Electronics","quantity":240,"reorder_level":50,"unit_price":199,"supplier_id":1}'
post /api/products  '{"sku":"OFF-2001","name":"A4 Copier Paper (500 sheets)","category":"Office","quantity":180,"reorder_level":60,"unit_price":320,"supplier_id":2}'
post /api/products  '{"sku":"PKG-3002","name":"Bubble Wrap Roll 50m","category":"Packaging","quantity":5,"reorder_level":15,"unit_price":650}'
post /api/movements '{"product_id":1,"movement_type":"OUT","quantity":40,"note":"Dispatch of customer orders"}'
echo "Seed complete -> $API/api/products/stats"
