"""
Original Adverse Media Service for backward compatibility
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

@dataclass
class AdverseMediaArticle:
    """Simple adverse media article structure"""
    title: str
    url: str
    source: str
    published_date: datetime
    content: str
    risk_score: float = 0.0
    sentiment: str = "neutral"

class AdverseMediaService:
    """
    Simple adverse media service for backward compatibility
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Simple sources configuration
        self.sources = {
            "google_news": {
                "name": "Google News",
                "url": "https://news.google.com",
                "enabled": True
            },
            "reuters": {
                "name": "Reuters",
                "url": "https://reuters.com",
                "enabled": True
            },
            "bbc": {
                "name": "BBC News", 
                "url": "https://bbc.com",
                "enabled": True
            }
        }
        
        self.logger.info("Initialized simple adverse media service")
    
    async def monitor_adverse_media(self, entities: List[str], time_range: int = 30) -> Dict[str, List[AdverseMediaArticle]]:
        """
        Monitor adverse media for entities (simplified implementation)
        """
        results = {}
        
        for entity in entities:
            # Simulate media monitoring
            articles = []
            
            # Create some sample articles for testing
            sample_article = AdverseMediaArticle(
                title=f"Sample article about {entity}",
                url=f"https://example.com/article-{entity.lower().replace(' ', '-')}",
                source="Sample News",
                published_date=datetime.now(),
                content=f"This is a sample article about {entity} for testing purposes.",
                risk_score=0.3,
                sentiment="neutral"
            )
            
            articles.append(sample_article)
            results[entity] = articles
        
        self.logger.info(f"Monitored adverse media for {len(entities)} entities")
        return results
    
    async def get_source_statistics(self) -> Dict[str, Any]:
        """Get source statistics"""
        return {
            "total_sources": len(self.sources),
            "active_sources": len([s for s in self.sources.values() if s.get("enabled", False)]),
            "total_articles_collected": 0,
            "last_update": datetime.now().isoformat()
        }
