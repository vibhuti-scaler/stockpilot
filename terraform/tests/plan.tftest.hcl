# Offline unit tests for the infrastructure code.
# `terraform test` runs these with a mocked AWS provider, so they need no credentials
# and create nothing. They verify that the configuration plans and that the network
# layout matches the capstone requirements (>= 2 public subnets, EKS node group, etc.).

mock_provider "aws" {
  # The mocked provider returns random strings for unknown attributes; IAM resources
  # validate policy documents as JSON, so give those data sources a valid default.
  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }
  mock_data "aws_partition" {
    defaults = {
      partition  = "aws"
      dns_suffix = "amazonaws.com"
    }
  }
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:user/terraform"
      user_id    = "AIDAEXAMPLE"
    }
  }
  mock_data "aws_iam_session_context" {
    defaults = {
      issuer_arn = "arn:aws:iam::123456789012:role/terraform"
    }
  }
}

variables {
  aws_region           = "ap-south-1"
  environment          = "test"
  availability_zones   = ["ap-south-1a", "ap-south-1b"]
  public_subnet_cidrs  = ["10.20.101.0/24", "10.20.102.0/24"]
  private_subnet_cidrs = ["10.20.1.0/24", "10.20.2.0/24"]
}

run "vpc_has_two_public_and_two_private_subnets" {
  command = plan

  assert {
    condition     = length(module.vpc.public_subnets) == 2
    error_message = "Expected exactly two public subnets."
  }

  assert {
    condition     = length(module.vpc.private_subnets) == 2
    error_message = "Expected exactly two private subnets."
  }

  assert {
    condition     = length(module.vpc.natgw_ids) == 1
    error_message = "Dev environment should use a single NAT gateway to limit cost."
  }
}

run "eks_cluster_is_configured" {
  command = plan

  assert {
    condition     = module.eks.cluster_name == "stockpilot-eks"
    error_message = "Cluster name should default to stockpilot-eks."
  }

  assert {
    condition     = contains(keys(module.eks.eks_managed_node_groups), "general")
    error_message = "A managed node group named 'general' must exist."
  }

  assert {
    condition     = output.configure_kubectl == "aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks"
    error_message = "kubectl helper output is wrong."
  }
}

run "rejects_single_availability_zone" {
  command = plan

  variables {
    availability_zones   = ["ap-south-1a"]
    public_subnet_cidrs  = ["10.20.101.0/24"]
    private_subnet_cidrs = ["10.20.1.0/24"]
  }

  expect_failures = [var.availability_zones]
}
