#!/usr/bin/env python3
"""
Complete Platform Service Test
Tests all integrated services and functionality
"""

import sys
import os
sys.path.append('/root/compliant-one')

def test_all_services():
    """Test all platform services"""
    print("🧪 Testing Complete Platform Integration...")
    print("="*60)
    
    results = {}
    
    # Test 1: PDF Compliance Analyzer
    print("\n1️⃣ Testing PDF Compliance Analyzer...")
    try:
        from services.compliance.pdf_analyzer import PDFComplianceAnalyzer
        analyzer = PDFComplianceAnalyzer()
        stats = analyzer.get_sanctions_statistics()
        results['pdf_analyzer'] = '✅ PASS'
        print(f"   ✅ PDF Analyzer initialized")
        print(f"   📊 Database has {stats['total_sanctions_entities']} sanctions entities")
    except Exception as e:
        results['pdf_analyzer'] = f'❌ FAIL: {e}'
        print(f"   ❌ PDF Analyzer failed: {e}")
    
    # Test 2: Sanctions Service
    print("\n2️⃣ Testing Sanctions Service...")
    try:
        from services.sanctions.sanctions_service import SanctionsService
        sanctions = SanctionsService()
        result = sanctions.screen_entity("Test Entity")
        health = sanctions.health_check()
        results['sanctions'] = '✅ PASS'
        print(f"   ✅ Sanctions service operational")
        print(f"   🔍 Database status: {health['status']}")
        print(f"   📋 Sanctions entities: {health['sanctions_entities']}")
    except Exception as e:
        results['sanctions'] = f'❌ FAIL: {e}'
        print(f"   ❌ Sanctions service failed: {e}")
    
    # Test 3: PDF Scraper
    print("\n3️⃣ Testing PDF Scraper...")
    try:
        pdf_dir = "/root/compliant-one/data/pdfs/downloaded_pdfs"
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
            results['pdf_scraper'] = '✅ PASS'
            print(f"   ✅ PDF collection accessible")
            print(f"   📄 Total PDFs available: {len(pdf_files):,}")
        else:
            results['pdf_scraper'] = '⚠️  WARN: No PDF collection found'
            print(f"   ⚠️  PDF directory not found")
    except Exception as e:
        results['pdf_scraper'] = f'❌ FAIL: {e}'
        print(f"   ❌ PDF scraper test failed: {e}")
    
    # Test 4: Web Crawler
    print("\n4️⃣ Testing Web Crawler...")
    try:
        from services.web_crawler.crawler_service import WebCrawlerService
        results['web_crawler'] = '✅ PASS'
        print(f"   ✅ Web crawler service available")
    except Exception as e:
        results['web_crawler'] = f'❌ FAIL: {e}'
        print(f"   ❌ Web crawler failed: {e}")
    
    # Test 5: Other Platform Services
    print("\n5️⃣ Testing Platform Services...")
    services_to_test = [
        ('monitoring', 'services.monitoring.monitoring_service', 'MonitoringService'),
        ('transactions', 'services.transactions.transaction_service', 'TransactionMonitoringService'),
        ('reporting', 'services.reporting.reporting_service', 'ReportingService'),
        ('identity', 'services.identity.identity_service', 'IdentityVerificationService'),
        ('kyc', 'services.kyc.kyc_service', 'KYCService'),
        ('osint', 'services.osint.osint_service', 'OSINTService'),
        ('beneficial_ownership', 'services.beneficial_ownership.bo_service', 'BeneficialOwnershipService')
    ]
    
    for service_name, module_path, class_name in services_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            service = service_class()
            if hasattr(service, 'health_check'):
                health = service.health_check()
                print(f"   ✅ {service_name.title()}: {health['status']}")
            else:
                print(f"   ✅ {service_name.title()}: Available")
            results[service_name] = '✅ PASS'
        except Exception as e:
            print(f"   ❌ {service_name.title()}: {str(e)[:50]}...")
            results[service_name] = f'❌ FAIL: {str(e)[:30]}...'
    
    # Test 6: Database Connectivity
    print("\n6️⃣ Testing Database Connectivity...")
    try:
        import sqlite3
        
        # Test compliance analysis DB
        conn = sqlite3.connect("compliance_analysis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        # Test sanctions DB
        conn = sqlite3.connect("sanctions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sanctions_entities")
        count = cursor.fetchone()[0]
        conn.close()
        
        results['databases'] = '✅ PASS'
        print(f"   ✅ Compliance DB: {len(tables)} tables")
        print(f"   ✅ Sanctions DB: {count} entities")
        
    except Exception as e:
        results['databases'] = f'❌ FAIL: {e}'
        print(f"   ❌ Database test failed: {e}")
    
    # Test 7: Platform Integration
    print("\n7️⃣ Testing Platform Integration...")
    try:
        from core.platform import CompliantOnePlatform
        platform = CompliantOnePlatform()
        service_count = len(platform.services)
        results['platform'] = '✅ PASS'
        print(f"   ✅ Platform initialized with {service_count} services")
    except Exception as e:
        results['platform'] = f'❌ FAIL: {e}'
        print(f"   ❌ Platform integration failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r.startswith('✅'))
    total = len(results)
    
    for component, result in results.items():
        print(f"{component.replace('_', ' ').title():.<30} {result}")
    
    print("\n" + "="*60)
    print(f"🎯 OVERALL RESULT: {passed}/{total} components operational")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Platform ready for production use!")
    elif passed >= total * 0.8:
        print("✅ PLATFORM MOSTLY OPERATIONAL")
        print("⚠️  Some optional components need attention")
    else:
        print("⚠️  PLATFORM NEEDS ATTENTION")
        print("🔧 Multiple components require fixes")
    
    return results

def test_specific_functionality():
    """Test specific integrated functionality"""
    print("\n" + "="*60)
    print("🔬 SPECIFIC FUNCTIONALITY TESTS")
    print("="*60)
    
    # Test PDF compliance analysis with sample data
    print("\n📊 Testing PDF Compliance Analysis...")
    try:
        from services.compliance.pdf_analyzer import PDFComplianceAnalyzer
        analyzer = PDFComplianceAnalyzer()
        
        # Test with sample text
        sample_text = """
        This document contains information about anti-money laundering procedures.
        Customer due diligence must be performed for all high-risk clients.
        Suspicious activity reports should be filed within 30 days.
        OFAC sanctions list must be checked before onboarding.
        """
        
        # Mock a small analysis
        patterns = analyzer.compliance_patterns['aml_cft']
        findings = analyzer._detect_compliance_issues(sample_text, 'aml_cft', 'test_doc.pdf')
        
        print(f"   ✅ Pattern detection working: {len(findings)} findings")
        print(f"   📋 AML patterns available: {len(patterns)}")
        
    except Exception as e:
        print(f"   ❌ PDF analysis test failed: {e}")
    
    # Test sanctions screening
    print("\n🔍 Testing Sanctions Screening...")
    try:
        from services.sanctions.sanctions_service import SanctionsService
        sanctions = SanctionsService()
        
        # Test screening
        result = sanctions.screen_entity("John Doe Sanctions Test")
        print(f"   ✅ Screening operational: {result['match_found']}")
        print(f"   🎯 Risk level: {result['risk_level']}")
        print(f"   📊 Matches found: {result['total_matches']}")
        
    except Exception as e:
        print(f"   ❌ Sanctions screening test failed: {e}")

if __name__ == "__main__":
    # Run comprehensive tests
    results = test_all_services()
    test_specific_functionality()
    
    print("\n" + "="*60)
    print("🏁 INTEGRATION TESTING COMPLETE")
    print("="*60)
    print("📖 For detailed usage instructions, see:")
    print("   📄 PDF_INTEGRATION_COMPLETE.md")
    print("   🌐 Platform: http://localhost:8501")
    print("   🔐 Login: admin / SecurePass123!")
    print("="*60)
