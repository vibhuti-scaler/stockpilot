"""Custom business metrics exported on /metrics next to the default HTTP metrics."""

from prometheus_client import Counter, Gauge

STOCK_MOVEMENTS = Counter(
    "stockpilot_stock_movements_total",
    "Number of stock movements recorded, by type (IN/OUT)",
    ["movement_type"],
)
PRODUCTS_TOTAL = Gauge("stockpilot_products_total", "Number of products in the catalogue")
LOW_STOCK_PRODUCTS = Gauge(
    "stockpilot_low_stock_products", "Products at or below their reorder level"
)
INVENTORY_VALUE = Gauge("stockpilot_inventory_value", "Total inventory value (quantity * price)")
