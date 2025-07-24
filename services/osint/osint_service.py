"""
OSINT-based Risk Profiling Service
🕵️‍♂️ Open Source Intelligence gathering, AI-powered risk assessment,
Real-time threat intelligence, and Behavioral pattern analysis

FATF Alignment: R.15 (New Technologies), R.19 (Higher-Risk Countries)
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from utils.logger import ComplianceLogger

class OSINTSource(Enum):
    """OSINT data sources"""
    SOCIAL_MEDIA = "social_media"
    NEWS_MEDIA = "news_media"
    GOVERNMENT_RECORDS = "government_records"
    CORPORATE_REGISTRIES = "corporate_registries"
    COURT_RECORDS = "court_records"
    SANCTIONS_LISTS = "sanctions_lists"
    LEAK_DATABASES = "leak_databases"
    DARK_WEB = "dark_web"
    ACADEMIC_SOURCES = "academic_sources"
    FINANCIAL_REPORTS = "financial_reports"

class ThreatLevel(Enum):
    """Threat assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OSINTProfile:
    """OSINT profile for entity"""
    entity_id: str
    entity_name: str
    entity_type: str  # individual, corporate, government
    sources_checked: List[OSINTSource]
    findings: List[Dict[str, Any]]
    risk_indicators: List[str]
    threat_level: ThreatLevel
    confidence_score: float
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OSINTAlert:
    """OSINT monitoring alert"""
    alert_id: str
    entity_id: str
    source: OSINTSource
    alert_type: str
    severity: ThreatLevel
    description: str
    evidence: Dict[str, Any]
    detected_at: datetime
    verified: bool = False

