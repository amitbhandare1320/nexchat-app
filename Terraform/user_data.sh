#!/bin/bash
# ─────────────────────────────────────────
# NexChat — EC2 User Data Script
# Runs automatically when EC2 starts
# ─────────────────────────────────────────

set -e
exec > /var/log/user_data.log 2>&1

echo "=== Starting NexChat setup ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose-plugin git curl

# Start Docker
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
apt-get install -y unzip
unzip awscliv2.zip
./aws/install

# Create app directory
mkdir -p /app
cd /app

# Create .env file
cat > /app/.env << ENVEOF
SECRET_KEY=${secret_key}
DB_USER=${db_username}
DB_PASSWORD=${db_password}
DB_HOST=${db_host}
DB_PORT=3306
DB_NAME=${db_name}
S3_BUCKET=${s3_bucket}
AWS_REGION=${aws_region}
ENVEOF

# Clone the repo (update with your repo URL)
git clone https://github.com/amitbhandare1320/nexchat-app.git /app/nexchat
cd /app/nexchat

# Copy .env
cp /app/.env .env

# Run with Docker Compose
docker compose up -d --build

echo "=== NexChat setup complete! ==="
echo "App running at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
