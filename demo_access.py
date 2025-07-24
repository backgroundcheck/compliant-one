#!/usr/bin/env python3
"""
Simple Demo Access Script for Compliant-One Platform
Bypasses authentication for quick access to CSV import functionality

Usage:
    python3 demo_access.py
"""

import os
import sys
from pathlib import Path
import subprocess
import time

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def print_banner():
    """Print demo access banner"""
    print("=" * 80)
    print("🚀 COMPLIANT-ONE DEMO ACCESS")
    print("=" * 80)
    print("Quick access to platform features without authentication")
    print("=" * 80)
    print()

def check_platform_status():
    """Check if platform is running"""
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_platform():
    """Start the platform"""
    print("🚀 Starting Compliant-One Platform...")
    
    # Check if start script exists
    start_script = project_root / "start_platform.sh"
    if start_script.exists():
        try:
            # Make script executable
            os.chmod(start_script, 0o755)
            
            # Start platform in background
            process = subprocess.Popen(
                ["bash", str(start_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_root)
            )
            
            print("⏳ Platform starting... (this may take 30-60 seconds)")
            print("💡 You can access the platform at: http://localhost:8501")
            
            # Wait a bit for startup
            for i in range(10, 0, -1):
                print(f"⏰ Waiting {i} seconds for platform to start...", end="\r")
                time.sleep(1)
            print()
            
            # Check if platform is running
            if check_platform_status():
                print("✅ Platform is running!")
                return True
            else:
                print("⏳ Platform is still starting up...")
                return True
                
        except Exception as e:
            print(f"❌ Error starting platform: {e}")
            return False
    else:
        print("❌ start_platform.sh not found")
        return False

def show_access_info():
    """Show access information"""
    print("🔐 PLATFORM ACCESS INFORMATION")
    print("-" * 40)
    
    print("📍 Platform URL: http://localhost:8501")
    print()
    
    print("🔑 Login Credentials:")
    print("   • Username: admin")
    print("   • Password: admin123")
    print()
    
    print("📥 CSV Import Access:")
    print("   1. Login to the platform")
    print("   2. Navigate to: Admin Panel → Web Crawler")
    print("   3. Click: 📊 Compliance Analysis tab")
    print("   4. Click: 📥 Import Sanctions Data subtab")
    print("   5. Upload your CSV files")
    print()
    
    print("💻 Command Line Import:")
    print("   python3 import_sanctions_csv.py --csv_file your_file.csv --preview")
    print("   python3 import_sanctions_csv.py --csv_file your_file.csv --list_name 'My_List'")
    print("   python3 import_sanctions_csv.py --stats")
    print()

def test_csv_importer():
    """Test CSV importer functionality"""
    print("🧪 Testing CSV Importer...")
    
    try:
        from services.sanctions.csv_importer import SanctionsCSVImporter
        importer = SanctionsCSVImporter()
        
        # Test database connection
        stats = importer.get_import_statistics()
        
        print("✅ CSV Importer working!")
        print(f"   • Database: Connected")
        print(f"   • Sanctions Entities: {stats['total_sanctions_entities']}")
        print(f"   • PEP Entities: {stats['total_pep_entities']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ CSV Importer Error: {e}")
        return False

def show_csv_import_help():
    """Show CSV import help"""
    print("📋 CSV IMPORT QUICK GUIDE")
    print("-" * 40)
    
    print("Supported CSV Formats:")
    print("   • OFAC SDN List")
    print("   • EU Consolidated List")
    print("   • UN Consolidated List")
    print("   • Generic CSV with standard fields")
    print()
    
    print("Quick Commands:")
    print("   # Preview your CSV file first")
    print("   python3 import_sanctions_csv.py --csv_file your_sanctions.csv --preview")
    print()
    print("   # Import your CSV file")
    print("   python3 import_sanctions_csv.py --csv_file your_sanctions.csv --list_name 'OFAC_2024'")
    print()
    print("   # Import all CSV files from a directory")
    print("   python3 import_sanctions_csv.py --directory /path/to/csv/files --auto_import")
    print()
    print("   # Check current database statistics")
    print("   python3 import_sanctions_csv.py --stats")
    print()

def main():
    """Main demo access function"""
    print_banner()
    
    # Check if platform is already running
    if check_platform_status():
        print("✅ Platform is already running!")
    else:
        print("🔄 Platform not detected. Starting...")
        if not start_platform():
            print("❌ Failed to start platform. Try running manually:")
            print("   cd /root/compliant-one")
            print("   ./start_platform.sh")
            print()
    
    # Test CSV importer
    csv_working = test_csv_importer()
    
    # Show access information
    show_access_info()
    
    # Show CSV import help
    show_csv_import_help()
    
    if csv_working:
        print("🎯 SYSTEM STATUS: Ready for CSV Import!")
        print("💡 Use the web interface or command line tools to import your sanctions data.")
    else:
        print("⚠️  CSV Importer needs attention - but web interface should still work.")
    
    # Show Phase 2 demo options
    print()
    print("🚀 PHASE 2 DEMO OPTIONS")
    print("-" * 40)
    print("Advanced AI & Compliance Automation Demos:")
    print("   # Basic Phase 2 overview with 3 scenarios")
    print("   python3 phase2_demo.py")
    print()
    print("   # Advanced business scenarios (8 demos)")
    print("   python3 phase2_advanced_demos.py")
    print()
    print("   # Interactive demo selector (choose specific demos)")
    print("   python3 interactive_demo.py")
    print()
    print("   # CSV import with Phase 2 AI analysis")
    print("   python3 csv_phase2_demo.py")
    print()
    
    print("🎯 Phase 2 Features Demonstrated:")
    print("   ✅ AI-Powered Risk Analytics & Anomaly Detection")
    print("   ✅ Advanced OSINT & Adverse Media Monitoring")
    print("   ✅ Customizable Risk Rules Engine")
    print("   ✅ Intelligent Case Management & Workflow")
    print("   ✅ Cryptocurrency Exchange Onboarding")
    print("   ✅ Shell Company Detection using AI")
    print("   ✅ Trade Finance & Wire Transfer Monitoring")
    print("   ✅ PEP Network Relationship Analysis")
    print("   ✅ Bulk Portfolio Screening")
    print("   ✅ Regulatory Change Impact Assessment")
    
    print()
    print("🔗 Quick Links:")
    print("   • Platform: http://localhost:8501")
    print("   • Login: admin / admin123")
    print("   • CSV Import: Admin Panel → Web Crawler → Compliance Analysis → Import Sanctions Data")

if __name__ == "__main__":
    main()
