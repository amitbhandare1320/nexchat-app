# ─────────────────────────────────────────
# NexChat — S3 Bucket for uploads
# ─────────────────────────────────────────

resource "aws_s3_bucket" "uploads" {
  bucket = "${var.project_name}-uploads-${random_string.suffix.result}"

  tags = {
    Name        = "${var.project_name}-uploads"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "uploads" {
  depends_on = [
    aws_s3_bucket_ownership_controls.uploads,
    aws_s3_bucket_public_access_block.uploads,
  ]
  bucket = aws_s3_bucket.uploads.id
  acl    = "public-read"
}

# ── ECR Repository for Docker images ──
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "${var.project_name}-ecr"
    Project = var.project_name
  }
}
