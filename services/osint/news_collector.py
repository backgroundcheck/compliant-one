"""
News and threat intelligence collector for Compliant.one
"""

import requests
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import feedparser
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class NewsCollector:
    """Collects threat intelligence from news sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # NewsAPI setup (if available)
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "daca0805ba8b4b579be54a9fb28247e1")
        
        # News sources and RSS feeds
        self.news_sources = {
            'cybersecurity_news': [
                'https://feeds.feedburner.com/TheHackersNews',
                'https://krebsonsecurity.com/feed/',
                'https://www.bleepingcomputer.com/feed/',
                'https://threatpost.com/feed/',
                'https://www.darkreading.com/rss.xml'
            ],
            'vulnerability_feeds': [
                'https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml'
            ]
        }
    
    def get_google_news(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Google News for a specific query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles
        """
        try:
            # Using Google News RSS feed
            url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_results]:
                article = {
                    'title': entry.title,
                    'url': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else 'Unknown',
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'source': 'Google News',
                    'query': query,
                    'collected_at': datetime.utcnow().isoformat()
                }
                articles.append(article)
            
            logger.info(f"Collected {len(articles)} articles for query: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Google News for query '{query}': {e}")
            return []
    
    def get_newsapi_articles(self, keyword: str = "cyber crime", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get articles using NewsAPI (legacy function for compatibility)
        """
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.newsapi_key)
            
            articles_raw = newsapi.get_everything(
                q=keyword, 
                language='en', 
                sort_by='publishedAt', 
                page_size=limit
            )
            articles = []

            for item in articles_raw['articles']:
                articles.append({
                    "title": item['title'],
                    "url": item['url'],
                    "published": item.get('publishedAt', 'Unknown'),
                    "source": item.get('source', {}).get('name', 'Unknown'),
                    "description": item.get('description', ''),
                    'collected_at': datetime.utcnow().isoformat()
                })

            return articles
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return [{"title": f"Error: {str(e)}", "url": ""}]
    
    def get_security_feeds(self) -> List[Dict[str, Any]]:
        """
        Collect articles from cybersecurity RSS feeds
        
        Returns:
            List of security articles
        """
        all_articles = []
        
        for category, feeds in self.news_sources.items():
            for feed_url in feeds:
                try:
                    logger.info(f"Fetching feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Limit per feed
                        article = {
                            'title': entry.title,
                            'url': entry.link,
                            'published': entry.published if hasattr(entry, 'published') else 'Unknown',
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'source': feed_url,
                            'category': category,
                            'collected_at': datetime.utcnow().isoformat()
                        }
                        all_articles.append(article)
                
                except Exception as e:
                    logger.error(f"Error fetching feed {feed_url}: {e}")
                    continue
        
        logger.info(f"Collected {len(all_articles)} security articles")
        return all_articles

# For backward compatibility with existing code
def get_google_news(keyword: str = "cyber crime", limit: int = 100) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    collector = NewsCollector()
    # Use both methods for better coverage
    newsapi_articles = collector.get_newsapi_articles(keyword, limit)
    google_articles = collector.get_google_news(keyword, limit)
    
    # Combine and deduplicate
    all_articles = newsapi_articles + google_articles
    seen_urls = set()
    unique_articles = []
    
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    return unique_articles
