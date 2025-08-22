#!/bin/bash
# Script to add a new web app

APP_NAME="$1"
APP_PORT="$2"
EXTERNAL_PORT="$3"

if [ -z "$APP_NAME" ] || [ -z "$APP_PORT" ] || [ -z "$EXTERNAL_PORT" ]; then
    echo "Usage: ./add-new-app.sh <app-name> <internal-port> <external-port>"
    echo "Example: ./add-new-app.sh myapp 8003 8100"
    exit 1
fi

INSTANCE_IP="18.136.211.185"

echo "🚀 Adding new app: $APP_NAME"

ssh -i compliant-one-key.pem ec2-user@$INSTANCE_IP << EOF
# Create app directory
mkdir -p ~/apps/$APP_NAME
cd ~/apps/$APP_NAME

# Create simple Flask app
cat > app.py << 'PYEOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>$APP_NAME</h1>
    <p>Running on port $APP_PORT</p>
    <p>Accessible via port $EXTERNAL_PORT</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=$APP_PORT)
PYEOF

# Create requirements
echo "flask==2.3.3" > requirements.txt

# Install and run
pip3 install --user -r requirements.txt
nohup python3 app.py > app.log 2>&1 &

# Add to Nginx config
sudo tee -a /etc/nginx/nginx.conf > /dev/null << 'NGINXADD'

    # $APP_NAME - Port $APP_PORT
    server {
        listen $EXTERNAL_PORT;
        server_name _;
        
        location / {
            proxy_pass http://localhost:$APP_PORT;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
NGINXADD

# Remove the extra closing brace and reload
sudo sed -i '\$d' /etc/nginx/nginx.conf
sudo systemctl reload nginx

echo "✅ $APP_NAME added successfully!"
echo "🌐 Access at: http://$INSTANCE_IP:$EXTERNAL_PORT"
EOF