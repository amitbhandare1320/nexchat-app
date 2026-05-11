# ─────────────────────────────────────────
# NexChat — Outputs
# ─────────────────────────────────────────

output "alb_dns_name" {
  description = "Load Balancer DNS name — use this as your app URL"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "NexChat app URL via Load Balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "app_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_eip.app.public_ip
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.mysql.address
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for uploads"
  value       = aws_s3_bucket.uploads.bucket
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker images"
  value       = aws_ecr_repository.app.repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_eip.app.public_ip}"
}
