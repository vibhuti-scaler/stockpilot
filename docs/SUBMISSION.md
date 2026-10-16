# Submission checklist — rubric to evidence

Student: **Vibhuti Bhatnagar** · Roll no: **24bcs10288** · Repository: `https://github.com/vibhuti-scaler/stockpilot`

| Module | Requirement | Evidence in this repository |
|--------|-------------|-----------------------------|
| M1 | Backend `/health`, ≥4 REST endpoints, Alembic-managed PostgreSQL table, React UI, responsive | `backend/app/`, `backend/alembic/versions/` (2 migrations), `frontend/`, screenshots 01–10, 16 |
| M2 | pytest runs, ≥5 tests over ≥3 endpoints, test DB not prod DB, `pytest.ini`/`conftest.py` | `backend/tests/` (28 tests, in-memory SQLite via `conftest.py`), screenshot 11 |
| M3 | Public repo, meaningful commits, `.gitignore` | `.gitignore`; **after push:** repository URL + commit history screenshot |
| M4 | Dockerfiles build, frontend multi-stage, non-root, compose starts 3 services | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, screenshots 13, 14, 01 |
| M5 | Workflow on push to main, pytest job gates, frontend build, both images, GHCR, SHA tags | `.github/workflows/ci-cd.yml`; **after push:** Actions run URL + GHCR package screenshot |
| M6 | Trivy on both images, fail on HIGH/CRITICAL, explanation | workflow Trivy steps, screenshots 19–20, README §7 explanation |
| M7 | Valid HCL, init, plan, VPC ≥2 public subnets, EKS node group, destroy, tfvars.example | `terraform/`, screenshots 17–18; **after apply:** AWS console + destroy screenshots |
| M8 | namespace.yaml, chart with Chart.yaml/values/templates, helm install, ≥2 replicas, ClusterIP, Ingress `/`→frontend `/api`→backend, pods Running | `k8s/`, `helm/stockpilot/`, screenshots 21–24 |
| M9 | `/metrics`, Prometheus scraping, Grafana accessible, ≥1 live panel | `monitoring/`, screenshots 15, 25, 26 |
| M10 | README explaining the app, live demo | `README.md`, `docs/DEMO.md` |

## Items that can only be captured after pushing / applying

These need the repository to exist on GitHub and/or real AWS credentials, which are intentionally
not part of the code base:

1. **GitHub repository URL** — create `stockpilot` under `vibhuti-scaler`, then
   `git remote add origin git@github.com:vibhuti-scaler/stockpilot.git && git push -u origin main`.
2. **Commit history screenshot (≥10 commits)** — the staged work is intended to be committed in logical
   steps (application, tests, Docker, CI, Terraform, Helm, monitoring, troubleshooting, docs…).
3. **GitHub Actions run URL** (green) and **GHCR package page** with the SHA tags — produced by the
   first push to `main`.
4. **AWS console screenshots** of the VPC and EKS cluster in `ap-south-1`, `terraform plan` against real
   credentials and the **`terraform destroy`** completion output — run the commands in
   `terraform/README.md` with `AWS_PROFILE` set.
5. **`KUBE_CONFIG_DATA` secret** (base64 of the EKS kubeconfig) in the repository settings enables the
   automatic Helm deployment job.

Everything else (application, tests, images, Trivy, chart, kind deployment, Ingress, HPA, Prometheus,
Grafana, troubleshooting) is reproducible offline from this repository and is documented with
screenshots in `docs/screenshots/`.
