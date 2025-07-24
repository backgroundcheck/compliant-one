#!/usr/bin/env python3
"""
Test Web Crawler Integration
Quick test to verify crawl4ai integration with Compliant.one
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

async def test_web_crawler():
    """Test web crawler functionality"""
    print("🕷️ Testing Web Crawler Integration...")
    
    try:
        from services.web_crawler.crawler_service import WebCrawlerService
        
        # Initialize crawler
        print("Initializing crawler...")
        crawler = WebCrawlerService()
        await crawler.initialize()
        print("✅ Crawler initialized successfully!")
        
        # Test single URL crawling
        test_url = "https://httpbin.org/json"  # Simple JSON API for testing
        print(f"Testing crawl: {test_url}")
        
        result = await crawler.crawl_url(test_url, 'default')
        
        if result['status'] == 'success':
            print("✅ Crawling successful!")
            print(f"   - Word count: {result['word_count']}")
            print(f"   - Content length: {result['content_length']}")
            print(f"   - Extraction strategy: {result['extraction_strategy']}")
            print(f"   - Entities found: {len(result['extracted_data'].get('entities', []))}")
        else:
            print(f"❌ Crawling failed: {result['message']}")
        
        # Test financial extraction
        print("\nTesting financial extraction strategy...")
        financial_result = await crawler.crawl_url(test_url, 'financial')
        
        if financial_result['status'] == 'success':
            print("✅ Financial extraction successful!")
            financial_data = financial_result['extracted_data'].get('financial_data', {})
            print(f"   - Financial patterns found: {len(financial_data)}")
        
        # Shutdown crawler
        await crawler.shutdown()
        print("✅ Crawler shutdown successfully!")
        
        return True
        
    except ImportError:
        print("❌ crawl4ai not available. Install with: pip install crawl4ai")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_imports():
    """Test all required imports"""
    print("📦 Testing imports...")
    
    try:
        # Test crawler import
        from services.web_crawler.crawler_service import WebCrawlerService
        print("✅ WebCrawlerService import successful")
        
        # Test crawl4ai import
        import crawl4ai
        print("✅ crawl4ai import successful")
        
        # Test admin dashboard import
        from dashboard.admin import render_web_crawler_section
        print("✅ Admin dashboard web crawler section import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Compliant.one Web Crawler Integration Test")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    print("\n✅ All imports successful!")
    
    # Test crawler functionality
    print("\n" + "=" * 50)
    
    try:
        result = asyncio.run(test_web_crawler())
        
        if result:
            print("\n🎉 All tests passed! Web crawler integration successful!")
            print("\nNext steps:")
            print("1. Run the admin dashboard: streamlit run dashboard/main.py")
            print("2. Navigate to 'Web Crawler' section")
            print("3. Initialize crawler and start crawling URLs")
            
        else:
            print("\n❌ Web crawler tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
