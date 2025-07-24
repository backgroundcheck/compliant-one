#!/bin/bash
# Quick Start Script for Compliant.one Platform
# Sets up login area and starts the platform

echo "🚀 Starting Compliant.one Platform..."
echo "=================================================="

# Change to project directory
cd /root/compliant-one

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install core dependencies for login system
echo "📥 Installing core dependencies..."
pip install -q streamlit pandas pymongo bcrypt python-jose passlib streamlit-authenticator plotly requests sqlalchemy PyPDF2 PyMuPDF beautifulsoup4 nltk spacy tqdm

# Check MongoDB status
echo "🔍 Checking MongoDB status..."
if ! systemctl is-active --quiet mongod; then
    echo "🚨 MongoDB is not running. Starting MongoDB..."
    sudo systemctl start mongod
    sleep 3
fi

if systemctl is-active --quiet mongod; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB failed to start. Please check MongoDB installation."
    exit 1
fi

# Set up admin user if not exists
echo "👤 Setting up admin user..."
python3 -c "
import sys
sys.path.append('/root/compliant-one')

try:
    from core.auth import MongoDBConnection, UserManager
    
    # Initialize MongoDB connection
    mongo_conn = MongoDBConnection()
    if mongo_conn.connect():
        # Initialize UserManager with database
        um = UserManager(mongo_conn.db)
        
        # Try to authenticate existing admin
        result = um.authenticate_user('admin', 'SecurePass123!')
        
        if result['success']:
            print('✅ Admin user already exists and is ready')
        else:
            # Create admin user
            print('🔧 Creating admin user...')
            success = um.create_user('admin', 'admin@company.com', 'SecurePass123!', 'admin')
            if success:
                print('✅ Admin user created successfully')
            else:
                print('❌ Failed to create admin user')
    else:
        print('❌ Failed to connect to MongoDB')
                
except Exception as e:
    print(f'⚠️  Authentication setup will complete during first login: {str(e)}')
"

# Initialize database tables
echo "🗄️  Initializing database tables..."
python3 -c "
import sys
sys.path.append('/root/compliant-one')

try:
    from dashboard.admin import DataSourceManager
    dsm = DataSourceManager()
    print('✅ Database tables initialized')
except Exception as e:
    print(f'⚠️  Database will initialize on first access: {str(e)}')
"

echo ""
echo "🎉 Compliant.one Platform is ready!"
echo "=================================================="
echo ""
echo "🔐 Login Information:"
echo "   👤 Username: admin"
echo "   🔑 Password: SecurePass123!"
echo "   📧 Email: admin@company.com"
echo ""
echo "🚀 Starting Streamlit dashboard..."
echo "   📍 URL: http://localhost:8501"
echo ""
echo "⚠️  SECURITY NOTE: Change the default password immediately after first login!"
echo ""

# Start Streamlit
streamlit run dashboard/main.py --server.port 8501 --server.address 0.0.0.0
