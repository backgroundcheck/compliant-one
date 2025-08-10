"""
Anti-Corruption Compliance Automation for Compliant.one
Automated sanctions screening, PEP monitoring, and adverse media detection
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import re
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

class ScreeningResult(Enum):
    """Screening result types"""
    CLEAR = "clear"
    POTENTIAL_MATCH = "potential_match"
    CONFIRMED_MATCH = "confirmed_match"
    REQUIRES_REVIEW = "requires_review"

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    OFAC = "ofac"
    EU_SANCTIONS = "eu_sanctions"
    UN_SANCTIONS = "un_sanctions"
    FATF = "fatf"
    WORLD_BANK_DEBARMENT = "world_bank_debarment"
    PEP_DATABASE = "pep_database"

@dataclass
class ScreeningMatch:
    """Screening match result"""
    entity_name: str
    matched_name: str
    match_score: float
    list_type: str
    list_source: str
    risk_level: str
    additional_info: Dict[str, Any]
    screening_date: datetime

@dataclass
class PEPRecord:
    """Politically Exposed Person record"""
    name: str
    aliases: List[str]
    position: str
    country: str
    jurisdiction: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    risk_category: str
    family_associates: List[str]
    source: str

class ComplianceAutomationEngine:
    """Automated compliance screening and monitoring engine"""
    
    def __init__(self, config):
        self.config = config
        self.sanctions_lists = {}
        self.pep_database = {}
        self.watchlists = {}
        self.adverse_media_sources = []
        self.screening_cache = {}
        
        # Initialize compliance data
        asyncio.create_task(self._initialize_compliance_data())
    
    async def _initialize_compliance_data(self):
        """Initialize compliance databases and watchlists"""
        try:
            logger.info("Initializing compliance data...")
            
            # Load sanctions lists
            await self._load_sanctions_lists()
            
            # Load PEP databases
            await self._load_pep_databases()
            
            # Load internal watchlists
            await self._load_internal_watchlists()
            
            # Setup adverse media sources
            self._setup_adverse_media_sources()
            
            logger.info("Compliance data initialization completed")
            
        except Exception as e:
            logger.error(f"Compliance data initialization failed: {e}")
    
    async def _load_sanctions_lists(self):
        """Load global sanctions lists"""
        # OFAC Sanctions
        self.sanctions_lists[ComplianceFramework.OFAC] = {
            'name': 'OFAC Specially Designated Nationals (SDN)',
            'url': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONS_PUBLIC.XML',
            'last_updated': None,
            'entries': []
        }
        
        # EU Sanctions
        self.sanctions_lists[ComplianceFramework.EU_SANCTIONS] = {
            'name': 'EU Consolidated Sanctions List',
            'url': 'https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content',
            'last_updated': None,
            'entries': []
        }
        
        # UN Sanctions
        self.sanctions_lists[ComplianceFramework.UN_SANCTIONS] = {
            'name': 'UN Security Council Sanctions List',
            'url': 'https://scsanctions.un.org/resources/xml/en/consolidated.xml',
            'last_updated': None,
            'entries': []
        }
        
        # World Bank Debarment
        self.sanctions_lists[ComplianceFramework.WORLD_BANK_DEBARMENT] = {
            'name': 'World Bank Debarment List',
            'url': 'https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_EXPRNCE_MGR/FIRM/DEBARRED',
            'last_updated': None,
            'entries': []
        }
        
        logger.info(f"Loaded {len(self.sanctions_lists)} sanctions list configurations")
    
    async def _load_pep_databases(self):
        """Load PEP (Politically Exposed Persons) databases"""
        # This would integrate with commercial PEP databases
        # For now, we'll use a sample structure
        
        sample_peps = [
            PEPRecord(
                name="John Doe",
                aliases=["J. Doe", "Jonathan Doe"],
                position="Minister of Finance",
                country="Sample Country",
                jurisdiction="Sample Jurisdiction",
                start_date=datetime(2020, 1, 1),
                end_date=None,
                risk_category="high",
                family_associates=["Jane Doe (spouse)"],
                source="Government Directory"
            )
        ]
        
        self.pep_database = {pep.name.lower(): pep for pep in sample_peps}
        logger.info(f"Loaded {len(self.pep_database)} PEP records")
    
    async def _load_internal_watchlists(self):
        """Load internal watchlists and custom screening lists"""
        # Internal high-risk entities
        self.watchlists['internal_high_risk'] = {
            'name': 'Internal High Risk Entities',
            'entries': [],
            'last_updated': datetime.utcnow()
        }
        
        # Custom industry watchlists
        self.watchlists['crypto_exchanges'] = {
            'name': 'High-Risk Crypto Exchanges',
            'entries': [
                {'name': 'Sample Exchange', 'jurisdiction': 'Unknown', 'risk_level': 'high'}
            ],
            'last_updated': datetime.utcnow()
        }
        
        logger.info(f"Loaded {len(self.watchlists)} internal watchlists")
    
    def _setup_adverse_media_sources(self):
        """Setup adverse media monitoring sources"""
        self.adverse_media_sources = [
            {
                'name': 'Reuters',
                'type': 'news',
                'weight': 0.9,
                'keywords': ['fraud', 'corruption', 'bribery', 'sanctions', 'investigation']
            },
            {
                'name': 'Financial Times',
                'type': 'financial_news',
                'weight': 0.85,
                'keywords': ['compliance violation', 'regulatory action', 'fine', 'penalty']
            },
            {
                'name': 'Anti-Corruption Digest',
                'type': 'specialized',
                'weight': 0.95,
                'keywords': ['anti-corruption', 'compliance', 'due diligence']
            }
        ]
    
    async def screen_entity(self, 
                          entity_name: str, 
                          entity_type: str = "individual",
                          additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive entity screening against sanctions, PEP, and watchlists
        
        Args:
            entity_name: Name of entity to screen
            entity_type: Type of entity (individual, organization, vessel, etc.)
            additional_info: Additional information for enhanced screening
            
        Returns:
            Comprehensive screening results
        """
        
        logger.info(f"Screening entity: {entity_name}")
        
        # Check cache first
        cache_key = self._generate_cache_key(entity_name, entity_type, additional_info)
        if cache_key in self.screening_cache:
            cached_result = self.screening_cache[cache_key]
            if (datetime.utcnow() - cached_result['timestamp']).hours < 24:
                logger.debug(f"Returning cached result for {entity_name}")
                return cached_result['result']
        
        screening_results = {
            'entity_name': entity_name,
            'entity_type': entity_type,
            'screening_timestamp': datetime.utcnow().isoformat(),
            'overall_result': ScreeningResult.CLEAR,
            'risk_score': 0.0,
            'matches': [],
            'pep_matches': [],
            'adverse_media': [],
            'recommendations': []
        }
        
        try:
            # Parallel screening tasks
            tasks = [
                self._screen_sanctions_lists(entity_name, entity_type),
                self._screen_pep_database(entity_name, entity_type),
                self._screen_internal_watchlists(entity_name, entity_type),
                self._search_adverse_media(entity_name, entity_type)
            ]
            
            sanctions_matches, pep_matches, watchlist_matches, adverse_media = await asyncio.gather(*tasks)
            
            # Combine results
            all_matches = sanctions_matches + watchlist_matches
            screening_results['matches'] = all_matches
            screening_results['pep_matches'] = pep_matches
            screening_results['adverse_media'] = adverse_media
            
            # Calculate overall risk score and result
            screening_results['risk_score'], screening_results['overall_result'] = self._calculate_screening_risk(
                all_matches, pep_matches, adverse_media
            )
            
            # Generate recommendations
            screening_results['recommendations'] = self._generate_recommendations(
                screening_results['overall_result'],
                screening_results['risk_score'],
                all_matches,
                pep_matches,
                adverse_media
            )
            
            # Cache result
            self.screening_cache[cache_key] = {
                'result': screening_results,
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"Screening completed for {entity_name}: {screening_results['overall_result'].value}")
            return screening_results
            
        except Exception as e:
            logger.error(f"Entity screening error for {entity_name}: {e}")
            screening_results['error'] = str(e)
            return screening_results
    
    async def _screen_sanctions_lists(self, entity_name: str, entity_type: str) -> List[ScreeningMatch]:
        """Screen against global sanctions lists"""
        matches = []
        
        for framework, sanctions_list in self.sanctions_lists.items():
            try:
                # Fuzzy matching against sanctions entries
                list_matches = self._fuzzy_match_sanctions(entity_name, sanctions_list)
                
                for match in list_matches:
                    screening_match = ScreeningMatch(
                        entity_name=entity_name,
                        matched_name=match['name'],
                        match_score=match['score'],
                        list_type='sanctions',
                        list_source=framework.value,
                        risk_level=self._determine_sanctions_risk_level(match['score']),
                        additional_info=match.get('details', {}),
                        screening_date=datetime.utcnow()
                    )
                    matches.append(screening_match.__dict__)
                    
            except Exception as e:
                logger.error(f"Sanctions screening error for {framework}: {e}")
        
        return matches
    
    async def _screen_pep_database(self, entity_name: str, entity_type: str) -> List[Dict[str, Any]]:
        """Screen against PEP databases"""
        matches = []
        
        if entity_type != "individual":
            return matches  # PEP screening only for individuals
        
        entity_lower = entity_name.lower()
        
        # Check direct matches
        if entity_lower in self.pep_database:
            pep_record = self.pep_database[entity_lower]
            matches.append({
                'entity_name': entity_name,
                'pep_name': pep_record.name,
                'position': pep_record.position,
                'country': pep_record.country,
                'risk_category': pep_record.risk_category,
                'match_type': 'direct',
                'match_score': 1.0,
                'additional_info': {
                    'aliases': pep_record.aliases,
                    'family_associates': pep_record.family_associates,
                    'jurisdiction': pep_record.jurisdiction
                }
            })
        
        # Check alias matches
        for pep_name, pep_record in self.pep_database.items():
            for alias in pep_record.aliases:
                if self._calculate_name_similarity(entity_name, alias) > 0.8:
                    matches.append({
                        'entity_name': entity_name,
                        'pep_name': pep_record.name,
                        'matched_alias': alias,
                        'position': pep_record.position,
                        'country': pep_record.country,
                        'risk_category': pep_record.risk_category,
                        'match_type': 'alias',
                        'match_score': self._calculate_name_similarity(entity_name, alias),
                        'additional_info': {
                            'aliases': pep_record.aliases,
                            'family_associates': pep_record.family_associates
                        }
                    })
        
        return matches
    
    async def _screen_internal_watchlists(self, entity_name: str, entity_type: str) -> List[ScreeningMatch]:
        """Screen against internal watchlists"""
        matches = []
        
        for watchlist_name, watchlist in self.watchlists.items():
            for entry in watchlist['entries']:
                entry_name = entry.get('name', '')
                similarity = self._calculate_name_similarity(entity_name, entry_name)
                
                if similarity > 0.7:  # Threshold for watchlist matching
                    screening_match = ScreeningMatch(
                        entity_name=entity_name,
                        matched_name=entry_name,
                        match_score=similarity,
                        list_type='watchlist',
                        list_source=watchlist_name,
                        risk_level=entry.get('risk_level', 'medium'),
                        additional_info=entry,
                        screening_date=datetime.utcnow()
                    )
                    matches.append(screening_match.__dict__)
        
        return matches
    
    async def _search_adverse_media(self, entity_name: str, entity_type: str) -> List[Dict[str, Any]]:
        """Search for adverse media mentions"""
        adverse_media = []
        
        # This would integrate with news APIs and media monitoring services
        # For now, we'll return a sample structure
        
        sample_adverse_media = [
            {
                'entity_name': entity_name,
                'headline': f'Sample adverse media about {entity_name}',
                'source': 'Sample News Source',
                'published_date': datetime.utcnow().isoformat(),
                'sentiment': 'negative',
                'risk_keywords': ['investigation', 'compliance'],
                'relevance_score': 0.7,
                'url': 'https://example.com/news'
            }
        ] if 'sample' in entity_name.lower() else []
        
        return sample_adverse_media
    
    def _fuzzy_match_sanctions(self, entity_name: str, sanctions_list: Dict) -> List[Dict]:
        """Fuzzy matching against sanctions list entries"""
        matches = []
        
        # Sample sanctions entries for demonstration
        sample_entries = [
            {'name': 'John Doe', 'type': 'individual', 'program': 'SANCTIONS_PROGRAM'},
            {'name': 'ABC Corporation', 'type': 'entity', 'program': 'SANCTIONS_PROGRAM'}
        ]
        
        for entry in sample_entries:
            similarity = self._calculate_name_similarity(entity_name, entry['name'])
            if similarity > 0.8:  # High threshold for sanctions matching
                matches.append({
                    'name': entry['name'],
                    'score': similarity,
                    'details': entry
                })
        
        return matches
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using fuzzy matching"""
        try:
            from fuzzywuzzy import fuzz
            return fuzz.ratio(name1.lower(), name2.lower()) / 100.0
        except ImportError:
            # Fallback to simple string matching
            name1_lower = name1.lower()
            name2_lower = name2.lower()
            
            if name1_lower == name2_lower:
                return 1.0
            elif name1_lower in name2_lower or name2_lower in name1_lower:
                return 0.8
            else:
                # Simple word overlap
                words1 = set(name1_lower.split())
                words2 = set(name2_lower.split())
                overlap = len(words1.intersection(words2))
                total = len(words1.union(words2))
                return overlap / total if total > 0 else 0.0
    
    def _determine_sanctions_risk_level(self, match_score: float) -> str:
        """Determine risk level based on sanctions match score"""
        if match_score >= 0.95:
            return "critical"
        elif match_score >= 0.85:
            return "high"
        elif match_score >= 0.75:
            return "medium"
        else:
            return "low"
    
    def _calculate_screening_risk(self, 
                                sanctions_matches: List[Dict],
                                pep_matches: List[Dict],
                                adverse_media: List[Dict]) -> Tuple[float, ScreeningResult]:
        """Calculate overall screening risk score and result"""
        
        risk_score = 0.0
        
        # Sanctions matches (highest weight)
        if sanctions_matches:
            max_sanctions_score = max(match['match_score'] for match in sanctions_matches)
            risk_score += max_sanctions_score * 0.6
        
        # PEP matches
        if pep_matches:
            max_pep_score = max(match['match_score'] for match in pep_matches)
            pep_risk_weight = {'high': 0.4, 'medium': 0.25, 'low': 0.1}
            for match in pep_matches:
                weight = pep_risk_weight.get(match.get('risk_category', 'medium'), 0.25)
                risk_score += match['match_score'] * weight
        
        # Adverse media
        if adverse_media:
            media_score = sum(article.get('relevance_score', 0.5) for article in adverse_media)
            risk_score += min(media_score / len(adverse_media) * 0.2, 0.2)
        
        # Determine overall result
        if risk_score >= 0.8:
            result = ScreeningResult.CONFIRMED_MATCH
        elif risk_score >= 0.6:
            result = ScreeningResult.POTENTIAL_MATCH
        elif risk_score >= 0.3:
            result = ScreeningResult.REQUIRES_REVIEW
        else:
            result = ScreeningResult.CLEAR
        
        return min(risk_score, 1.0), result
    
    def _generate_recommendations(self,
                                overall_result: ScreeningResult,
                                risk_score: float,
                                sanctions_matches: List[Dict],
                                pep_matches: List[Dict],
                                adverse_media: List[Dict]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if overall_result == ScreeningResult.CONFIRMED_MATCH:
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: High-confidence match detected",
                "Do not proceed with transaction until cleared by compliance team",
                "Escalate to senior compliance officer immediately",
                "Document all screening results and decisions"
            ])
        
        elif overall_result == ScreeningResult.POTENTIAL_MATCH:
            recommendations.extend([
                "Enhanced due diligence required before proceeding",
                "Manual review by compliance team recommended",
                "Gather additional identifying information",
                "Consider source of funds and transaction purpose"
            ])
        
        elif overall_result == ScreeningResult.REQUIRES_REVIEW:
            recommendations.extend([
                "Review adverse media and PEP status",
                "Document decision rationale",
                "Consider ongoing monitoring"
            ])
        
        if pep_matches:
            recommendations.append("PEP status detected - enhanced ongoing monitoring required")
        
        if adverse_media:
            recommendations.append("Adverse media found - review for reputational risk")
        
        if not recommendations:
            recommendations.append("No significant compliance concerns identified")
        
        return recommendations
    
    def _generate_cache_key(self, entity_name: str, entity_type: str, additional_info: Dict = None) -> str:
        """Generate cache key for screening results"""
        content = f"{entity_name}|{entity_type}|{json.dumps(additional_info or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def batch_screen_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch screening of multiple entities"""
        logger.info(f"Batch screening {len(entities)} entities")
        
        tasks = [
            self.screen_entity(
                entity['name'],
                entity.get('type', 'individual'),
                entity.get('additional_info', {})
            )
            for entity in entities
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch screening error for entity {i}: {result}")
                processed_results.append({
                    'entity_name': entities[i]['name'],
                    'error': str(result),
                    'overall_result': ScreeningResult.REQUIRES_REVIEW.value
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def generate_compliance_report(self, 
                                       entity_name: str,
                                       screening_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        report = {
            'report_id': hashlib.md5(f"{entity_name}{datetime.utcnow()}".encode()).hexdigest()[:8],
            'entity_name': entity_name,
            'report_date': datetime.utcnow().isoformat(),
            'screening_summary': {
                'overall_result': screening_results['overall_result'],
                'risk_score': screening_results['risk_score'],
                'sanctions_matches': len(screening_results['matches']),
                'pep_matches': len(screening_results['pep_matches']),
                'adverse_media_articles': len(screening_results['adverse_media'])
            },
            'detailed_findings': screening_results,
            'compliance_status': self._determine_compliance_status(screening_results),
            'required_actions': screening_results['recommendations'],
            'audit_trail': {
                'screened_by': 'Compliant.one Automated System',
                'screening_timestamp': screening_results['screening_timestamp'],
                'data_sources': list(self.sanctions_lists.keys()),
                'screening_version': '1.0'
            }
        }
        
        return report
    
    def _determine_compliance_status(self, screening_results: Dict[str, Any]) -> str:
        """Determine compliance status based on screening results"""
        result = screening_results['overall_result']
        
        if result == ScreeningResult.CLEAR.value:
            return "COMPLIANT"
        elif result == ScreeningResult.REQUIRES_REVIEW.value:
            return "REQUIRES_REVIEW"
        elif result == ScreeningResult.POTENTIAL_MATCH.value:
            return "NON_COMPLIANT_POTENTIAL"
        else:
            return "NON_COMPLIANT_CONFIRMED"
    
    async def update_compliance_data(self):
        """Update compliance data from external sources"""
        logger.info("Updating compliance data...")
        
        try:
            # This would fetch updated sanctions lists, PEP databases, etc.
            # For now, we'll just update the timestamp
            for framework in self.sanctions_lists:
                self.sanctions_lists[framework]['last_updated'] = datetime.utcnow()
            
            # Clear cache to force fresh screening
            self.screening_cache.clear()
            
            logger.info("Compliance data updated successfully")
            
        except Exception as e:
            logger.error(f"Compliance data update failed: {e}")
    
    async def monitor_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Monitor transactions for suspicious patterns (future implementation)"""
        # Placeholder for transaction monitoring integration
        return [{
            'transaction_id': trans.get('id'),
            'screening_result': 'pending_implementation',
            'message': 'Transaction monitoring will be implemented in future phase'
        } for trans in transactions]
