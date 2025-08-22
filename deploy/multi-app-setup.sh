#!/bin/bash
# Multi-App Setup Script for EC2

INSTANCE_IP="18.136.211.185"

echo "🚀 Setting up multiple web apps on $INSTANCE_IP"

ssh -i compliant-one-key.pem ec2-user@$INSTANCE_IP << 'EOF'
# Install Nginx for reverse proxy
sudo yum install -y nginx
sudo systemctl enable nginx

# Create Nginx configuration for multiple apps
sudo tee /etc/nginx/nginx.conf > /dev/null << 'NGINXCONF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Main app (Compliant-One) - Default
    server {
        listen 80 default_server;
        server_name _;
        
        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # App 2 - Port 8001
    server {
        listen 8080;
        server_name _;
        
        location / {
            proxy_pass http://localhost:8001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # App 3 - Port 8002
    server {
        listen 8090;
        server_name _;
        
        location / {
            proxy_pass http://localhost:8002;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
NGINXCONF

# Start Nginx
sudo systemctl start nginx

# Create directory for additional apps
mkdir -p ~/apps

echo "✅ Multi-app setup complete!"
echo "📋 App ports:"
echo "   Main app (Compliant-One): http://$HOSTNAME (port 80)"
echo "   App 2: http://$HOSTNAME:8080 (internal port 8001)"
echo "   App 3: http://$HOSTNAME:8090 (internal port 8002)"
EOF