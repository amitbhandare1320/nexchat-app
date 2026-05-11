# ─────────────────────────────────────────
# NexChat — EC2 Instance
# ─────────────────────────────────────────

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.ec2_instance_type
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  key_name               = var.key_pair_name
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  credit_specification {
    cpu_credits = "standard"
  }

  user_data = base64encode(templatefile("${path.module}/scripts/user_data.sh", {
    db_host     = aws_db_instance.mysql.address
    db_name     = var.db_name
    db_username = var.db_username
    db_password = var.db_password
    secret_key  = var.secret_key
    s3_bucket   = aws_s3_bucket.uploads.bucket
    aws_region  = var.aws_region
  }))

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = "${var.project_name}-app-server"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ── Elastic IP ──
resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-eip"
    Project = var.project_name
  }
}
