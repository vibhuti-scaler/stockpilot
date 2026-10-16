# k8s/ — bootstrap manifests

Everything application-related is packaged in the Helm chart under `helm/stockpilot`.
This folder only holds the cluster bootstrap objects that are applied once before Helm:

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates the `stockpilot` namespace (baseline Pod Security admission label) |

```bash
kubectl apply -f k8s/namespace.yaml
kubectl get ns stockpilot --show-labels
```
