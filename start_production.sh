#!/bin/bash

# Production Startup Script for Threat Intelligence System
# This script performs pre-flight checks and starts the system safely

set -e  # Exit on any error

echo "=== Compliant.one Threat Intelligence System ==="
echo "Production Startup Script"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then edit .env file with your actual API keys:"
    echo "  - HIBP_API_KEY"
    echo "  - VIRUSTOTAL_API_KEY"
    echo "  - SHODAN_API_KEY"
    exit 1
fi

print_status ".env file found"

# Source environment variables
source .env

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher required. Found: $PYTHON_VERSION"
    exit 1
fi

print_status "Python version: $PYTHON_VERSION"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Virtual environment activated: $(basename $VIRTUAL_ENV)"
else
    print_warning "No virtual environment detected. Consider using one for isolation."
fi

# Check required directories
echo ""
echo "Checking directory structure..."

REQUIRED_DIRS=("data" "logs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        print_warning "Creating missing directory: $dir"
        mkdir -p "$dir"
    else
        print_status "Directory exists: $dir"
    fi
done

# Check write permissions
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -w "$dir" ]; then
        print_error "No write permission for directory: $dir"
        exit 1
    fi
done

print_status "Directory permissions OK"

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."

REQUIRED_PACKAGES=("fastapi" "uvicorn" "aiohttp" "sqlite3" "pandas" "streamlit")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    print_error "Missing Python packages: ${MISSING_PACKAGES[*]}"
    echo ""
    echo "Install missing packages with:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

print_status "All required Python packages available"

# Check API key configuration
echo ""
echo "Checking API key configuration..."

API_KEYS_CONFIGURED=0
TOTAL_API_KEYS=3

if [ -n "$HIBP_API_KEY" ] && [ "$HIBP_API_KEY" != "your_hibp_api_key_here" ]; then
    print_status "HIBP API key configured"
    ((API_KEYS_CONFIGURED++))
else
    print_warning "HIBP API key not configured"
fi

if [ -n "$VIRUSTOTAL_API_KEY" ] && [ "$VIRUSTOTAL_API_KEY" != "your_virustotal_api_key_here" ]; then
    print_status "VirusTotal API key configured"
    ((API_KEYS_CONFIGURED++))
else
    print_warning "VirusTotal API key not configured"
fi

if [ -n "$SHODAN_API_KEY" ] && [ "$SHODAN_API_KEY" != "your_shodan_api_key_here" ]; then
    print_status "Shodan API key configured"
    ((API_KEYS_CONFIGURED++))
else
    print_warning "Shodan API key not configured"
fi

if [ $API_KEYS_CONFIGURED -eq 0 ]; then
    print_error "No API keys configured! The system will have limited functionality."
    echo ""
    echo "Please configure at least one API key in the .env file:"
    echo "  - HIBP_API_KEY (Have I Been Pwned)"
    echo "  - VIRUSTOTAL_API_KEY (VirusTotal)"
    echo "  - SHODAN_API_KEY (Shodan)"
    echo ""
    echo "See docs/THREAT_INTELLIGENCE_SETUP.md for details"
    
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_status "$API_KEYS_CONFIGURED/$TOTAL_API_KEYS API keys configured"
fi

# Check network connectivity
echo ""
echo "Checking network connectivity..."

# Test connectivity to key services
CONNECTIVITY_TESTS=(
    "google.com:443"
    "api.pwnedpasswords.com:443"
    "www.virustotal.com:443"
    "api.shodan.io:443"
)

for test in "${CONNECTIVITY_TESTS[@]}"; do
    host=$(echo $test | cut -d':' -f1)
    port=$(echo $test | cut -d':' -f2)
    
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        print_status "Connectivity to $host:$port OK"
    else
        print_warning "Cannot connect to $host:$port"
    fi
done

# Check if port is available
API_PORT=${API_PORT:-8000}
if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_error "Port $API_PORT is already in use"
    echo "Another process is using the API port. Stop it or change API_PORT in .env"
    exit 1
else
    print_status "Port $API_PORT is available"
fi

# Security checks
echo ""
echo "Performing security checks..."

# Check if default secret key is being used
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-in-production" ]; then
    print_error "Default or missing SECRET_KEY detected!"
    echo "Generate a secure secret key:"
    echo '  python3 -c "import secrets; print(secrets.token_urlsafe(32))"'
    echo "Then add it to your .env file"
    exit 1
fi

print_status "Secret key configured"

# Check environment setting
ENVIRONMENT=${ENVIRONMENT:-development}
if [ "$ENVIRONMENT" = "production" ]; then
    print_status "Environment: Production"
    
    # Additional production checks
    if [ "$API_DEBUG" = "true" ]; then
        print_warning "Debug mode enabled in production!"
    fi
    
    if [ "$LOG_LEVEL" = "DEBUG" ]; then
        print_warning "Debug logging enabled in production!"
    fi
else
    print_warning "Environment: $ENVIRONMENT (consider setting ENVIRONMENT=production)"
fi

# Database initialization
echo ""
echo "Initializing database..."

# The database will be created automatically by the service
if [ -f "${THREAT_DB_PATH:-./data/threat_intelligence.db}" ]; then
    print_status "Database file exists"
else
    print_status "Database will be created on first run"
fi

# Final pre-flight check
echo ""
echo "=========================================="
echo "Pre-flight checks completed!"
echo ""

if [ $API_KEYS_CONFIGURED -gt 0 ]; then
    print_status "System ready to start with $API_KEYS_CONFIGURED API sources"
else
    print_warning "System will start with limited functionality (no API keys)"
fi

echo ""
echo "Starting services..."
echo "=========================================="

# Start the API server
echo "Starting API server on port $API_PORT..."
echo "API will be available at: http://${API_HOST:-localhost}:$API_PORT"
echo "Admin panel will be available at: http://${API_HOST:-localhost}:$API_PORT/threat-intel/admin"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Export environment variables for uvicorn
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-8000}

# Start with proper error handling
if ! python3 -m uvicorn api.main:app --host $API_HOST --port $API_PORT --reload; then
    print_error "Failed to start API server"
    echo ""
    echo "Check the logs for details:"
    echo "  tail -f logs/threat_intelligence.log"
    exit 1
fi
