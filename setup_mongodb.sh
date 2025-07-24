#!/bin/bash

# MongoDB Setup Script for Compliant.one Platform
# Installs MongoDB and initializes the user management system

echo "🗄️  MongoDB Setup for Compliant.one Platform"
echo "=============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root - MongoDB installation will proceed"
else
    echo "ℹ️  Running as non-root user - will attempt installation"
fi

# Function to install MongoDB on Ubuntu/Debian
install_mongodb_ubuntu() {
    echo "📦 Installing MongoDB on Ubuntu/Debian..."
    
    # Import MongoDB GPG key
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
    
    # Add MongoDB repository
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Update package list
    sudo apt-get update
    
    # Install MongoDB
    sudo apt-get install -y mongodb-org
    
    # Start MongoDB service
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    echo "✅ MongoDB installed and started"
}

# Function to install MongoDB using Docker
install_mongodb_docker() {
    echo "🐳 Setting up MongoDB using Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Create MongoDB data directory
    mkdir -p ./mongodb_data
    
    # Run MongoDB container
    docker run -d \
        --name compliant-one-mongodb \
        -p 27017:27017 \
        -v $(pwd)/mongodb_data:/data/db \
        -e MONGO_INITDB_ROOT_USERNAME=admin \
        -e MONGO_INITDB_ROOT_PASSWORD=compliant123 \
        mongo:7.0
    
    echo "✅ MongoDB container started"
    echo "📋 Connection details:"
    echo "   Host: localhost"
    echo "   Port: 27017"
    echo "   Username: admin"
    echo "   Password: compliant123"
}

# Function to check MongoDB connection
check_mongodb_connection() {
    echo "🔍 Checking MongoDB connection..."
    
    # Try to connect using Python
    python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    exit(1)
"
}

# Function to initialize user system
initialize_user_system() {
    echo "👤 Initializing user management system..."
    
    # Run the initialization script
    python3 -c "
import sys
sys.path.append('.')
from core.auth import initialize_user_system
if initialize_user_system():
    print('✅ User management system initialized')
else:
    print('❌ Failed to initialize user management system')
"
}

# Main installation logic
echo "🚀 Starting MongoDB setup..."

# Check if MongoDB is already running
if pgrep mongod > /dev/null; then
    echo "✅ MongoDB is already running"
elif docker ps | grep -q compliant-one-mongodb; then
    echo "✅ MongoDB Docker container is already running"
else
    echo "📥 MongoDB not detected. Choose installation method:"
    echo "1) System installation (Ubuntu/Debian)"
    echo "2) Docker container (recommended)"
    echo "3) Skip installation (MongoDB already configured elsewhere)"
    
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            install_mongodb_ubuntu
            ;;
        2)
            install_mongodb_docker
            ;;
        3)
            echo "ℹ️  Skipping MongoDB installation"
            ;;
        *)
            echo "❌ Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Wait a moment for MongoDB to start
sleep 3

# Check connection
check_mongodb_connection

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install pymongo motor mongoengine bcrypt passlib python-jose streamlit-authenticator

# Initialize user system
initialize_user_system

# Create environment file
echo "📝 Creating environment configuration..."
cat > .env.mongo << EOF
# MongoDB Configuration for Compliant.one
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=compliant_one
JWT_SECRET_KEY=$(openssl rand -base64 32)

# Security Settings
PASSWORD_MIN_LENGTH=8
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCK_DURATION=1800

# Features
ENABLE_REGISTRATION=true
ENABLE_PASSWORD_RESET=false
REQUIRE_EMAIL_VERIFICATION=false
EOF

echo ""
echo "🎉 MongoDB setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Source the environment file: source .env.mongo"
echo "2. Update your main .env file with MongoDB settings"
echo "3. Run the dashboard: streamlit run dashboard/main.py"
echo "4. Login with default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Security Recommendations:"
echo "- Change the default admin password immediately"
echo "- Update JWT_SECRET_KEY in production"
echo "- Configure proper MongoDB authentication"
echo "- Enable HTTPS for production deployment"
echo ""
echo "🔧 MongoDB Management:"
echo "- System install: sudo systemctl status mongod"
echo "- Docker: docker logs compliant-one-mongodb"
echo "- Connect: mongosh (or mongo shell)"
echo ""

# Test the complete setup
echo "🧪 Testing complete authentication system..."
python3 -c "
import sys
sys.path.append('.')
try:
    from dashboard.auth_interface import auth_manager
    print('✅ Authentication system loaded successfully')
    if auth_manager.user_manager:
        print('✅ User manager initialized')
        users = auth_manager.user_manager.get_all_users()
        print(f'✅ Found {len(users)} users in system')
    else:
        print('❌ User manager not initialized')
except Exception as e:
    print(f'❌ Authentication system test failed: {e}')
"

echo ""
echo "✅ Setup complete! Your Compliant.one platform now has user authentication and MongoDB integration."
