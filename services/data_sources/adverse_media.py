"""
Comprehensive Adverse Media Monitoring System
Real-time monitoring for negative news and reputational risk assessment
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import json
import re
from dataclasses import dataclass
from enum import Enum
logger = logging.getLogger(__name__)

try:
    import feedparser
except ImportError:
    feedparser = None
    logger.warning("feedparser not available. RSS feed parsing will be disabled.")

from bs4 import BeautifulSoup
import nltk

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None
    logger.warning("textblob not available. Advanced sentiment analysis will use fallback methods.")

import hashlib

class MediaSentiment(Enum):
    """Media sentiment classifications"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class AdverseCategory(Enum):
    """Categories of adverse media"""
    CORRUPTION = "corruption"
    FINANCIAL_CRIME = "financial_crime"
    SANCTIONS_VIOLATION = "sanctions_violation"
    REGULATORY_BREACH = "regulatory_breach"
    CRIMINAL_ACTIVITY = "criminal_activity"
    REPUTATIONAL_DAMAGE = "reputational_damage"
    LITIGATION = "litigation"
    COMPLIANCE_FAILURE = "compliance_failure"
    FRAUD = "fraud"
    MONEY_LAUNDERING = "money_laundering"

@dataclass
class MediaAlert:
    """Media alert data structure"""
    alert_id: str
    entity_name: str
    headline: str
    url: str
    source: str
    published_date: datetime
    sentiment: MediaSentiment
    categories: List[AdverseCategory]
    risk_score: float
    content_snippet: str
    confidence_score: float
    detected_at: datetime

