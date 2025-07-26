"""
Corruption and Financial Crime Data Service
Comprehensive intelligence on corruption cases, financial crimes, and enforcement actions
"""

import asyncio
import json
import logging
import requests
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import aiohttp
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CorruptionCase:
    """Individual corruption case data model"""
    source: str
    case_id: str
    case_type: str  # bribery, embezzlement, fraud, kickback, etc.
    title: str
    description: str
    jurisdiction: str
    enforcement_agency: str
    individuals_involved: List[Dict[str, str]]  # name, role, charges
    companies_involved: List[Dict[str, str]]   # name, role, penalties
    charges_filed: List[str]
    conviction_status: str  # pending, convicted, acquitted, settled
    penalties: Dict[str, Any]  # fines, prison_sentences, etc.
    case_date: datetime
    resolution_date: Optional[datetime] = None
    amount_involved: Optional[float] = None
    currency: str = "USD"
    sectors_involved: List[str] = None
    countries_involved: List[str] = None
    case_documents: List[str] = None  # URLs to court documents
    related_cases: List[str] = None
    risk_score: float = 0.0
    last_updated: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.sectors_involved is None:
            self.sectors_involved = []
        if self.countries_involved is None:
            self.countries_involved = []
        if self.case_documents is None:
            self.case_documents = []
        if self.related_cases is None:
            self.related_cases = []

@dataclass
class CorruptionDataSource:
    """Corruption data source configuration"""
    source_id: str
    name: str
    jurisdiction: str
    source_type: str  # enforcement, court, transparency, news
    agency_type: str  # doj, sec, sfo, etc.
    coverage_scope: str  # domestic, international
    data_quality: str  # high, medium, low
    update_frequency: str  # daily, weekly, monthly
    access_method: str  # api, scraping, download, manual
    base_url: str
    requires_authentication: bool = False
    cost_model: str = "free"
    last_updated: Optional[datetime] = None
    status: str = "active"
    cases_collected: int = 0

