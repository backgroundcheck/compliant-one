#!/bin/bash

# Compliant.one Platform Quick Start Script
echo "🛡️ Compliant.one Platform - Quick Start"
echo "========================================="
echo

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi
echo "✅ Python 3 is available"
echo

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo

# Install basic dependencies for setup
echo "📥 Installing basic dependencies..."
pip install --upgrade pip
pip install python-dotenv pathlib
echo "✅ Basic dependencies installed"
echo

# Run setup script
echo "🚀 Running platform setup..."
python3 setup.py
echo

# Install full requirements (commented out for demo)
echo "📦 To install full dependencies, run:"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo

# Database setup reminder
echo "🗄️ Database Setup Required:"
echo "   1. Install PostgreSQL and Redis"
echo "   2. Create database 'compliant_one'"
echo "   3. Update .env file with connection strings"
echo

# Start instructions
echo "🎯 To start the platform:"
echo "   1. source venv/bin/activate"
echo "   2. pip install streamlit pandas plotly"
echo "   3. streamlit run dashboard/main.py"
echo

echo "🎉 Quick start setup complete!"
echo "📚 Visit the dashboard at http://localhost:8501 once started"
