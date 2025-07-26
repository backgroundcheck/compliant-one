"""
PEP (Politically Exposed Persons) Data Service
Comprehensive integration with global PEP data sources
"""

import asyncio
import json
import logging
import requests
import csv
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import aiohttp
import re
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PEPEntry:
    """Individual PEP entry data model"""
    source: str
    entity_id: str
    primary_name: str
    aliases: List[str]
    positions: List[Dict[str, str]]  # role, organization, start_date, end_date
    countries: List[str]
    date_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    nationality: List[str] = None
    family_members: List[Dict[str, str]] = None  # name, relationship, positions
    business_interests: List[str] = None
    pep_classification: str = "domestic"  # domestic, foreign, international
    risk_level: str = "medium"  # low, medium, high, critical
    is_current: bool = True
    last_position_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.positions is None:
            self.positions = []
        if self.countries is None:
            self.countries = []
        if self.nationality is None:
            self.nationality = []
        if self.family_members is None:
            self.family_members = []
        if self.business_interests is None:
            self.business_interests = []

@dataclass
class PEPDataSource:
    """PEP data source configuration"""
    source_id: str
    name: str
    coverage_type: str  # global, regional, national
    countries_covered: List[str]
    data_quality: str  # high, medium, low
    update_frequency: str  # daily, weekly, monthly, quarterly
    access_method: str  # api, download, scraping, manual
    url: str
    api_key_required: bool = False
    cost_model: str = "free"  # free, subscription, per_query
    last_updated: Optional[datetime] = None
    status: str = "active"
    record_count: int = 0