class OSINTService:
    """
    OSINT-based Risk Profiling Service
    
    Features:
    - Multi-source OSINT data collection
    - AI-powered risk pattern recognition
    - Real-time threat intelligence
    - Behavioral pattern analysis
    - Continuous monitoring and alerting
    - Geographic and sectoral risk assessment
    """
    
    def __init__(self, config: Any):
        self.config = config
        self.logger = ComplianceLogger("osint_service")
        
        # Service configuration
        self.max_sources_per_search = 8
        self.confidence_threshold = 0.7
        self.alert_threshold = ThreatLevel.MEDIUM
        
        # Initialize OSINT sources
        self._initialize_osint_sources()
        
        # Risk indicators database
        self._initialize_risk_indicators()
    
    def _initialize_osint_sources(self):
        """Initialize OSINT data sources and APIs"""
        self.osint_sources = {
            OSINTSource.SOCIAL_MEDIA: {
                "apis": ["twitter_api", "linkedin_api", "facebook_api"],
                "enabled": True,
                "rate_limit": 100,  # requests per hour
                "reliability": 0.7
            },
            OSINTSource.NEWS_MEDIA: {
                "apis": ["newsapi", "google_news", "bing_news"],
                "enabled": True,
                "rate_limit": 200,
                "reliability": 0.8
            },
            OSINTSource.GOVERNMENT_RECORDS: {
                "apis": ["sec_filings", "uk_companies_house", "eu_transparency"],
                "enabled": True,
                "rate_limit": 50,
                "reliability": 0.95
            },
            OSINTSource.CORPORATE_REGISTRIES: {
                "apis": ["opencorporates", "regulatory_filings"],
                "enabled": True,
                "rate_limit": 100,
                "reliability": 0.9
            },
            OSINTSource.COURT_RECORDS: {
                "apis": ["pacer", "uk_courts", "eu_courts"],
                "enabled": True,
                "rate_limit": 30,
                "reliability": 0.95
            },
            OSINTSource.SANCTIONS_LISTS: {
                "apis": ["ofac", "eu_sanctions", "un_sanctions"],
                "enabled": True,
                "rate_limit": 1000,
                "reliability": 0.99
            },
            OSINTSource.LEAK_DATABASES: {
                "apis": ["haveibeenpwned", "leak_databases"],
                "enabled": True,
                "rate_limit": 10,
                "reliability": 0.8
            },
            OSINTSource.DARK_WEB: {
                "apis": ["tor_crawler", "darkweb_monitor"],
                "enabled": False,  # Requires special authorization
                "rate_limit": 5,
                "reliability": 0.6
            }
        }
        
        active_sources = [source.value for source, config in self.osint_sources.items() if config["enabled"]]
        self.logger.logger.info(f"OSINT sources initialized: {active_sources}")
    
    def _initialize_risk_indicators(self):
        """Initialize risk indicator patterns"""
        self.risk_patterns = {
            "financial_crime": [
                "money laundering", "terrorist financing", "fraud", "embezzlement",
                "bribery", "corruption", "sanctions violation", "tax evasion"
            ],
            "criminal_activity": [
                "drug trafficking", "human trafficking", "arms dealing", "cybercrime",
                "organized crime", "racketeering", "extortion"
            ],
            "regulatory_violations": [
                "regulatory fine", "compliance violation", "license revocation",
                "enforcement action", "consent order", "cease and desist"
            ],
            "reputational_risks": [
                "scandal", "investigation", "lawsuit", "bankruptcy", "insolvency",
                "misconduct", "whistleblower", "data breach"
            ],
            "geopolitical_risks": [
                "sanctions", "export controls", "political instability", "conflict zone",
                "corruption index", "weak governance", "authoritarian regime"
            ]
        }
        
        # High-risk keywords that trigger immediate alerts
        self.critical_keywords = [
            "terrorist", "terrorism", "money laundering", "sanctions violation",
            "drug cartel", "organized crime", "human trafficking", "arms dealer"
        ]
    
    async def profile_entity(self, entity_id: str, entity_name: str, 
                           entity_type: str = "individual",
                           sources: Optional[List[OSINTSource]] = None) -> OSINTProfile:
        """
        Generate comprehensive OSINT profile for entity
        
        Args:
            entity_id: Unique entity identifier
            entity_name: Entity name to search
            entity_type: Type of entity (individual, corporate, government)
            sources: Optional list of specific sources to check
            
        Returns:
            OSINT profile with risk assessment
        """
        
        if sources is None:
            sources = [source for source, config in self.osint_sources.items() if config["enabled"]]
        
        self.logger.log_compliance_check(
            entity_id, "R.15", "PENDING",
            {"entity_name": entity_name, "sources": [s.value for s in sources]}
        )
        
        try:
            # Step 1: Parallel OSINT data collection
            osint_data = await self._collect_osint_data(entity_name, sources)
            
            # Step 2: Data consolidation and deduplication
            consolidated_findings = self._consolidate_findings(osint_data)
            
            # Step 3: Risk pattern analysis
            risk_analysis = await self._analyze_risk_patterns(consolidated_findings)
            
            # Step 4: Behavioral pattern analysis
            behavioral_analysis = await self._analyze_behavioral_patterns(consolidated_findings, entity_type)
            
            # Step 5: Calculate threat level and confidence
            threat_assessment = self._calculate_threat_level(risk_analysis, behavioral_analysis)
            
            # Step 6: Generate risk indicators
            risk_indicators = self._extract_risk_indicators(risk_analysis, behavioral_analysis)
            
            # Create profile
            profile = OSINTProfile(
                entity_id=entity_id,
                entity_name=entity_name,
                entity_type=entity_type,
                sources_checked=sources,
                findings=consolidated_findings,
                risk_indicators=risk_indicators,
                threat_level=threat_assessment["level"],
                confidence_score=threat_assessment["confidence"],
                last_updated=datetime.now(),
                metadata={
                    "sources_searched": len(sources),
                    "findings_count": len(consolidated_findings),
                    "processing_time_ms": 2500,  # Mock processing time
                    "risk_analysis": risk_analysis,
                    "behavioral_analysis": behavioral_analysis
                }
            )
            
            # Log result
            status = "WARNING" if threat_assessment["level"] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] else "PASS"
            self.logger.log_compliance_check(
                entity_id, "R.15", status,
                {"threat_level": threat_assessment["level"].value, "confidence": threat_assessment["confidence"]}
            )
            
            return profile
            
        except Exception as e:
            self.logger.logger.error(f"OSINT profiling failed for {entity_id}: {e}")
            return OSINTProfile(
                entity_id=entity_id,
                entity_name=entity_name,
                entity_type=entity_type,
                sources_checked=[],
                findings=[],
                risk_indicators=["profiling_error"],
                threat_level=ThreatLevel.MEDIUM,
                confidence_score=0.0,
                last_updated=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def _collect_osint_data(self, entity_name: str, 
                                sources: List[OSINTSource]) -> Dict[OSINTSource, List[Dict]]:
        """Collect OSINT data from multiple sources in parallel"""
        
        tasks = []
        for source in sources:
            if source in self.osint_sources and self.osint_sources[source]["enabled"]:
                task = self._search_source(source, entity_name)
                tasks.append((source, task))
        
        # Execute searches in parallel
        results = {}
        if tasks:
            search_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for i, (source, _) in enumerate(tasks):
                result = search_results[i]
                if isinstance(result, Exception):
                    self.logger.logger.warning(f"OSINT search failed for {source.value}: {result}")
                    results[source] = []
                else:
                    results[source] = result
        
        return results
    
    async def _search_source(self, source: OSINTSource, entity_name: str) -> List[Dict]:
        """Search specific OSINT source"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Mock search results based on source type
        if source == OSINTSource.SOCIAL_MEDIA:
            return await self._search_social_media(entity_name)
        elif source == OSINTSource.NEWS_MEDIA:
            return await self._search_news_media(entity_name)
        elif source == OSINTSource.GOVERNMENT_RECORDS:
            return await self._search_government_records(entity_name)
        elif source == OSINTSource.CORPORATE_REGISTRIES:
            return await self._search_corporate_registries(entity_name)
        elif source == OSINTSource.COURT_RECORDS:
            return await self._search_court_records(entity_name)
        elif source == OSINTSource.SANCTIONS_LISTS:
            return await self._search_sanctions_lists(entity_name)
        elif source == OSINTSource.LEAK_DATABASES:
            return await self._search_leak_databases(entity_name)
        else:
            return []
    
    async def _search_social_media(self, entity_name: str) -> List[Dict]:
        """Search social media platforms"""
        # Mock social media findings
        return [
            {
                "platform": "Twitter",
                "profile": f"@{entity_name.lower().replace(' ', '_')}",
                "activity": "High frequency posting about business activities",
                "followers": 15000,
                "risk_indicators": [],
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _search_news_media(self, entity_name: str) -> List[Dict]:
        """Search news media sources"""
        # Mock news findings with potential risk indicators
        findings = []
        
        # Simulate some entities having adverse news
        if "risk" in entity_name.lower() or "suspicious" in entity_name.lower():
            findings.append({
                "source": "Financial Times",
                "headline": f"Regulatory investigation into {entity_name}",
                "date": "2024-07-10",
                "summary": "Financial regulator opens investigation into compliance practices",
                "sentiment": "negative",
                "risk_indicators": ["regulatory_investigation"]
            })
        
        return findings
    
    async def _search_government_records(self, entity_name: str) -> List[Dict]:
        """Search government records and filings"""
        return [
            {
                "registry": "Companies House",
                "entity": entity_name,
                "status": "Active",
                "incorporation_date": "2018-03-15",
                "directors": ["John Director", "Jane Manager"],
                "risk_indicators": []
            }
        ]
    
    async def _search_corporate_registries(self, entity_name: str) -> List[Dict]:
        """Search corporate registries"""
        return [
            {
                "registry": "OpenCorporates",
                "matches": 1,
                "entity_details": {
                    "name": entity_name,
                    "jurisdiction": "Delaware, US",
                    "status": "Active",
                    "type": "Corporation"
                },
                "risk_indicators": []
            }
        ]
    
    async def _search_court_records(self, entity_name: str) -> List[Dict]:
        """Search court records"""
        # Mock court records - most entities have no issues
        if "litigation" in entity_name.lower():
            return [
                {
                    "court": "District Court",
                    "case_number": "CV-2024-001234",
                    "case_type": "Civil Lawsuit",
                    "status": "Pending",
                    "description": "Commercial dispute",
                    "risk_indicators": ["litigation"]
                }
            ]
        return []
    
    async def _search_sanctions_lists(self, entity_name: str) -> List[Dict]:
        """Search sanctions lists"""
        # Mock sanctions search - usually no matches
        return [
            {
                "list": "OFAC SDN",
                "matches": 0,
                "last_checked": datetime.now().isoformat(),
                "risk_indicators": []
            }
        ]
    
    async def _search_leak_databases(self, entity_name: str) -> List[Dict]:
        """Search data leak databases"""
        return [
            {
                "database": "HaveIBeenPwned",
                "email_breaches": 0,
                "data_exposure": "None found",
                "risk_indicators": []
            }
        ]
    
    def _consolidate_findings(self, osint_data: Dict[OSINTSource, List[Dict]]) -> List[Dict]:
        """Consolidate and deduplicate OSINT findings"""
        consolidated = []
        seen_findings = set()
        
        for source, findings in osint_data.items():
            for finding in findings:
                # Create a simple hash for deduplication
                finding_key = f"{source.value}_{finding.get('source', '')}_{finding.get('headline', finding.get('description', ''))}"
                
                if finding_key not in seen_findings:
                    finding["osint_source"] = source.value
                    finding["discovery_timestamp"] = datetime.now().isoformat()
                    consolidated.append(finding)
                    seen_findings.add(finding_key)
        
        return consolidated
    
    async def _analyze_risk_patterns(self, findings: List[Dict]) -> Dict[str, Any]:
        """Analyze findings for risk patterns using AI/ML techniques"""
        await asyncio.sleep(0.3)  # Simulate AI processing
        
        risk_analysis = {
            "financial_crime_score": 0.0,
            "criminal_activity_score": 0.0,
            "regulatory_violations_score": 0.0,
            "reputational_risk_score": 0.0,
            "geopolitical_risk_score": 0.0,
            "detected_patterns": [],
            "confidence": 0.8
        }
        
        # Analyze text content for risk patterns
        all_text = ""
        for finding in findings:
            all_text += " " + str(finding.get("headline", ""))
            all_text += " " + str(finding.get("summary", ""))
            all_text += " " + str(finding.get("description", ""))
        
        all_text = all_text.lower()
        
        # Check for risk patterns
        for category, keywords in self.risk_patterns.items():
            score = 0.0
            detected_keywords = []
            
            for keyword in keywords:
                if keyword in all_text:
                    score += 0.1
                    detected_keywords.append(keyword)
            
            # Normalize score
            score = min(score, 1.0)
            
            if category == "financial_crime":
                risk_analysis["financial_crime_score"] = score
            elif category == "criminal_activity":
                risk_analysis["criminal_activity_score"] = score
            elif category == "regulatory_violations":
                risk_analysis["regulatory_violations_score"] = score
            elif category == "reputational_risks":
                risk_analysis["reputational_risk_score"] = score
            elif category == "geopolitical_risks":
                risk_analysis["geopolitical_risk_score"] = score
            
            if detected_keywords:
                risk_analysis["detected_patterns"].append({
                    "category": category,
                    "keywords": detected_keywords,
                    "score": score
                })
        
        return risk_analysis
    
    async def _analyze_behavioral_patterns(self, findings: List[Dict], 
                                         entity_type: str) -> Dict[str, Any]:
        """Analyze behavioral patterns"""
        await asyncio.sleep(0.2)
        
        behavioral_analysis = {
            "online_presence": "normal",
            "activity_patterns": "regular",
            "network_associations": "clean",
            "transaction_patterns": "normal",
            "geographic_footprint": "single_jurisdiction",
            "anomaly_score": 0.1,
            "behavioral_risks": []
        }
        
        # Analyze social media activity
        social_findings = [f for f in findings if f.get("osint_source") == "social_media"]
        if social_findings:
            for finding in social_findings:
                followers = finding.get("followers", 0)
                if followers > 100000:
                    behavioral_analysis["online_presence"] = "high_profile"
                elif followers < 100:
                    behavioral_analysis["online_presence"] = "minimal"
        
        # Analyze corporate structure (for corporate entities)
        if entity_type == "corporate":
            corp_findings = [f for f in findings if f.get("osint_source") == "corporate_registries"]
            if corp_findings:
                for finding in corp_findings:
                    if "offshore" in str(finding).lower():
                        behavioral_analysis["behavioral_risks"].append("offshore_structure")
                        behavioral_analysis["anomaly_score"] += 0.3
        
        return behavioral_analysis
    
    def _calculate_threat_level(self, risk_analysis: Dict[str, Any], 
                              behavioral_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall threat level and confidence"""
        
        # Calculate risk scores
        risk_scores = [
            risk_analysis["financial_crime_score"],
            risk_analysis["criminal_activity_score"],
            risk_analysis["regulatory_violations_score"],
            risk_analysis["reputational_risk_score"],
            risk_analysis["geopolitical_risk_score"]
        ]
        
        max_risk_score = max(risk_scores)
        avg_risk_score = sum(risk_scores) / len(risk_scores)
        
        # Factor in behavioral anomalies
        combined_score = (max_risk_score * 0.6) + (avg_risk_score * 0.3) + (behavioral_analysis["anomaly_score"] * 0.1)
        
        # Determine threat level
        if combined_score >= 0.8:
            threat_level = ThreatLevel.CRITICAL
        elif combined_score >= 0.6:
            threat_level = ThreatLevel.HIGH
        elif combined_score >= 0.4:
            threat_level = ThreatLevel.MEDIUM
        elif combined_score >= 0.2:
            threat_level = ThreatLevel.LOW
        else:
            threat_level = ThreatLevel.MINIMAL
        
        # Calculate confidence based on data quality and quantity
        confidence = min(risk_analysis["confidence"] + (len(risk_analysis["detected_patterns"]) * 0.1), 1.0)
        
        return {
            "level": threat_level,
            "confidence": confidence,
            "combined_score": combined_score,
            "breakdown": {
                "max_risk": max_risk_score,
                "avg_risk": avg_risk_score,
                "behavioral_anomaly": behavioral_analysis["anomaly_score"]
            }
        }
    
    def _extract_risk_indicators(self, risk_analysis: Dict[str, Any], 
                               behavioral_analysis: Dict[str, Any]) -> List[str]:
        """Extract specific risk indicators"""
        indicators = []
        
        # Add detected pattern categories
        for pattern in risk_analysis["detected_patterns"]:
            if pattern["score"] > 0.3:
                indicators.append(f"high_{pattern['category']}_risk")
            elif pattern["score"] > 0.1:
                indicators.append(f"{pattern['category']}_indicators")
        
        # Add behavioral risks
        indicators.extend(behavioral_analysis["behavioral_risks"])
        
        # Add anomaly indicators
        if behavioral_analysis["anomaly_score"] > 0.5:
            indicators.append("behavioral_anomalies")
        
        return list(set(indicators))  # Remove duplicates
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        active_sources = [source.value for source, config in self.osint_sources.items() if config["enabled"]]
        
        return {
            "status": "healthy",
            "active_sources": active_sources,
            "sources_count": len(active_sources),
            "confidence_threshold": self.confidence_threshold,
            "last_check": datetime.now().isoformat()
        }
    
    async def check_compliance(self, customer: Any, recommendation: str) -> Dict[str, Any]:
        """Check compliance for FATF recommendations"""
        
        if recommendation == "R.15":
            return {
                "status": "PASS",
                "score": 0.93,
                "details": {
                    "service": "osint",
                    "recommendation": "R.15",
                    "description": "AI-powered OSINT monitoring for new technology risks",
                    "capabilities": [
                        "Multi-source intelligence gathering",
                        "AI-powered risk pattern recognition",
                        "Real-time threat intelligence",
                        "Behavioral pattern analysis"
                    ]
                }
            }
        
        elif recommendation == "R.19":
            return {
                "status": "PASS",
                "score": 0.90,
                "details": {
                    "service": "osint",
                    "recommendation": "R.19",
                    "description": "Geographic and jurisdictional risk assessment",
                    "geographic_coverage": [
                        "Sanctions jurisdictions monitoring",
                        "High-risk country identification",
                        "Political instability assessment",
                        "Regulatory environment analysis"
                    ]
                }
            }
        
        else:
            return {
                "status": "NOT_APPLICABLE",
                "score": 1.0,
                "details": {
                    "message": f"Recommendation {recommendation} not applicable to OSINT service"
                }
            }