class AdverseMediaMonitor:
    """Advanced adverse media monitoring with ML-powered analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitored_entities = set()
        self.adverse_keywords = self._load_adverse_keywords()
        self.media_sources = self._initialize_media_sources()
        self.alerts = []
        self.sentiment_analyzer = None
        self._initialize_nlp()
        
    def _initialize_nlp(self):
        """Initialize NLP components"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            logger.info("NLP components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize advanced NLP: {e}. Using fallback methods.")
    
    def _load_adverse_keywords(self) -> Dict[AdverseCategory, List[str]]:
        """Load adverse keywords for each category"""
        return {
            AdverseCategory.CORRUPTION: [
                'bribery', 'kickback', 'corruption', 'corrupt', 'embezzlement',
                'graft', 'payoff', 'under the table', 'illicit payment',
                'political corruption', 'abuse of power', 'cronyism'
            ],
            AdverseCategory.FINANCIAL_CRIME: [
                'financial crime', 'market manipulation', 'insider trading',
                'securities fraud', 'tax evasion', 'tax fraud', 'ponzi scheme',
                'pyramid scheme', 'investment fraud', 'accounting fraud'
            ],
            AdverseCategory.SANCTIONS_VIOLATION: [
                'sanctions violation', 'embargo breach', 'restricted entity',
                'blocked assets', 'ofac violation', 'trade restriction',
                'economic sanctions', 'financial sanctions'
            ],
            AdverseCategory.REGULATORY_BREACH: [
                'regulatory violation', 'compliance breach', 'regulatory fine',
                'consent order', 'cease and desist', 'enforcement action',
                'regulatory investigation', 'non-compliance'
            ],
            AdverseCategory.CRIMINAL_ACTIVITY: [
                'criminal charges', 'indictment', 'arrest', 'prosecution',
                'criminal investigation', 'felony', 'misdemeanor',
                'criminal conduct', 'illegal activity'
            ],
            AdverseCategory.LITIGATION: [
                'lawsuit', 'legal action', 'court case', 'litigation',
                'class action', 'settlement', 'judgment', 'damages',
                'civil suit', 'legal dispute'
            ],
            AdverseCategory.FRAUD: [
                'fraud', 'fraudulent', 'deception', 'misrepresentation',
                'false statements', 'scheme to defraud', 'wire fraud',
                'mail fraud', 'bank fraud', 'credit card fraud'
            ],
            AdverseCategory.MONEY_LAUNDERING: [
                'money laundering', 'aml violation', 'suspicious transactions',
                'structuring', 'smurfing', 'placement', 'layering',
                'integration', 'suspicious activity report', 'currency transaction report'
            ]
        }
    
    def _initialize_media_sources(self) -> List[Dict[str, str]]:
        """Initialize media sources for monitoring"""
        return [
            {
                'name': 'Reuters',
                'url': 'https://feeds.reuters.com/reuters/topNews',
                'type': 'rss'
            },
            {
                'name': 'Associated Press',
                'url': 'https://feeds.apnews.com/rss/apf-topnews',
                'type': 'rss'
            },
            {
                'name': 'Financial Times',
                'url': 'https://www.ft.com/rss/home',
                'type': 'rss'
            },
            {
                'name': 'BBC News',
                'url': 'http://feeds.bbci.co.uk/news/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Wall Street Journal',
                'url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
                'type': 'rss'
            },
            {
                'name': 'Bloomberg',
                'url': 'https://feeds.bloomberg.com/top-headlines.rss',
                'type': 'rss'
            }
        ]
    
    def add_monitored_entity(self, entity_name: str, entity_type: str = "general") -> bool:
        """
        Add entity to monitoring list
        
        Args:
            entity_name: Name of entity to monitor
            entity_type: Type of entity (person, organization, etc.)
            
        Returns:
            Success status
        """
        try:
            entity_key = f"{entity_name.lower()}:{entity_type}"
            self.monitored_entities.add(entity_key)
            logger.info(f"Added {entity_name} to adverse media monitoring")
            return True
        except Exception as e:
            logger.error(f"Error adding entity to monitoring: {e}")
            return False
    
    def remove_monitored_entity(self, entity_name: str, entity_type: str = "general") -> bool:
        """Remove entity from monitoring list"""
        try:
            entity_key = f"{entity_name.lower()}:{entity_type}"
            self.monitored_entities.discard(entity_key)
            logger.info(f"Removed {entity_name} from adverse media monitoring")
            return True
        except Exception as e:
            logger.error(f"Error removing entity from monitoring: {e}")
            return False
    
    async def monitor_continuous(self) -> None:
        """Continuous monitoring of adverse media"""
        logger.info("Starting continuous adverse media monitoring")
        
        while True:
            try:
                await self.scan_all_sources()
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def scan_all_sources(self) -> List[MediaAlert]:
        """Scan all media sources for adverse content"""
        logger.info("Scanning all media sources for adverse content")
        
        new_alerts = []
        tasks = []
        
        # Create tasks for each media source
        for source in self.media_sources:
            task = self._scan_media_source(source)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Media scanning error: {result}")
                continue
            
            if result:
                new_alerts.extend(result)
        
        # Store new alerts
        self.alerts.extend(new_alerts)
        
        # Keep only recent alerts (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.alerts = [alert for alert in self.alerts if alert.detected_at > cutoff_date]
        
        logger.info(f"Completed media scan: {len(new_alerts)} new alerts found")
        return new_alerts
    
    async def _scan_media_source(self, source: Dict[str, str]) -> List[MediaAlert]:
        """Scan a specific media source"""
        alerts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source['url'], timeout=30) as response:
                    content = await response.text()
                    
                    if source['type'] == 'rss':
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries:
                            # Check if article is relevant to monitored entities
                            relevance_results = self._check_entity_relevance(entry)
                            
                            if relevance_results:
                                # Analyze for adverse content
                                adverse_analysis = self._analyze_adverse_content(entry)
                                
                                if adverse_analysis['is_adverse']:
                                    alert = self._create_media_alert(
                                        entry, source['name'], 
                                        relevance_results, adverse_analysis
                                    )
                                    alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error scanning {source['name']}: {e}")
        
        return alerts
    
    def _check_entity_relevance(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if article is relevant to monitored entities"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        relevant_entities = []
        
        for entity_key in self.monitored_entities:
            entity_name, entity_type = entity_key.split(':', 1)
            
            # Check for entity mentions
            if entity_name in content:
                # Calculate relevance strength
                mentions = content.count(entity_name)
                relevance_score = min(mentions * 0.2, 1.0)
                
                relevant_entities.append({
                    'entity_name': entity_name,
                    'entity_type': entity_type,
                    'mentions': mentions,
                    'relevance_score': relevance_score
                })
        
        if relevant_entities:
            return {
                'entities': relevant_entities,
                'max_relevance': max(e['relevance_score'] for e in relevant_entities)
            }
        
        return None
    
    def _analyze_adverse_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze article content for adverse indicators"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = f"{title} {summary}".lower()
        
        # Check for adverse keywords
        detected_categories = []
        category_scores = {}
        
        for category, keywords in self.adverse_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in content:
                    matches = content.count(keyword)
                    score += matches * (len(keyword) / 10)  # Weight by keyword length
                    matched_keywords.append(keyword)
            
            if score > 0:
                detected_categories.append(category)
                category_scores[category.value] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        # Sentiment analysis
        sentiment_result = self._analyze_sentiment(content)
        
        # Calculate overall adverse score
        adverse_score = 0
        if detected_categories:
            category_weight = len(detected_categories) * 0.3
            keyword_weight = sum(scores['score'] for scores in category_scores.values()) * 0.1
            sentiment_weight = abs(sentiment_result['compound']) * 0.4
            
            adverse_score = min(category_weight + keyword_weight + sentiment_weight, 1.0)
        
        is_adverse = adverse_score > 0.3  # Threshold for adverse content
        
        return {
            'is_adverse': is_adverse,
            'adverse_score': adverse_score,
            'detected_categories': detected_categories,
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text content"""
        try:
            if self.sentiment_analyzer:
                # Use VADER sentiment analyzer
                scores = self.sentiment_analyzer.polarity_scores(text)
                return scores
            elif TEXTBLOB_AVAILABLE:
                # Fallback to TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                return {
                    'negative': max(-polarity, 0),
                    'neutral': 1 - abs(polarity),
                    'positive': max(polarity, 0),
                    'compound': polarity
                }
            else:
                # Basic sentiment analysis fallback
                negative_words = ['bad', 'negative', 'fraud', 'criminal', 'illegal', 'violation']
                positive_words = ['good', 'positive', 'success', 'growth', 'profit']
                
                text_lower = text.lower()
                neg_count = sum(1 for word in negative_words if word in text_lower)
                pos_count = sum(1 for word in positive_words if word in text_lower)
                
                if neg_count > pos_count:
                    compound = -0.5
                elif pos_count > neg_count:
                    compound = 0.5
                else:
                    compound = 0.0
                
                return {
                    'negative': max(-compound, 0),
                    'neutral': 1 - abs(compound),
                    'positive': max(compound, 0),
                    'compound': compound
                }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'negative': 0, 'neutral': 1, 'positive': 0, 'compound': 0}
    
    def _create_media_alert(self, article: Dict[str, Any], source_name: str,
                           relevance: Dict[str, Any], adverse_analysis: Dict[str, Any]) -> MediaAlert:
        """Create media alert from analysis results"""
        
        # Generate unique alert ID
        alert_content = f"{article.get('title', '')}{article.get('link', '')}{source_name}"
        alert_id = hashlib.md5(alert_content.encode()).hexdigest()
        
        # Determine primary entity
        primary_entity = relevance['entities'][0]['entity_name']
        
        # Map sentiment score to enum
        sentiment_score = adverse_analysis['sentiment']['compound']
        if sentiment_score <= -0.6:
            sentiment = MediaSentiment.VERY_NEGATIVE
        elif sentiment_score <= -0.2:
            sentiment = MediaSentiment.NEGATIVE
        elif sentiment_score <= 0.2:
            sentiment = MediaSentiment.NEUTRAL
        elif sentiment_score <= 0.6:
            sentiment = MediaSentiment.POSITIVE
        else:
            sentiment = MediaSentiment.VERY_POSITIVE
        
        # Parse published date
        published_str = article.get('published', '')
        try:
            from dateutil import parser
            published_date = parser.parse(published_str)
        except:
            published_date = datetime.now()
        
        alert = MediaAlert(
            alert_id=alert_id,
            entity_name=primary_entity,
            headline=article.get('title', ''),
            url=article.get('link', ''),
            source=source_name,
            published_date=published_date,
            sentiment=sentiment,
            categories=adverse_analysis['detected_categories'],
            risk_score=adverse_analysis['adverse_score'],
            content_snippet=article.get('summary', '')[:500],
            confidence_score=adverse_analysis['confidence'],
            detected_at=datetime.now()
        )
        
        return alert
    
    def get_alerts_for_entity(self, entity_name: str, 
                             days_back: int = 7) -> List[MediaAlert]:
        """Get recent alerts for a specific entity"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        entity_alerts = [
            alert for alert in self.alerts
            if (alert.entity_name.lower() == entity_name.lower() and
                alert.detected_at > cutoff_date)
        ]
        
        # Sort by risk score (highest first)
        entity_alerts.sort(key=lambda x: x.risk_score, reverse=True)
        
        return entity_alerts
    
    def get_high_risk_alerts(self, risk_threshold: float = 0.7,
                           days_back: int = 7) -> List[MediaAlert]:
        """Get high-risk alerts across all entities"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        high_risk_alerts = [
            alert for alert in self.alerts
            if (alert.risk_score >= risk_threshold and
                alert.detected_at > cutoff_date)
        ]
        
        # Sort by risk score (highest first)
        high_risk_alerts.sort(key=lambda x: x.risk_score, reverse=True)
        
        return high_risk_alerts
    
    def generate_media_report(self, entity_name: str = None) -> Dict[str, Any]:
        """Generate comprehensive adverse media report"""
        report_date = datetime.now()
        
        if entity_name:
            alerts = self.get_alerts_for_entity(entity_name, days_back=30)
            title = f"Adverse Media Report - {entity_name}"
        else:
            alerts = [alert for alert in self.alerts 
                     if alert.detected_at > (report_date - timedelta(days=30))]
            title = "Global Adverse Media Report"
        
        # Calculate statistics
        total_alerts = len(alerts)
        high_risk_count = len([a for a in alerts if a.risk_score >= 0.7])
        medium_risk_count = len([a for a in alerts if 0.4 <= a.risk_score < 0.7])
        low_risk_count = len([a for a in alerts if a.risk_score < 0.4])
        
        # Category breakdown
        category_counts = {}
        for alert in alerts:
            for category in alert.categories:
                category_counts[category.value] = category_counts.get(category.value, 0) + 1
        
        # Source breakdown
        source_counts = {}
        for alert in alerts:
            source_counts[alert.source] = source_counts.get(alert.source, 0) + 1
        
        # Trend analysis
        daily_counts = {}
        for alert in alerts:
            date_key = alert.detected_at.strftime('%Y-%m-%d')
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        report = {
            'report_title': title,
            'generated_at': report_date.isoformat(),
            'period_days': 30,
            'summary': {
                'total_alerts': total_alerts,
                'high_risk_alerts': high_risk_count,
                'medium_risk_alerts': medium_risk_count,
                'low_risk_alerts': low_risk_count,
                'monitored_entities': len(self.monitored_entities)
            },
            'category_breakdown': category_counts,
            'source_breakdown': source_counts,
            'daily_trend': daily_counts,
            'top_alerts': [
                {
                    'entity': alert.entity_name,
                    'headline': alert.headline,
                    'source': alert.source,
                    'risk_score': alert.risk_score,
                    'sentiment': alert.sentiment.value,
                    'url': alert.url,
                    'detected_at': alert.detected_at.isoformat()
                }
                for alert in sorted(alerts, key=lambda x: x.risk_score, reverse=True)[:10]
            ]
        }
        
        return report
    
    async def search_historical_media(self, entity_name: str, 
                                    keywords: List[str] = None,
                                    date_range: Tuple[datetime, datetime] = None) -> List[Dict[str, Any]]:
        """Search historical media for specific entity and keywords"""
        # This would integrate with media archives and search APIs
        # Implementation would depend on available media database APIs
        
        logger.info(f"Historical media search for {entity_name}")
        
        # Placeholder implementation
        return [{
            'message': 'Historical media search functionality ready for implementation',
            'entity': entity_name,
            'keywords': keywords,
            'date_range': date_range,
            'note': 'Requires integration with media archive APIs'
        }]
