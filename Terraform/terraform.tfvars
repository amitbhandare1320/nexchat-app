# ─────────────────────────────────────────
# NexChat — Terraform Variables
# Copy this to terraform.tfvars and fill in
# ─────────────────────────────────────────

aws_region        = "ap-south-1"
project_name      = "nexchat"
environment       = "production"
ec2_instance_type = "t3.micro"
key_pair_name     = "nexchat-key"
db_instance_class = "db.t3.micro"
db_name           = "nexchat"
db_username       = "nexchat"
db_password       = "YourStrongPassword123!"
secret_key        = "your-super-secret-flask-key-change-this"
