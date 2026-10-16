# terraform/ — AWS infrastructure for StockPilot

Provisions the production-style environment that the Helm chart is deployed to:

```text
AWS (ap-south-1)
└── VPC 10.20.0.0/16
    ├── public subnets  10.20.101.0/24 (ap-south-1a), 10.20.102.0/24 (ap-south-1b)
    │     └── Internet Gateway, NAT Gateway, ELB tags
    ├── private subnets 10.20.1.0/24 (ap-south-1a), 10.20.2.0/24 (ap-south-1b)
    │     └── EKS managed node group "general" (t3.medium, 2-4 nodes)
    └── EKS control plane stockpilot-eks (Kubernetes 1.31)
          └── add-ons: coredns, kube-proxy, vpc-cni, pod-identity-agent, aws-ebs-csi-driver
```

| File | Content |
|------|---------|
| `versions.tf` | Terraform / provider constraints, provider + default tags, optional S3 backend |
| `variables.tf` | All tunables with defaults and validation |
| `locals.tf` | Naming + tag map |
| `vpc.tf` | `terraform-aws-modules/vpc` |
| `eks.tf` | `terraform-aws-modules/eks` + IRSA role for the EBS CSI driver |
| `outputs.tf` | Cluster name/endpoint, subnet IDs, kubeconfig command |
| `terraform.tfvars.example` | Sample variable file (no credentials) |
| `tests/plan.tftest.hcl` | Offline `terraform test` suite with a mocked AWS provider |

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # optional: tweak sizes/region
export AWS_PROFILE=<your-profile>              # credentials never go in files

terraform init
terraform fmt -check -recursive
terraform validate
terraform test                                  # offline, mocked provider - no AWS calls
terraform plan -out=tfplan
terraform apply tfplan

aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
kubectl get nodes
```

Tear everything down after the evaluation (an EKS control plane + NAT gateway costs money every hour):

```bash
terraform destroy
```

## Notes

* State: local by default. For teams, uncomment the S3 backend in `versions.tf`.
* Credentials: provided through the AWS CLI / environment, never committed. `terraform.tfvars` is git-ignored.
* PostgreSQL in the chart runs on an EBS-backed PVC (`gp2`). For production, swap it for Amazon RDS and set `postgres.enabled=false` in the Helm values.