class CorruptionDataService:
    """Comprehensive corruption and financial crime data service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.sources = {}
        self.cases_cache = {}
        self.cache_ttl = timedelta(hours=24)  # 24 hour cache
        
        # Corruption type classifications
        self.corruption_types = {
            "bribery": ["bribe", "kickback", "payoff", "under the table"],
            "embezzlement": ["embezzlement", "misappropriation", "theft", "stealing funds"],
            "fraud": ["fraud", "false statements", "misrepresentation", "deception"],
            "money_laundering": ["money laundering", "structuring", "shell companies", "layering"],
            "tax_evasion": ["tax evasion", "tax fraud", "offshore accounts", "unreported income"],
            "procurement_fraud": ["bid rigging", "procurement fraud", "contract manipulation"],
            "securities_fraud": ["securities fraud", "insider trading", "market manipulation"],
            "corruption": ["corruption", "graft", "abuse of office", "conflict of interest"]
        }
        
        # Initialize data sources
        self._initialize_sources()
        
        self.logger.info(f"Initialized {len(self.sources)} corruption data sources")
    
    def _initialize_sources(self):
        """Initialize all corruption data sources"""
        
        # US Department of Justice
        doj_source = CorruptionDataSource(
            source_id="us_doj",
            name="US Department of Justice",
            jurisdiction="United States",
            source_type="enforcement",
            agency_type="doj",
            coverage_scope="international",
            data_quality="high",
            update_frequency="daily",
            access_method="scraping",
            base_url="https://www.justice.gov/news",
            requires_authentication=False,
            cost_model="free"
        )
        
        # US Securities and Exchange Commission
        sec_source = CorruptionDataSource(
            source_id="us_sec",
            name="US Securities and Exchange Commission",
            jurisdiction="United States",
            source_type="enforcement",
            agency_type="sec",
            coverage_scope="international",
            data_quality="high",
            update_frequency="daily",
            access_method="api",
            base_url="https://www.sec.gov/litigation/litreleases.shtml",
            requires_authentication=False,
            cost_model="free"
        )
        
        # UK Serious Fraud Office
        sfo_source = CorruptionDataSource(
            source_id="uk_sfo",
            name="UK Serious Fraud Office",
            jurisdiction="United Kingdom",
            source_type="enforcement",
            agency_type="sfo",
            coverage_scope="international",
            data_quality="high",
            update_frequency="weekly",
            access_method="scraping",
            base_url="https://www.sfo.gov.uk/cases/",
            requires_authentication=False,
            cost_model="free"
        )
        
        # OECD Anti-Bribery Convention
        oecd_source = CorruptionDataSource(
            source_id="oecd_bribery",
            name="OECD Anti-Bribery Convention",
            jurisdiction="International",
            source_type="enforcement",
            agency_type="oecd",
            coverage_scope="international",
            data_quality="high",
            update_frequency="monthly",
            access_method="download",
            base_url="https://www.oecd.org/corruption/anti-bribery/",
            requires_authentication=False,
            cost_model="free"
        )
        
        # Transparency International
        ti_source = CorruptionDataSource(
            source_id="transparency_intl",
            name="Transparency International",
            jurisdiction="International",
            source_type="transparency",
            agency_type="ngo",
            coverage_scope="international",
            data_quality="medium",
            update_frequency="monthly",
            access_method="scraping",
            base_url="https://www.transparency.org/en/news",
            requires_authentication=False,
            cost_model="free"
        )
        
        # World Bank Sanctions
        wb_sanctions_source = CorruptionDataSource(
            source_id="world_bank_sanctions",
            name="World Bank Sanctions",
            jurisdiction="International",
            source_type="enforcement",
            agency_type="world_bank",
            coverage_scope="international",
            data_quality="high",
            update_frequency="monthly",
            access_method="download",
            base_url="https://www.worldbank.org/en/projects-operations/procurement/debarred-firms",
            requires_authentication=False,
            cost_model="free"
        )
        
        # Financial Crimes Enforcement Network (FinCEN)
        fincen_source = CorruptionDataSource(
            source_id="fincen",
            name="FinCEN Enforcement Actions",
            jurisdiction="United States",
            source_type="enforcement",
            agency_type="fincen",
            coverage_scope="international",
            data_quality="high",
            update_frequency="monthly",
            access_method="scraping",
            base_url="https://www.fincen.gov/news-room/enforcement-actions",
            requires_authentication=False,
            cost_model="free"
        )
        
        # European Anti-Fraud Office (OLAF)
        olaf_source = CorruptionDataSource(
            source_id="eu_olaf",
            name="European Anti-Fraud Office",
            jurisdiction="European Union",
            source_type="enforcement",
            agency_type="olaf",
            coverage_scope="international",
            data_quality="high",
            update_frequency="monthly",
            access_method="scraping",
            base_url="https://ec.europa.eu/anti-fraud/media-corner/news_en",
            requires_authentication=False,
            cost_model="free"
        )
        
        # FCPA Database
        fcpa_source = CorruptionDataSource(
            source_id="fcpa_database",
            name="FCPA Enforcement Database",
            jurisdiction="United States",
            source_type="enforcement",
            agency_type="doj_sec",
            coverage_scope="international",
            data_quality="high",
            update_frequency="weekly",
            access_method="scraping",
            base_url="https://fcpa.stanford.edu/fcpac/",
            requires_authentication=False,
            cost_model="free"
        )
        
        # Global Corruption Database
        global_corruption_source = CorruptionDataSource(
            source_id="global_corruption_db",
            name="Global Corruption Database",
            jurisdiction="International",
            source_type="transparency",
            agency_type="academic",
            coverage_scope="international",
            data_quality="medium",
            update_frequency="quarterly",
            access_method="download",
            base_url="https://globalcorruption.example.com/data",
            requires_authentication=False,
            cost_model="free"
        )
        
        sources = [
            doj_source, sec_source, sfo_source, oecd_source, ti_source,
            wb_sanctions_source, fincen_source, olaf_source, fcpa_source, global_corruption_source
        ]
        
        for source in sources:
            self.sources[source.source_id] = source
    
    async def fetch_corruption_data(self, source_id: Optional[str] = None, 
                                  force_refresh: bool = False) -> Dict[str, List[CorruptionCase]]:
        """Fetch corruption data from specified source or all sources"""
        
        if source_id:
            if source_id not in self.sources:
                raise ValueError(f"Unknown source: {source_id}")
            sources_to_fetch = [source_id]
        else:
            sources_to_fetch = list(self.sources.keys())
        
        results = {}
        
        for source_id in sources_to_fetch:
            try:
                # Check cache first
                if not force_refresh and source_id in self.cases_cache:
                    cache_entry = self.cases_cache[source_id]
                    if datetime.now() - cache_entry['timestamp'] < self.cache_ttl:
                        results[source_id] = cache_entry['data']
                        self.logger.info(f"Using cached corruption data for {source_id}")
                        continue
                
                # Fetch fresh data
                source = self.sources[source_id]
                self.logger.info(f"Fetching corruption data from {source.name}")
                
                if source.access_method == "scraping":
                    data = await self._fetch_scraping_source(source)
                elif source.access_method == "api":
                    data = await self._fetch_api_source(source)
                elif source.access_method == "download":
                    data = await self._fetch_download_source(source)
                elif source.access_method == "manual":
                    data = await self._fetch_manual_source(source)
                else:
                    self.logger.warning(f"Unknown access method for {source_id}: {source.access_method}")
                    continue
                
                # Cache the data
                self.cases_cache[source_id] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                
                results[source_id] = data
                
                # Update source metadata
                source.last_updated = datetime.now()
                source.cases_collected = len(data)
                source.status = "active"
                
                self.logger.info(f"Successfully fetched {len(data)} corruption cases from {source.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to fetch corruption data from {source_id}: {e}")
                source.status = "error"
                results[source_id] = []
        
        return results
    
    async def _fetch_scraping_source(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch data from scraping-based sources"""
        
        if source.source_id == "us_doj":
            return await self._scrape_doj_cases(source)
        elif source.source_id == "uk_sfo":
            return await self._scrape_sfo_cases(source)
        elif source.source_id == "transparency_intl":
            return await self._scrape_transparency_intl(source)
        elif source.source_id == "fincen":
            return await self._scrape_fincen_cases(source)
        elif source.source_id == "eu_olaf":
            return await self._scrape_olaf_cases(source)
        elif source.source_id == "fcpa_database":
            return await self._scrape_fcpa_database(source)
        else:
            self.logger.warning(f"No scraper for source: {source.source_id}")
            return []
    
    async def _fetch_api_source(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch data from API-based sources"""
        
        if source.source_id == "us_sec":
            return await self._fetch_sec_api(source)
        else:
            self.logger.warning(f"No API fetcher for source: {source.source_id}")
            return []
    
    async def _fetch_download_source(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch data from download-based sources"""
        
        if source.source_id == "oecd_bribery":
            return await self._fetch_oecd_data(source)
        elif source.source_id == "world_bank_sanctions":
            return await self._fetch_world_bank_data(source)
        elif source.source_id == "global_corruption_db":
            return await self._fetch_global_corruption_data(source)
        else:
            self.logger.warning(f"No download fetcher for source: {source.source_id}")
            return []
    
    async def _scrape_doj_cases(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape DOJ corruption cases"""
        cases = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search for corruption-related press releases
                search_url = f"{source.base_url}?search=corruption%20OR%20bribery%20OR%20fraud"
                async with session.get(search_url) as response:
                    content = await response.text()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find press release links
            press_releases = soup.find_all('a', href=re.compile(r'/news/press-release/'))
            
            for release in press_releases[:10]:  # Limit to avoid overload
                try:
                    release_url = urljoin(source.base_url, release['href'])
                    
                    # Fetch individual press release
                    async with aiohttp.ClientSession() as session:
                        async with session.get(release_url) as response:
                            release_content = await response.text()
                    
                    release_soup = BeautifulSoup(release_content, 'html.parser')
                    
                    title = release_soup.find('h1')
                    title_text = title.text.strip() if title else "Unknown Case"
                    
                    # Extract case details
                    content_div = release_soup.find('div', class_='field-item')
                    description = content_div.text.strip() if content_div else ""
                    
                    # Create case
                    case = CorruptionCase(
                        source=source.source_id,
                        case_id=f"doj_{hash(release_url)}",
                        case_type=self._classify_corruption_type(title_text + " " + description),
                        title=title_text,
                        description=description,
                        jurisdiction="United States",
                        enforcement_agency="US Department of Justice",
                        individuals_involved=[],
                        companies_involved=[],
                        charges_filed=[],
                        conviction_status="pending",
                        penalties={},
                        case_date=datetime.now(),
                        sectors_involved=[],
                        countries_involved=["United States"],
                        case_documents=[release_url],
                        risk_score=0.8,
                        last_updated=datetime.now()
                    )
                    
                    cases.append(case)
                    
                except Exception as e:
                    self.logger.error(f"Failed to parse DOJ case: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Failed to scrape DOJ cases: {e}")
        
        return cases
    
    async def _scrape_sfo_cases(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape UK SFO cases"""
        cases = []
        
        # Simulated SFO cases
        sfo_cases_data = [
            {
                "title": "SFO v. Multinational Corporation - Bribery Investigation",
                "description": "Investigation into alleged bribery payments to foreign officials",
                "case_type": "bribery",
                "status": "ongoing"
            },
            {
                "title": "Fraud Investigation - Financial Services Sector",
                "description": "Complex fraud investigation involving misrepresentation of financial products",
                "case_type": "fraud",
                "status": "convicted"
            }
        ]
        
        for case_data in sfo_cases_data:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"sfo_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="United Kingdom",
                enforcement_agency="UK Serious Fraud Office",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status=case_data["status"],
                penalties={},
                case_date=datetime.now() - timedelta(days=180),
                countries_involved=["United Kingdom"],
                risk_score=0.8,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _scrape_transparency_intl(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape Transparency International cases"""
        cases = []
        
        # Simulated TI cases
        ti_cases = [
            {
                "title": "Global Corruption Perception Index 2023 - Country Analysis",
                "description": "Analysis of corruption levels across different countries and sectors",
                "case_type": "corruption"
            }
        ]
        
        for case_data in ti_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"ti_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="International",
                enforcement_agency="Transparency International",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="analysis",
                penalties={},
                case_date=datetime.now() - timedelta(days=30),
                countries_involved=["Global"],
                risk_score=0.6,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _scrape_fincen_cases(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape FinCEN enforcement actions"""
        cases = []
        
        # Simulated FinCEN cases
        fincen_cases = [
            {
                "title": "Money Laundering Enforcement Action - Major Bank",
                "description": "Civil penalty for failure to maintain adequate anti-money laundering program",
                "case_type": "money_laundering",
                "penalty_amount": 50000000
            }
        ]
        
        for case_data in fincen_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"fincen_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="United States",
                enforcement_agency="FinCEN",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="settled",
                penalties={"fine": case_data.get("penalty_amount", 0)},
                case_date=datetime.now() - timedelta(days=60),
                amount_involved=case_data.get("penalty_amount"),
                countries_involved=["United States"],
                risk_score=0.9,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _scrape_olaf_cases(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape EU OLAF cases"""
        cases = []
        
        # Simulated OLAF cases
        olaf_cases = [
            {
                "title": "EU Funds Fraud Investigation",
                "description": "Investigation into misuse of European Union agricultural funds",
                "case_type": "fraud"
            }
        ]
        
        for case_data in olaf_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"olaf_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="European Union",
                enforcement_agency="OLAF",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="pending",
                penalties={},
                case_date=datetime.now() - timedelta(days=90),
                countries_involved=["EU Member States"],
                risk_score=0.7,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _scrape_fcpa_database(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Scrape Stanford FCPA database"""
        cases = []
        
        # Simulated FCPA cases
        fcpa_cases = [
            {
                "title": "FCPA Settlement - Technology Company",
                "description": "Settlement for improper payments to government officials in Asia",
                "case_type": "bribery",
                "penalty_amount": 25000000
            }
        ]
        
        for case_data in fcpa_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"fcpa_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="United States",
                enforcement_agency="DOJ/SEC",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=["FCPA Violations"],
                conviction_status="settled",
                penalties={"fine": case_data.get("penalty_amount", 0)},
                case_date=datetime.now() - timedelta(days=120),
                amount_involved=case_data.get("penalty_amount"),
                sectors_involved=["Technology"],
                countries_involved=["United States", "Asia"],
                risk_score=0.9,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _fetch_sec_api(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch SEC enforcement actions via API"""
        cases = []
        
        # Simulated SEC API data
        sec_cases = [
            {
                "title": "SEC Charges Investment Advisor with Fraud",
                "description": "SEC charges investment advisor for fraudulent scheme involving client funds",
                "case_type": "securities_fraud",
                "penalty_amount": 5000000
            }
        ]
        
        for case_data in sec_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"sec_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="United States",
                enforcement_agency="SEC",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=["Securities Fraud"],
                conviction_status="charged",
                penalties={"fine": case_data.get("penalty_amount", 0)},
                case_date=datetime.now() - timedelta(days=30),
                amount_involved=case_data.get("penalty_amount"),
                sectors_involved=["Financial Services"],
                countries_involved=["United States"],
                risk_score=0.8,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _fetch_oecd_data(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch OECD anti-bribery data"""
        cases = []
        
        # Simulated OECD data
        oecd_cases = [
            {
                "title": "OECD Anti-Bribery Convention - Country Review",
                "description": "Review of country implementation of anti-bribery measures",
                "case_type": "bribery"
            }
        ]
        
        for case_data in oecd_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"oecd_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="International",
                enforcement_agency="OECD",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="review",
                penalties={},
                case_date=datetime.now() - timedelta(days=200),
                countries_involved=["OECD Members"],
                risk_score=0.5,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _fetch_world_bank_data(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch World Bank sanctions data"""
        cases = []
        
        # Simulated World Bank data
        wb_cases = [
            {
                "title": "World Bank Debarment - Construction Company",
                "description": "Company debarred for fraudulent practices in development projects",
                "case_type": "fraud"
            }
        ]
        
        for case_data in wb_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"wb_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="International",
                enforcement_agency="World Bank",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="debarred",
                penalties={"debarment": True},
                case_date=datetime.now() - timedelta(days=150),
                sectors_involved=["Construction"],
                countries_involved=["Developing Countries"],
                risk_score=0.7,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    async def _fetch_global_corruption_data(self, source: CorruptionDataSource) -> List[CorruptionCase]:
        """Fetch global corruption database"""
        cases = []
        
        # Simulated global corruption data
        global_cases = [
            {
                "title": "Cross-Border Corruption Network Exposed",
                "description": "International investigation reveals multi-country corruption network",
                "case_type": "corruption"
            }
        ]
        
        for case_data in global_cases:
            case = CorruptionCase(
                source=source.source_id,
                case_id=f"global_{hash(case_data['title'])}",
                case_type=case_data["case_type"],
                title=case_data["title"],
                description=case_data["description"],
                jurisdiction="International",
                enforcement_agency="Multiple Agencies",
                individuals_involved=[],
                companies_involved=[],
                charges_filed=[],
                conviction_status="investigation",
                penalties={},
                case_date=datetime.now() - timedelta(days=100),
                countries_involved=["Multiple"],
                risk_score=0.9,
                last_updated=datetime.now()
            )
            
            cases.append(case)
        
        return cases
    
    def _classify_corruption_type(self, content: str) -> str:
        """Classify corruption type based on content"""
        content_lower = content.lower()
        
        for corruption_type, keywords in self.corruption_types.items():
            if any(keyword in content_lower for keyword in keywords):
                return corruption_type
        
        return "corruption"  # Default
    
    async def search_corruption_cases(self, query: str, 
                                    source_ids: Optional[List[str]] = None,
                                    jurisdictions: Optional[List[str]] = None,
                                    case_types: Optional[List[str]] = None,
                                    min_amount: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search corruption cases with filtering"""
        
        # Fetch data if not cached
        corruption_data = await self.fetch_corruption_data()
        
        if source_ids:
            filtered_data = {k: v for k, v in corruption_data.items() if k in source_ids}
        else:
            filtered_data = corruption_data
        
        matches = []
        query_lower = query.lower()
        
        for source_id, cases in filtered_data.items():
            for case in cases:
                # Apply filters
                if jurisdictions and case.jurisdiction not in jurisdictions:
                    continue
                    
                if case_types and case.case_type not in case_types:
                    continue
                    
                if min_amount and (case.amount_involved is None or case.amount_involved < min_amount):
                    continue
                
                # Check if query matches
                searchable_text = f"{case.title} {case.description}".lower()
                if query_lower in searchable_text:
                    matches.append({
                        "match_score": self._calculate_relevance_score(query_lower, searchable_text),
                        "case": asdict(case)
                    })
        
        # Sort by relevance
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """Calculate relevance score for search results"""
        
        if not query or not content:
            return 0.0
        
        # Count query word occurrences
        query_words = query.split()
        content_words = content.split()
        
        matches = sum(1 for word in query_words if word in content_words)
        
        if len(query_words) == 0:
            return 0.0
        
        return matches / len(query_words)
    
    async def get_corruption_statistics(self) -> Dict[str, Any]:
        """Get comprehensive corruption statistics"""
        
        # Fetch all data
        all_data = await self.fetch_corruption_data()
        
        all_cases = []
        for cases in all_data.values():
            all_cases.extend(cases)
        
        # Calculate statistics
        total_cases = len(all_cases)
        
        # By case type
        by_type = {}
        for case in all_cases:
            case_type = case.case_type
            by_type[case_type] = by_type.get(case_type, 0) + 1
        
        # By jurisdiction
        by_jurisdiction = {}
        for case in all_cases:
            jurisdiction = case.jurisdiction
            by_jurisdiction[jurisdiction] = by_jurisdiction.get(jurisdiction, 0) + 1
        
        # By enforcement agency
        by_agency = {}
        for case in all_cases:
            agency = case.enforcement_agency
            by_agency[agency] = by_agency.get(agency, 0) + 1
        
        # Financial impact
        total_amount = sum(case.amount_involved for case in all_cases if case.amount_involved)
        average_amount = total_amount / max(len([c for c in all_cases if c.amount_involved]), 1)
        
        # Risk distribution
        high_risk_cases = len([c for c in all_cases if c.risk_score > 0.7])
        
        return {
            "total_cases": total_cases,
            "by_case_type": by_type,
            "by_jurisdiction": by_jurisdiction,
            "by_enforcement_agency": by_agency,
            "financial_impact": {
                "total_amount": total_amount,
                "average_amount": average_amount,
                "currency": "USD"
            },
            "risk_distribution": {
                "high_risk_cases": high_risk_cases,
                "percentage_high_risk": (high_risk_cases / max(total_cases, 1)) * 100
            },
            "sources_active": len([s for s in self.sources.values() if s.status == "active"]),
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all corruption data sources"""
        
        status = {}
        
        for source_id, source in self.sources.items():
            status[source_id] = {
                "name": source.name,
                "jurisdiction": source.jurisdiction,
                "agency_type": source.agency_type,
                "status": source.status,
                "last_updated": source.last_updated.isoformat() if source.last_updated else None,
                "cases_collected": source.cases_collected,
                "update_frequency": source.update_frequency,
                "access_method": source.access_method,
                "data_quality": source.data_quality
            }
        
        return status
    
    async def update_all_sources(self) -> Dict[str, Any]:
        """Update all corruption sources"""
        
        self.logger.info("Starting update of all corruption sources")
        
        results = await self.fetch_corruption_data(force_refresh=True)
        
        summary = {
            "updated_at": datetime.now().isoformat(),
            "sources_updated": len(results),
            "total_cases": sum(len(cases) for cases in results.values()),
            "sources": {}
        }
        
        for source_id, cases in results.items():
            summary["sources"][source_id] = {
                "cases": len(cases),
                "status": self.sources[source_id].status
            }
        
        self.logger.info(f"Updated {len(results)} corruption sources with {summary['total_cases']} total cases")
        
        return summary
