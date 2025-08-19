#!/bin/bash
# Simple EC2 User Data for Compliant-One

# Update system
yum update -y
yum install -y docker git python3 python3-pip

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Upload and setup full application
cd /home/ec2-user

# Create application directory
mkdir -p compliant-one
cd compliant-one

# Clone repository
git clone https://github.com/backgroundcheck/compliant-one.git repo || true
cd repo

# Use production compose if available
COMPOSE_FILE="docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

# Create .env from example if missing
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
fi

# Ensure data directories exist for bind mounts
mkdir -p logs data deploy/ssl deploy/nginx || true

# Set permissions
chown -R ec2-user:ec2-user /home/ec2-user/compliant-one
cd /home/ec2-user/compliant-one/repo

# Build and start application (api and redis services only; nginx optional)
/usr/local/bin/docker-compose -f "$COMPOSE_FILE" up -d --build api redis || /usr/local/bin/docker-compose up -d --build

# Create startup service
cat > /etc/systemd/system/compliant-one.service << 'EOF'
[Unit]
Description=Compliant-One Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/compliant-one
ExecStart=/usr/local/bin/docker-compose -f %h/compliant-one/repo/$COMPOSE_FILE up -d
ExecStop=/usr/local/bin/docker-compose -f %h/compliant-one/repo/$COMPOSE_FILE down
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

systemctl enable compliant-one
systemctl start compliant-one

# Log deployment
echo "Compliant-One deployed successfully at $(date)" >> /var/log/deployment.log