class PEPDataService:
    """Comprehensive PEP data service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.sources = {}
        self.pep_cache = {}
        self.cache_ttl = timedelta(hours=48)  # 48 hour cache for PEP data
        
        # Initialize data sources
        self._initialize_sources()
        
        self.logger.info(f"Initialized {len(self.sources)} PEP data sources")
    
    def _initialize_sources(self):
        """Initialize all PEP data sources"""
        
        # World-Check (Refinitiv) - Premium commercial database
        world_check_source = PEPDataSource(
            source_id="world_check",
            name="World-Check (Refinitiv)",
            coverage_type="global",
            countries_covered=["ALL"],
            data_quality="high",
            update_frequency="daily",
            access_method="api",
            url="https://api.refinitiv.com/worldcheck/v1",
            api_key_required=True,
            cost_model="subscription"
        )
        
        # Dow Jones Risk & Compliance
        dj_source = PEPDataSource(
            source_id="dow_jones",
            name="Dow Jones Risk & Compliance",
            coverage_type="global",
            countries_covered=["ALL"],
            data_quality="high",
            update_frequency="daily",
            access_method="api",
            url="https://api.dowjones.com/risk",
            api_key_required=True,
            cost_model="subscription"
        )
        
        # LexisNexis World Compliance
        lexis_source = PEPDataSource(
            source_id="lexisnexis",
            name="LexisNexis World Compliance",
            coverage_type="global",
            countries_covered=["ALL"],
            data_quality="high",
            update_frequency="daily",
            access_method="api",
            url="https://api.lexisnexis.com/worldcompliance",
            api_key_required=True,
            cost_model="subscription"
        )
        
        # OpenSanctions PEP Database (Open Source)
        opensanctions_source = PEPDataSource(
            source_id="opensanctions",
            name="OpenSanctions PEP Database",
            coverage_type="global",
            countries_covered=["ALL"],
            data_quality="medium",
            update_frequency="weekly",
            access_method="download",
            url="https://data.opensanctions.org/datasets/latest/peps/entities.ftm.json",
            api_key_required=False,
            cost_model="free"
        )
        
        # EU Politicians Database
        eu_politicians_source = PEPDataSource(
            source_id="eu_politicians",
            name="EU Politicians Database",
            coverage_type="regional",
            countries_covered=["EU_MEMBERS"],
            data_quality="high",
            update_frequency="monthly",
            access_method="scraping",
            url="https://www.europarl.europa.eu/meps/en/full-list",
            api_key_required=False,
            cost_model="free"
        )
        
        # US Government Officials (multiple sources)
        us_officials_source = PEPDataSource(
            source_id="us_officials",
            name="US Government Officials",
            coverage_type="national",
            countries_covered=["US"],
            data_quality="high",
            update_frequency="monthly",
            access_method="scraping",
            url="https://www.congress.gov/members",
            api_key_required=False,
            cost_model="free"
        )
        
        # UK Parliament Members
        uk_parliament_source = PEPDataSource(
            source_id="uk_parliament",
            name="UK Parliament Members",
            coverage_type="national",
            countries_covered=["UK"],
            data_quality="high",
            update_frequency="monthly",
            access_method="api",
            url="https://members-api.parliament.uk/api/Members",
            api_key_required=False,
            cost_model="free"
        )
        
        # Global SOE (State-Owned Enterprises) Database
        soe_source = PEPDataSource(
            source_id="global_soe",
            name="Global State-Owned Enterprises",
            coverage_type="global",
            countries_covered=["ALL"],
            data_quality="medium",
            update_frequency="quarterly",
            access_method="manual",
            url="https://www.oecd.org/corporate/soe-database.htm",
            api_key_required=False,
            cost_model="free"
        )
        
        # International Organizations Officials
        intl_orgs_source = PEPDataSource(
            source_id="intl_organizations",
            name="International Organizations Officials",
            coverage_type="global",
            countries_covered=["INTERNATIONAL"],
            data_quality="medium",
            update_frequency="monthly",
            access_method="scraping",
            url="https://www.un.org/sg/en/content/senior-staff",
            api_key_required=False,
            cost_model="free"
        )
        
        # African Development Bank PEPs
        afdb_source = PEPDataSource(
            source_id="afdb_peps",
            name="African Development Bank PEPs",
            coverage_type="regional",
            countries_covered=["AFRICA"],
            data_quality="medium",
            update_frequency="quarterly",
            access_method="scraping",
            url="https://www.afdb.org/en/about/organizational-structure",
            api_key_required=False,
            cost_model="free"
        )
        
        sources = [
            world_check_source, dj_source, lexis_source, opensanctions_source,
            eu_politicians_source, us_officials_source, uk_parliament_source,
            soe_source, intl_orgs_source, afdb_source
        ]
        
        for source in sources:
            self.sources[source.source_id] = source
    
    async def fetch_pep_data(self, source_id: Optional[str] = None, 
                           force_refresh: bool = False) -> Dict[str, List[PEPEntry]]:
        """Fetch PEP data from specified source or all sources"""
        
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
                if not force_refresh and source_id in self.pep_cache:
                    cache_entry = self.pep_cache[source_id]
                    if datetime.now() - cache_entry['timestamp'] < self.cache_ttl:
                        results[source_id] = cache_entry['data']
                        self.logger.info(f"Using cached PEP data for {source_id}")
                        continue
                
                # Fetch fresh data
                source = self.sources[source_id]
                self.logger.info(f"Fetching PEP data from {source.name}")
                
                if source.access_method == "download":
                    data = await self._fetch_download_source(source)
                elif source.access_method == "api":
                    data = await self._fetch_api_source(source)
                elif source.access_method == "scraping":
                    data = await self._fetch_scraping_source(source)
                elif source.access_method == "manual":
                    data = await self._fetch_manual_source(source)
                else:
                    self.logger.warning(f"Unknown access method for {source_id}: {source.access_method}")
                    continue
                
                # Cache the data
                self.pep_cache[source_id] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                
                results[source_id] = data
                
                # Update source metadata
                source.last_updated = datetime.now()
                source.record_count = len(data)
                source.status = "active"
                
                self.logger.info(f"Successfully fetched {len(data)} PEP entries from {source.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to fetch PEP data from {source_id}: {e}")
                source.status = "error"
                results[source_id] = []
        
        return results
    
    async def _fetch_download_source(self, source: PEPDataSource) -> List[PEPEntry]:
        """Fetch data from download-based sources"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} when fetching {source.url}")
                
                content = await response.text()
                
                # Parse based on source
                if source.source_id == "opensanctions":
                    return self._parse_opensanctions_json(content, source)
                else:
                    self.logger.warning(f"No parser for download source: {source.source_id}")
                    return []
    
    async def _fetch_api_source(self, source: PEPDataSource) -> List[PEPEntry]:
        """Fetch data from API-based sources"""
        
        headers = {}
        
        # Add API key if required
        if source.api_key_required:
            api_key = self._get_api_key(source.source_id)
            if api_key:
                if source.source_id in ["world_check", "dow_jones", "lexisnexis"]:
                    headers["Authorization"] = f"Bearer {api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} when fetching {source.url}")
                
                content = await response.text()
                
                # Parse based on source
                if source.source_id == "uk_parliament":
                    return self._parse_uk_parliament_json(content, source)
                elif source.source_id in ["world_check", "dow_jones", "lexisnexis"]:
                    return self._parse_commercial_api(content, source)
                else:
                    self.logger.warning(f"No API parser for source: {source.source_id}")
                    return []
    
    async def _fetch_scraping_source(self, source: PEPDataSource) -> List[PEPEntry]:
        """Fetch data from scraping-based sources"""
        
        if source.source_id == "eu_politicians":
            return await self._scrape_eu_politicians(source)
        elif source.source_id == "us_officials":
            return await self._scrape_us_officials(source)
        elif source.source_id == "intl_organizations":
            return await self._scrape_intl_organizations(source)
        elif source.source_id == "afdb_peps":
            return await self._scrape_afdb_peps(source)
        else:
            self.logger.warning(f"No scraper for source: {source.source_id}")
            return []
    
    async def _fetch_manual_source(self, source: PEPDataSource) -> List[PEPEntry]:
        """Fetch data from manual/curated sources"""
        
        if source.source_id == "global_soe":
            return await self._fetch_global_soe_data(source)
        else:
            self.logger.warning(f"No manual fetcher for source: {source.source_id}")
            return []
    
    def _parse_opensanctions_json(self, json_content: str, source: PEPDataSource) -> List[PEPEntry]:
        """Parse OpenSanctions PEP JSON format"""
        entries = []
        
        try:
            for line in json_content.strip().split('\n'):
                if not line.strip():
                    continue
                    
                data = json.loads(line)
                
                if data.get("schema") != "Person":
                    continue
                
                properties = data.get("properties", {})
                
                # Extract names
                names = properties.get("name", [])
                primary_name = names[0] if names else "Unknown"
                aliases = names[1:] if len(names) > 1 else []
                
                # Extract positions
                positions = []
                roles = properties.get("position", [])
                for role in roles:
                    positions.append({
                        "role": role,
                        "organization": properties.get("organization", [""])[0],
                        "start_date": None,
                        "end_date": None
                    })
                
                # Extract countries
                countries = properties.get("country", [])
                nationality = properties.get("nationality", [])
                
                entry = PEPEntry(
                    source=source.source_id,
                    entity_id=data.get("id", ""),
                    primary_name=primary_name,
                    aliases=aliases,
                    positions=positions,
                    countries=countries,
                    nationality=nationality,
                    pep_classification="domestic",
                    risk_level="medium",
                    is_current=True,
                    created_date=datetime.now(),
                    last_updated=datetime.now()
                )
                
                entries.append(entry)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse OpenSanctions JSON: {e}")
        
        return entries
    
    def _parse_uk_parliament_json(self, json_content: str, source: PEPDataSource) -> List[PEPEntry]:
        """Parse UK Parliament API JSON format"""
        entries = []
        
        try:
            data = json.loads(json_content)
            
            for member in data.get("value", []):
                name_display = member.get("nameDisplayAs", "Unknown")
                
                # Extract current memberships
                positions = []
                if member.get("latestHouseMembership"):
                    house = member["latestHouseMembership"].get("house", "")
                    positions.append({
                        "role": f"Member of {house}",
                        "organization": "UK Parliament",
                        "start_date": member["latestHouseMembership"].get("membershipStartDate"),
                        "end_date": member["latestHouseMembership"].get("membershipEndDate")
                    })
                
                entry = PEPEntry(
                    source=source.source_id,
                    entity_id=str(member.get("id", "")),
                    primary_name=name_display,
                    aliases=[],
                    positions=positions,
                    countries=["UK"],
                    nationality=["UK"],
                    pep_classification="domestic",
                    risk_level="medium",
                    is_current=member["latestHouseMembership"].get("membershipEndDate") is None,
                    created_date=datetime.now(),
                    last_updated=datetime.now()
                )
                
                entries.append(entry)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse UK Parliament JSON: {e}")
        
        return entries
    
    def _parse_commercial_api(self, json_content: str, source: PEPDataSource) -> List[PEPEntry]:
        """Parse commercial PEP API responses (World-Check, Dow Jones, LexisNexis)"""
        entries = []
        
        try:
            data = json.loads(json_content)
            
            # This is a simplified parser - actual implementation would depend on specific API format
            for record in data.get("records", []):
                primary_name = record.get("name", "Unknown")
                aliases = record.get("aliases", [])
                
                positions = []
                for position in record.get("positions", []):
                    positions.append({
                        "role": position.get("title", ""),
                        "organization": position.get("organization", ""),
                        "start_date": position.get("startDate"),
                        "end_date": position.get("endDate")
                    })
                
                entry = PEPEntry(
                    source=source.source_id,
                    entity_id=record.get("id", ""),
                    primary_name=primary_name,
                    aliases=aliases,
                    positions=positions,
                    countries=record.get("countries", []),
                    nationality=record.get("nationality", []),
                    pep_classification=record.get("pepClassification", "domestic"),
                    risk_level=record.get("riskLevel", "medium"),
                    is_current=record.get("isCurrent", True),
                    created_date=datetime.now(),
                    last_updated=datetime.now(),
                    additional_data=record.get("additionalInfo", {})
                )
                
                entries.append(entry)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse commercial API JSON: {e}")
        
        return entries
    
    async def _scrape_eu_politicians(self, source: PEPDataSource) -> List[PEPEntry]:
        """Scrape EU Parliament politicians"""
        entries = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url) as response:
                    content = await response.text()
                    
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find MEP entries (simplified - actual scraping would be more complex)
            mep_elements = soup.find_all('div', class_='mep-item')
            
            for mep in mep_elements:
                name_elem = mep.find('h3', class_='mep-name')
                if not name_elem:
                    continue
                    
                name = name_elem.text.strip()
                
                # Extract country from profile
                country_elem = mep.find('span', class_='mep-country')
                country = country_elem.text.strip() if country_elem else "Unknown"
                
                entry = PEPEntry(
                    source=source.source_id,
                    entity_id=f"eu_mep_{hash(name)}",
                    primary_name=name,
                    aliases=[],
                    positions=[{
                        "role": "Member of European Parliament",
                        "organization": "European Parliament",
                        "start_date": None,
                        "end_date": None
                    }],
                    countries=[country],
                    nationality=[country],
                    pep_classification="international",
                    risk_level="medium",
                    is_current=True,
                    created_date=datetime.now(),
                    last_updated=datetime.now()
                )
                
                entries.append(entry)
                
        except Exception as e:
            self.logger.error(f"Failed to scrape EU politicians: {e}")
        
        return entries
    
    async def _scrape_us_officials(self, source: PEPDataSource) -> List[PEPEntry]:
        """Scrape US government officials"""
        entries = []
        
        # Simulated US officials data (in production, scrape from multiple government sources)
        officials_data = [
            {"name": "Joe Biden", "role": "President", "organization": "Executive Branch"},
            {"name": "Kamala Harris", "role": "Vice President", "organization": "Executive Branch"},
            {"name": "Nancy Pelosi", "role": "Speaker of the House", "organization": "House of Representatives"},
            {"name": "Chuck Schumer", "role": "Senate Majority Leader", "organization": "US Senate"},
        ]
        
        for official in officials_data:
            entry = PEPEntry(
                source=source.source_id,
                entity_id=f"us_official_{hash(official['name'])}",
                primary_name=official["name"],
                aliases=[],
                positions=[{
                    "role": official["role"],
                    "organization": official["organization"],
                    "start_date": None,
                    "end_date": None
                }],
                countries=["US"],
                nationality=["US"],
                pep_classification="domestic",
                risk_level="high" if "President" in official["role"] else "medium",
                is_current=True,
                created_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            entries.append(entry)
        
        return entries
    
    async def _scrape_intl_organizations(self, source: PEPDataSource) -> List[PEPEntry]:
        """Scrape international organization officials"""
        entries = []
        
        # Simulated international organization data
        intl_officials = [
            {"name": "António Guterres", "role": "Secretary-General", "org": "United Nations"},
            {"name": "Christine Lagarde", "role": "President", "org": "European Central Bank"},
            {"name": "Kristalina Georgieva", "role": "Managing Director", "org": "International Monetary Fund"},
        ]
        
        for official in intl_officials:
            entry = PEPEntry(
                source=source.source_id,
                entity_id=f"intl_org_{hash(official['name'])}",
                primary_name=official["name"],
                aliases=[],
                positions=[{
                    "role": official["role"],
                    "organization": official["org"],
                    "start_date": None,
                    "end_date": None
                }],
                countries=["INTERNATIONAL"],
                nationality=[],
                pep_classification="international",
                risk_level="high",
                is_current=True,
                created_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            entries.append(entry)
        
        return entries
    
    async def _scrape_afdb_peps(self, source: PEPDataSource) -> List[PEPEntry]:
        """Scrape African Development Bank PEPs"""
        entries = []
        
        # Simulated AfDB officials
        afdb_officials = [
            {"name": "Akinwumi Adesina", "role": "President", "org": "African Development Bank"},
        ]
        
        for official in afdb_officials:
            entry = PEPEntry(
                source=source.source_id,
                entity_id=f"afdb_{hash(official['name'])}",
                primary_name=official["name"],
                aliases=[],
                positions=[{
                    "role": official["role"],
                    "organization": official["org"],
                    "start_date": None,
                    "end_date": None
                }],
                countries=["AFRICA"],
                nationality=[],
                pep_classification="international",
                risk_level="medium",
                is_current=True,
                created_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            entries.append(entry)
        
        return entries
    
    async def _fetch_global_soe_data(self, source: PEPDataSource) -> List[PEPEntry]:
        """Fetch global state-owned enterprise data"""
        entries = []
        
        # Simulated SOE executives data
        soe_executives = [
            {"name": "Zhang Wei", "role": "CEO", "org": "China National Petroleum Corporation", "country": "China"},
            {"name": "Wang Li", "role": "Chairman", "org": "State Grid Corporation", "country": "China"},
        ]
        
        for executive in soe_executives:
            entry = PEPEntry(
                source=source.source_id,
                entity_id=f"soe_{hash(executive['name'])}",
                primary_name=executive["name"],
                aliases=[],
                positions=[{
                    "role": executive["role"],
                    "organization": executive["org"],
                    "start_date": None,
                    "end_date": None
                }],
                countries=[executive["country"]],
                nationality=[executive["country"]],
                pep_classification="domestic",
                risk_level="medium",
                is_current=True,
                created_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            entries.append(entry)
        
        return entries
    
    def _get_api_key(self, source_id: str) -> Optional[str]:
        """Get API key for source (in production, load from secure config)"""
        # In production, load from secure configuration
        api_keys = {
            "world_check": None,  # Requires subscription
            "dow_jones": None,    # Requires subscription
            "lexisnexis": None,   # Requires subscription
        }
        
        return api_keys.get(source_id)
    
    async def search_peps(self, query: str, source_ids: Optional[List[str]] = None,
                         countries: Optional[List[str]] = None,
                         risk_levels: Optional[List[str]] = None,
                         fuzzy_match: bool = True, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search PEP data across sources with filtering"""
        
        # Fetch data if not cached
        pep_data = await self.fetch_pep_data()
        
        if source_ids:
            filtered_data = {k: v for k, v in pep_data.items() if k in source_ids}
        else:
            filtered_data = pep_data
        
        matches = []
        query_lower = query.lower()
        
        for source_id, entries in filtered_data.items():
            for entry in entries:
                # Apply filters
                if countries and not any(country in entry.countries for country in countries):
                    continue
                    
                if risk_levels and entry.risk_level not in risk_levels:
                    continue
                
                # Check primary name
                if self._name_matches(query_lower, entry.primary_name.lower(), fuzzy_match, threshold):
                    matches.append({
                        "match_type": "primary_name",
                        "match_score": self._calculate_match_score(query_lower, entry.primary_name.lower()),
                        "entry": asdict(entry)
                    })
                    continue
                
                # Check aliases
                for alias in entry.aliases:
                    if self._name_matches(query_lower, alias.lower(), fuzzy_match, threshold):
                        matches.append({
                            "match_type": "alias",
                            "match_score": self._calculate_match_score(query_lower, alias.lower()),
                            "entry": asdict(entry)
                        })
                        break
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def _name_matches(self, query: str, name: str, fuzzy_match: bool, threshold: float) -> bool:
        """Check if names match based on criteria"""
        
        if not fuzzy_match:
            return query in name or name in query
        
        score = self._calculate_match_score(query, name)
        return score >= threshold
    
    def _calculate_match_score(self, query: str, name: str) -> float:
        """Calculate match score between query and name"""
        
        if not query or not name:
            return 0.0
        
        if query == name:
            return 1.0
        
        if query in name or name in query:
            shorter = min(len(query), len(name))
            longer = max(len(query), len(name))
            return shorter / longer
        
        query_chars = set(query.replace(" ", ""))
        name_chars = set(name.replace(" ", ""))
        
        if not query_chars or not name_chars:
            return 0.0
        
        overlap = len(query_chars.intersection(name_chars))
        total = len(query_chars.union(name_chars))
        
        return overlap / total if total > 0 else 0.0
    
    async def get_pep_family_networks(self, pep_id: str) -> Dict[str, Any]:
        """Get family and business networks for a PEP"""
        
        # In production, this would query relationship databases
        network_data = {
            "pep_id": pep_id,
            "family_members": [],
            "business_associates": [],
            "corporate_connections": [],
            "network_risk_score": 0.0
        }
        
        return network_data
    
    async def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics for all PEP sources"""
        
        total_sources = len(self.sources)
        active_sources = len([s for s in self.sources.values() if s.status == "active"])
        total_records = sum(s.record_count for s in self.sources.values())
        
        # Group by coverage type
        by_coverage = {}
        for source in self.sources.values():
            coverage = source.coverage_type
            if coverage not in by_coverage:
                by_coverage[coverage] = {"sources": 0, "records": 0}
            by_coverage[coverage]["sources"] += 1
            by_coverage[coverage]["records"] += source.record_count
        
        # Group by cost model
        by_cost = {}
        for source in self.sources.values():
            cost_model = source.cost_model
            if cost_model not in by_cost:
                by_cost[cost_model] = {"sources": 0, "records": 0}
            by_cost[cost_model]["sources"] += 1
            by_cost[cost_model]["records"] += source.record_count
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_records": total_records,
            "by_coverage_type": by_coverage,
            "by_cost_model": by_cost,
            "cache_entries": len(self.pep_cache),
            "last_cache_update": max([
                entry['timestamp'] for entry in self.pep_cache.values()
            ]).isoformat() if self.pep_cache else None
        }
    
    async def update_all_sources(self) -> Dict[str, Any]:
        """Update all PEP sources"""
        
        self.logger.info("Starting update of all PEP sources")
        
        results = await self.fetch_pep_data(force_refresh=True)
        
        summary = {
            "updated_at": datetime.now().isoformat(),
            "sources_updated": len(results),
            "total_records": sum(len(entries) for entries in results.values()),
            "sources": {}
        }
        
        for source_id, entries in results.items():
            summary["sources"][source_id] = {
                "records": len(entries),
                "status": self.sources[source_id].status
            }
        
        self.logger.info(f"Updated {len(results)} PEP sources with {summary['total_records']} total records")
        
        return summary
