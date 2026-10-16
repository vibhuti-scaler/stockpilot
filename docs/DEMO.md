# StockPilot — live demo script

**Presenter:** Vibhuti Bhatnagar (24bcs10288) · Duration ≈ 15 minutes

Prerequisites: `docker compose up -d` running locally, kind (or EKS) cluster deployed with
`scripts/kind-up.sh`, Prometheus and Grafana port-forwarded, GitHub repository open in a browser tab.

| # | Step | What to show | Command / URL |
|---|------|--------------|---------------|
| 1 | Application | Dashboard, create a product, issue stock, watch KPIs and ledger update | http://localhost:3000 |
| 2 | API | Swagger: `POST /api/products`, `GET /api/products/{id}`, `PUT`, `DELETE` | http://localhost:8000/docs |
| 3 | Database | Tables created by Alembic, the product just created | `docker compose exec postgres psql -U stockpilot -c '\dt' -c 'select sku,name,quantity from products;'` |
| 4 | Git | Make a small change (e.g. dashboard subtitle), commit with a meaningful message | `git commit -am "feat(frontend): update overview subtitle"` |
| 5 | CI | Push, open the Actions run, show the `test` job (ruff, pytest, npm build) | `git push` → GitHub Actions tab |
| 6 | Docker | The two images and their non-root users | `docker images \| grep stockpilot` · `docker compose exec backend id` |
| 7 | Security | Trivy step output in the `build-scan-push` job (0 HIGH/CRITICAL) | Actions log · or `trivy image stockpilot-backend:local` |
| 8 | Registry | GHCR packages with SHA tags | https://github.com/vibhuti-scaler?tab=packages |
| 9 | Terraform | VPC/EKS code, `terraform test`, (if applied) AWS console VPC + EKS | `cd terraform && terraform test` |
| 10 | Kubernetes | Pods and Services in the namespace | `kubectl get pods,svc -n stockpilot` |
| 11 | Helm | Release list, `helm test`, a `helm upgrade` with the new SHA, `helm rollback` | `helm list -n stockpilot` · `helm history stockpilot -n stockpilot` |
| 12 | Ingress | Application through the Ingress hostname; `/api/products/stats` on the same host | http://stockpilot.local/ (or `stockpilot.127.0.0.1.nip.io`) |
| 13 | HPA | Run the load test, watch replicas grow | `./scripts/load-test.sh 20 120` · `kubectl get hpa -n stockpilot -w` |
| 14 | Monitoring | Prometheus Targets page (`UP`), Grafana dashboard reacting to the load | :9090/targets · :3001 |
| 15 | Failure simulation | Apply `broken-service.yaml`, show empty endpoints, fix the selector live | see `troubleshooting/README.md` |

Closing: walk through the pipeline diagram in the README — every running Pod's image tag equals the
Git commit SHA that produced it, which is the traceability story of the whole project.
