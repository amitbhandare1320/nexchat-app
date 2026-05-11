#!/bin/bash
# ─────────────────────────────────────────
# Install Jenkins on Ubuntu EC2
# Run this on your EC2 server
# ─────────────────────────────────────────

set -e
echo "=== Installing Jenkins ==="

# Update system
sudo apt-get update -y

# Install Java (Jenkins needs Java 17+)
sudo apt-get install -y fontconfig openjdk-17-jre

# Verify Java
java -version

# Add Jenkins repo
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Jenkins
sudo apt-get update -y
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Add jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Get initial admin password
echo ""
echo "=== Jenkins installed! ==="
echo "Access Jenkins at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"
echo ""
echo "=== Initial Admin Password ==="
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
