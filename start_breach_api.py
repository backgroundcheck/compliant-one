#!/usr/bin/env python3
"""
Startup script for Compliant-One Breach Intelligence API
Privacy-compliant breach monitoring platform
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/breach_api.log')
        ]
    )

def main():
    """Start the Breach Intelligence API server"""
    
    print("🔐 Compliant-One Breach Intelligence Platform")
    print("=" * 60)
    print("🚀 Starting Privacy-Compliant Breach Monitoring API...")
    print("=" * 60)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Import after setting up paths
        import uvicorn
        from api.main import app
        
        logger.info("Starting Breach Intelligence API server...")
        
        print("\n🌟 Features Available:")
        print("   ✅ K-Anonymity credential breach checking")
        print("   ✅ Ethical paste site monitoring (respects robots.txt)")
        print("   ✅ Privacy-compliant dark web monitoring")
        print("   ✅ SpiderFoot/Maltego integration for data enrichment")
        print("   ✅ GDPR/CCPA compliant data handling")
        print("   ✅ Automatic data retention cleanup")
        print("   ✅ Hash-based privacy protection")
        
        print("\n🔗 API Endpoints:")
        print("   📊 Health Check: /api/v1/breach-intel/health")
        print("   🔍 Credential Check: /api/v1/breach-intel/check-credential")
        print("   📡 Add Monitoring: /api/v1/breach-intel/add-monitoring")
        print("   📰 Paste Monitoring: /api/v1/breach-intel/monitor-paste-sites")
        print("   🕸️  Dark Web Monitoring: /api/v1/breach-intel/monitor-darkweb")
        print("   📈 Statistics: /api/v1/breach-intel/statistics")
        print("   🧹 Privacy Cleanup: /api/v1/breach-intel/cleanup-expired")
        
        print("\n🔑 Authentication:")
        print("   Use Bearer token with prefix 'compliant-'")
        print("   Example: Authorization: Bearer compliant-your-api-key")
        
        print("\n🌐 Starting server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("=" * 60)
        
        # Start the server; disable reload by default for stability in background runs
        reload_enabled = os.getenv("BREACH_API_RELOAD", "false").lower() == "true"
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=reload_enabled,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        print(f"\n❌ Error: Missing dependency - {e}")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
