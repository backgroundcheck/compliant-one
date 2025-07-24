#!/bin/bash

# Compliant.one Admin Dashboard Test Script
# Tests the admin functionality and data processing capabilities

echo "🔧 Compliant.one Admin Dashboard Test"
echo "======================================"

# Check if admin database exists
if [ -f "database/data_sources.db" ]; then
    echo "✅ Admin database found"
else
    echo "❌ Admin database not found. Running initialization..."
    python3 database/init_admin_db.py
fi

# Check required directories
echo "📁 Checking directory structure..."
directories=("data/uploads" "data/processed" "logs" "database")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing - creating..."
        mkdir -p "$dir"
    fi
done

# Test file creation for demo
echo "📄 Creating sample test files..."

# Create sample CSV
cat > data/uploads/sample_sanctions.csv << EOF
Name,Type,Country,Date_Listed,Reason
John Doe,Individual,US,2023-01-15,Money Laundering
ABC Corporation,Entity,UK,2023-02-20,Terrorism Financing
Jane Smith,Individual,FR,2023-03-10,Sanctions Violation
XYZ Holdings,Entity,DE,2023-04-05,Proliferation Financing
EOF

# Create sample XML
cat > data/uploads/sample_pep.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<pep_list>
    <person>
        <name>Political Figure One</name>
        <position>Minister of Finance</position>
        <country>CountryA</country>
        <risk_level>High</risk_level>
    </person>
    <person>
        <name>Political Figure Two</name>
        <position>Central Bank Governor</position>
        <country>CountryB</country>
        <risk_level>Medium</risk_level>
    </person>
</pep_list>
EOF

# Create sample JSON
cat > data/uploads/sample_beneficial_ownership.json << EOF
{
    "companies": [
        {
            "name": "Example Corp Ltd",
            "registration_number": "12345678",
            "beneficial_owners": [
                {
                    "name": "Beneficial Owner One",
                    "ownership_percentage": 75.5,
                    "type": "Individual"
                },
                {
                    "name": "Shell Company ABC",
                    "ownership_percentage": 24.5,
                    "type": "Corporate"
                }
            ]
        }
    ]
}
EOF

# Create sample text file
cat > data/uploads/sample_adverse_media.txt << EOF
Investigation Report - Suspicious Activities

The following entities have been identified in connection with money laundering activities:
- Company XYZ Limited (Registration: ABC123)
- Individual: Suspicious Person (DOB: 1980-01-01)

This report contains allegations of:
- Money laundering through offshore accounts
- Terrorism financing connections
- Sanctions violations
- Corruption in government contracts

Contact: investigation@agency.gov
Phone: +1-555-0123
EOF

echo "✅ Sample files created in data/uploads/"
echo ""

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
python3 -c "
import sys
required_packages = [
    'sqlite3',
    'pathlib', 
    'json',
    'xml.etree.ElementTree',
    're',
    'csv'
]

missing = []
for package in required_packages:
    try:
        __import__(package)
        print(f'✅ {package}')
    except ImportError:
        print(f'❌ {package}')
        missing.append(package)

optional_packages = {
    'pandas': 'For CSV/Excel processing',
    'openpyxl': 'For Excel file support',
    'docx': 'For Word document support', 
    'bs4': 'For HTML processing',
    'PyPDF2': 'For PDF processing'
}

print('\n📦 Optional packages (install for full functionality):')
for package, description in optional_packages.items():
    try:
        __import__(package)
        print(f'✅ {package} - {description}')
    except ImportError:
        print(f'❌ {package} - {description}')
"

echo ""
echo "🚀 Admin Dashboard Setup Complete!"
echo ""
echo "To access the admin dashboard:"
echo "1. Install required dependencies: pip install -r requirements.txt"
echo "2. Run the dashboard: streamlit run dashboard/main.py"
echo "3. Navigate to '🔧 Admin Dashboard' in the sidebar"
echo ""
echo "Sample files available for testing:"
echo "- data/uploads/sample_sanctions.csv"
echo "- data/uploads/sample_pep.xml"
echo "- data/uploads/sample_beneficial_ownership.json"
echo "- data/uploads/sample_adverse_media.txt"
echo ""
echo "Database location: database/data_sources.db"
echo "Upload folder: data/uploads/"
echo "Processed folder: data/processed/"
