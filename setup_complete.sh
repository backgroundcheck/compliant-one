 #!/bin/bash

# Complete Setup Script for Compliant.one Platform with MongoDB and Authentication
# This script sets up the entire platform with user management and authentication

echo "🚀 Compliant.one Platform Setup with MongoDB & Authentication"
echo "=============================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✅]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️ ]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ️ ]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version)
        print_status "Python 3 found: $python_version"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
    else
        print_warning "pip3 not found. Installing..."
        sudo apt update
        sudo apt install -y python3-pip
    fi
}

# Create virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Install core dependencies
    pip install -r requirements.txt
    
    # Install additional authentication dependencies
    pip install \
        pymongo>=4.6.0 \
        motor>=3.3.0 \
        bcrypt>=4.1.0 \
        passlib>=1.7.0 \
        python-jose>=3.3.0 \
        streamlit-authenticator>=0.2.3
    
    print_status "Python dependencies installed"
}

# Setup MongoDB
setup_mongodb() {
    print_info "Setting up MongoDB..."
    
    # Check if MongoDB is already running
    if pgrep mongod > /dev/null; then
        print_status "MongoDB is already running"
        return
    fi
    
    # Check if Docker is available
    if command -v docker &> /dev/null; then
        print_info "Docker found. Setting up MongoDB container..."
        
        # Create MongoDB data directory
        mkdir -p ./mongodb_data
        
        # Stop existing container if it exists
        docker stop compliant-one-mongodb 2>/dev/null || true
        docker rm compliant-one-mongodb 2>/dev/null || true
        
        # Run MongoDB container
        docker run -d \
            --name compliant-one-mongodb \
            -p 27017:27017 \
            -v $(pwd)/mongodb_data:/data/db \
            -e MONGO_INITDB_ROOT_USERNAME=admin \
            -e MONGO_INITDB_ROOT_PASSWORD=compliant123 \
            --restart unless-stopped \
            mongo:7.0
        
        # Wait for MongoDB to start
        sleep 10
        
        print_status "MongoDB container started"
    else
        print_warning "Docker not found. Please install Docker or MongoDB manually."
        print_info "MongoDB installation guide: https://docs.mongodb.com/manual/installation/"
        
        read -p "Do you want to continue without MongoDB? (y/N): " continue_setup
        if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Test MongoDB connection
test_mongodb() {
    print_info "Testing MongoDB connection..."
    
    python3 -c "
import pymongo
import sys
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    sys.exit(1)
" || exit 1
}

# Initialize databases
init_databases() {
    print_info "Initializing databases..."
    
    # Initialize SQLite admin database
    python3 database/init_admin_db.py
    
    # Initialize MongoDB user system
    python3 -c "
import sys
sys.path.append('.')
from core.auth import initialize_user_system
if initialize_user_system():
    print('✅ User management system initialized')
else:
    print('❌ Failed to initialize user management system')
    sys.exit(1)
"
    
    print_status "Databases initialized"
}

# Create environment configuration
create_env_config() {
    print_info "Creating environment configuration..."
    
    # Generate JWT secret key
    jwt_secret=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Create .env file
    cat > .env << EOF
# Compliant.one Platform Configuration

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=compliant_one

# Authentication
JWT_SECRET_KEY=$jwt_secret
PASSWORD_MIN_LENGTH=8
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCK_DURATION=1800

# Features
ENABLE_REGISTRATION=true
ENABLE_PASSWORD_RESET=false
REQUIRE_EMAIL_VERIFICATION=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/compliant_one
REDIS_URL=redis://localhost:6379/0

# API Keys (configure these for production)
WORLD_CHECK_API_KEY=your-api-key
DOW_JONES_API_KEY=your-api-key
LEXISNEXIS_API_KEY=your-api-key

# Security
ENVIRONMENT=development
DEBUG=true
EOF
    
    print_status "Environment configuration created"
}

# Setup sample data
setup_sample_data() {
    print_info "Setting up sample data..."
    
    # Run the test script to create sample files
    chmod +x test_admin.sh
    ./test_admin.sh > /dev/null 2>&1
    
    print_status "Sample data created"
}

# Final verification
verify_setup() {
    print_info "Verifying complete setup..."
    
    # Test authentication system
    python3 -c "
import sys
sys.path.append('.')
try:
    from dashboard.auth_interface import auth_manager
    if auth_manager.user_manager:
        users = auth_manager.user_manager.get_all_users()
        print(f'✅ Authentication system: {len(users)} users found')
    else:
        print('❌ Authentication system not working')
        sys.exit(1)
except Exception as e:
    print(f'❌ Authentication test failed: {e}')
    sys.exit(1)
"
    
    # Test admin dashboard components
    python3 -c "
import sys
sys.path.append('.')
try:
    from dashboard.admin import DataSourceManager
    dsm = DataSourceManager()
    sources = dsm.get_data_sources()
    print(f'✅ Admin dashboard: {len(sources)} data sources configured')
except Exception as e:
    print(f'❌ Admin dashboard test failed: {e}')
    sys.exit(1)
"
    
    print_status "Setup verification completed"
}

# Display final instructions
show_instructions() {
    echo ""
    echo "🎉 Compliant.one Platform Setup Complete!"
    echo "========================================"
    echo ""
    echo "📋 What has been set up:"
    echo "  • MongoDB database for user management"
    echo "  • SQLite database for admin functions"
    echo "  • User authentication system with role-based access"
    echo "  • Admin dashboard for data source management"
    echo "  • Sample data sources and test files"
    echo ""
    echo "🚀 To start the platform:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Start the dashboard: streamlit run dashboard/main.py"
    echo "  3. Open browser to: http://localhost:8501"
    echo ""
    echo "🔐 Default login credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo "⚠️  Security Notes:"
    echo "  • Change the default admin password immediately"
    echo "  • Update API keys in .env file for production"
    echo "  • Configure proper MongoDB authentication for production"
    echo "  • Enable HTTPS for production deployment"
    echo ""
    echo "📁 Important directories:"
    echo "  • data/uploads/     - File upload directory"
    echo "  • data/processed/   - Processed files"
    echo "  • database/         - SQLite databases"
    echo "  • logs/             - Application logs"
    echo "  • mongodb_data/     - MongoDB data (if using Docker)"
    echo ""
    echo "🔧 Management commands:"
    echo "  • MongoDB logs: docker logs compliant-one-mongodb"
    echo "  • MongoDB shell: mongosh mongodb://localhost:27017"
    echo "  • Restart platform: streamlit run dashboard/main.py"
    echo ""
    echo "📚 Documentation:"
    echo "  • Admin Guide: docs/ADMIN_DASHBOARD.md"
    echo "  • Deployment: DEPLOYMENT.md"
    echo ""
}

# Main setup process
main() {
    echo "Starting Compliant.one Platform setup..."
    echo ""
    
    # Pre-flight checks
    check_python
    check_pip
    
    # Setup Python environment
    setup_venv
    install_dependencies
    
    # Setup databases
    setup_mongodb
    test_mongodb
    init_databases
    
    # Configuration
    create_env_config
    setup_sample_data
    
    # Verification
    verify_setup
    
    # Final instructions
    show_instructions
    
    print_status "Setup completed successfully!"
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted. Cleaning up...${NC}"; exit 1' INT

# Run main setup
main

echo ""
echo "✨ Ready to launch Compliant.one Platform with MongoDB & Authentication!"
echo "Run: streamlit run dashboard/main.py"
