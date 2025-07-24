"""
Advanced OSINT Expansion - Phase 2 Enhancements
🌐 Social Media Monitoring, News Aggregation, Adverse Media Detection
Real-time Intelligence Gathering with AI-powered Analysis
"""

import asyncio
import aiohttp
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import re
from urllib.parse import quote, urljoin

# Optional dependencies with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import nltk
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

from utils.logger import ComplianceLogger

@dataclass
class AdverseMediaResult:
    """Enhanced adverse media result with detailed metadata"""
    entity_name: str
    source: str
    source_type: str
    content: str
    url: str
    timestamp: datetime
    relevance_score: float
    sentiment_score: float
    risk_score: float
    risk_indicators: List[str]
    entities_mentioned: List[str]
    keywords_matched: List[str]
    language: str
    credibility_score: float
    metadata: Dict[str, Any]

@dataclass
class OSINTAlert:
    """Enhanced OSINT alert with actionable intelligence"""
    alert_id: str
    entity_id: str
    entity_name: str
    alert_type: str
    severity: str
    description: str
    source: str
    evidence: Dict[str, Any]
    risk_indicators: List[str]
    recommended_actions: List[str]
    created_at: datetime
    expires_at: datetime
    status: str = "ACTIVE"
    assignee: Optional[str] = None
    notes: List[str] = None

