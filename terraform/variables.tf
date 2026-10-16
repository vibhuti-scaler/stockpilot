variable "aws_region" {
  description = "AWS region where the VPC and EKS cluster are created"
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Project name used as a prefix for every resource"
  type        = string
  default     = "stockpilot"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner tag applied to every resource"
  type        = string
  default     = "Vibhuti Bhatnagar (24bcs10288)"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to spread subnets across (at least two)"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least two availability zones are required for EKS."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets (load balancers, NAT gateway)"
  type        = list(string)
  default     = ["10.20.101.0/24", "10.20.102.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets (EKS worker nodes)"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "single_nat_gateway" {
  description = "Use one NAT gateway for all private subnets (cheaper, fine for dev)"
  type        = bool
  default     = true
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "stockpilot-eks"
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS control plane"
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "EC2 instance types for the managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 4
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDRs allowed to reach the public EKS API endpoint (restrict to your IP in production)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
