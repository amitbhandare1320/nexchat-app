#!/bin/bash
apt-get update -y
apt-get install -y docker.io docker-compose-plugin git curl unzip
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu
mkdir -p /app
cat > /app/.env << ENVEOF
SECRET_KEY=${secret_key}
DB_USER=${db_username}
DB_PASSWORD=${db_password}
DB_HOST=${db_host}
DB_PORT=3306
DB_NAME=${db_name}
ENVEOF
git clone https://github.com/amitbhandare1320/nexchat-app.git /app/nexchat
cd /app/nexchat
cp /app/.env .env
docker compose up -d --build