"""
Adverse Media Intelligence Service
Comprehensive monitoring and analysis of negative news and media coverage
"""

import asyncio
import json
import logging
import requests
import re
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import aiohttp
from bs4 import BeautifulSoup
import feedparser
import textblob
from urllib.parse import urljoin, urlparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AdverseMediaArticle:
    """Individual adverse media article data model"""
    source: str
    article_id: str
    title: str
    url: str
    content: str
    publish_date: datetime
    author: Optional[str] = None
    publication: Optional[str] = None
    language: str = "en"
    sentiment_score: float = 0.0  # -1 (negative) to 1 (positive)
    severity_score: float = 0.0   # 0 (low) to 1 (high)
    entities_mentioned: List[str] = None
    topics: List[str] = None
    keywords: List[str] = None
    geographic_relevance: List[str] = None
    risk_categories: List[str] = None  # corruption, sanctions, crime, etc.
    credibility_score: float = 0.5  # 0 (low) to 1 (high)
    impact_score: float = 0.0     # Combined metric
    last_updated: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.entities_mentioned is None:
            self.entities_mentioned = []
        if self.topics is None:
            self.topics = []
        if self.keywords is None:
            self.keywords = []
        if self.geographic_relevance is None:
            self.geographic_relevance = []
        if self.risk_categories is None:
            self.risk_categories = []

@dataclass
class MediaSource:
    """Media source configuration"""
    source_id: str
    name: str
    source_type: str  # news, social, blog, forum, darkweb
    coverage_scope: str  # global, regional, national, local
    language: str
    update_frequency: str  # realtime, hourly, daily
    access_method: str  # rss, api, scraping, social_api
    base_url: str
    credibility_rating: float = 0.5  # 0 (low) to 1 (high)
    api_key_required: bool = False
    rate_limit: Optional[int] = None  # requests per hour
    cost_model: str = "free"
    last_updated: Optional[datetime] = None
    status: str = "active"
    articles_collected: int = 0

