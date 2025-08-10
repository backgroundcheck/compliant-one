"""
Advanced OSINT Data Aggregation System for Compliant.one
Multi-source intelligence collection with real-time streaming capabilities
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
import feedparser
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class SourceType(Enum):
    """OSINT source types"""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    DARK_WEB = "dark_web"
    REGULATORY = "regulatory"
    SANCTIONS = "sanctions"
    PUBLIC_RECORDS = "public_records"
    FINANCIAL = "financial"
    GEOSPATIAL = "geospatial"

@dataclass
class OSINTSource:
    """OSINT source configuration"""
    name: str
    source_type: SourceType
    url: str
    headers: Dict[str, str]
    rate_limit: float  # requests per second
    enabled: bool = True
    api_key: Optional[str] = None
    last_collection: Optional[datetime] = None

class MultiSourceOSINTCollector:
    """Advanced multi-source OSINT data collector with real-time capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.sources = self._initialize_sources()
        self.session_pool = aiohttp.ClientSession()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def _initialize_sources(self) -> List[OSINTSource]:
        """Initialize OSINT sources configuration"""
        return [
            # News Sources
            OSINTSource(
                name="Reuters",
                source_type=SourceType.NEWS,
                url="https://feeds.reuters.com/reuters/topNews",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.5
            ),
            OSINTSource(
                name="Associated Press",
                source_type=SourceType.NEWS,
                url="https://feeds.apnews.com/rss/apf-topnews",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.5
            ),
            OSINTSource(
                name="Financial Times",
                source_type=SourceType.FINANCIAL,
                url="https://www.ft.com/rss/home",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.3
            ),
            
            # Regulatory Sources
            OSINTSource(
                name="SEC EDGAR",
                source_type=SourceType.REGULATORY,
                url="https://www.sec.gov/Archives/edgar/xbrlrss.xml",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.2
            ),
            OSINTSource(
                name="OFAC Sanctions",
                source_type=SourceType.SANCTIONS,
                url="https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONS_PUBLIC.XML",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.1
            ),
            
            # Social Media Sources (placeholder for API integration)
            OSINTSource(
                name="Twitter API v2",
                source_type=SourceType.SOCIAL_MEDIA,
                url="https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {self.config.get('TWITTER_BEARER_TOKEN', '')}"},
                rate_limit=0.1,
                api_key=self.config.get('TWITTER_BEARER_TOKEN')
            ),
            
            # Geospatial Sources
            OSINTSource(
                name="Natural Earth Data",
                source_type=SourceType.GEOSPATIAL,
                url="https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/",
                headers={"User-Agent": "Compliant.one OSINT Collector"},
                rate_limit=0.1
            )
        ]
    
    async def collect_real_time_streams(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Real-time data streaming from multiple OSINT sources
        
        Yields:
            Dict containing collected data with metadata
        """
        logger.info("Starting real-time OSINT data collection")
        
        while True:
            try:
                # Collect from all enabled sources
                tasks = []
                for source in self.sources:
                    if source.enabled:
                        if self._should_collect(source):
                            tasks.append(self._collect_from_source(source))
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error(f"Collection error: {result}")
                            continue
                        
                        if result:
                            yield result
                
                # Rate limiting - sleep between collection cycles
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Real-time collection error: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    def _should_collect(self, source: OSINTSource) -> bool:
        """Determine if we should collect from this source based on rate limiting"""
        if not source.last_collection:
            return True
        
        time_since_last = datetime.utcnow() - source.last_collection
        min_interval = timedelta(seconds=1.0 / source.rate_limit)
        
        return time_since_last >= min_interval
    
    async def _collect_from_source(self, source: OSINTSource) -> Optional[Dict[str, Any]]:
        """
        Collect data from a specific OSINT source
        
        Args:
            source: OSINT source configuration
            
        Returns:
            Collected data with metadata
        """
        try:
            logger.debug(f"Collecting from {source.name}")
            
            if source.source_type == SourceType.NEWS:
                data = await self._collect_news_feed(source)
            elif source.source_type == SourceType.SANCTIONS:
                data = await self._collect_sanctions_data(source)
            elif source.source_type == SourceType.REGULATORY:
                data = await self._collect_regulatory_data(source)
            elif source.source_type == SourceType.SOCIAL_MEDIA:
                data = await self._collect_social_media(source)
            elif source.source_type == SourceType.GEOSPATIAL:
                data = await self._collect_geospatial_data(source)
            else:
                data = await self._collect_generic_feed(source)
            
            if data:
                source.last_collection = datetime.utcnow()
                return {
                    'source_name': source.name,
                    'source_type': source.source_type.value,
                    'collected_at': datetime.utcnow().isoformat(),
                    'data': data
                }
            
        except Exception as e:
            logger.error(f"Error collecting from {source.name}: {e}")
            return None
    
    async def _collect_news_feed(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Collect news feed data"""
        try:
            async with self.session_pool.get(source.url, headers=source.headers) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:20]:  # Limit to recent articles
                    article = {
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'author': entry.get('author', ''),
                        'categories': [tag.term for tag in entry.get('tags', [])],
                        'raw_entry': dict(entry)
                    }
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"News feed collection error for {source.name}: {e}")
            return []
    
    async def _collect_sanctions_data(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Collect sanctions and watchlist data"""
        try:
            async with self.session_pool.get(source.url, headers=source.headers) as response:
                content = await response.text()
                
                # Parse XML sanctions data
                from xml.etree import ElementTree as ET
                root = ET.fromstring(content)
                
                sanctions = []
                # Parse OFAC XML structure
                for entry in root.findall('.//sdnEntry'):
                    sanction = {
                        'uid': entry.get('uid', ''),
                        'first_name': entry.findtext('.//firstName', ''),
                        'last_name': entry.findtext('.//lastName', ''),
                        'title': entry.findtext('.//title', ''),
                        'entity_type': entry.get('sdnType', ''),
                        'programs': [prog.text for prog in entry.findall('.//program')],
                        'addresses': [addr.text for addr in entry.findall('.//address')],
                        'dates_of_birth': [dob.text for dob in entry.findall('.//dateOfBirth')],
                        'places_of_birth': [pob.text for pob in entry.findall('.//placeOfBirth')],
                        'nationalities': [nat.text for nat in entry.findall('.//nationality')],
                        'citizenships': [cit.text for cit in entry.findall('.//citizenship')]
                    }
                    sanctions.append(sanction)
                
                return sanctions[:100]  # Limit for processing
                
        except Exception as e:
            logger.error(f"Sanctions data collection error for {source.name}: {e}")
            return []
    
    async def _collect_regulatory_data(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Collect regulatory filings and data"""
        try:
            async with self.session_pool.get(source.url, headers=source.headers) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                filings = []
                for entry in feed.entries[:50]:
                    filing = {
                        'title': entry.get('title', ''),
                        'company': entry.get('edgar:xbrlFiling', {}).get('edgar:companyName', ''),
                        'cik': entry.get('edgar:xbrlFiling', {}).get('edgar:cikNumber', ''),
                        'form_type': entry.get('edgar:xbrlFiling', {}).get('edgar:formType', ''),
                        'filing_date': entry.get('edgar:xbrlFiling', {}).get('edgar:filingDate', ''),
                        'period': entry.get('edgar:xbrlFiling', {}).get('edgar:period', ''),
                        'url': entry.get('link', ''),
                        'description': entry.get('summary', '')
                    }
                    filings.append(filing)
                
                return filings
                
        except Exception as e:
            logger.error(f"Regulatory data collection error for {source.name}: {e}")
            return []
    
    async def _collect_social_media(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Collect social media data (Twitter API example)"""
        if not source.api_key:
            logger.warning(f"No API key configured for {source.name}")
            return []
        
        try:
            # Example Twitter API v2 search
            params = {
                'query': 'compliance OR sanctions OR corruption',
                'max_results': 100,
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations'
            }
            
            async with self.session_pool.get(
                source.url,
                headers=source.headers,
                params=params
            ) as response:
                data = await response.json()
                
                tweets = []
                for tweet in data.get('data', []):
                    tweet_data = {
                        'id': tweet.get('id'),
                        'text': tweet.get('text'),
                        'created_at': tweet.get('created_at'),
                        'author_id': tweet.get('author_id'),
                        'retweet_count': tweet.get('public_metrics', {}).get('retweet_count', 0),
                        'like_count': tweet.get('public_metrics', {}).get('like_count', 0),
                        'context_annotations': tweet.get('context_annotations', [])
                    }
                    tweets.append(tweet_data)
                
                return tweets
                
        except Exception as e:
            logger.error(f"Social media collection error for {source.name}: {e}")
            return []
    
    async def _collect_geospatial_data(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Collect geospatial intelligence data"""
        try:
            # Placeholder for geospatial data collection
            # Could integrate with various mapping APIs, satellite data, etc.
            return [{
                'type': 'geospatial_placeholder',
                'message': 'Geospatial data collection ready for implementation',
                'timestamp': datetime.utcnow().isoformat()
            }]
            
        except Exception as e:
            logger.error(f"Geospatial collection error for {source.name}: {e}")
            return []
    
    async def _collect_generic_feed(self, source: OSINTSource) -> List[Dict[str, Any]]:
        """Generic feed collection for unspecified source types"""
        try:
            async with self.session_pool.get(source.url, headers=source.headers) as response:
                content = await response.text()
                
                # Try RSS/Atom first
                feed = feedparser.parse(content)
                if feed.entries:
                    return [dict(entry) for entry in feed.entries[:20]]
                
                # Try JSON
                try:
                    data = json.loads(content)
                    return [data] if isinstance(data, dict) else data[:20] if isinstance(data, list) else []
                except:
                    pass
                
                # Fallback to raw content
                return [{
                    'raw_content': content[:1000],
                    'content_type': response.headers.get('content-type', 'unknown')
                }]
                
        except Exception as e:
            logger.error(f"Generic collection error for {source.name}: {e}")
            return []
    
    async def search_entity(self, entity_name: str, entity_type: str = None) -> Dict[str, Any]:
        """
        Search for specific entity across all OSINT sources
        
        Args:
            entity_name: Name of entity to search for
            entity_type: Type of entity (person, organization, etc.)
            
        Returns:
            Aggregated search results
        """
        logger.info(f"Searching for entity: {entity_name}")
        
        results = {
            'entity_name': entity_name,
            'entity_type': entity_type,
            'search_timestamp': datetime.utcnow().isoformat(),
            'sources': {}
        }
        
        # Search across enabled sources
        for source in self.sources:
            if source.enabled:
                try:
                    source_results = await self._search_source_for_entity(source, entity_name)
                    if source_results:
                        results['sources'][source.name] = source_results
                except Exception as e:
                    logger.error(f"Entity search error for {source.name}: {e}")
        
        return results
    
    async def _search_source_for_entity(self, source: OSINTSource, entity_name: str) -> List[Dict[str, Any]]:
        """Search specific source for entity mentions"""
        # Implementation would vary by source type and API
        # This is a simplified example
        try:
            if source.source_type == SourceType.NEWS:
                # Search news articles for entity mentions
                return await self._search_news_for_entity(source, entity_name)
            elif source.source_type == SourceType.SANCTIONS:
                # Search sanctions lists for entity
                return await self._search_sanctions_for_entity(source, entity_name)
            # Add more source-specific search implementations
            
        except Exception as e:
            logger.error(f"Entity search error in {source.name}: {e}")
            return []
    
    async def _search_news_for_entity(self, source: OSINTSource, entity_name: str) -> List[Dict[str, Any]]:
        """Search news sources for entity mentions"""
        # Simplified implementation - would need proper search API integration
        data = await self._collect_from_source(source)
        if not data or 'data' not in data:
            return []
        
        matches = []
        for article in data['data']:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            entity_lower = entity_name.lower()
            
            if entity_lower in title or entity_lower in summary:
                matches.append(article)
        
        return matches
    
    async def _search_sanctions_for_entity(self, source: OSINTSource, entity_name: str) -> List[Dict[str, Any]]:
        """Search sanctions lists for entity"""
        data = await self._collect_from_source(source)
        if not data or 'data' not in data:
            return []
        
        matches = []
        entity_lower = entity_name.lower()
        
        for sanction in data['data']:
            first_name = sanction.get('first_name', '').lower()
            last_name = sanction.get('last_name', '').lower()
            full_name = f"{first_name} {last_name}".strip()
            
            if (entity_lower in full_name or 
                entity_lower in first_name or 
                entity_lower in last_name):
                matches.append(sanction)
        
        return matches
    
    async def close(self):
        """Clean up resources"""
        await self.session_pool.close()
        self.executor.shutdown(wait=True)
