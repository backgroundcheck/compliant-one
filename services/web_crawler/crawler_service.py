"""
Web Crawler Service using Crawl4AI
Handles web scraping for OSINT and data collection
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy, CosineStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)

class WebCrawlerService:
    """Advanced web crawler using Crawl4AI for compliance data collection"""
    
    def __init__(self):
        self.crawler = None
        self.session_cache = {}
        self.extraction_strategies = {
            'default': self._default_extraction,
            'financial': self._financial_extraction,
            'regulatory': self._regulatory_extraction,
            'sanctions': self._sanctions_extraction,
            'news': self._news_extraction
        }
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning("Crawl4AI not available. Web crawling functionality will be limited.")
    
    async def initialize(self):
        """Initialize the async web crawler"""
        if not CRAWL4AI_AVAILABLE:
            raise ImportError("Crawl4AI is not installed. Please install it with: pip install crawl4ai")
        
        self.crawler = AsyncWebCrawler(verbose=True)
        await self.crawler.start()
        logger.info("Web crawler initialized successfully")
    
    async def shutdown(self):
        """Shutdown the crawler"""
        if self.crawler:
            await self.crawler.close()
            logger.info("Web crawler shutdown")
    
    async def crawl_url(self, 
                       url: str, 
                       extraction_strategy: str = 'default',
                       custom_instructions: Optional[str] = None,
                       wait_for: Optional[str] = None,
                       css_selector: Optional[str] = None,
                       word_count_threshold: int = 50) -> Dict:
        """
        Crawl a single URL with specified extraction strategy
        
        Args:
            url: Target URL to crawl
            extraction_strategy: Strategy for data extraction
            custom_instructions: Custom LLM instructions for extraction
            wait_for: CSS selector to wait for before extraction
            css_selector: Specific CSS selector to extract
            word_count_threshold: Minimum word count for content
        """
        if not self.crawler:
            await self.initialize()
        
        try:
            # Generate cache key
            cache_key = hashlib.md5(f"{url}_{extraction_strategy}".encode()).hexdigest()
            
            # Check cache (valid for 1 hour)
            if cache_key in self.session_cache:
                cached_data = self.session_cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):
                    logger.info(f"Returning cached data for {url}")
                    return cached_data['data']
            
            # Prepare extraction strategy
            extraction_func = self.extraction_strategies.get(extraction_strategy, self._default_extraction)
            
            # Crawl the URL
            result = await self.crawler.arun(
                url=url,
                word_count_threshold=word_count_threshold,
                wait_for=wait_for,
                css_selector=css_selector,
                bypass_cache=True
            )
            
            if not result.success:
                return {
                    'status': 'error',
                    'message': f"Failed to crawl {url}: {result.error_message}",
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Extract structured data
            extracted_data = await extraction_func(result, custom_instructions)
            
            # Prepare response
            response_data = {
                'status': 'success',
                'url': url,
                'title': result.metadata.get('title', ''),
                'description': result.metadata.get('description', ''),
                'content_length': len(result.cleaned_html),
                'word_count': len(result.markdown.split()) if result.markdown else 0,
                'extraction_strategy': extraction_strategy,
                'extracted_data': extracted_data,
                'metadata': {
                    'status_code': result.status_code,
                    'response_headers': dict(result.response_headers) if result.response_headers else {},
                    'links': result.links,
                    'media': {
                        'images': result.media.get('images', []) if result.media else [],
                        'videos': result.media.get('videos', []) if result.media else []
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.session_cache[cache_key] = {
                'data': response_data,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Successfully crawled {url} - {response_data['word_count']} words")
            return response_data
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {
                'status': 'error',
                'message': f"Crawling error: {str(e)}",
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    async def crawl_multiple_urls(self, 
                                 urls: List[str], 
                                 extraction_strategy: str = 'default',
                                 max_concurrent: int = 5) -> List[Dict]:
        """Crawl multiple URLs concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url):
            async with semaphore:
                return await self.crawl_url(url, extraction_strategy)
        
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'message': f"Exception occurred: {str(result)}",
                    'url': urls[i],
                    'timestamp': datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def search_and_crawl(self, 
                              search_query: str, 
                              domains: Optional[List[str]] = None,
                              max_results: int = 10) -> List[Dict]:
        """
        Search for URLs related to a query and crawl them
        This is a basic implementation - in production you'd integrate with search APIs
        """
        # For now, we'll accept a list of URLs to crawl based on the search query
        # In a full implementation, this would integrate with search engines
        
        if domains:
            urls = [f"https://{domain}" for domain in domains[:max_results]]
            return await self.crawl_multiple_urls(urls, 'default')
        
        logger.warning("Search functionality requires domain list or search API integration")
        return []
    
    async def _default_extraction(self, result, custom_instructions: Optional[str] = None) -> Dict:
        """Default extraction strategy - extracts basic content"""
        return {
            'content_type': 'general',
            'text_content': result.markdown[:5000] if result.markdown else '',  # Limit to 5k chars
            'entities': self._extract_entities(result.markdown or result.cleaned_html),
            'links_found': len(result.links) if result.links else 0,
            'images_found': len(result.media.get('images', [])) if result.media else 0
        }
    
    async def _financial_extraction(self, result, custom_instructions: Optional[str] = None) -> Dict:
        """Extract financial and regulatory information"""
        content = result.markdown or result.cleaned_html
        
        # Extract financial patterns
        financial_patterns = {
            'currency_amounts': re.findall(r'[\$€£¥]\s?[\d,]+(?:\.\d{2})?', content),
            'percentages': re.findall(r'\d+(?:\.\d+)?%', content),
            'financial_institutions': re.findall(r'\b(?:Bank|Credit Union|Trust|Investment|Fund|Capital)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content),
            'regulatory_terms': re.findall(r'\b(?:compliance|regulation|audit|filing|disclosure|SEC|FINRA|CFTC|OCC)\b', content, re.IGNORECASE)
        }
        
        return {
            'content_type': 'financial',
            'financial_data': financial_patterns,
            'entities': self._extract_entities(content),
            'risk_indicators': self._identify_risk_indicators(content),
            'text_content': content[:3000]  # Limit for financial content
        }
    
    async def _regulatory_extraction(self, result, custom_instructions: Optional[str] = None) -> Dict:
        """Extract regulatory and compliance information"""
        content = result.markdown or result.cleaned_html
        
        regulatory_patterns = {
            'regulations': re.findall(r'\b(?:CFR|USC|FR|Federal Register)\s+\d+(?:\.\d+)*\b', content),
            'agencies': re.findall(r'\b(?:SEC|CFTC|FINRA|OCC|FDIC|FRB|Treasury|FinCEN|OFAC)\b', content),
            'compliance_terms': re.findall(r'\b(?:AML|KYC|CDD|EDD|SAR|CTR|BSA|PATRIOT Act)\b', content, re.IGNORECASE),
            'enforcement_actions': re.findall(r'\b(?:fine|penalty|enforcement|violation|cease and desist)\b', content, re.IGNORECASE)
        }
        
        return {
            'content_type': 'regulatory',
            'regulatory_data': regulatory_patterns,
            'entities': self._extract_entities(content),
            'compliance_indicators': self._identify_compliance_indicators(content),
            'text_content': content[:3000]
        }
    
    async def _sanctions_extraction(self, result, custom_instructions: Optional[str] = None) -> Dict:
        """Extract sanctions and watchlist information"""
        content = result.markdown or result.cleaned_html
        
        sanctions_patterns = {
            'sanctions_programs': re.findall(r'\b(?:OFAC|UN|EU|HMT)\s+(?:sanctions|embargo|restrictions)\b', content, re.IGNORECASE),
            'blocked_entities': re.findall(r'\b(?:SDN|blocked|designated|sanctioned)\s+(?:person|entity|individual)\b', content, re.IGNORECASE),
            'countries': re.findall(r'\b(?:Iran|North Korea|Syria|Cuba|Russia|Belarus|Myanmar)\b', content),
            'watchlist_terms': re.findall(r'\b(?:watchlist|blacklist|PEP|politically exposed)\b', content, re.IGNORECASE)
        }
        
        return {
            'content_type': 'sanctions',
            'sanctions_data': sanctions_patterns,
            'entities': self._extract_entities(content),
            'risk_level': self._calculate_sanctions_risk(content),
            'text_content': content[:3000]
        }
    
    async def _news_extraction(self, result, custom_instructions: Optional[str] = None) -> Dict:
        """Extract news and media information"""
        content = result.markdown or result.cleaned_html
        
        # Extract news-specific information
        news_data = {
            'headline': result.metadata.get('title', ''),
            'publication_date': self._extract_date(content),
            'author': self._extract_author(content),
            'key_topics': self._extract_topics(content),
            'sentiment': self._analyze_sentiment(content)
        }
        
        return {
            'content_type': 'news',
            'news_data': news_data,
            'entities': self._extract_entities(content),
            'relevance_score': self._calculate_relevance_score(content),
            'text_content': content[:4000]
        }
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """Extract named entities from content"""
        entities = []
        
        # Person names (basic pattern)
        persons = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', content)
        for person in persons[:10]:  # Limit to first 10
            entities.append({
                'type': 'person',
                'value': person,
                'confidence': 0.7
            })
        
        # Organizations
        orgs = re.findall(r'\b[A-Z][A-Z\s&]+(?:INC|LLC|LTD|CORP|COMPANY|BANK|TRUST)\b', content)
        for org in orgs[:10]:
            entities.append({
                'type': 'organization',
                'value': org,
                'confidence': 0.8
            })
        
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        for email in emails[:5]:
            entities.append({
                'type': 'email',
                'value': email,
                'confidence': 0.9
            })
        
        return entities
    
    def _identify_risk_indicators(self, content: str) -> List[str]:
        """Identify financial risk indicators"""
        risk_terms = [
            'money laundering', 'terrorist financing', 'sanctions violation',
            'suspicious activity', 'compliance violation', 'regulatory action',
            'enforcement', 'penalty', 'fine', 'investigation'
        ]
        
        found_indicators = []
        for term in risk_terms:
            if re.search(term, content, re.IGNORECASE):
                found_indicators.append(term)
        
        return found_indicators
    
    def _identify_compliance_indicators(self, content: str) -> List[str]:
        """Identify compliance-related indicators"""
        compliance_terms = [
            'AML program', 'KYC procedures', 'customer due diligence',
            'enhanced due diligence', 'suspicious activity report',
            'currency transaction report', 'bank secrecy act'
        ]
        
        found_indicators = []
        for term in compliance_terms:
            if re.search(term, content, re.IGNORECASE):
                found_indicators.append(term)
        
        return found_indicators
    
    def _calculate_sanctions_risk(self, content: str) -> str:
        """Calculate sanctions risk level"""
        high_risk_terms = ['OFAC', 'SDN', 'sanctions violation', 'blocked person']
        medium_risk_terms = ['sanctions', 'embargo', 'restricted']
        
        high_risk_count = sum(1 for term in high_risk_terms if re.search(term, content, re.IGNORECASE))
        medium_risk_count = sum(1 for term in medium_risk_terms if re.search(term, content, re.IGNORECASE))
        
        if high_risk_count > 0:
            return 'high'
        elif medium_risk_count > 1:
            return 'medium'
        else:
            return 'low'
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extract publication date"""
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group()
        
        return None
    
    def _extract_author(self, content: str) -> Optional[str]:
        """Extract author information"""
        author_patterns = [
            r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Author:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Written by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics from content"""
        financial_topics = [
            'banking', 'finance', 'investment', 'regulatory', 'compliance',
            'sanctions', 'AML', 'KYC', 'fraud', 'money laundering'
        ]
        
        found_topics = []
        for topic in financial_topics:
            if re.search(topic, content, re.IGNORECASE):
                found_topics.append(topic)
        
        return found_topics[:5]  # Limit to top 5
    
    def _analyze_sentiment(self, content: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ['positive', 'good', 'excellent', 'success', 'approved', 'compliant']
        negative_words = ['negative', 'bad', 'violation', 'penalty', 'failed', 'non-compliant', 'risk']
        
        positive_count = sum(1 for word in positive_words if re.search(word, content, re.IGNORECASE))
        negative_count = sum(1 for word in negative_words if re.search(word, content, re.IGNORECASE))
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'
    
    def _calculate_relevance_score(self, content: str) -> float:
        """Calculate relevance score for compliance purposes"""
        compliance_keywords = [
            'compliance', 'regulatory', 'AML', 'KYC', 'sanctions', 'OFAC',
            'financial', 'banking', 'money laundering', 'suspicious activity'
        ]
        
        keyword_count = sum(1 for keyword in compliance_keywords 
                          if re.search(keyword, content, re.IGNORECASE))
        
        # Normalize to 0-1 scale
        max_score = len(compliance_keywords)
        return min(keyword_count / max_score, 1.0)

# Utility functions for easy access
async def crawl_url_simple(url: str, strategy: str = 'default') -> Dict:
    """Simple function to crawl a single URL"""
    crawler = WebCrawlerService()
    try:
        result = await crawler.crawl_url(url, strategy)
        await crawler.shutdown()
        return result
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Crawling failed: {str(e)}",
            'url': url
        }

# Export main classes
__all__ = ['WebCrawlerService', 'crawl_url_simple']
