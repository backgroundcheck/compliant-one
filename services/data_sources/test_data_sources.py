"""
Test Suite for Data Sources Module
Comprehensive testing of all data source services
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.data_sources.manager import DataSourcesManager
from services.data_sources.sanctions_watchlists import SanctionsWatchlistService
from services.data_sources.pep_data import PEPDataService
from services.data_sources.adverse_media import AdverseMediaService
from services.data_sources.corruption_data import CorruptionDataService

def test_data_sources_manager_initialization():
    """Test DataSourcesManager initialization"""
    print("Testing DataSourcesManager initialization...")
    
    manager = DataSourcesManager()
    
    # Check that all services are initialized
    assert manager.sanctions_service is not None
    assert manager.pep_service is not None
    assert manager.adverse_media_service is not None
    assert manager.corruption_service is not None
    
    # Check configurations are loaded
    assert len(manager.source_configs) > 0
    
    print("✅ DataSourcesManager initialization: PASSED")

def test_sanctions_service():
    """Test SanctionsWatchlistService"""
    print("Testing SanctionsWatchlistService...")
    
    service = SanctionsWatchlistService()
    
    # Check sources are initialized
    assert len(service.sources) > 0
    
    # Check source types
    expected_sources = ["un_consolidated", "ofac_sdn", "uk_hmt", "eu_consolidated"]
    for source_id in expected_sources:
        assert source_id in service.sources
    
    # Test statistics
    stats = service.get_statistics()
    assert "total_sources" in stats
    assert "by_jurisdiction" in stats
    assert "by_type" in stats
    
    print("✅ SanctionsWatchlistService: PASSED")

def test_pep_service():
    """Test PEPDataService"""
    print("Testing PEPDataService...")
    
    service = PEPDataService()
    
    # Check sources are initialized
    assert len(service.sources) > 0
    
    # Check source types
    expected_sources = ["opensanctions", "uk_parliament", "us_officials"]
    for source_id in expected_sources:
        assert source_id in service.sources
    
    print("✅ PEPDataService: PASSED")

def test_adverse_media_service():
    """Test AdverseMediaService"""
    print("Testing AdverseMediaService...")
    
    service = AdverseMediaService()
    
    # Check sources are initialized
    assert len(service.sources) > 0
    
    # Check source types
    expected_sources = ["reuters", "bbc_news", "twitter", "reddit"]
    for source_id in expected_sources:
        assert source_id in service.sources
    
    # Check risk keywords are loaded
    assert len(service.risk_keywords) > 0
    assert "corruption" in service.risk_keywords
    assert "sanctions" in service.risk_keywords
    
    print("✅ AdverseMediaService: PASSED")

def test_corruption_service():
    """Test CorruptionDataService"""
    print("Testing CorruptionDataService...")
    
    service = CorruptionDataService()
    
    # Check sources are initialized
    assert len(service.sources) > 0
    
    # Check source types
    expected_sources = ["us_doj", "us_sec", "uk_sfo", "oecd_bribery"]
    for source_id in expected_sources:
        assert source_id in service.sources
    
    # Check corruption types are loaded
    assert len(service.corruption_types) > 0
    assert "bribery" in service.corruption_types
    assert "fraud" in service.corruption_types
    
    print("✅ CorruptionDataService: PASSED")

async def test_sanctions_search():
    """Test sanctions search functionality"""
    print("Testing sanctions search...")
    
    service = SanctionsWatchlistService()
    
    # Test search with common name
    results = await service.search_sanctions("John Smith")
    assert isinstance(results, list)
    
    # Test fuzzy matching
    results_fuzzy = await service.search_sanctions("Jon Smith", fuzzy_match=True)
    assert isinstance(results_fuzzy, list)
    
    print("✅ Sanctions search: PASSED")

async def test_pep_search():
    """Test PEP search functionality"""
    print("Testing PEP search...")
    
    service = PEPDataService()
    
    # Test search with politician name
    results = await service.search_peps("Biden")
    assert isinstance(results, list)
    
    # Test search with filtering
    results_filtered = await service.search_peps("Minister", countries=["UK"])
    assert isinstance(results_filtered, list)
    
    print("✅ PEP search: PASSED")

async def test_adverse_media_monitoring():
    """Test adverse media monitoring"""
    print("Testing adverse media monitoring...")
    
    service = AdverseMediaService()
    
    # Test monitoring for entities
    entities = ["Test Company", "John Doe"]
    results = await service.monitor_adverse_media(entities, time_range=7)
    assert isinstance(results, dict)
    
    print("✅ Adverse media monitoring: PASSED")

async def test_corruption_search():
    """Test corruption case search"""
    print("Testing corruption case search...")
    
    service = CorruptionDataService()
    
    # Test search for corruption cases
    results = await service.search_corruption_cases("bribery")
    assert isinstance(results, list)
    
    # Test search with filters
    results_filtered = await service.search_corruption_cases(
        "fraud", 
        jurisdictions=["United States"]
    )
    assert isinstance(results_filtered, list)
    
    print("✅ Corruption search: PASSED")

async def test_comprehensive_screening():
    """Test comprehensive entity screening"""
    print("Testing comprehensive entity screening...")
    
    manager = DataSourcesManager()
    
    # Test comprehensive screening
    results = await manager.comprehensive_entity_screening("John Smith")
    
    assert "entity_name" in results
    assert "risk_assessment" in results
    assert "detailed_results" in results
    
    # Check risk assessment structure
    risk_assessment = results["risk_assessment"]
    assert "risk_level" in risk_assessment
    assert "overall_risk_score" in risk_assessment
    assert "risk_factors" in risk_assessment
    
    print("✅ Comprehensive screening: PASSED")

async def test_health_check():
    """Test system health check"""
    print("Testing system health check...")
    
    manager = DataSourcesManager()
    
    health_status = await manager.health_check()
    
    assert "overall_status" in health_status
    assert "services" in health_status
    assert "checked_at" in health_status
    
    # Check individual services
    services = health_status["services"]
    expected_services = ["sanctions", "pep", "adverse_media", "corruption"]
    
    for service in expected_services:
        assert service in services
        assert "status" in services[service]
        assert "sources_active" in services[service]
    
    print("✅ Health check: PASSED")

async def test_statistics():
    """Test comprehensive statistics"""
    print("Testing comprehensive statistics...")
    
    manager = DataSourcesManager()
    
    stats = await manager.get_comprehensive_statistics()
    
    assert "sanctions" in stats
    assert "pep" in stats
    assert "adverse_media" in stats
    assert "corruption" in stats
    assert "summary" in stats
    
    # Check summary structure
    summary = stats["summary"]
    assert "total_data_sources" in summary
    assert "total_records" in summary
    assert "services_active" in summary
    
    print("✅ Comprehensive statistics: PASSED")

async def test_update_all_sources():
    """Test updating all sources"""
    print("Testing source updates...")
    
    manager = DataSourcesManager()
    
    # Test update (this will use cached/simulated data)
    update_results = await manager.update_all_sources()
    
    assert "started_at" in update_results
    assert "sanctions" in update_results
    assert "pep" in update_results
    assert "corruption" in update_results
    assert "summary" in update_results
    
    print("✅ Source updates: PASSED")

def test_source_configurations():
    """Test source configuration management"""
    print("Testing source configurations...")
    
    manager = DataSourcesManager()
    
    # Get all configurations
    configs = manager.get_source_configurations()
    assert len(configs) > 0
    
    # Test configuration update
    first_source = list(configs.keys())[0]
    result = manager.update_source_configuration(
        first_source, 
        update_priority=5
    )
    assert result is True
    
    # Verify update
    updated_configs = manager.get_source_configurations()
    assert updated_configs[first_source]["update_priority"] == 5
    
    print("✅ Source configurations: PASSED")

async def run_all_tests():
    """Run all data sources tests"""
    print("=" * 60)
    print("DATA SOURCES MODULE - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Synchronous tests
    test_data_sources_manager_initialization()
    test_sanctions_service()
    test_pep_service()
    test_adverse_media_service()
    test_corruption_service()
    test_source_configurations()
    
    # Asynchronous tests
    await test_sanctions_search()
    await test_pep_search()
    await test_adverse_media_monitoring()
    await test_corruption_search()
    await test_comprehensive_screening()
    await test_health_check()
    await test_statistics()
    await test_update_all_sources()
    
    print("=" * 60)
    print("✅ ALL DATA SOURCES TESTS PASSED!")
    print("=" * 60)
    
    # Summary statistics
    manager = DataSourcesManager()
    stats = await manager.get_comprehensive_statistics()
    
    print(f"📊 Total Data Sources: {stats['summary']['total_data_sources']}")
    print(f"📈 Total Records: {stats['summary']['total_records']}")
    print(f"🔧 Services Active: {stats['summary']['services_active']}")
    
    coverage = stats['summary']['coverage']
    print(f"🌍 Sanctions Jurisdictions: {coverage['sanctions_jurisdictions']}")
    print(f"👥 PEP Coverage Types: {coverage['pep_coverage_types']}")
    print(f"📰 Media Source Types: {coverage['media_source_types']}")
    print(f"⚖️  Corruption Agencies: {coverage['corruption_agencies']}")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