class EnhancedNewsAggregator:
    """Advanced news aggregation with AI-powered analysis"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("news_aggregator")
        
        # News sources configuration
        self.news_sources = self._get_enhanced_news_sources()
        self.languages = self.config.get('languages', ['en', 'es', 'fr', 'de', 'zh'])
        self.lookback_days = self.config.get('lookback_days', 30)
        self.max_articles_per_source = self.config.get('max_articles_per_source', 50)
        
        # Risk assessment configuration
        self.risk_keywords = self._load_risk_keywords()
        self.entity_extraction_patterns = self._compile_entity_patterns()
        
        # Rate limiting
        self.rate_limits = {
            'rss': 100,  # requests per hour
            'api': 1000,
            'scraping': 50
        }
        
        self.last_request_times = {}
    
    def _get_enhanced_news_sources(self) -> List[Dict]:
        """Get comprehensive news sources configuration"""
        return [
            # Financial News
            {
                'name': 'Reuters Business',
                'rss_url': 'https://feeds.reuters.com/reuters/businessNews',
                'type': 'rss',
                'credibility': 0.95,
                'category': 'financial',
                'language': 'en',
                'region': 'global'
            },
            {
                'name': 'Financial Times',
                'rss_url': 'https://www.ft.com/rss/home',
                'type': 'rss', 
                'credibility': 0.95,
                'category': 'financial',
                'language': 'en',
                'region': 'global'
            },
            {
                'name': 'Bloomberg',
                'rss_url': 'https://feeds.bloomberg.com/markets/news.rss',
                'type': 'rss',
                'credibility': 0.95,
                'category': 'financial',
                'language': 'en',
                'region': 'global'
            },
            {
                'name': 'Wall Street Journal',
                'rss_url': 'https://feeds.wsj.com/wsj/xml/rss/3_7085.xml',
                'type': 'rss',
                'credibility': 0.93,
                'category': 'financial',
                'language': 'en',
                'region': 'us'
            },
            
            # General News
            {
                'name': 'BBC News',
                'rss_url': 'http://feeds.bbci.co.uk/news/business/rss.xml',
                'type': 'rss',
                'credibility': 0.90,
                'category': 'general',
                'language': 'en',
                'region': 'uk'
            },
            {
                'name': 'Associated Press',
                'rss_url': 'https://feeds.apnews.com/rss/apf-topnews',
                'type': 'rss',
                'credibility': 0.92,
                'category': 'general',
                'language': 'en',
                'region': 'us'
            },
            
            # Legal and Regulatory News
            {
                'name': 'Law360',
                'rss_url': 'https://www.law360.com/compliance/rss',
                'type': 'rss',
                'credibility': 0.88,
                'category': 'legal',
                'language': 'en',
                'region': 'us'
            },
            {
                'name': 'Compliance Week',
                'rss_url': 'https://www.complianceweek.com/rss/all',
                'type': 'rss',
                'credibility': 0.85,
                'category': 'compliance',
                'language': 'en',
                'region': 'global'
            },
            
            # International Sources
            {
                'name': 'Euractiv',
                'rss_url': 'https://www.euractiv.com/feed/',
                'type': 'rss',
                'credibility': 0.83,
                'category': 'regulatory',
                'language': 'en',
                'region': 'eu'
            },
            {
                'name': 'Nikkei Asia',
                'rss_url': 'https://asia.nikkei.com/rss/feed/nar',
                'type': 'rss',
                'credibility': 0.87,
                'category': 'financial',
                'language': 'en',
                'region': 'asia'
            }
        ]
    
    def _load_risk_keywords(self) -> Dict[str, List[str]]:
        """Load comprehensive risk keyword dictionary"""
        return {
            'financial_crime': [
                'money laundering', 'terrorist financing', 'fraud', 'embezzlement',
                'bribery', 'corruption', 'sanctions violation', 'tax evasion',
                'wire fraud', 'bank fraud', 'securities fraud', 'ponzi scheme',
                'market manipulation', 'insider trading', 'structuring', 'smurfing'
            ],
            'criminal_activity': [
                'drug trafficking', 'human trafficking', 'arms dealing', 'cybercrime',
                'organized crime', 'racketeering', 'extortion', 'kidnapping',
                'assassination', 'terrorism', 'narcotics', 'weapons trafficking'
            ],
            'regulatory_violations': [
                'regulatory fine', 'compliance violation', 'license revocation',
                'enforcement action', 'consent order', 'cease and desist',
                'regulatory sanctions', 'license suspension', 'regulatory investigation',
                'compliance failure', 'regulatory breach', 'violation notice'
            ],
            'litigation_risks': [
                'lawsuit', 'litigation', 'class action', 'settlement', 'judgment',
                'court order', 'injunction', 'bankruptcy', 'insolvency',
                'receivership', 'liquidation', 'administration'
            ],
            'reputational_risks': [
                'scandal', 'investigation', 'whistleblower', 'data breach',
                'privacy violation', 'misconduct', 'unethical', 'controversy',
                'allegations', 'accusations', 'impropriety', 'malpractice'
            ],
            'sanctions_related': [
                'sanctions', 'sanctioned', 'blocked person', 'designated entity',
                'sdn list', 'ofac', 'freezing order', 'asset freeze',
                'export control', 'embargo', 'trade restriction'
            ]
        }
    
    def _compile_entity_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for entity extraction"""
        return {
            'company': re.compile(r'\b[A-Z][a-zA-Z\s&,.-]*(?:Inc\.?|Ltd\.?|Corp\.?|LLC|Company|Corporation|Limited|plc|AG|SA|SL|GmbH)\b'),
            'person': re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'),
            'location': re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:City|State|Country|Province|County|District))\b'),
            'money': re.compile(r'\$[\d,]+(?:\.\d{2})?(?:\s+(?:million|billion|thousand))?'),
            'date': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b')
        }
    
    async def search_adverse_media(self, entity_name: str, search_config: Dict = None) -> List[AdverseMediaResult]:
        """Search for adverse media mentions across all news sources"""
        config = search_config or {}
        
        self.logger.logger.info(f"Starting adverse media search for: {entity_name}")
        
        results = []
        search_terms = self._generate_search_terms(entity_name, config)
        
        # Search each news source
        for source in self.news_sources:
            try:
                if not self._check_rate_limit(source['type']):
                    continue
                
                source_results = await self._search_news_source(source, search_terms, entity_name)
                results.extend(source_results)
                
            except Exception as e:
                self.logger.logger.error(f"Error searching {source['name']}: {e}")
                continue
        
        # Filter and rank results
        filtered_results = self._filter_adverse_results(results, entity_name)
        ranked_results = self._rank_results_by_risk(filtered_results)
        
        self.logger.logger.info(f"Found {len(ranked_results)} adverse media results for {entity_name}")
        
        return ranked_results[:config.get('max_results', 100)]
    
    def _generate_search_terms(self, entity_name: str, config: Dict) -> List[str]:
        """Generate comprehensive search terms for entity"""
        terms = [entity_name]
        
        # Add variations
        if ' ' in entity_name:
            # Add quoted exact match
            terms.append(f'"{entity_name}"')
            
            # Add individual words for broader search
            words = entity_name.split()
            if len(words) > 1:
                terms.extend(words)
        
        # Add entity-specific terms
        entity_type = config.get('entity_type', 'unknown')
        if entity_type == 'corporate':
            # Add common corporate suffixes
            base_name = entity_name.replace(' Inc', '').replace(' Ltd', '').replace(' Corp', '')
            terms.extend([
                f"{base_name} Inc",
                f"{base_name} Ltd", 
                f"{base_name} Corp",
                f"{base_name} Company"
            ])
        
        return list(set(terms))  # Remove duplicates
    
    async def _search_news_source(self, source: Dict, search_terms: List[str], entity_name: str) -> List[AdverseMediaResult]:
        """Search individual news source"""
        results = []
        
        if source['type'] == 'rss':
            results = await self._search_rss_feed(source, search_terms, entity_name)
        elif source['type'] == 'api':
            results = await self._search_news_api(source, search_terms, entity_name)
        elif source['type'] == 'scraping':
            results = await self._search_web_scraping(source, search_terms, entity_name)
        
        return results
    
    async def _search_rss_feed(self, source: Dict, search_terms: List[str], entity_name: str) -> List[AdverseMediaResult]:
        """Search RSS feed for adverse mentions"""
        if not FEEDPARSER_AVAILABLE:
            self.logger.logger.warning("feedparser not available for RSS parsing")
            return []
        
        results = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(source['rss_url'])
            
            for entry in feed.entries:
                # Get article content
                title = getattr(entry, 'title', '')
                summary = getattr(entry, 'summary', '')
                content = f"{title} {summary}"
                
                # Check if entity is mentioned
                if not self._entity_mentioned(content, search_terms):
                    continue
                
                # Check for adverse indicators
                risk_indicators = self._detect_risk_indicators(content)
                if not risk_indicators and not self._has_adverse_context(content):
                    continue
                
                # Parse publication date
                pub_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Skip old articles
                if (datetime.now() - pub_date).days > self.lookback_days:
                    continue
                
                # Calculate scores
                relevance_score = self._calculate_relevance(content, entity_name)
                sentiment_score = self._analyze_sentiment(content)
                risk_score = self._calculate_risk_score(content, risk_indicators)
                
                # Extract entities and keywords
                entities = self._extract_entities(content)
                keywords = self._extract_matched_keywords(content)
                
                result = AdverseMediaResult(
                    entity_name=entity_name,
                    source=source['name'],
                    source_type='news_rss',
                    content=content.strip(),
                    url=getattr(entry, 'link', ''),
                    timestamp=pub_date,
                    relevance_score=relevance_score,
                    sentiment_score=sentiment_score,
                    risk_score=risk_score,
                    risk_indicators=risk_indicators,
                    entities_mentioned=entities,
                    keywords_matched=keywords,
                    language=source.get('language', 'en'),
                    credibility_score=source.get('credibility', 0.7),
                    metadata={
                        'category': source.get('category', 'general'),
                        'region': source.get('region', 'global'),
                        'word_count': len(content.split()),
                        'article_title': title
                    }
                )
                
                results.append(result)
                
        except Exception as e:
            self.logger.logger.error(f"Error parsing RSS feed {source['rss_url']}: {e}")
        
        return results
    
    def _entity_mentioned(self, content: str, search_terms: List[str]) -> bool:
        """Check if entity is mentioned in content"""
        content_lower = content.lower()
        
        for term in search_terms:
            if term.lower() in content_lower:
                return True
        
        return False
    
    def _detect_risk_indicators(self, content: str) -> List[str]:
        """Detect risk indicators in content"""
        content_lower = content.lower()
        detected_indicators = []
        
        for category, keywords in self.risk_keywords.items():
            category_indicators = []
            for keyword in keywords:
                if keyword in content_lower:
                    category_indicators.append(keyword)
            
            if category_indicators:
                detected_indicators.append(category)
        
        return detected_indicators
    
    def _has_adverse_context(self, content: str) -> bool:
        """Check if content has adverse context even without specific keywords"""
        adverse_patterns = [
            r'\b(?:accused|alleged|charged|indicted|convicted|guilty|sentenced)\b',
            r'\b(?:investigation|probe|inquiry|audit|review)\b.*\b(?:into|of|regarding)\b',
            r'\b(?:fine|penalty|sanctions|punishment|disciplinary)\b',
            r'\b(?:lawsuit|litigation|legal action|court case)\b',
            r'\b(?:breach|violation|non-compliance|misconduct)\b',
            r'\b(?:suspended|banned|prohibited|restricted)\b',
            r'\b(?:criminal|illegal|unlawful|fraudulent)\b'
        ]
        
        content_lower = content.lower()
        
        for pattern in adverse_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def _calculate_relevance(self, content: str, entity_name: str) -> float:
        """Calculate relevance score for content"""
        content_lower = content.lower()
        entity_lower = entity_name.lower()
        
        # Direct mentions
        direct_mentions = content_lower.count(entity_lower)
        
        # Word-based scoring
        entity_words = entity_lower.split()
        content_words = content_lower.split()
        
        word_matches = sum(1 for word in entity_words if word in content_words)
        word_score = word_matches / len(entity_words) if entity_words else 0
        
        # Position scoring (mentions in title/beginning are more relevant)
        position_score = 1.0
        if entity_lower in content_lower[:200]:  # First 200 characters
            position_score = 1.5
        
        # Combine scores
        relevance = min(1.0, (direct_mentions * 0.5 + word_score * 0.3 + position_score * 0.2))
        
        return relevance
    
    def _analyze_sentiment(self, content: str) -> float:
        """Analyze sentiment of content"""
        if SENTIMENT_AVAILABLE:
            try:
                blob = TextBlob(content)
                return blob.sentiment.polarity  # Range: -1 to 1
            except Exception:
                pass
        
        # Fallback to keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'growth', 'profit', 'win', 'achievement']
        negative_words = ['bad', 'terrible', 'negative', 'loss', 'decline', 'problem', 'crisis', 'scandal', 'fail', 'violation']
        
        content_lower = content.lower()
        
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        
        total_score = positive_score + negative_score
        if total_score == 0:
            return 0.0
        
        sentiment = (positive_score - negative_score) / total_score
        return sentiment
    
    def _calculate_risk_score(self, content: str, risk_indicators: List[str]) -> float:
        """Calculate overall risk score for content"""
        base_score = len(risk_indicators) * 0.2
        
        # Adjust based on severity keywords
        high_severity_keywords = ['criminal', 'illegal', 'fraud', 'laundering', 'terrorist', 'sanctions']
        content_lower = content.lower()
        
        severity_multiplier = 1.0
        for keyword in high_severity_keywords:
            if keyword in content_lower:
                severity_multiplier += 0.3
        
        risk_score = min(1.0, base_score * severity_multiplier)
        return risk_score
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content using regex patterns"""
        entities = []
        
        for entity_type, pattern in self.entity_extraction_patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                if len(match) > 3 and len(match) < 100:  # Filter reasonable lengths
                    entities.append(match.strip())
        
        return list(set(entities))  # Remove duplicates
    
    def _extract_matched_keywords(self, content: str) -> List[str]:
        """Extract keywords that matched risk categories"""
        matched_keywords = []
        content_lower = content.lower()
        
        for category, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    matched_keywords.append(keyword)
        
        return list(set(matched_keywords))
    
    def _filter_adverse_results(self, results: List[AdverseMediaResult], entity_name: str) -> List[AdverseMediaResult]:
        """Filter results to only include truly adverse mentions"""
        filtered = []
        
        for result in results:
            # Must have risk indicators or negative sentiment
            if result.risk_indicators or result.sentiment_score < -0.1:
                # Must be sufficiently relevant
                if result.relevance_score > 0.3:
                    # Must have minimum risk score
                    if result.risk_score > 0.1:
                        filtered.append(result)
        
        return filtered
    
    def _rank_results_by_risk(self, results: List[AdverseMediaResult]) -> List[AdverseMediaResult]:
        """Rank results by risk score and relevance"""
        def risk_ranking_score(result):
            # Combine risk score, relevance, and credibility
            return (result.risk_score * 0.5 + 
                   result.relevance_score * 0.3 + 
                   result.credibility_score * 0.2)
        
        return sorted(results, key=risk_ranking_score, reverse=True)
    
    def _check_rate_limit(self, source_type: str) -> bool:
        """Check rate limiting for source type"""
        current_time = datetime.now().timestamp()
        
        if source_type not in self.last_request_times:
            self.last_request_times[source_type] = []
        
        # Clean old requests (older than 1 hour)
        hour_ago = current_time - 3600
        self.last_request_times[source_type] = [
            t for t in self.last_request_times[source_type] if t > hour_ago
        ]
        
        # Check if under rate limit
        if len(self.last_request_times[source_type]) < self.rate_limits[source_type]:
            self.last_request_times[source_type].append(current_time)
            return True
        
        return False

class EnhancedSocialMediaMonitor:
    """Advanced social media monitoring with platform-specific analysis"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("social_media_monitor")
        
        # Platform configuration
        self.platforms = self._get_platform_configs()
        self.api_keys = self.config.get('api_keys', {})
        
        # Monitoring configuration
        self.max_results_per_platform = self.config.get('max_results_per_platform', 50)
        self.sentiment_threshold = self.config.get('sentiment_threshold', -0.3)
        self.engagement_threshold = self.config.get('engagement_threshold', 100)
        
        # Content analysis
        self.risk_keywords = self._load_social_media_risk_keywords()
        self.influence_indicators = self._load_influence_indicators()
    
    def _get_platform_configs(self) -> Dict[str, Dict]:
        """Get social media platform configurations"""
        return {
            'twitter': {
                'name': 'Twitter/X',
                'api_endpoint': 'https://api.twitter.com/2',
                'rate_limit': 300,  # requests per 15 minutes
                'credibility_base': 0.6,
                'influence_weight': 0.8,
                'real_time_capability': True
            },
            'linkedin': {
                'name': 'LinkedIn',
                'api_endpoint': 'https://api.linkedin.com/v2',
                'rate_limit': 100,
                'credibility_base': 0.75,
                'influence_weight': 0.9,
                'real_time_capability': False
            },
            'facebook': {
                'name': 'Facebook',
                'api_endpoint': 'https://graph.facebook.com',
                'rate_limit': 200,
                'credibility_base': 0.5,
                'influence_weight': 0.7,
                'real_time_capability': False
            },
            'reddit': {
                'name': 'Reddit',
                'api_endpoint': 'https://oauth.reddit.com',
                'rate_limit': 60,
                'credibility_base': 0.4,
                'influence_weight': 0.6,
                'real_time_capability': True
            },
            'telegram': {
                'name': 'Telegram',
                'api_endpoint': 'https://api.telegram.org',
                'rate_limit': 30,
                'credibility_base': 0.3,
                'influence_weight': 0.5,
                'real_time_capability': True
            }
        }
    
    def _load_social_media_risk_keywords(self) -> Dict[str, List[str]]:
        """Load social media specific risk keywords"""
        return {
            'financial_scams': [
                'investment scam', 'ponzi scheme', 'crypto scam', 'pump and dump',
                'fake investment', 'financial fraud', 'romance scam', 'advance fee fraud'
            ],
            'reputation_damage': [
                'exposing', 'leaked documents', 'whistleblower', 'scandal',
                'corruption exposed', 'truth revealed', 'investigate', 'evidence'
            ],
            'threats_violence': [
                'threat', 'violence', 'harm', 'revenge', 'retaliation',
                'going after', 'will pay', 'consequences'
            ],
            'market_manipulation': [
                'pump', 'dump', 'short squeeze', 'coordinated buying',
                'market manipulation', 'insider information', 'stock tip'
            ],
            'criminal_associations': [
                'cartel', 'mafia', 'organized crime', 'money mule',
                'drug dealer', 'criminal network', 'illicit activity'
            ]
        }
    
    def _load_influence_indicators(self) -> Dict[str, int]:
        """Load social media influence indicators"""
        return {
            'verified_account': 100,
            'high_follower_count': 50,
            'media_coverage': 75,
            'government_official': 150,
            'industry_expert': 80,
            'influencer': 60,
            'journalist': 90
        }
    
    async def monitor_entity(self, entity_name: str, monitoring_config: Dict = None) -> Dict[str, Any]:
        """Monitor entity across social media platforms"""
        config = monitoring_config or {}
        
        self.logger.logger.info(f"Starting social media monitoring for: {entity_name}")
        
        results = {
            'entity_name': entity_name,
            'monitoring_timestamp': datetime.now().isoformat(),
            'platforms_monitored': [],
            'total_mentions': 0,
            'adverse_mentions': 0,
            'sentiment_analysis': {},
            'influence_analysis': {},
            'risk_assessment': {},
            'detailed_results': {}
        }
        
        # Monitor each platform
        for platform_id, platform_config in self.platforms.items():
            if not config.get(f'monitor_{platform_id}', True):
                continue
            
            try:
                platform_results = await self._monitor_platform(
                    platform_id, platform_config, entity_name, config
                )
                
                results['platforms_monitored'].append(platform_id)
                results['detailed_results'][platform_id] = platform_results
                results['total_mentions'] += platform_results['mention_count']
                results['adverse_mentions'] += platform_results['adverse_count']
                
            except Exception as e:
                self.logger.logger.error(f"Error monitoring {platform_id}: {e}")
                results['detailed_results'][platform_id] = {'error': str(e)}
        
        # Aggregate analysis
        results['sentiment_analysis'] = self._aggregate_sentiment_analysis(results['detailed_results'])
        results['influence_analysis'] = self._aggregate_influence_analysis(results['detailed_results'])
        results['risk_assessment'] = self._calculate_social_media_risk(results)
        
        return results
    
    async def _monitor_platform(self, platform_id: str, platform_config: Dict, 
                              entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor specific social media platform"""
        
        # Mock implementation - in production would use actual APIs
        if platform_id == 'twitter':
            return await self._monitor_twitter(entity_name, config)
        elif platform_id == 'linkedin':
            return await self._monitor_linkedin(entity_name, config)
        elif platform_id == 'facebook':
            return await self._monitor_facebook(entity_name, config)
        elif platform_id == 'reddit':
            return await self._monitor_reddit(entity_name, config)
        elif platform_id == 'telegram':
            return await self._monitor_telegram(entity_name, config)
        else:
            return {'mention_count': 0, 'adverse_count': 0, 'posts': []}
    
    async def _monitor_twitter(self, entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor Twitter for entity mentions"""
        # Mock Twitter monitoring results
        mock_posts = [
            {
                'id': 'tweet_123456789',
                'text': f'Breaking: Investigation launched into {entity_name} for compliance violations',
                'user': {
                    'username': 'FinancialNews',
                    'followers_count': 125000,
                    'verified': True
                },
                'created_at': datetime.now() - timedelta(hours=2),
                'metrics': {
                    'retweet_count': 45,
                    'like_count': 128,
                    'reply_count': 23
                },
                'url': 'https://twitter.com/status/123456789'
            },
            {
                'id': 'tweet_987654321',
                'text': f'Analysis shows {entity_name} improving compliance framework',
                'user': {
                    'username': 'ComplianceExpert',
                    'followers_count': 15000,
                    'verified': False
                },
                'created_at': datetime.now() - timedelta(hours=6),
                'metrics': {
                    'retweet_count': 12,
                    'like_count': 67,
                    'reply_count': 8
                },
                'url': 'https://twitter.com/status/987654321'
            }
        ]
        
        analyzed_posts = []
        adverse_count = 0
        
        for post in mock_posts:
            analysis = self._analyze_social_media_post(post, entity_name, 'twitter')
            analyzed_posts.append(analysis)
            
            if analysis['is_adverse']:
                adverse_count += 1
        
        return {
            'platform': 'twitter',
            'mention_count': len(mock_posts),
            'adverse_count': adverse_count,
            'posts': analyzed_posts,
            'platform_metrics': {
                'total_engagement': sum(p['metrics']['retweet_count'] + p['metrics']['like_count'] for p in mock_posts),
                'average_sentiment': sum(p.get('sentiment_score', 0) for p in analyzed_posts) / len(analyzed_posts) if analyzed_posts else 0,
                'influence_score': sum(p.get('influence_score', 0) for p in analyzed_posts) / len(analyzed_posts) if analyzed_posts else 0
            }
        }
    
    async def _monitor_linkedin(self, entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor LinkedIn for entity mentions"""
        # Mock LinkedIn results
        mock_posts = [
            {
                'id': 'linkedin_post_123',
                'text': f'Our compliance assessment of {entity_name} shows strong improvements in risk management',
                'author': {
                    'name': 'John Compliance Officer',
                    'title': 'Chief Compliance Officer',
                    'company': 'RegTech Solutions'
                },
                'created_at': datetime.now() - timedelta(days=1),
                'metrics': {
                    'like_count': 45,
                    'comment_count': 12,
                    'share_count': 8
                },
                'url': 'https://linkedin.com/posts/123'
            }
        ]
        
        analyzed_posts = []
        for post in mock_posts:
            analysis = self._analyze_social_media_post(post, entity_name, 'linkedin')
            analyzed_posts.append(analysis)
        
        return {
            'platform': 'linkedin',
            'mention_count': len(mock_posts),
            'adverse_count': 0,  # This example shows positive mention
            'posts': analyzed_posts,
            'platform_metrics': {
                'total_engagement': sum(p['metrics']['like_count'] + p['metrics']['comment_count'] for p in mock_posts),
                'professional_credibility': 0.8
            }
        }
    
    async def _monitor_facebook(self, entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor Facebook for entity mentions"""
        return {'platform': 'facebook', 'mention_count': 0, 'adverse_count': 0, 'posts': []}
    
    async def _monitor_reddit(self, entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor Reddit for entity mentions"""
        return {'platform': 'reddit', 'mention_count': 0, 'adverse_count': 0, 'posts': []}
    
    async def _monitor_telegram(self, entity_name: str, config: Dict) -> Dict[str, Any]:
        """Monitor Telegram for entity mentions"""
        return {'platform': 'telegram', 'mention_count': 0, 'adverse_count': 0, 'posts': []}
    
    def _analyze_social_media_post(self, post: Dict, entity_name: str, platform: str) -> Dict[str, Any]:
        """Analyze individual social media post"""
        text = post.get('text', '')
        
        # Sentiment analysis
        sentiment_score = self._analyze_sentiment(text)
        
        # Risk indicators
        risk_indicators = self._detect_social_media_risks(text)
        
        # Influence score
        influence_score = self._calculate_influence_score(post, platform)
        
        # Adversity assessment
        is_adverse = (sentiment_score < self.sentiment_threshold or 
                     len(risk_indicators) > 0 or
                     self._has_adverse_context(text))
        
        return {
            'post_id': post.get('id', ''),
            'text': text,
            'platform': platform,
            'created_at': post.get('created_at', datetime.now()).isoformat(),
            'url': post.get('url', ''),
            'sentiment_score': sentiment_score,
            'risk_indicators': risk_indicators,
            'influence_score': influence_score,
            'is_adverse': is_adverse,
            'engagement_metrics': post.get('metrics', {}),
            'author_info': post.get('user', post.get('author', {}))
        }
    
    def _detect_social_media_risks(self, text: str) -> List[str]:
        """Detect social media specific risks"""
        text_lower = text.lower()
        detected_risks = []
        
        for category, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_risks.append(category)
                    break
        
        return list(set(detected_risks))
    
    def _calculate_influence_score(self, post: Dict, platform: str) -> float:
        """Calculate influence score for social media post"""
        platform_config = self.platforms.get(platform, {})
        base_credibility = platform_config.get('credibility_base', 0.5)
        
        influence_score = base_credibility
        
        # User metrics
        user = post.get('user', post.get('author', {}))
        
        if user.get('verified', False):
            influence_score += 0.2
        
        followers = user.get('followers_count', user.get('follower_count', 0))
        if followers > 100000:
            influence_score += 0.3
        elif followers > 10000:
            influence_score += 0.2
        elif followers > 1000:
            influence_score += 0.1
        
        # Engagement metrics
        metrics = post.get('metrics', {})
        total_engagement = (metrics.get('like_count', 0) + 
                          metrics.get('retweet_count', 0) + 
                          metrics.get('share_count', 0) + 
                          metrics.get('comment_count', 0))
        
        if total_engagement > self.engagement_threshold:
            influence_score += 0.2
        
        return min(1.0, influence_score)
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of social media text"""
        # Use same sentiment analysis as news aggregator
        if SENTIMENT_AVAILABLE:
            try:
                blob = TextBlob(text)
                return blob.sentiment.polarity
            except Exception:
                pass
        
        # Fallback keyword-based sentiment
        positive_indicators = ['great', 'excellent', 'good', 'positive', 'success', 'improvement']
        negative_indicators = ['terrible', 'bad', 'awful', 'scandal', 'fraud', 'illegal', 'violation']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _has_adverse_context(self, text: str) -> bool:
        """Check for adverse context in social media post"""
        adverse_patterns = [
            r'\b(?:exposed|revealed|leaked|investigation|probe)\b',
            r'\b(?:scam|fraud|illegal|criminal|violation)\b',
            r'\b(?:avoid|warning|beware|caution)\b',
            r'\b(?:lawsuit|court|legal action|charges)\b'
        ]
        
        text_lower = text.lower()
        
        for pattern in adverse_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _aggregate_sentiment_analysis(self, platform_results: Dict) -> Dict[str, Any]:
        """Aggregate sentiment analysis across platforms"""
        all_sentiments = []
        platform_sentiments = {}
        
        for platform, results in platform_results.items():
            if 'error' in results:
                continue
            
            platform_posts = results.get('posts', [])
            platform_sentiment_scores = [p.get('sentiment_score', 0) for p in platform_posts]
            
            if platform_sentiment_scores:
                platform_avg = sum(platform_sentiment_scores) / len(platform_sentiment_scores)
                platform_sentiments[platform] = platform_avg
                all_sentiments.extend(platform_sentiment_scores)
        
        overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'platform_breakdown': platform_sentiments,
            'sentiment_distribution': {
                'positive': len([s for s in all_sentiments if s > 0.1]),
                'neutral': len([s for s in all_sentiments if -0.1 <= s <= 0.1]),
                'negative': len([s for s in all_sentiments if s < -0.1])
            }
        }
    
    def _aggregate_influence_analysis(self, platform_results: Dict) -> Dict[str, Any]:
        """Aggregate influence analysis across platforms"""
        total_influence = 0
        platform_influence = {}
        high_influence_posts = []
        
        for platform, results in platform_results.items():
            if 'error' in results:
                continue
            
            platform_posts = results.get('posts', [])
            platform_influence_scores = [p.get('influence_score', 0) for p in platform_posts]
            
            if platform_influence_scores:
                platform_avg = sum(platform_influence_scores) / len(platform_influence_scores)
                platform_influence[platform] = platform_avg
                total_influence += sum(platform_influence_scores)
                
                # Collect high influence posts
                high_influence_posts.extend([
                    p for p in platform_posts if p.get('influence_score', 0) > 0.7
                ])
        
        return {
            'total_influence_score': total_influence,
            'platform_breakdown': platform_influence,
            'high_influence_posts_count': len(high_influence_posts),
            'high_influence_posts': high_influence_posts[:10]  # Top 10
        }
    
    def _calculate_social_media_risk(self, monitoring_results: Dict) -> Dict[str, Any]:
        """Calculate overall social media risk assessment"""
        total_mentions = monitoring_results['total_mentions']
        adverse_mentions = monitoring_results['adverse_mentions']
        
        if total_mentions == 0:
            return {
                'risk_level': 'MINIMAL',
                'risk_score': 0.0,
                'factors': ['no_social_media_presence']
            }
        
        # Calculate adverse ratio
        adverse_ratio = adverse_mentions / total_mentions
        
        # Factor in sentiment
        overall_sentiment = monitoring_results['sentiment_analysis'].get('overall_sentiment', 0)
        sentiment_risk = max(0, -overall_sentiment)  # Negative sentiment increases risk
        
        # Factor in influence
        total_influence = monitoring_results['influence_analysis'].get('total_influence_score', 0)
        influence_multiplier = 1.0 + (total_influence / 100)  # High influence increases impact
        
        # Calculate overall risk
        risk_score = min(1.0, (adverse_ratio * 0.6 + sentiment_risk * 0.3) * influence_multiplier)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'CRITICAL'
        elif risk_score >= 0.6:
            risk_level = 'HIGH'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
        elif risk_score >= 0.2:
            risk_level = 'LOW'
        else:
            risk_level = 'MINIMAL'
        
        # Identify risk factors
        factors = []
        if adverse_ratio > 0.5:
            factors.append('high_adverse_mention_ratio')
        if overall_sentiment < -0.3:
            factors.append('negative_sentiment')
        if total_influence > 50:
            factors.append('high_influence_exposure')
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'adverse_ratio': adverse_ratio,
            'sentiment_risk': sentiment_risk,
            'influence_multiplier': influence_multiplier,
            'factors': factors
        }

class AdverseMediaManager:
    """Central manager for adverse media monitoring"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("adverse_media_manager")
        
        # Initialize services with safe config access
        news_config = self.config.get('news', {}) if self.config else {}
        social_config = self.config.get('social_media', {}) if self.config else {}
        
        self.news_aggregator = EnhancedNewsAggregator(news_config)
        self.social_media_monitor = EnhancedSocialMediaMonitor(social_config)
        
        # Monitoring configuration with safe access
        self.monitoring_interval = self.config.get('monitoring_interval', 3600) if self.config else 3600  # 1 hour
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'risk_score': 0.6,
            'sentiment_threshold': -0.4,
            'influence_threshold': 0.7
        }) if self.config else {
            'risk_score': 0.6,
            'sentiment_threshold': -0.4,
            'influence_threshold': 0.7
        }
        
        # Active monitoring
        self.monitored_entities = {}
        self.active_alerts = []
    
    async def comprehensive_adverse_media_scan(self, entity_name: str, 
                                             scan_config: Dict = None) -> Dict[str, Any]:
        """Perform comprehensive adverse media scan"""
        config = scan_config or {}
        
        self.logger.logger.info(f"Starting comprehensive adverse media scan for: {entity_name}")
        
        # Parallel scanning
        news_task = self.news_aggregator.search_adverse_media(entity_name, config.get('news', {}))
        social_task = self.social_media_monitor.monitor_entity(entity_name, config.get('social_media', {}))
        
        news_results, social_results = await asyncio.gather(news_task, social_task)
        
        # Consolidate results
        scan_results = {
            'entity_name': entity_name,
            'scan_timestamp': datetime.now().isoformat(),
            'news_media_results': {
                'total_articles': len(news_results),
                'adverse_articles': len([r for r in news_results if r.risk_score > 0.3]),
                'average_sentiment': sum(r.sentiment_score for r in news_results) / len(news_results) if news_results else 0,
                'average_risk_score': sum(r.risk_score for r in news_results) / len(news_results) if news_results else 0,
                'articles': [asdict(r) for r in news_results[:20]]  # Top 20 results
            },
            'social_media_results': social_results,
            'overall_assessment': {}
        }
        
        # Calculate overall assessment
        scan_results['overall_assessment'] = self._calculate_overall_assessment(
            news_results, social_results, entity_name
        )
        
        # Generate alerts if necessary
        alerts = self._generate_alerts(scan_results)
        if alerts:
            scan_results['alerts_generated'] = alerts
            self.active_alerts.extend(alerts)
        
        return scan_results
    
    def _calculate_overall_assessment(self, news_results: List[AdverseMediaResult], 
                                    social_results: Dict, entity_name: str) -> Dict[str, Any]:
        """Calculate overall adverse media assessment"""
        
        # News media assessment
        news_risk_score = 0.0
        news_sentiment = 0.0
        if news_results:
            news_risk_score = sum(r.risk_score for r in news_results) / len(news_results)
            news_sentiment = sum(r.sentiment_score for r in news_results) / len(news_results)
        
        # Social media assessment
        social_risk_score = social_results.get('risk_assessment', {}).get('risk_score', 0.0)
        social_sentiment = social_results.get('sentiment_analysis', {}).get('overall_sentiment', 0.0)
        
        # Combined assessment
        overall_risk_score = (news_risk_score * 0.6 + social_risk_score * 0.4)
        overall_sentiment = (news_sentiment * 0.6 + social_sentiment * 0.4)
        
        # Determine risk level
        if overall_risk_score >= 0.8:
            risk_level = 'CRITICAL'
        elif overall_risk_score >= 0.6:
            risk_level = 'HIGH'
        elif overall_risk_score >= 0.4:
            risk_level = 'MEDIUM'
        elif overall_risk_score >= 0.2:
            risk_level = 'LOW'
        else:
            risk_level = 'MINIMAL'
        
        # Key findings
        key_findings = []
        
        if news_results:
            adverse_news_count = len([r for r in news_results if r.risk_score > 0.3])
            if adverse_news_count > 0:
                key_findings.append(f"{adverse_news_count} adverse news articles found")
        
        if social_results['adverse_mentions'] > 0:
            key_findings.append(f"{social_results['adverse_mentions']} adverse social media mentions")
        
        if overall_sentiment < -0.3:
            key_findings.append("Predominantly negative sentiment detected")
        
        # Risk indicators
        all_risk_indicators = []
        for result in news_results:
            all_risk_indicators.extend(result.risk_indicators)
        
        risk_indicator_counts = {}
        for indicator in all_risk_indicators:
            risk_indicator_counts[indicator] = risk_indicator_counts.get(indicator, 0) + 1
        
        top_risk_indicators = sorted(risk_indicator_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'overall_risk_level': risk_level,
            'overall_risk_score': round(overall_risk_score, 3),
            'overall_sentiment': round(overall_sentiment, 3),
            'news_risk_score': round(news_risk_score, 3),
            'social_risk_score': round(social_risk_score, 3),
            'key_findings': key_findings,
            'top_risk_indicators': [{'indicator': indicator, 'count': count} for indicator, count in top_risk_indicators],
            'recommendation': self._generate_recommendation(risk_level, overall_risk_score, key_findings)
        }
    
    def _generate_recommendation(self, risk_level: str, risk_score: float, key_findings: List[str]) -> str:
        """Generate recommendation based on assessment"""
        if risk_level == 'CRITICAL':
            return "IMMEDIATE ACTION REQUIRED: High-risk adverse media detected. Conduct thorough investigation and consider enhanced due diligence measures."
        elif risk_level == 'HIGH':
            return "URGENT REVIEW: Significant adverse media found. Review relationship and implement additional monitoring."
        elif risk_level == 'MEDIUM':
            return "MONITOR CLOSELY: Some adverse indicators detected. Continue monitoring and review periodically."
        elif risk_level == 'LOW':
            return "STANDARD MONITORING: Low risk detected. Maintain regular monitoring schedule."
        else:
            return "NO ACTION REQUIRED: Minimal or no adverse media found. Continue standard monitoring."
    
    def _generate_alerts(self, scan_results: Dict) -> List[OSINTAlert]:
        """Generate alerts based on scan results"""
        alerts = []
        entity_name = scan_results['entity_name']
        overall_assessment = scan_results['overall_assessment']
        
        # High risk alert
        if overall_assessment['overall_risk_score'] >= self.alert_thresholds['risk_score']:
            alert = OSINTAlert(
                alert_id=f"AM_{entity_name}_{int(datetime.now().timestamp())}",
                entity_id=entity_name,
                entity_name=entity_name,
                alert_type="HIGH_RISK_ADVERSE_MEDIA",
                severity=overall_assessment['overall_risk_level'],
                description=f"High-risk adverse media detected for {entity_name}",
                source="adverse_media_scan",
                evidence=overall_assessment,
                risk_indicators=overall_assessment.get('top_risk_indicators', []),
                recommended_actions=[
                    "Conduct enhanced due diligence",
                    "Review customer risk rating",
                    "Consider additional monitoring",
                    "Document findings in customer file"
                ],
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30)
            )
            alerts.append(alert)
        
        # Negative sentiment alert
        if overall_assessment['overall_sentiment'] <= self.alert_thresholds['sentiment_threshold']:
            alert = OSINTAlert(
                alert_id=f"SENT_{entity_name}_{int(datetime.now().timestamp())}",
                entity_id=entity_name,
                entity_name=entity_name,
                alert_type="NEGATIVE_SENTIMENT",
                severity="MEDIUM",
                description=f"Predominantly negative sentiment detected for {entity_name}",
                source="sentiment_analysis",
                evidence={'sentiment_score': overall_assessment['overall_sentiment']},
                risk_indicators=["negative_media_sentiment"],
                recommended_actions=[
                    "Review recent media coverage",
                    "Assess reputational risk impact",
                    "Monitor for developing issues"
                ],
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=14)
            )
            alerts.append(alert)
        
        return alerts
    
    async def start_continuous_monitoring(self, entity_name: str, monitoring_config: Dict = None):
        """Start continuous monitoring for an entity"""
        config = monitoring_config or {}
        
        self.monitored_entities[entity_name] = {
            'entity_name': entity_name,
            'config': config,
            'started_at': datetime.now(),
            'last_scan': None,
            'scan_count': 0,
            'alerts_generated': 0
        }
        
        self.logger.logger.info(f"Started continuous monitoring for: {entity_name}")
    
    async def stop_monitoring(self, entity_name: str):
        """Stop monitoring for an entity"""
        if entity_name in self.monitored_entities:
            del self.monitored_entities[entity_name]
            self.logger.logger.info(f"Stopped monitoring for: {entity_name}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get status of adverse media monitoring"""
        return {
            'monitored_entities_count': len(self.monitored_entities),
            'monitored_entities': list(self.monitored_entities.keys()),
            'active_alerts_count': len(self.active_alerts),
            'monitoring_interval': self.monitoring_interval,
            'alert_thresholds': self.alert_thresholds,
            'service_status': {
                'news_aggregator': 'active',
                'social_media_monitor': 'active'
            }
        }

# Initialize global adverse media manager with default config
adverse_media_manager = AdverseMediaManager(config={})

def get_adverse_media_manager() -> AdverseMediaManager:
    """Get the global adverse media manager"""
    return adverse_media_manager
