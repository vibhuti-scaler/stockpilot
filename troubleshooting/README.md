# Troubleshooting lab

Three deliberately broken manifests. Apply one, investigate with the commands shown, fix it, clean up.

| Scenario | File | Symptom | Root cause |
|----------|------|---------|------------|
| 1 | `broken-image.yaml` | Pod stuck in `ImagePullBackOff` | image tag does not exist |
| 2 | `broken-service.yaml` | Service has no endpoints, requests time out | selector does not match any Pod labels |
| 3 | `broken-probe.yaml` | Pod in `CrashLoopBackOff`, readiness never passes | wrong database host, migrations fail |

## Scenario 1 — ImagePullBackOff

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n stockpilot -l app=broken-image
kubectl describe pod -n stockpilot -l app=broken-image | tail -n 15
kubectl get events -n stockpilot --sort-by=.lastTimestamp | tail -n 5
```

`describe` shows `Failed to pull image ...` (unknown tag / repository not found) and the kubelet backs off with growing delays. Fix by pointing the Deployment at a tag that exists:

```bash
kubectl set image deployment/stockpilot-broken-image backend=stockpilot-backend:local -n stockpilot
kubectl delete -f troubleshooting/broken-image.yaml
```

## Scenario 2 — Service without endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get svc,endpoints -n stockpilot stockpilot-broken-service
kubectl get pods -n stockpilot --show-labels
```

`ENDPOINTS` is `<none>`: the selector asks for `component: backend-typo` but the Pods carry `component: backend`. A Service only forwards to Pods whose labels match its selector. Fix the selector (or patch it live) and the endpoints appear immediately:

```bash
kubectl patch svc stockpilot-broken-service -n stockpilot \
  -p '{"spec":{"selector":{"app.kubernetes.io/name":"stockpilot","app.kubernetes.io/component":"backend"}}}'
kubectl get endpoints -n stockpilot stockpilot-broken-service
kubectl delete -f troubleshooting/broken-service.yaml
```

## Scenario 3 — CrashLoopBackOff (bad database host)

```bash
kubectl apply -f troubleshooting/broken-probe.yaml
kubectl get pods -n stockpilot -l app=broken-db -w
kubectl logs -n stockpilot -l app=broken-db --tail=20
```

Logs show `could not translate host name "no-such-database"`. The entrypoint gives up after `DB_WAIT_ATTEMPTS` tries and the container exits, so Kubernetes restarts it with growing back-off. Fix the `DATABASE_URL` (point it at the `stockpilot-postgres` Service) or delete the lab Deployment:

```bash
kubectl delete -f troubleshooting/broken-probe.yaml
```

## General investigation order

1. `kubectl get pods -n <ns>` — what state is the Pod in?
2. `kubectl describe pod <pod>` — events: image pull, scheduling, probe failures.
3. `kubectl logs <pod> [--previous]` — application errors, crashes.
4. `kubectl get svc,endpoints` — does traffic have somewhere to go?
5. `kubectl get events --sort-by=.lastTimestamp` — the cluster's own timeline.
