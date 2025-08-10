"""
Data Sources Management Service
Central coordination and management of all data sources
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger
from services.data_sources.sanctions_watchlists import SanctionsWatchlistService
from services.data_sources.pep_data import PEPDataService
from services.data_sources.corruption_data import CorruptionDataService

# For backward compatibility, try to import the original adverse media service
try:
    from services.data_sources.adverse_media_simple import AdverseMediaService
except ImportError:
    # Fallback to the enhanced version from sigmanaut
    try:
        from services.data_sources.adverse_media import AdverseMediaMonitor as AdverseMediaService
    except ImportError:
        AdverseMediaService = None

logger = get_logger(__name__)

@dataclass
class DataSourceConfig:
    """Data source configuration"""
    source_id: str
    source_type: str  # sanctions, pep, adverse_media, corruption, etc.
    is_enabled: bool = True
    update_priority: int = 1  # 1 (high) to 5 (low)
    max_retry_attempts: int = 3
    timeout_seconds: int = 300
    rate_limit_per_hour: Optional[int] = None
    cost_per_query: Optional[float] = None
    data_retention_days: int = 365

@dataclass
class UpdateTask:
    """Data source update task"""
    task_id: str
    source_id: str
    source_type: str
    status: str  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    records_processed: int = 0
    error_message: Optional[str] = None

class DataSourcesManager:
    """Central manager for all data sources"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize individual services
        self.sanctions_service = SanctionsWatchlistService()
        self.pep_service = PEPDataService()
        self.corruption_service = CorruptionDataService()
        
        # Initialize adverse media service if available
        if AdverseMediaService:
            self.adverse_media_service = AdverseMediaService()
        else:
            self.adverse_media_service = None
            self.logger.warning("AdverseMediaService not available")
        
        # Task management
        self.active_tasks = {}
        self.task_history = []
        self.max_concurrent_tasks = 5
        
        # Configuration
        self.source_configs = {}
        self._initialize_configurations()
        
        self.logger.info("Initialized Data Sources Manager with 4 core services")
    
    def _initialize_configurations(self):
        """Initialize data source configurations"""
        
        # Sanctions sources configuration
        for source_id in self.sanctions_service.sources.keys():
            self.source_configs[source_id] = DataSourceConfig(
                source_id=source_id,
                source_type="sanctions",
                is_enabled=True,
                update_priority=1,  # High priority for sanctions
                rate_limit_per_hour=100
            )
        
        # PEP sources configuration
        for source_id in self.pep_service.sources.keys():
            self.source_configs[source_id] = DataSourceConfig(
                source_id=source_id,
                source_type="pep",
                is_enabled=True,
                update_priority=2,  # Medium-high priority
                rate_limit_per_hour=50
            )
        
        # Adverse media sources configuration
        if self.adverse_media_service:
            for source_id in getattr(self.adverse_media_service, 'sources', {}).keys():
                self.source_configs[source_id] = DataSourceConfig(
                    source_id=source_id,
                    source_type="adverse_media",
                    is_enabled=True,
                    update_priority=3,  # Medium priority
                    rate_limit_per_hour=200
                )
        
        # Corruption sources configuration
        for source_id in self.corruption_service.sources.keys():
            self.source_configs[source_id] = DataSourceConfig(
                source_id=source_id,
                source_type="corruption",
                is_enabled=True,
                update_priority=2,  # Medium-high priority
                rate_limit_per_hour=30
            )
    
    async def update_all_sources(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Update all data sources"""
        
        self.logger.info("Starting comprehensive update of all data sources")
        
        update_results = {
            "started_at": datetime.now().isoformat(),
            "sanctions": {},
            "pep": {},
            "adverse_media": {},
            "corruption": {},
            "summary": {}
        }
        
        try:
            # Update sanctions sources
            self.logger.info("Updating sanctions sources...")
            sanctions_result = await self.sanctions_service.update_all_sources()
            update_results["sanctions"] = sanctions_result
            
            # Update PEP sources
            self.logger.info("Updating PEP sources...")
            pep_result = await self.pep_service.update_all_sources()
            update_results["pep"] = pep_result
            
            # Update corruption sources
            self.logger.info("Updating corruption sources...")
            corruption_result = await self.corruption_service.update_all_sources()
            update_results["corruption"] = corruption_result
            
            # Note: Adverse media is monitored on-demand, not bulk updated
            update_results["adverse_media"] = {
                "note": "Adverse media is monitored on-demand based on entity queries"
            }
            
            # Calculate summary
            total_sources = (
                sanctions_result.get("sources_updated", 0) +
                pep_result.get("sources_updated", 0) +
                corruption_result.get("sources_updated", 0)
            )
            
            total_records = (
                sanctions_result.get("total_records", 0) +
                pep_result.get("total_records", 0) +
                corruption_result.get("total_cases", 0)
            )
            
            update_results["summary"] = {
                "total_sources_updated": total_sources,
                "total_records_processed": total_records,
                "sanctions_sources": sanctions_result.get("sources_updated", 0),
                "pep_sources": pep_result.get("sources_updated", 0),
                "corruption_sources": corruption_result.get("sources_updated", 0),
                "completed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully updated {total_sources} sources with {total_records} total records")
            
        except Exception as e:
            self.logger.error(f"Failed to update all sources: {e}")
            update_results["error"] = str(e)
        
        return update_results
    
    async def search_all_sources(self, query: str, 
                               source_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search across all data sources"""
        
        if source_types is None:
            source_types = ["sanctions", "pep", "adverse_media", "corruption"]
        
        search_results = {
            "query": query,
            "searched_at": datetime.now().isoformat(),
            "results": {}
        }
        
        # Search sanctions if requested
        if "sanctions" in source_types:
            try:
                sanctions_matches = await self.sanctions_service.search_sanctions(query)
                search_results["results"]["sanctions"] = {
                    "matches_found": len(sanctions_matches),
                    "matches": sanctions_matches
                }
            except Exception as e:
                self.logger.error(f"Failed to search sanctions: {e}")
                search_results["results"]["sanctions"] = {"error": str(e)}
        
        # Search PEPs if requested
        if "pep" in source_types:
            try:
                pep_matches = await self.pep_service.search_peps(query)
                search_results["results"]["pep"] = {
                    "matches_found": len(pep_matches),
                    "matches": pep_matches
                }
            except Exception as e:
                self.logger.error(f"Failed to search PEPs: {e}")
                search_results["results"]["pep"] = {"error": str(e)}
        
        # Search adverse media if requested
        if "adverse_media" in source_types and self.adverse_media_service:
            try:
                # For adverse media, perform monitoring for the query entity
                entities = [query]  # Treat query as entity name
                media_results = await self.adverse_media_service.monitor_adverse_media(entities, time_range=30)
                
                # Flatten results
                all_articles = []
                for source_articles in media_results.values():
                    all_articles.extend(source_articles)
                
                search_results["results"]["adverse_media"] = {
                    "articles_found": len(all_articles),
                    "articles": [asdict(article) for article in all_articles]
                }
            except Exception as e:
                self.logger.error(f"Failed to search adverse media: {e}")
                search_results["results"]["adverse_media"] = {"error": str(e)}
        elif "adverse_media" in source_types:
            search_results["results"]["adverse_media"] = {"error": "Adverse media service not available"}
        
        # Search corruption data if requested
        if "corruption" in source_types:
            try:
                corruption_matches = await self.corruption_service.search_corruption_cases(query)
                search_results["results"]["corruption"] = {
                    "cases_found": len(corruption_matches),
                    "cases": corruption_matches
                }
            except Exception as e:
                self.logger.error(f"Failed to search corruption data: {e}")
                search_results["results"]["corruption"] = {"error": str(e)}
        
        return search_results
    
    async def comprehensive_entity_screening(self, entity_name: str, 
                                           entity_type: str = "person") -> Dict[str, Any]:
        """Perform comprehensive screening across all data sources"""
        
        self.logger.info(f"Performing comprehensive screening for entity: {entity_name}")
        
        screening_results = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "screening_date": datetime.now().isoformat(),
            "risk_assessment": {},
            "detailed_results": {}
        }
        
        try:
            # Search all sources
            search_results = await self.search_all_sources(entity_name)
            screening_results["detailed_results"] = search_results["results"]
            
            # Calculate comprehensive risk assessment
            risk_assessment = self._calculate_comprehensive_risk(search_results["results"])
            screening_results["risk_assessment"] = risk_assessment
            
            self.logger.info(f"Completed comprehensive screening for {entity_name}")
            
        except Exception as e:
            self.logger.error(f"Failed comprehensive screening for {entity_name}: {e}")
            screening_results["error"] = str(e)
        
        return screening_results
    
    def _calculate_comprehensive_risk(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk assessment"""
        
        risk_factors = {
            "sanctions_risk": 0.0,
            "pep_risk": 0.0,
            "adverse_media_risk": 0.0,
            "corruption_risk": 0.0,
            "overall_risk": 0.0
        }
        
        risk_level = "LOW"
        risk_reasons = []
        
        # Sanctions risk
        sanctions_data = search_results.get("sanctions", {})
        if not isinstance(sanctions_data, dict) or "error" in sanctions_data:
            pass  # Skip if error
        else:
            sanctions_matches = sanctions_data.get("matches", [])
            if sanctions_matches:
                risk_factors["sanctions_risk"] = 1.0
                risk_level = "CRITICAL"
                risk_reasons.append(f"Found {len(sanctions_matches)} sanctions matches")
        
        # PEP risk
        pep_data = search_results.get("pep", {})
        if not isinstance(pep_data, dict) or "error" in pep_data:
            pass  # Skip if error
        else:
            pep_matches = pep_data.get("matches", [])
            if pep_matches:
                risk_factors["pep_risk"] = 0.6
                if risk_level in ["LOW", "MEDIUM"]:
                    risk_level = "HIGH"
                risk_reasons.append(f"Found {len(pep_matches)} PEP matches")
        
        # Adverse media risk
        media_data = search_results.get("adverse_media", {})
        if not isinstance(media_data, dict) or "error" in media_data:
            pass  # Skip if error
        else:
            articles = media_data.get("articles", [])
            high_impact_articles = [a for a in articles if a.get("impact_score", 0) > 0.7]
            if high_impact_articles:
                risk_factors["adverse_media_risk"] = 0.8
                if risk_level == "LOW":
                    risk_level = "HIGH"
                risk_reasons.append(f"Found {len(high_impact_articles)} high-impact adverse media articles")
            elif articles:
                risk_factors["adverse_media_risk"] = 0.4
                if risk_level == "LOW":
                    risk_level = "MEDIUM"
                risk_reasons.append(f"Found {len(articles)} adverse media articles")
        
        # Corruption risk
        corruption_data = search_results.get("corruption", {})
        if not isinstance(corruption_data, dict) or "error" in corruption_data:
            pass  # Skip if error
        else:
            corruption_cases = corruption_data.get("cases", [])
            if corruption_cases:
                risk_factors["corruption_risk"] = 0.9
                risk_level = "CRITICAL"
                risk_reasons.append(f"Found {len(corruption_cases)} corruption cases")
        
        # Calculate overall risk
        weights = {
            "sanctions_risk": 0.4,
            "pep_risk": 0.2,
            "adverse_media_risk": 0.2,
            "corruption_risk": 0.2
        }
        
        overall_risk = sum(risk_factors[factor] * weights[factor] for factor in weights)
        risk_factors["overall_risk"] = overall_risk
        
        # Determine final risk level based on overall score
        if overall_risk >= 0.8:
            final_risk_level = "CRITICAL"
        elif overall_risk >= 0.6:
            final_risk_level = "HIGH"
        elif overall_risk >= 0.3:
            final_risk_level = "MEDIUM"
        else:
            final_risk_level = "LOW"
        
        return {
            "risk_level": final_risk_level,
            "overall_risk_score": overall_risk,
            "risk_factors": risk_factors,
            "risk_reasons": risk_reasons,
            "recommendation": self._get_risk_recommendation(final_risk_level, risk_reasons)
        }
    
    def _get_risk_recommendation(self, risk_level: str, risk_reasons: List[str]) -> str:
        """Get risk-based recommendation"""
        
        if risk_level == "CRITICAL":
            return "REJECT: Critical risk factors identified. Do not proceed with business relationship."
        elif risk_level == "HIGH":
            return "ENHANCED DUE DILIGENCE: High risk factors present. Conduct enhanced due diligence and senior management approval required."
        elif risk_level == "MEDIUM":
            return "STANDARD DUE DILIGENCE: Medium risk factors present. Standard due diligence procedures apply."
        else:
            return "PROCEED: Low risk profile. Standard onboarding procedures may proceed."
    
    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all data sources"""
        
        stats = {
            "generated_at": datetime.now().isoformat(),
            "sanctions": {},
            "pep": {},
            "adverse_media": {},
            "corruption": {},
            "summary": {}
        }
        
        try:
            # Get individual service statistics
            stats["sanctions"] = self.sanctions_service.get_statistics()
            stats["pep"] = await self.pep_service.get_source_statistics()
            if self.adverse_media_service:
                stats["adverse_media"] = await self.adverse_media_service.get_source_statistics()
            else:
                stats["adverse_media"] = {"error": "Service not available"}
            stats["corruption"] = await self.corruption_service.get_corruption_statistics()
            
            # Calculate summary
            total_sources = (
                stats["sanctions"].get("total_sources", 0) +
                stats["pep"].get("total_sources", 0) +
                (stats["adverse_media"].get("total_sources", 0) if self.adverse_media_service else 0) +
                len(self.corruption_service.sources)
            )
            
            total_records = (
                stats["sanctions"].get("total_records", 0) +
                stats["pep"].get("total_records", 0) +
                (stats["adverse_media"].get("total_articles_collected", 0) if self.adverse_media_service else 0) +
                stats["corruption"].get("total_cases", 0)
            )
            
            stats["summary"] = {
                "total_data_sources": total_sources,
                "total_records": total_records,
                "services_active": 4,
                "coverage": {
                    "sanctions_jurisdictions": len(set(
                        source.jurisdiction for source in self.sanctions_service.sources.values()
                    )),
                    "pep_coverage_types": len(set(
                        source.coverage_type for source in self.pep_service.sources.values()
                    )),
                    "media_source_types": len(set(
                        source.source_type for source in self.adverse_media_service.sources.values()
                    )) if self.adverse_media_service else 0,
                    "corruption_agencies": len(set(
                        source.agency_type for source in self.corruption_service.sources.values()
                    ))
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive statistics: {e}")
            stats["error"] = str(e)
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all data sources"""
        
        health_status = {
            "overall_status": "HEALTHY",
            "checked_at": datetime.now().isoformat(),
            "services": {},
            "issues": []
        }
        
        try:
            # Check sanctions service
            sanctions_status = await self.sanctions_service.get_source_status()
            health_status["services"]["sanctions"] = {
                "status": "HEALTHY",
                "sources_active": len([s for s in sanctions_status.values() if s["status"] == "active"]),
                "total_sources": len(sanctions_status)
            }
            
            # Check PEP service
            pep_stats = await self.pep_service.get_source_statistics()
            health_status["services"]["pep"] = {
                "status": "HEALTHY",
                "sources_active": pep_stats.get("active_sources", 0),
                "total_sources": pep_stats.get("total_sources", 0)
            }
            
            # Check adverse media service
            if self.adverse_media_service:
                media_stats = await self.adverse_media_service.get_source_statistics()
                health_status["services"]["adverse_media"] = {
                    "status": "HEALTHY",
                    "sources_active": media_stats.get("active_sources", 0),
                    "total_sources": media_stats.get("total_sources", 0)
                }
            else:
                health_status["services"]["adverse_media"] = {
                    "status": "NOT_AVAILABLE",
                    "sources_active": 0,
                    "total_sources": 0
                }
            
            # Check corruption service
            corruption_status = await self.corruption_service.get_source_status()
            health_status["services"]["corruption"] = {
                "status": "HEALTHY",
                "sources_active": len([s for s in corruption_status.values() if s["status"] == "active"]),
                "total_sources": len(corruption_status)
            }
            
            # Check for any issues
            for service_name, service_data in health_status["services"].items():
                if service_data["sources_active"] < service_data["total_sources"]:
                    inactive_count = service_data["total_sources"] - service_data["sources_active"]
                    health_status["issues"].append(f"{service_name}: {inactive_count} sources inactive")
            
            if health_status["issues"]:
                health_status["overall_status"] = "DEGRADED"
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_status["overall_status"] = "UNHEALTHY"
            health_status["error"] = str(e)
        
        return health_status
    
    def get_source_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get all source configurations"""
        
        configs = {}
        for source_id, config in self.source_configs.items():
            configs[source_id] = asdict(config)
        
        return configs
    
    def update_source_configuration(self, source_id: str, **kwargs) -> bool:
        """Update source configuration"""
        
        if source_id not in self.source_configs:
            return False
        
        config = self.source_configs[source_id]
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.logger.info(f"Updated configuration for source {source_id}")
        return True
