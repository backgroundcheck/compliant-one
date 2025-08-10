#!/usr/bin/env python3
"""
Test script for PDF processing functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_pdf_processor():
    """Test the batch PDF processor"""
    print("🧪 Testing PDF Processor...")
    
    try:
        from process_pdfs import BatchPDFProcessor
        
        # Initialize processor
        processor = BatchPDFProcessor()
        print("✅ Processor initialized successfully")
        
        # Find PDFs
        pdf_files = processor.find_all_pdfs()
        print(f"✅ Found {len(pdf_files)} PDF files")
        
        if pdf_files:
            # Test processing first file
            test_file = pdf_files[0]
            print(f"🔄 Testing with: {test_file.name}")
            
            success = processor.process_single_pdf(test_file)
            if success:
                print("✅ Single file processing successful")
                
                # Test search
                results = processor.search_entities("corruption", limit=5)
                print(f"✅ Search test: found {len(results)} corruption-related entities")
                
                # Get stats
                stats = processor.get_statistics()
                print(f"✅ Statistics: {stats['documents_processed']} docs, {stats['total_entities']} entities")
                
                return True
            else:
                print("❌ Single file processing failed")
                return False
        else:
            print("⚠️  No PDF files found to test")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirements():
    """Check if required packages are available"""
    print("🔍 Checking requirements...")
    
    required_packages = ['sqlite3', 'pathlib', 'datetime', 'hashlib', 're']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    # Check optional packages
    optional_packages = ['PyPDF2', 'pdfplumber', 'pdfminer']
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} (optional)")
        except ImportError:
            print(f"⚠️  {package} (optional - not installed)")
    
    return len(missing) == 0

def main():
    """Main test function"""
    print("🚀 Starting PDF Processor Tests\n")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Missing required packages")
        return False
    
    print()
    
    # Test processor
    success = test_pdf_processor()
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed'}")
    return success

if __name__ == "__main__":
    main()
