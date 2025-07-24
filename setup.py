#!/usr/bin/env python3
"""
Compliant.one Platform Initialization Script
Sets up the RegTech platform for first-time use
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_project_structure():
    """Create necessary project directories"""
    directories = [
        "core",
        "services/identity",
        "services/kyc", 
        "services/osint",
        "services/beneficial_ownership",
        "services/sanctions",
        "services/monitoring",
        "services/transactions",
        "services/reporting",
        "integrations",
        "api",
        "dashboard",
        "database",
        "config",
        "utils",
        "tests",
        "logs",
        "data",
        "docs"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if not directory.startswith(('logs', 'data', 'docs')):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Compliant.one package"""\n')
    
    print("✅ Project structure created successfully")

def create_env_file():
    """Create environment configuration file"""
    env_content = """# Compliant.one Platform Configuration

# Platform Settings
PLATFORM_NAME=Compliant.one
PLATFORM_VERSION=1.0.0
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql://localhost/compliant_one
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-change-this-in-production

# Service Configuration
IDENTITY_SERVICE_URL=http://localhost:8001
KYC_SERVICE_URL=http://localhost:8002
OSINT_SERVICE_URL=http://localhost:8003
SANCTIONS_SERVICE_URL=http://localhost:8004

# Third-Party API Keys (Replace with actual keys)
WORLD_CHECK_API_KEY=your-world-check-api-key
DOWJONES_API_KEY=your-dowjones-api-key
LEXISNEXIS_API_KEY=your-lexisnexis-api-key
ACUANT_API_KEY=your-acuant-api-key
JUMIO_API_KEY=your-jumio-api-key
ONFIDO_API_KEY=your-onfido-api-key

# Monitoring & Logging
LOG_LEVEL=INFO
MONITORING_ENABLED=true
SENTRY_DSN=your-sentry-dsn

# Security Settings
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key
MFA_ENABLED=true

# Email & Notifications
SENDGRID_API_KEY=your-sendgrid-api-key
ADMIN_EMAIL=admin@compliant.one
ALERT_EMAIL=alerts@compliant.one

# Compliance Settings
UBO_THRESHOLD=25.0
PEP_MONITORING=true
ADVERSE_MEDIA_MONITORING=true
DATA_RETENTION_DAYS=365
"""
    
    env_file = project_root / ".env"
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Environment configuration file created")
    else:
        print("ℹ️ Environment file already exists")

async def test_platform_initialization():
    """Test platform initialization"""
    try:
        # Import and initialize platform
        from core.platform import initialize_platform
        
        print("🚀 Initializing Compliant.one platform...")
        platform = await initialize_platform()
        
        # Test service status
        print("🔍 Checking service status...")
        status = await platform.get_service_status()
        
        print(f"✅ Platform initialized with {len(status)} services")
        
        # Test FATF coverage
        coverage = await platform.get_fatf_coverage()
        print(f"📋 FATF Coverage: {coverage['coverage_percentage']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform initialization failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    print("Run the following command to install dependencies:")
    print("pip install -r requirements.txt")
    print()

def setup_database():
    """Database setup instructions"""
    print("🗄️ Database Setup Instructions:")
    print()
    print("1. PostgreSQL Setup:")
    print("   - Install PostgreSQL")
    print("   - Create database: CREATE DATABASE compliant_one;")
    print("   - Update DATABASE_URL in .env file")
    print()
    print("2. Redis Setup:")
    print("   - Install Redis server")
    print("   - Start Redis: redis-server")
    print("   - Update REDIS_URL in .env file")
    print()

def show_next_steps():
    """Show next steps for platform deployment"""
    print("🎯 Next Steps:")
    print()
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Configure environment:")
    print("   - Edit .env file with your API keys and database URLs")
    print("   - Set up PostgreSQL and Redis databases")
    print()
    print("3. Start the platform:")
    print("   streamlit run dashboard/main.py")
    print()
    print("4. Access the dashboard:")
    print("   - Open http://localhost:8501 in your browser")
    print("   - Start with Platform Overview")
    print()
    print("5. API Documentation:")
    print("   - REST API will be available at http://localhost:8000/docs")
    print("   - Integration guides in docs/ directory")
    print()

async def main():
    """Main initialization function"""
    print("🛡️ Compliant.one Platform Setup")
    print("=" * 50)
    print()
    
    # Step 1: Create project structure
    print("📁 Step 1: Creating project structure...")
    setup_project_structure()
    print()
    
    # Step 2: Create environment file
    print("⚙️ Step 2: Creating configuration...")
    create_env_file()
    print()
    
    # Step 3: Show dependency installation
    print("📦 Step 3: Dependencies...")
    install_dependencies()
    print()
    
    # Step 4: Database setup
    print("🗄️ Step 4: Database setup...")
    setup_database()
    print()
    
    # Step 5: Test initialization (if dependencies available)
    print("🧪 Step 5: Testing platform...")
    try:
        success = await test_platform_initialization()
        if success:
            print("✅ Platform test successful!")
        else:
            print("⚠️ Platform test failed - install dependencies first")
    except ImportError:
        print("ℹ️ Dependencies not installed yet - skipping test")
    print()
    
    # Step 6: Show next steps
    print("🚀 Step 6: Deployment instructions...")
    show_next_steps()
    
    print("🎉 Compliant.one platform setup complete!")
    print("📚 Visit https://github.com/compliant-one/platform for documentation")

if __name__ == "__main__":
    asyncio.run(main())
