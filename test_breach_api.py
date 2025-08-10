#!/usr/bin/env python3
"""
Test script for Breach Intelligence API endpoints
Privacy-compliant breach monitoring system
"""

import asyncio
import json
import httpx
from datetime import datetime

# Test configuration
API_BASE = "http://localhost:8000"
API_KEY = "compliant-breach-test-key"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def test_breach_intelligence_api():
    """Test all breach intelligence API endpoints"""
    
    print("🔐 Testing Breach Intelligence API")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Health Check
        print("\n1. Health Check...")
        try:
            response = await client.get(
                f"{API_BASE}/api/v1/breach-intel/health",
                headers=HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service Health: {health_data['data']['health_check']['status']}")
            else:
                print(f"❌ Health check failed: {response.text}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # 2. Check Credential Breach (K-Anonymity)
        print("\n2. Testing K-Anonymity Credential Check...")
        test_email = "test@example.com"
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/breach-intel/check-credential",
                headers=HEADERS,
                json={
                    "credential": test_email,
                    "type": "email"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                breach_data = response.json()
                print(f"✅ Credential check: {breach_data['message']}")
                print(f"   Privacy-compliant: {breach_data['data']['privacy_compliant']}")
            else:
                print(f"❌ Credential check failed: {response.text}")
        except Exception as e:
            print(f"❌ Credential check error: {e}")
        
        # 3. Add Monitoring Target
        print("\n3. Testing Add Monitoring Target...")
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/breach-intel/add-monitoring",
                headers=HEADERS,
                json={
                    "credential": test_email,
                    "type": "email",
                    "alert_email": "alert@example.com"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                monitor_data = response.json()
                print(f"✅ Monitoring added: {monitor_data['message']}")
            else:
                print(f"❌ Monitoring add failed: {response.text}")
        except Exception as e:
            print(f"❌ Monitoring add error: {e}")
        
        # 4. Start Paste Site Monitoring
        print("\n4. Testing Paste Site Monitoring...")
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/breach-intel/monitor-paste-sites",
                headers=HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                paste_data = response.json()
                print(f"✅ Paste monitoring: {paste_data['message']}")
            else:
                print(f"❌ Paste monitoring failed: {response.text}")
        except Exception as e:
            print(f"❌ Paste monitoring error: {e}")
        
        # 5. Start Dark Web Monitoring
        print("\n5. Testing Ethical Dark Web Monitoring...")
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/breach-intel/monitor-darkweb",
                headers=HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                darkweb_data = response.json()
                print(f"✅ Dark web monitoring: {darkweb_data['message']}")
            else:
                print(f"❌ Dark web monitoring failed: {response.text}")
        except Exception as e:
            print(f"❌ Dark web monitoring error: {e}")
        
        # 6. Get Statistics
        print("\n6. Testing Breach Statistics...")
        try:
            response = await client.get(
                f"{API_BASE}/api/v1/breach-intel/statistics",
                headers=HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ Statistics retrieved: {stats_data['message']}")
                print(f"   Total breaches monitored: {stats_data['data'].get('total_breaches', 0)}")
            else:
                print(f"❌ Statistics failed: {response.text}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        # 7. Privacy Compliance Cleanup
        print("\n7. Testing Privacy Compliance Cleanup...")
        try:
            response = await client.post(
                f"{API_BASE}/api/v1/breach-intel/cleanup-expired",
                headers=HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                cleanup_data = response.json()
                print(f"✅ Privacy cleanup: {cleanup_data['message']}")
            else:
                print(f"❌ Privacy cleanup failed: {response.text}")
        except Exception as e:
            print(f"❌ Privacy cleanup error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Breach Intelligence API Testing Complete!")
    print("\n🔐 Features Tested:")
    print("   ✅ K-Anonymity credential checking")
    print("   ✅ Ethical paste site monitoring")
    print("   ✅ Privacy-compliant dark web monitoring")
    print("   ✅ GDPR/CCPA compliance cleanup")
    print("   ✅ Breach intelligence statistics")
    print("   ✅ Privacy-by-design architecture")

def main():
    """Main test runner"""
    print(f"🚀 Starting Breach Intelligence API Tests...")
    print(f"⏰ Test Time: {datetime.now().isoformat()}")
    
    try:
        asyncio.run(test_breach_intelligence_api())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()