class AdverseMediaService:
    """Comprehensive adverse media monitoring and intelligence service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.sources = {}
        self.articles_cache = {}
        self.cache_ttl = timedelta(hours=6)  # 6 hour cache for media
        
        # Risk keywords for classification
        self.risk_keywords = {
            "corruption": ["bribery", "corruption", "kickback", "embezzlement", "fraud", "laundering"],
            "sanctions": ["sanctions", "embargo", "blocked", "frozen assets", "OFAC", "designated"],
            "crime": ["arrested", "charged", "convicted", "indicted", "criminal", "illegal"],
            "terrorism": ["terrorist", "terrorism", "extremist", "radical", "bomb", "attack"],
            "tax_evasion": ["tax evasion", "tax fraud", "offshore", "tax haven", "undeclared"],
            "drug_trafficking": ["drug trafficking", "narcotics", "cocaine", "heroin", "cartel"],
            "human_trafficking": ["human trafficking", "forced labor", "sex trafficking", "slavery"],
            "cybercrime": ["cybercrime", "hacking", "malware", "ransomware", "data breach"],
            "financial_crime": ["financial crime", "securities fraud", "insider trading", "market manipulation"]
        }
        
        # Initialize media sources
        self._initialize_sources()
        
        self.logger.info(f"Initialized {len(self.sources)} adverse media sources")
    
    def _initialize_sources(self):
        """Initialize all adverse media sources"""
        
        # Reuters News API
        reuters_source = MediaSource(
            source_id="reuters",
            name="Reuters News",
            source_type="news",
            coverage_scope="global",
            language="en",
            update_frequency="realtime",
            access_method="api",
            base_url="https://api.reuters.com/v1",
            credibility_rating=0.9,
            api_key_required=True,
            cost_model="subscription"
        )
        
        # Associated Press
        ap_source = MediaSource(
            source_id="associated_press",
            name="Associated Press",
            source_type="news",
            coverage_scope="global",
            language="en",
            update_frequency="realtime",
            access_method="rss",
            base_url="https://feeds.apnews.com/rss/apf-topnews",
            credibility_rating=0.9,
            api_key_required=False,
            cost_model="free"
        )
        
        # BBC News
        bbc_source = MediaSource(
            source_id="bbc_news",
            name="BBC News",
            source_type="news",
            coverage_scope="global",
            language="en",
            update_frequency="hourly",
            access_method="rss",
            base_url="http://feeds.bbci.co.uk/news/rss.xml",
            credibility_rating=0.85,
            api_key_required=False,
            cost_model="free"
        )
        
        # Financial Times
        ft_source = MediaSource(
            source_id="financial_times",
            name="Financial Times",
            source_type="news",
            coverage_scope="global",
            language="en",
            update_frequency="daily",
            access_method="scraping",
            base_url="https://www.ft.com",
            credibility_rating=0.9,
            api_key_required=False,
            cost_model="subscription"
        )
        
        # Twitter/X API for social media monitoring
        twitter_source = MediaSource(
            source_id="twitter",
            name="Twitter/X",
            source_type="social",
            coverage_scope="global",
            language="en",
            update_frequency="realtime",
            access_method="social_api",
            base_url="https://api.twitter.com/2",
            credibility_rating=0.3,
            api_key_required=True,
            rate_limit=300,
            cost_model="freemium"
        )
        
        # Reddit for forum monitoring
        reddit_source = MediaSource(
            source_id="reddit",
            name="Reddit",
            source_type="forum",
            coverage_scope="global",
            language="en",
            update_frequency="realtime",
            access_method="api",
            base_url="https://www.reddit.com/api/v1",
            credibility_rating=0.2,
            api_key_required=True,
            cost_model="free"
        )
        
        # GDELT Project for global events
        gdelt_source = MediaSource(
            source_id="gdelt",
            name="GDELT Project",
            source_type="news",
            coverage_scope="global",
            language="multi",
            update_frequency="daily",
            access_method="api",
            base_url="https://api.gdeltproject.org/api/v2",
            credibility_rating=0.7,
            api_key_required=False,
            cost_model="free"
        )
        
        # Dark Web Monitoring (simulated)
        darkweb_source = MediaSource(
            source_id="darkweb_monitor",
            name="Dark Web Intelligence",
            source_type="darkweb",
            coverage_scope="global",
            language="multi",
            update_frequency="daily",
            access_method="specialized",
            base_url="https://darkweb-intel.example.com",
            credibility_rating=0.4,
            api_key_required=True,
            cost_model="subscription"
        )
        
        # Local News Aggregator
        local_news_source = MediaSource(
            source_id="local_news_agg",
            name="Local News Aggregator",
            source_type="news",
            coverage_scope="regional",
            language="en",
            update_frequency="daily",
            access_method="rss",
            base_url="https://local-news-feeds.example.com",
            credibility_rating=0.6,
            api_key_required=False,
            cost_model="free"
        )
        
        # Regulatory Announcements
        regulatory_source = MediaSource(
            source_id="regulatory_announcements",
            name="Regulatory Announcements",
            source_type="news",
            coverage_scope="global",
            language="en",
            update_frequency="daily",
            access_method="scraping",
            base_url="https://regulatory-feeds.example.com",
            credibility_rating=0.95,
            api_key_required=False,
            cost_model="free"
        )
        
        sources = [
            reuters_source, ap_source, bbc_source, ft_source, twitter_source,
            reddit_source, gdelt_source, darkweb_source, local_news_source, regulatory_source
        ]
        
        for source in sources:
            self.sources[source.source_id] = source
    
    async def monitor_adverse_media(self, entities: List[str], 
                                  source_ids: Optional[List[str]] = None,
                                  time_range: Optional[int] = 7) -> Dict[str, List[AdverseMediaArticle]]:
        """Monitor adverse media for specified entities"""
        
        if source_ids:
            sources_to_monitor = [self.sources[sid] for sid in source_ids if sid in self.sources]
        else:
            sources_to_monitor = list(self.sources.values())
        
        results = {}
        
        for source in sources_to_monitor:
            try:
                self.logger.info(f"Monitoring {source.name} for entities: {entities}")
                
                if source.access_method == "rss":
                    articles = await self._monitor_rss_source(source, entities, time_range)
                elif source.access_method == "api":
                    articles = await self._monitor_api_source(source, entities, time_range)
                elif source.access_method == "social_api":
                    articles = await self._monitor_social_source(source, entities, time_range)
                elif source.access_method == "scraping":
                    articles = await self._monitor_scraping_source(source, entities, time_range)
                elif source.access_method == "specialized":
                    articles = await self._monitor_specialized_source(source, entities, time_range)
                else:
                    self.logger.warning(f"Unknown access method for {source.source_id}: {source.access_method}")
                    continue
                
                # Process and analyze articles
                processed_articles = []
                for article in articles:
                    processed_article = await self._process_article(article, entities)
                    if processed_article:
                        processed_articles.append(processed_article)
                
                results[source.source_id] = processed_articles
                
                # Update source metadata
                source.last_updated = datetime.now()
                source.articles_collected = len(processed_articles)
                source.status = "active"
                
                self.logger.info(f"Collected {len(processed_articles)} relevant articles from {source.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to monitor {source.source_id}: {e}")
                source.status = "error"
                results[source.source_id] = []
        
        return results
    
    async def _monitor_rss_source(self, source: MediaSource, entities: List[str], 
                                time_range: int) -> List[Dict[str, Any]]:
        """Monitor RSS-based sources"""
        articles = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.base_url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    rss_content = await response.text()
            
            # Parse RSS feed
            feed = feedparser.parse(rss_content)
            
            cutoff_date = datetime.now() - timedelta(days=time_range)
            
            for entry in feed.entries:
                # Parse publication date
                pub_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Skip old articles
                if pub_date < cutoff_date:
                    continue
                
                # Check if any entity is mentioned
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                content = f"{title} {summary}"
                
                if self._contains_entities(content, entities):
                    articles.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'content': summary,
                        'publish_date': pub_date,
                        'author': entry.get('author', None),
                        'publication': source.name
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to parse RSS from {source.name}: {e}")
        
        return articles
    
    async def _monitor_api_source(self, source: MediaSource, entities: List[str], 
                                time_range: int) -> List[Dict[str, Any]]:
        """Monitor API-based sources"""
        articles = []
        
        headers = {}
        
        # Add API key if required
        if source.api_key_required:
            api_key = self._get_api_key(source.source_id)
            if api_key:
                if source.source_id == "reuters":
                    headers["Authorization"] = f"Bearer {api_key}"
                elif source.source_id == "gdelt":
                    # GDELT doesn't require auth but has specific format
                    pass
        
        try:
            # Build search query
            query_params = self._build_api_query(source, entities, time_range)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{source.base_url}/search", 
                                     headers=headers, params=query_params) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    data = await response.json()
            
            # Parse API response based on source
            if source.source_id == "reuters":
                articles = self._parse_reuters_response(data)
            elif source.source_id == "gdelt":
                articles = self._parse_gdelt_response(data)
            elif source.source_id == "reddit":
                articles = self._parse_reddit_response(data)
            
        except Exception as e:
            self.logger.error(f"Failed to query API for {source.name}: {e}")
        
        return articles
    
    async def _monitor_social_source(self, source: MediaSource, entities: List[str], 
                                   time_range: int) -> List[Dict[str, Any]]:
        """Monitor social media sources"""
        articles = []
        
        if source.source_id == "twitter":
            articles = await self._monitor_twitter(entities, time_range)
        
        return articles
    
    async def _monitor_scraping_source(self, source: MediaSource, entities: List[str], 
                                     time_range: int) -> List[Dict[str, Any]]:
        """Monitor scraping-based sources"""
        articles = []
        
        if source.source_id == "financial_times":
            articles = await self._scrape_financial_times(entities, time_range)
        elif source.source_id == "regulatory_announcements":
            articles = await self._scrape_regulatory_announcements(entities, time_range)
        
        return articles
    
    async def _monitor_specialized_source(self, source: MediaSource, entities: List[str], 
                                        time_range: int) -> List[Dict[str, Any]]:
        """Monitor specialized sources like dark web"""
        articles = []
        
        if source.source_id == "darkweb_monitor":
            articles = await self._monitor_darkweb(entities, time_range)
        
        return articles
    
    async def _monitor_twitter(self, entities: List[str], time_range: int) -> List[Dict[str, Any]]:
        """Monitor Twitter for mentions"""
        articles = []
        
        # Simulated Twitter monitoring (in production, use Twitter API v2)
        simulated_tweets = [
            {
                "title": f"Breaking: Investigation into {entities[0] if entities else 'Company X'}",
                "content": f"Authorities are investigating allegations of financial irregularities involving {entities[0] if entities else 'Company X'}. More details to follow.",
                "url": "https://twitter.com/user/status/123456789",
                "publish_date": datetime.now() - timedelta(hours=2),
                "author": "@NewsReporter"
            }
        ]
        
        return simulated_tweets
    
    async def _scrape_financial_times(self, entities: List[str], time_range: int) -> List[Dict[str, Any]]:
        """Scrape Financial Times"""
        articles = []
        
        # Simulated FT scraping
        for entity in entities[:1]:  # Limit to avoid overload
            simulated_article = {
                "title": f"Regulatory scrutiny increases for {entity}",
                "content": f"Financial regulators are stepping up oversight of {entity} following recent compliance concerns.",
                "url": f"https://www.ft.com/content/example-{hash(entity)}",
                "publish_date": datetime.now() - timedelta(days=1),
                "author": "Financial Reporter",
                "publication": "Financial Times"
            }
            articles.append(simulated_article)
        
        return articles
    
    async def _scrape_regulatory_announcements(self, entities: List[str], time_range: int) -> List[Dict[str, Any]]:
        """Scrape regulatory announcements"""
        articles = []
        
        # Simulated regulatory announcements
        regulatory_articles = [
            {
                "title": "SEC Enforcement Action Notice",
                "content": f"The Securities and Exchange Commission announced enforcement proceedings against {entities[0] if entities else 'undisclosed entity'}.",
                "url": "https://www.sec.gov/news/press-release/example",
                "publish_date": datetime.now() - timedelta(days=2),
                "author": "SEC",
                "publication": "SEC Press Releases"
            }
        ]
        
        return regulatory_articles
    
    async def _monitor_darkweb(self, entities: List[str], time_range: int) -> List[Dict[str, Any]]:
        """Monitor dark web for mentions"""
        articles = []
        
        # Simulated dark web monitoring
        darkweb_mentions = [
            {
                "title": f"Data breach discussion involving {entities[0] if entities else 'target entity'}",
                "content": f"Forum users discussing potential vulnerabilities in {entities[0] if entities else 'target entity'} systems.",
                "url": "onion://darkforum.onion/thread/12345",
                "publish_date": datetime.now() - timedelta(days=3),
                "author": "Anonymous",
                "publication": "Dark Web Forum"
            }
        ]
        
        return darkweb_mentions
    
    def _contains_entities(self, content: str, entities: List[str]) -> bool:
        """Check if content contains any of the specified entities"""
        content_lower = content.lower()
        return any(entity.lower() in content_lower for entity in entities)
    
    def _build_api_query(self, source: MediaSource, entities: List[str], time_range: int) -> Dict[str, Any]:
        """Build API query parameters"""
        
        query = " OR ".join(f'"{entity}"' for entity in entities)
        
        params = {
            "q": query,
            "from": (datetime.now() - timedelta(days=time_range)).isoformat(),
            "to": datetime.now().isoformat(),
            "sortBy": "publishedAt",
            "language": source.language
        }
        
        return params
    
    def _parse_reuters_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Reuters API response"""
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': article.get('description', ''),
                'publish_date': datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                'author': article.get('author'),
                'publication': 'Reuters'
            })
        
        return articles
    
    def _parse_gdelt_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse GDELT API response"""
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': article.get('content', ''),
                'publish_date': datetime.fromisoformat(article.get('seendate', '')),
                'author': None,
                'publication': article.get('domain', '')
            })
        
        return articles
    
    def _parse_reddit_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Reddit API response"""
        articles = []
        
        for post in data.get('data', {}).get('children', []):
            post_data = post.get('data', {})
            articles.append({
                'title': post_data.get('title', ''),
                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                'content': post_data.get('selftext', ''),
                'publish_date': datetime.fromtimestamp(post_data.get('created_utc', 0)),
                'author': post_data.get('author'),
                'publication': f"r/{post_data.get('subreddit', '')}"
            })
        
        return articles
    
    async def _process_article(self, article_data: Dict[str, Any], 
                             target_entities: List[str]) -> Optional[AdverseMediaArticle]:
        """Process and analyze article for adverse content"""
        
        try:
            # Generate unique article ID
            article_id = hashlib.md5(
                f"{article_data.get('url', '')}{article_data.get('title', '')}".encode()
            ).hexdigest()
            
            # Extract content for analysis
            content = f"{article_data.get('title', '')} {article_data.get('content', '')}"
            
            # Sentiment analysis
            sentiment_score = self._analyze_sentiment(content)
            
            # Risk category classification
            risk_categories = self._classify_risk_categories(content)
            
            # Only process if adverse content is detected
            if sentiment_score > -0.2 and not risk_categories:
                return None
            
            # Entity extraction
            entities_mentioned = self._extract_mentioned_entities(content, target_entities)
            
            # Geographic relevance
            geographic_relevance = self._extract_geographic_relevance(content)
            
            # Calculate severity and impact scores
            severity_score = self._calculate_severity_score(content, risk_categories)
            impact_score = self._calculate_impact_score(sentiment_score, severity_score, 
                                                      len(entities_mentioned))
            
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Create article object
            article = AdverseMediaArticle(
                source=article_data.get('publication', 'Unknown'),
                article_id=article_id,
                title=article_data.get('title', ''),
                url=article_data.get('url', ''),
                content=content,
                publish_date=article_data.get('publish_date', datetime.now()),
                author=article_data.get('author'),
                publication=article_data.get('publication'),
                sentiment_score=sentiment_score,
                severity_score=severity_score,
                entities_mentioned=entities_mentioned,
                keywords=keywords,
                geographic_relevance=geographic_relevance,
                risk_categories=risk_categories,
                credibility_score=self._calculate_credibility_score(article_data),
                impact_score=impact_score,
                last_updated=datetime.now()
            )
            
            return article
            
        except Exception as e:
            self.logger.error(f"Failed to process article: {e}")
            return None
    
    def _analyze_sentiment(self, content: str) -> float:
        """Analyze sentiment of content"""
        try:
            blob = textblob.TextBlob(content)
            return blob.sentiment.polarity
        except:
            # Simple keyword-based sentiment as fallback
            negative_words = ["fraud", "illegal", "criminal", "scandal", "corrupt", "violation"]
            positive_words = ["success", "growth", "expansion", "award", "achievement"]
            
            content_lower = content.lower()
            negative_count = sum(1 for word in negative_words if word in content_lower)
            positive_count = sum(1 for word in positive_words if word in content_lower)
            
            if negative_count + positive_count == 0:
                return 0.0
            
            return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _classify_risk_categories(self, content: str) -> List[str]:
        """Classify risk categories based on content"""
        content_lower = content.lower()
        categories = []
        
        for category, keywords in self.risk_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def _extract_mentioned_entities(self, content: str, target_entities: List[str]) -> List[str]:
        """Extract mentioned entities from content"""
        mentioned = []
        content_lower = content.lower()
        
        for entity in target_entities:
            if entity.lower() in content_lower:
                mentioned.append(entity)
        
        return mentioned
    
    def _extract_geographic_relevance(self, content: str) -> List[str]:
        """Extract geographic relevance from content"""
        # Simple country extraction
        countries = [
            "United States", "China", "Russia", "Germany", "United Kingdom",
            "France", "Japan", "India", "Brazil", "Canada", "Australia"
        ]
        
        content_lower = content.lower()
        relevant = []
        
        for country in countries:
            if country.lower() in content_lower:
                relevant.append(country)
        
        return relevant
    
    def _calculate_severity_score(self, content: str, risk_categories: List[str]) -> float:
        """Calculate severity score based on content and risk categories"""
        base_score = len(risk_categories) * 0.2
        
        # High-impact keywords
        high_impact_words = ["criminal charges", "indictment", "conviction", "prison", 
                           "sanctions", "banned", "frozen assets"]
        
        content_lower = content.lower()
        high_impact_count = sum(1 for word in high_impact_words if word in content_lower)
        
        severity = min(base_score + (high_impact_count * 0.15), 1.0)
        return severity
    
    def _calculate_impact_score(self, sentiment: float, severity: float, 
                              entities_count: int) -> float:
        """Calculate overall impact score"""
        # Negative sentiment contributes positively to adverse impact
        sentiment_impact = abs(min(sentiment, 0))
        
        # Combine factors
        impact = (sentiment_impact * 0.4) + (severity * 0.5) + (min(entities_count * 0.1, 0.1))
        
        return min(impact, 1.0)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content"""
        # Simple keyword extraction
        risk_words = []
        content_lower = content.lower()
        
        all_risk_words = []
        for category_words in self.risk_keywords.values():
            all_risk_words.extend(category_words)
        
        for word in all_risk_words:
            if word in content_lower:
                risk_words.append(word)
        
        return list(set(risk_words))
    
    def _calculate_credibility_score(self, article_data: Dict[str, Any]) -> float:
        """Calculate credibility score based on source and article characteristics"""
        publication = article_data.get('publication', '').lower()
        
        # High credibility sources
        if any(source in publication for source in ['reuters', 'ap news', 'bbc', 'financial times']):
            return 0.9
        
        # Medium credibility sources
        if any(source in publication for source in ['bloomberg', 'wsj', 'guardian']):
            return 0.7
        
        # Social media and forums
        if any(source in publication for source in ['twitter', 'reddit', 'forum']):
            return 0.3
        
        # Default
        return 0.5
    
    def _get_api_key(self, source_id: str) -> Optional[str]:
        """Get API key for source"""
        # In production, load from secure configuration
        api_keys = {
            "reuters": None,
            "twitter": None,
            "reddit": None,
            "darkweb_monitor": None,
        }
        
        return api_keys.get(source_id)
    
    async def search_adverse_media(self, query: str, 
                                 source_ids: Optional[List[str]] = None,
                                 time_range: Optional[int] = 30,
                                 min_impact_score: float = 0.3) -> List[Dict[str, Any]]:
        """Search existing adverse media articles"""
        
        # In production, this would query a database of stored articles
        # For now, simulate search results
        
        search_results = []
        
        # Simulated search results
        if "corruption" in query.lower():
            search_results.append({
                "article_id": "corruption_article_1",
                "title": f"Corruption investigation launched into {query}",
                "url": "https://example-news.com/corruption-investigation",
                "sentiment_score": -0.8,
                "severity_score": 0.9,
                "impact_score": 0.85,
                "risk_categories": ["corruption", "crime"],
                "publish_date": datetime.now() - timedelta(days=5),
                "source": "Reuters"
            })
        
        return search_results
    
    async def get_adverse_media_summary(self, entities: List[str], 
                                      time_range: int = 30) -> Dict[str, Any]:
        """Get comprehensive adverse media summary for entities"""
        
        # Monitor all sources
        monitoring_results = await self.monitor_adverse_media(entities, time_range=time_range)
        
        # Aggregate results
        all_articles = []
        for source_articles in monitoring_results.values():
            all_articles.extend(source_articles)
        
        # Sort by impact score
        all_articles.sort(key=lambda x: x.impact_score, reverse=True)
        
        # Calculate summary statistics
        total_articles = len(all_articles)
        high_impact_articles = len([a for a in all_articles if a.impact_score > 0.7])
        risk_categories = {}
        
        for article in all_articles:
            for category in article.risk_categories:
                risk_categories[category] = risk_categories.get(category, 0) + 1
        
        summary = {
            "entities": entities,
            "time_range_days": time_range,
            "total_articles": total_articles,
            "high_impact_articles": high_impact_articles,
            "average_impact_score": sum(a.impact_score for a in all_articles) / max(total_articles, 1),
            "average_sentiment_score": sum(a.sentiment_score for a in all_articles) / max(total_articles, 1),
            "risk_categories": risk_categories,
            "top_articles": [asdict(a) for a in all_articles[:10]],
            "sources_monitored": list(monitoring_results.keys()),
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    async def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics for all media sources"""
        
        total_sources = len(self.sources)
        active_sources = len([s for s in self.sources.values() if s.status == "active"])
        total_articles = sum(s.articles_collected for s in self.sources.values())
        
        # Group by source type
        by_type = {}
        for source in self.sources.values():
            source_type = source.source_type
            if source_type not in by_type:
                by_type[source_type] = {"sources": 0, "articles": 0}
            by_type[source_type]["sources"] += 1
            by_type[source_type]["articles"] += source.articles_collected
        
        # Group by coverage scope
        by_scope = {}
        for source in self.sources.values():
            scope = source.coverage_scope
            if scope not in by_scope:
                by_scope[scope] = {"sources": 0, "articles": 0}
            by_scope[scope]["sources"] += 1
            by_scope[scope]["articles"] += source.articles_collected
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_articles_collected": total_articles,
            "by_source_type": by_type,
            "by_coverage_scope": by_scope,
            "risk_categories_tracked": len(self.risk_keywords),
            "cache_entries": len(self.articles_cache)
        }
