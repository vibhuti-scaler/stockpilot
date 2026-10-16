# monitoring/ — Prometheus + Grafana

| File | Purpose |
|------|---------|
| `kube-prometheus-stack-values.yaml` | Helm values for `prometheus-community/kube-prometheus-stack` (Prometheus Operator, Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics) |
| `grafana-dashboard-configmap.yaml` | ConfigMap labelled `grafana_dashboard=1`; the Grafana sidecar auto-imports it |
| `dashboards/stockpilot-overview.json` | The same dashboard as plain JSON (importable through the Grafana UI) |
| `stockpilot-alert-rules.yaml` | `PrometheusRule` with backend-down, error-rate, latency and reorder alerts |

The backend exposes Prometheus metrics on `/metrics` (via `prometheus-fastapi-instrumentator`) plus
custom business gauges/counters (`stockpilot_products_total`, `stockpilot_low_stock_products`,
`stockpilot_inventory_value`, `stockpilot_stock_movements_total`). The Helm chart creates a
`ServiceMonitor` (`monitoring.serviceMonitor.enabled=true`) so the Prometheus Operator scrapes every
backend Pod through the backend Service.

## Install

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml

kubectl apply -f monitoring/grafana-dashboard-configmap.yaml
kubectl apply -f monitoring/stockpilot-alert-rules.yaml
```

## Access

```bash
# Prometheus (targets page: Status -> Targets, look for serviceMonitor/stockpilot/stockpilot-backend)
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090

# Grafana (admin / stockpilot) - dashboard "StockPilot - Application Overview" in folder StockPilot
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80
```

Useful PromQL:

```promql
sum(rate(http_requests_total{job=~".*stockpilot-backend.*"}[1m]))                                   # request rate
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))              # p95 latency
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))             # error ratio
stockpilot_low_stock_products                                                                      # business metric
```
