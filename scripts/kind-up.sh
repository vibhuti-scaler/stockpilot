#!/usr/bin/env bash
# Creates a local kind cluster with ingress-nginx, metrics-server and kube-prometheus-stack,
# builds the StockPilot images, loads them into kind and deploys the Helm chart.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER="${CLUSTER:-stockpilot}"
NS=stockpilot

echo "==> Creating kind cluster '$CLUSTER'"
kind get clusters | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --config scripts/kind-config.yaml

echo "==> Installing ingress-nginx"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait -n ingress-nginx --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=180s

echo "==> Installing metrics-server (required by the HPA)"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

echo "==> Installing kube-prometheus-stack (Prometheus + Grafana)"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml --wait --timeout 10m
kubectl apply -f monitoring/grafana-dashboard-configmap.yaml
kubectl apply -f monitoring/stockpilot-alert-rules.yaml

echo "==> Building and loading application images"
docker build -t stockpilot-backend:local ./backend
docker build -t stockpilot-frontend:local ./frontend
kind load docker-image stockpilot-backend:local stockpilot-frontend:local --name "$CLUSTER"

echo "==> Deploying StockPilot"
kubectl apply -f k8s/namespace.yaml
helm upgrade --install stockpilot ./helm/stockpilot -n "$NS" -f helm/stockpilot/values-kind.yaml --wait --timeout 5m
kubectl get pods,svc,ingress,hpa -n "$NS"

echo
echo "App:        http://stockpilot.127.0.0.1.nip.io/"
echo "Swagger:    http://stockpilot.127.0.0.1.nip.io/docs"
echo "Grafana:    kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80   (admin / stockpilot)"
echo "Prometheus: kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090"
