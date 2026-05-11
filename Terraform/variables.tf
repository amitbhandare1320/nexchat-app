# ─────────────────────────────────────────
# NexChat — Variables
# ─────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1" # Mumbai — closest to Bangalore
}

variable "project_name" {
  description = "Project name used for tagging"
  type        = string
  default     = "nexchat"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# ── VPC ──
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

# ── EC2 ──
variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro" # Free tier eligible
}

variable "key_pair_name" {
  description = "AWS Key Pair name for SSH access"
  type        = string
  default     = "nexchat-key"
}

# ── RDS ──
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro" # Free tier eligible
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nexchat"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "nexchat"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask secret key"
  type        = string
  sensitive   = true
  default     = "nexchat-production-secret-key-change-this"
}
