"""
Enhanced Data Sources Manager - Sigmanaut Integration
Combines compliant-one data sources with sigmanaut's advanced OSINT and AI capabilities
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

# Import existing data sources
from services.data_sources.sanctions_watchlists import SanctionsWatchlistService
from services.data_sources.pep_data import PEPDataService
from services.data_sources.corruption_data import CorruptionDataService

# Import enhanced capabilities from sigmanaut merge
try:
    from services.osint.osint_collector import MultiSourceOSINTCollector, SourceType
    from services.osint.news_collector import NewsCollector
    from services.ai_engine.nlp_analyzer import AdvancedNLPAnalyzer
    from services.ai_engine.advanced_models import AdvancedModelManager
    from services.data_sources.adverse_media import AdverseMediaMonitor
    from services.compliance.case_management import CaseManagementSystem, CasePriority, CaseCategory
    from services.compliance.risk_rules import CustomRiskRulesEngine
    from services.compliance.automation_engine import AutomationEngine
    ENHANCED_FEATURES_AVAILABLE = True
    logger = get_logger(__name__)
    logger.info("Enhanced features from sigmanaut successfully loaded")
except ImportError as e:
    ENHANCED_FEATURES_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning(f"Enhanced features not available: {e}")

@dataclass
class EnhancedScreeningConfig:
    """Configuration for enhanced screening capabilities"""
    enable_ai_analysis: bool = True
    enable_osint_collection: bool = True
    enable_adverse_media: bool = True
    enable_case_management: bool = True
    enable_automation: bool = True
    sentiment_analysis: bool = True
    anomaly_detection: bool = True
    real_time_monitoring: bool = True

class EnhancedDataSourcesManager:
    """
    Enhanced data sources manager combining compliant-one and sigmanaut capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.config = config or {}
        
        # Initialize base data sources (existing compliant-one)
        self.sanctions_service = SanctionsWatchlistService()
        self.pep_service = PEPDataService()
        self.corruption_service = CorruptionDataService()
        
        # Initialize enhanced capabilities (from sigmanaut)
        if ENHANCED_FEATURES_AVAILABLE:
            self._initialize_enhanced_services()
        else:
            self.logger.warning("Enhanced features not available - running in basic mode")
            
        self.screening_config = EnhancedScreeningConfig()
        self.logger.info("Enhanced Data Sources Manager initialized")
    
    def _initialize_enhanced_services(self):
        """Initialize enhanced services from sigmanaut integration"""
        try:
            # OSINT Collection
            self.osint_collector = MultiSourceOSINTCollector(self.config)
            self.news_collector = NewsCollector()
            
            # AI & NLP
            self.nlp_analyzer = AdvancedNLPAnalyzer(self.config)
            self.model_manager = AdvancedModelManager(self.config)
            
            # Enhanced Adverse Media
            self.adverse_media_monitor = AdverseMediaMonitor(self.config)
            
            # Case Management
            self.case_management = CaseManagementSystem(self.config)
            
            # Risk Rules Engine
            self.risk_rules = CustomRiskRulesEngine(self.config)
            
            # Automation Engine
            self.automation_engine = AutomationEngine(self.config)
            
            self.logger.info("All enhanced services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced services: {e}")
            raise
    
    async def enhanced_entity_screening(self, entity_name: str, 
                                      entity_type: str = "person",
                                      screening_config: Optional[EnhancedScreeningConfig] = None) -> Dict[str, Any]:
        """
        Perform enhanced entity screening with AI and OSINT capabilities
        """
        config = screening_config or self.screening_config
        
        self.logger.info(f"Starting enhanced screening for entity: {entity_name}")
        
        screening_results = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "screening_date": datetime.now().isoformat(),
            "screening_type": "enhanced",
            "basic_results": {},
            "enhanced_results": {},
            "ai_analysis": {},
            "risk_assessment": {},
            "case_recommendations": {}
        }
        
        try:
            # 1. Basic screening (existing compliant-one functionality)
            basic_results = await self._perform_basic_screening(entity_name)
            screening_results["basic_results"] = basic_results
            
            if not ENHANCED_FEATURES_AVAILABLE:
                return screening_results
            
            # 2. Enhanced OSINT collection
            if config.enable_osint_collection:
                osint_results = await self._perform_osint_screening(entity_name)
                screening_results["enhanced_results"]["osint"] = osint_results
            
            # 3. Advanced adverse media monitoring
            if config.enable_adverse_media:
                media_results = await self._perform_enhanced_media_screening(entity_name)
                screening_results["enhanced_results"]["adverse_media"] = media_results
            
            # 4. AI-powered analysis
            if config.enable_ai_analysis:
                ai_results = await self._perform_ai_analysis(entity_name, screening_results)
                screening_results["ai_analysis"] = ai_results
            
            # 5. Enhanced risk assessment
            risk_assessment = await self._calculate_enhanced_risk(screening_results, config)
            screening_results["risk_assessment"] = risk_assessment
            
            # 6. Case management recommendations
            if config.enable_case_management:
                case_recommendations = await self._generate_case_recommendations(screening_results)
                screening_results["case_recommendations"] = case_recommendations
            
            # 7. Trigger automation if configured
            if config.enable_automation:
                await self._trigger_automation_workflows(screening_results)
            
            self.logger.info(f"Enhanced screening completed for {entity_name}")
            
        except Exception as e:
            self.logger.error(f"Enhanced screening failed for {entity_name}: {e}")
            screening_results["error"] = str(e)
        
        return screening_results
    
    async def _perform_basic_screening(self, entity_name: str) -> Dict[str, Any]:
        """Perform basic screening using existing services"""
        
        basic_results = {
            "sanctions": {},
            "pep": {},
            "corruption": {}
        }
        
        try:
            # Sanctions screening
            sanctions_matches = await self.sanctions_service.search_sanctions(entity_name)
            basic_results["sanctions"] = {
                "matches_found": len(sanctions_matches),
                "matches": sanctions_matches
            }
            
            # PEP screening
            pep_matches = await self.pep_service.search_peps(entity_name)
            basic_results["pep"] = {
                "matches_found": len(pep_matches),
                "matches": pep_matches
            }
            
            # Corruption screening
            corruption_matches = await self.corruption_service.search_corruption_cases(entity_name)
            basic_results["corruption"] = {
                "cases_found": len(corruption_matches),
                "cases": corruption_matches
            }
            
        except Exception as e:
            self.logger.error(f"Basic screening failed: {e}")
            basic_results["error"] = str(e)
        
        return basic_results
    
    async def _perform_osint_screening(self, entity_name: str) -> Dict[str, Any]:
        """Perform enhanced OSINT screening"""
        
        osint_results = {
            "news_intelligence": {},
            "social_media": {},
            "public_records": {},
            "financial_intelligence": {}
        }
        
        try:
            # News intelligence collection
            news_data = await self.news_collector.get_google_news(
                query=f'"{entity_name}" compliance risk sanctions',
                max_results=50
            )
            osint_results["news_intelligence"] = {
                "articles_found": len(news_data),
                "articles": news_data[:10]  # Limit for response size
            }
            
            # Multi-source OSINT collection
            osint_data = await self.osint_collector.collect_entity_intelligence(
                entity_name, 
                source_types=[SourceType.NEWS, SourceType.PUBLIC_RECORDS, SourceType.FINANCIAL]
            )
            osint_results.update(osint_data)
            
        except Exception as e:
            self.logger.error(f"OSINT screening failed: {e}")
            osint_results["error"] = str(e)
        
        return osint_results
    
    async def _perform_enhanced_media_screening(self, entity_name: str) -> Dict[str, Any]:
        """Perform enhanced adverse media screening"""
        
        media_results = {
            "adverse_alerts": [],
            "sentiment_analysis": {},
            "risk_categories": [],
            "media_coverage_summary": {}
        }
        
        try:
            # Monitor adverse media
            self.adverse_media_monitor.add_entity(entity_name)
            alerts = await self.adverse_media_monitor.scan_for_adverse_media([entity_name])
            
            media_results["adverse_alerts"] = [asdict(alert) for alert in alerts]
            
            # Sentiment analysis
            if alerts:
                sentiment_data = await self.nlp_analyzer.analyze_sentiment_batch(
                    [alert.content_snippet for alert in alerts]
                )
                media_results["sentiment_analysis"] = sentiment_data
            
        except Exception as e:
            self.logger.error(f"Enhanced media screening failed: {e}")
            media_results["error"] = str(e)
        
        return media_results
    
    async def _perform_ai_analysis(self, entity_name: str, screening_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI-powered analysis on screening results"""
        
        ai_results = {
            "anomaly_detection": {},
            "pattern_analysis": {},
            "predictive_risk": {},
            "text_analysis": {}
        }
        
        try:
            # Anomaly detection on collected data
            all_data = []
            for category, data in screening_results.get("basic_results", {}).items():
                if isinstance(data, dict) and "matches" in data:
                    all_data.extend(data["matches"])
            
            if all_data:
                anomalies = await self.model_manager.detect_anomalies(all_data)
                ai_results["anomaly_detection"] = anomalies
            
            # NLP analysis on text content
            text_content = []
            for category, data in screening_results.get("enhanced_results", {}).items():
                if isinstance(data, dict):
                    if "articles" in data:
                        text_content.extend([article.get("content", "") for article in data["articles"]])
            
            if text_content:
                nlp_analysis = await self.nlp_analyzer.comprehensive_analysis(text_content)
                ai_results["text_analysis"] = nlp_analysis
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            ai_results["error"] = str(e)
        
        return ai_results
    
    async def _calculate_enhanced_risk(self, screening_results: Dict[str, Any], 
                                     config: EnhancedScreeningConfig) -> Dict[str, Any]:
        """Calculate enhanced risk assessment with AI insights"""
        
        risk_assessment = {
            "overall_risk_score": 0.0,
            "risk_level": "LOW",
            "risk_factors": {},
            "ai_risk_indicators": {},
            "recommendation": "",
            "confidence_score": 0.0
        }
        
        try:
            # Basic risk factors (existing logic)
            basic_risk = self._calculate_basic_risk_factors(screening_results.get("basic_results", {}))
            risk_assessment["risk_factors"].update(basic_risk)
            
            # Enhanced risk factors
            enhanced_risk = self._calculate_enhanced_risk_factors(screening_results.get("enhanced_results", {}))
            risk_assessment["risk_factors"].update(enhanced_risk)
            
            # AI risk indicators
            ai_risk = self._calculate_ai_risk_indicators(screening_results.get("ai_analysis", {}))
            risk_assessment["ai_risk_indicators"] = ai_risk
            
            # Calculate overall risk
            overall_score = self._calculate_overall_risk_score(risk_assessment)
            risk_assessment["overall_risk_score"] = overall_score
            risk_assessment["risk_level"] = self._determine_risk_level(overall_score)
            risk_assessment["recommendation"] = self._get_enhanced_recommendation(risk_assessment)
            
        except Exception as e:
            self.logger.error(f"Enhanced risk calculation failed: {e}")
            risk_assessment["error"] = str(e)
        
        return risk_assessment
    
    def _calculate_basic_risk_factors(self, basic_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk factors from basic screening"""
        risk_factors = {}
        
        # Sanctions risk
        sanctions_data = basic_results.get("sanctions", {})
        if sanctions_data.get("matches_found", 0) > 0:
            risk_factors["sanctions_risk"] = 1.0
        else:
            risk_factors["sanctions_risk"] = 0.0
        
        # PEP risk
        pep_data = basic_results.get("pep", {})
        if pep_data.get("matches_found", 0) > 0:
            risk_factors["pep_risk"] = 0.6
        else:
            risk_factors["pep_risk"] = 0.0
        
        # Corruption risk
        corruption_data = basic_results.get("corruption", {})
        if corruption_data.get("cases_found", 0) > 0:
            risk_factors["corruption_risk"] = 0.9
        else:
            risk_factors["corruption_risk"] = 0.0
        
        return risk_factors
    
    def _calculate_enhanced_risk_factors(self, enhanced_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk factors from enhanced screening"""
        risk_factors = {}
        
        # OSINT risk
        osint_data = enhanced_results.get("osint", {})
        news_articles = osint_data.get("news_intelligence", {}).get("articles_found", 0)
        if news_articles > 5:
            risk_factors["osint_risk"] = 0.4
        elif news_articles > 0:
            risk_factors["osint_risk"] = 0.2
        else:
            risk_factors["osint_risk"] = 0.0
        
        # Adverse media risk
        media_data = enhanced_results.get("adverse_media", {})
        adverse_alerts = len(media_data.get("adverse_alerts", []))
        if adverse_alerts > 3:
            risk_factors["adverse_media_risk"] = 0.8
        elif adverse_alerts > 0:
            risk_factors["adverse_media_risk"] = 0.4
        else:
            risk_factors["adverse_media_risk"] = 0.0
        
        return risk_factors
    
    def _calculate_ai_risk_indicators(self, ai_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate AI-based risk indicators"""
        ai_risk = {}
        
        # Anomaly detection risk
        anomalies = ai_analysis.get("anomaly_detection", {})
        if isinstance(anomalies, dict) and anomalies.get("anomalies_detected", 0) > 0:
            ai_risk["anomaly_risk"] = 0.7
        else:
            ai_risk["anomaly_risk"] = 0.0
        
        # Text analysis risk
        text_analysis = ai_analysis.get("text_analysis", {})
        if isinstance(text_analysis, dict):
            sentiment = text_analysis.get("overall_sentiment", {})
            if sentiment.get("negative_score", 0) > 0.7:
                ai_risk["sentiment_risk"] = 0.6
            else:
                ai_risk["sentiment_risk"] = 0.0
        
        return ai_risk
    
    def _calculate_overall_risk_score(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        risk_factors = risk_assessment.get("risk_factors", {})
        ai_indicators = risk_assessment.get("ai_risk_indicators", {})
        
        # Weights for different risk types
        weights = {
            "sanctions_risk": 0.3,
            "pep_risk": 0.15,
            "corruption_risk": 0.2,
            "osint_risk": 0.1,
            "adverse_media_risk": 0.15,
            "anomaly_risk": 0.05,
            "sentiment_risk": 0.05
        }
        
        overall_score = 0.0
        for factor, weight in weights.items():
            if factor in risk_factors:
                overall_score += risk_factors[factor] * weight
            elif factor in ai_indicators:
                overall_score += ai_indicators[factor] * weight
        
        return min(overall_score, 1.0)  # Cap at 1.0
    
    def _determine_risk_level(self, overall_score: float) -> str:
        """Determine risk level from overall score"""
        if overall_score >= 0.8:
            return "CRITICAL"
        elif overall_score >= 0.6:
            return "HIGH"
        elif overall_score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_enhanced_recommendation(self, risk_assessment: Dict[str, Any]) -> str:
        """Get enhanced recommendation based on risk assessment"""
        risk_level = risk_assessment.get("risk_level", "LOW")
        ai_indicators = risk_assessment.get("ai_risk_indicators", {})
        
        if risk_level == "CRITICAL":
            return "REJECT: Critical risk factors identified. Immediate escalation required."
        elif risk_level == "HIGH":
            base_rec = "ENHANCED DUE DILIGENCE: High risk factors present."
            if ai_indicators.get("anomaly_risk", 0) > 0.5:
                base_rec += " AI anomaly detection triggered - recommend expert review."
            return base_rec
        elif risk_level == "MEDIUM":
            return "STANDARD DUE DILIGENCE: Medium risk factors present. Monitor ongoing."
        else:
            return "PROCEED: Low risk profile. Standard onboarding may proceed."
    
    async def _generate_case_recommendations(self, screening_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate case management recommendations"""
        
        recommendations = {
            "should_create_case": False,
            "case_priority": "LOW",
            "case_category": "ROUTINE_SCREENING",
            "recommended_actions": [],
            "review_timeline": "30_DAYS"
        }
        
        try:
            risk_level = screening_results.get("risk_assessment", {}).get("risk_level", "LOW")
            
            if risk_level in ["CRITICAL", "HIGH"]:
                recommendations["should_create_case"] = True
                recommendations["case_priority"] = "HIGH" if risk_level == "CRITICAL" else "MEDIUM"
                recommendations["case_category"] = "HIGH_RISK_ENTITY"
                recommendations["recommended_actions"] = [
                    "Immediate senior review required",
                    "Enhanced due diligence investigation",
                    "Document decision rationale",
                    "Monitor for ongoing developments"
                ]
                recommendations["review_timeline"] = "7_DAYS"
            
            elif risk_level == "MEDIUM":
                recommendations["should_create_case"] = True
                recommendations["case_priority"] = "MEDIUM"
                recommendations["case_category"] = "MEDIUM_RISK_ENTITY"
                recommendations["recommended_actions"] = [
                    "Standard due diligence review",
                    "Document findings",
                    "Set monitoring schedule"
                ]
                recommendations["review_timeline"] = "14_DAYS"
                
        except Exception as e:
            self.logger.error(f"Case recommendations failed: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def _trigger_automation_workflows(self, screening_results: Dict[str, Any]):
        """Trigger automation workflows based on screening results"""
        
        try:
            risk_level = screening_results.get("risk_assessment", {}).get("risk_level", "LOW")
            
            if risk_level == "CRITICAL":
                # Trigger immediate alert workflow
                await self.automation_engine.trigger_workflow("critical_risk_alert", {
                    "entity_name": screening_results.get("entity_name"),
                    "risk_level": risk_level,
                    "screening_results": screening_results
                })
            
            # Create case if recommended
            case_rec = screening_results.get("case_recommendations", {})
            if case_rec.get("should_create_case", False):
                await self.case_management.create_case_from_screening(screening_results)
                
        except Exception as e:
            self.logger.error(f"Automation workflow failed: {e}")
    
    async def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics including enhanced capabilities"""
        
        stats = {
            "generated_at": datetime.now().isoformat(),
            "basic_services": {},
            "enhanced_services": {},
            "ai_capabilities": {},
            "summary": {}
        }
        
        try:
            # Basic service statistics
            stats["basic_services"] = {
                "sanctions": self.sanctions_service.get_statistics(),
                "pep": await self.pep_service.get_source_statistics(),
                "corruption": await self.corruption_service.get_corruption_statistics()
            }
            
            if ENHANCED_FEATURES_AVAILABLE:
                # Enhanced service statistics
                stats["enhanced_services"] = {
                    "osint_sources": await self.osint_collector.get_source_statistics(),
                    "case_management": await self.case_management.get_case_statistics(),
                    "risk_rules": self.risk_rules.get_rules_statistics(),
                    "automation": await self.automation_engine.get_workflow_statistics()
                }
                
                # AI capabilities status
                stats["ai_capabilities"] = {
                    "nlp_models_loaded": await self.nlp_analyzer.get_model_status(),
                    "advanced_models": await self.model_manager.get_model_status(),
                    "features_available": True
                }
            else:
                stats["enhanced_services"] = {"status": "not_available"}
                stats["ai_capabilities"] = {"features_available": False}
            
            # Summary
            total_sources = (
                stats["basic_services"]["sanctions"].get("total_sources", 0) +
                stats["basic_services"]["pep"].get("total_sources", 0) +
                len(self.corruption_service.sources)
            )
            
            if ENHANCED_FEATURES_AVAILABLE:
                total_sources += stats["enhanced_services"]["osint_sources"].get("total_sources", 0)
            
            stats["summary"] = {
                "total_data_sources": total_sources,
                "enhanced_features_available": ENHANCED_FEATURES_AVAILABLE,
                "services_active": 3 + (4 if ENHANCED_FEATURES_AVAILABLE else 0),
                "ai_powered": ENHANCED_FEATURES_AVAILABLE
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced statistics failed: {e}")
            stats["error"] = str(e)
        
        return stats

# Backward compatibility - maintain existing interface
class DataSourcesManager(EnhancedDataSourcesManager):
    """Backward compatible interface"""
    
    async def comprehensive_entity_screening(self, entity_name: str, entity_type: str = "person") -> Dict[str, Any]:
        """Maintain backward compatibility while using enhanced screening"""
        return await self.enhanced_entity_screening(entity_name, entity_type)
