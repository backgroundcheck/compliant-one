"""
Sanctions and Watchlists Data Service
Comprehensive integration with global sanctions and watchlist sources
"""

import asyncio
import json
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import aiohttp
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SanctionEntry:
    """Individual sanctions entry data model"""
    source: str
    list_type: str
    entity_id: str
    entity_type: str  # individual, entity, vessel, aircraft
    primary_name: str
    aliases: List[str]
    date_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    nationality: List[str] = None
    passport_numbers: List[str] = None
    national_ids: List[str] = None
    addresses: List[Dict[str, str]] = None
    sanctions_programs: List[str] = None
    designation_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    risk_score: float = 0.0
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.nationality is None:
            self.nationality = []
        if self.passport_numbers is None:
            self.passport_numbers = []
        if self.national_ids is None:
            self.national_ids = []
        if self.addresses is None:
            self.addresses = []
        if self.sanctions_programs is None:
            self.sanctions_programs = []
        if self.aliases is None:
            self.aliases = []

@dataclass
class WatchlistSource:
    """Watchlist source configuration"""
    source_id: str
    name: str
    jurisdiction: str
    source_type: str  # sanctions, terrorist, law_enforcement
    update_frequency: str  # daily, weekly, monthly
    access_method: str  # api, download, scraping
    url: str
    api_key_required: bool = False
    last_updated: Optional[datetime] = None
    status: str = "active"  # active, inactive, error
    record_count: int = 0

class SanctionsWatchlistService:
    """Comprehensive sanctions and watchlist data service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.sources = {}
        self.sanctions_cache = {}
        self.cache_ttl = timedelta(hours=24)  # 24 hour cache
        
        # Initialize data sources
        self._initialize_sources()
        
        self.logger.info(f"Initialized {len(self.sources)} sanctions and watchlist sources")
    
    def _initialize_sources(self):
        """Initialize all sanctions and watchlist sources"""
        
        # UN Security Council Consolidated List
        un_source = WatchlistSource(
            source_id="un_consolidated",
            name="UN Security Council Consolidated List",
            jurisdiction="International",
            source_type="sanctions",
            update_frequency="weekly",
            access_method="download",
            url="https://scsanctions.un.org/resources/xml/en/consolidated.xml",
            api_key_required=False
        )
        
        # US OFAC SDN List
        ofac_sdn_source = WatchlistSource(
            source_id="ofac_sdn",
            name="OFAC Specially Designated Nationals (SDN)",
            jurisdiction="United States",
            source_type="sanctions",
            update_frequency="daily",
            access_method="download",
            url="https://www.treasury.gov/ofac/downloads/sdn.xml",
            api_key_required=False
        )
        
        # OFAC Consolidated Sanctions List
        ofac_csl_source = WatchlistSource(
            source_id="ofac_csl",
            name="OFAC Consolidated Sanctions List",
            jurisdiction="United States", 
            source_type="sanctions",
            update_frequency="daily",
            access_method="download",
            url="https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml",
            api_key_required=False
        )
        
        # UK HMT Consolidated List
        uk_hmt_source = WatchlistSource(
            source_id="uk_hmt",
            name="HMT Consolidated List of Financial Sanctions Targets",
            jurisdiction="United Kingdom",
            source_type="sanctions",
            update_frequency="daily",
            access_method="api",
            url="https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.json",
            api_key_required=False
        )
        
        # EU Consolidated List
        eu_source = WatchlistSource(
            source_id="eu_consolidated",
            name="EU Consolidated List of Sanctions",
            jurisdiction="European Union",
            source_type="sanctions",
            update_frequency="daily",
            access_method="download",
            url="https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList/content",
            api_key_required=False
        )
        
        # Australia DFAT Sanctions
        au_dfat_source = WatchlistSource(
            source_id="au_dfat",
            name="DFAT Consolidated List",
            jurisdiction="Australia",
            source_type="sanctions",
            update_frequency="daily",
            access_method="download",
            url="https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xml",
            api_key_required=False
        )
        
        # Interpol Red Notices (requires scraping/API)
        interpol_source = WatchlistSource(
            source_id="interpol_red",
            name="Interpol Red Notices",
            jurisdiction="International",
            source_type="law_enforcement",
            update_frequency="daily",
            access_method="api",
            url="https://ws-public.interpol.int/notices/v1/red",
            api_key_required=True
        )
        
        # FATF High Risk Jurisdictions
        fatf_source = WatchlistSource(
            source_id="fatf_high_risk",
            name="FATF High Risk Jurisdictions",
            jurisdiction="International",
            source_type="sanctions",
            update_frequency="monthly",
            access_method="scraping",
            url="https://www.fatf-gafi.org/en/publications/high-risk-and-other-monitored-jurisdictions.html",
            api_key_required=False
        )
        
        # World Bank Debarred Firms
        wb_source = WatchlistSource(
            source_id="world_bank_debarred",
            name="World Bank Debarred Firms and Individuals",
            jurisdiction="International",
            source_type="sanctions",
            update_frequency="monthly",
            access_method="download",
            url="https://web.worldbank.org/external/default/WDSContentServer/WDSP/IB/2023/01/01/000020953_20230101100001/Rendered/INDEX/Debarred0firms0and0individuals.txt",
            api_key_required=False
        )
        
        # Store all sources
        sources = [
            un_source, ofac_sdn_source, ofac_csl_source, uk_hmt_source,
            eu_source, au_dfat_source, interpol_source, fatf_source, wb_source
        ]
        
        for source in sources:
            self.sources[source.source_id] = source
    
    async def fetch_sanctions_data(self, source_id: Optional[str] = None, 
                                 force_refresh: bool = False) -> Dict[str, List[SanctionEntry]]:
        """Fetch sanctions data from specified source or all sources"""
        
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
                if not force_refresh and source_id in self.sanctions_cache:
                    cache_entry = self.sanctions_cache[source_id]
                    if datetime.now() - cache_entry['timestamp'] < self.cache_ttl:
                        results[source_id] = cache_entry['data']
                        self.logger.info(f"Using cached data for {source_id}")
                        continue
                
                # Fetch fresh data
                source = self.sources[source_id]
                self.logger.info(f"Fetching data from {source.name}")
                
                if source.access_method == "download":
                    data = await self._fetch_download_source(source)
                elif source.access_method == "api":
                    data = await self._fetch_api_source(source)
                elif source.access_method == "scraping":
                    data = await self._fetch_scraping_source(source)
                else:
                    self.logger.warning(f"Unknown access method for {source_id}: {source.access_method}")
                    continue
                
                # Cache the data
                self.sanctions_cache[source_id] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                
                results[source_id] = data
                
                # Update source metadata
                source.last_updated = datetime.now()
                source.record_count = len(data)
                source.status = "active"
                
                self.logger.info(f"Successfully fetched {len(data)} entries from {source.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to fetch data from {source_id}: {e}")
                source.status = "error"
                results[source_id] = []
        
        return results
    
    async def _fetch_download_source(self, source: WatchlistSource) -> List[SanctionEntry]:
        """Fetch data from download-based sources"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} when fetching {source.url}")
                
                content = await response.text()
                
                # Parse based on source
                if source.source_id == "un_consolidated":
                    return self._parse_un_xml(content, source)
                elif source.source_id.startswith("ofac"):
                    return self._parse_ofac_xml(content, source)
                elif source.source_id == "eu_consolidated":
                    return self._parse_eu_xml(content, source)
                elif source.source_id == "au_dfat":
                    return self._parse_au_xml(content, source)
                else:
                    self.logger.warning(f"No parser for source: {source.source_id}")
                    return []
    
    async def _fetch_api_source(self, source: WatchlistSource) -> List[SanctionEntry]:
        """Fetch data from API-based sources"""
        
        headers = {}
        
        # Add API key if required
        if source.api_key_required:
            # In production, load from secure config
            api_key = self._get_api_key(source.source_id)
            if api_key:
                if source.source_id == "interpol_red":
                    headers["Authorization"] = f"Bearer {api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} when fetching {source.url}")
                
                content = await response.text()
                
                # Parse based on source
                if source.source_id == "uk_hmt":
                    return self._parse_uk_json(content, source)
                elif source.source_id == "interpol_red":
                    return self._parse_interpol_json(content, source)
                else:
                    self.logger.warning(f"No API parser for source: {source.source_id}")
                    return []
    
    async def _fetch_scraping_source(self, source: WatchlistSource) -> List[SanctionEntry]:
        """Fetch data from scraping-based sources"""
        
        # FATF high-risk jurisdictions scraping
        if source.source_id == "fatf_high_risk":
            return await self._scrape_fatf_jurisdictions(source)
        else:
            self.logger.warning(f"No scraper for source: {source.source_id}")
            return []
    
    def _parse_un_xml(self, xml_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse UN Security Council XML format"""
        entries = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for individual in root.findall(".//INDIVIDUAL"):
                # Extract basic info
                names = individual.findall(".//NAME")
                primary_name = names[0].find("WHOLE_NAME").text if names else "Unknown"
                
                aliases = []
                for name in names[1:]:
                    if name.find("WHOLE_NAME") is not None:
                        aliases.append(name.find("WHOLE_NAME").text)
                
                # Extract additional data
                dob_elements = individual.findall(".//DATE_OF_BIRTH")
                dob = dob_elements[0].find("DATE").text if dob_elements else None
                
                pob_elements = individual.findall(".//PLACE_OF_BIRTH")
                pob = pob_elements[0].find("CITY").text if pob_elements else None
                
                # Create entry
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="UN_CONSOLIDATED",
                    entity_id=individual.get("ID", ""),
                    entity_type="individual",
                    primary_name=primary_name,
                    aliases=aliases,
                    date_of_birth=dob,
                    place_of_birth=pob,
                    sanctions_programs=["UN Security Council"],
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.9  # UN sanctions are high risk
                )
                
                entries.append(entry)
            
            # Parse entities
            for entity in root.findall(".//ENTITY"):
                names = entity.findall(".//NAME")
                primary_name = names[0].find("WHOLE_NAME").text if names else "Unknown"
                
                aliases = []
                for name in names[1:]:
                    if name.find("WHOLE_NAME") is not None:
                        aliases.append(name.find("WHOLE_NAME").text)
                
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="UN_CONSOLIDATED",
                    entity_id=entity.get("ID", ""),
                    entity_type="entity",
                    primary_name=primary_name,
                    aliases=aliases,
                    sanctions_programs=["UN Security Council"],
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.9
                )
                
                entries.append(entry)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse UN XML: {e}")
        
        return entries
    
    def _parse_ofac_xml(self, xml_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse OFAC XML format"""
        entries = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for sdn_entry in root.findall(".//sdnEntry"):
                # Extract basic info
                names = sdn_entry.findall(".//aka")
                primary_name = names[0].find("wholeName").text if names else "Unknown"
                
                aliases = []
                for name in names[1:]:
                    if name.find("wholeName") is not None:
                        aliases.append(name.find("wholeName").text)
                
                # Extract entity type
                entity_type = "individual" if sdn_entry.find(".//dateOfBirth") is not None else "entity"
                
                # Extract programs
                programs = []
                for program in sdn_entry.findall(".//program"):
                    programs.append(program.text)
                
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="OFAC_SDN",
                    entity_id=sdn_entry.get("uid", ""),
                    entity_type=entity_type,
                    primary_name=primary_name,
                    aliases=aliases,
                    sanctions_programs=programs,
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.95  # OFAC sanctions are very high risk
                )
                
                entries.append(entry)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse OFAC XML: {e}")
        
        return entries
    
    def _parse_eu_xml(self, xml_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse EU sanctions XML format"""
        entries = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for person in root.findall(".//PERSON"):
                # Extract names
                names = person.findall(".//NAME")
                primary_name = names[0].get("WHOLE_NAME", "Unknown") if names else "Unknown"
                
                aliases = []
                for name in names[1:]:
                    if name.get("WHOLE_NAME"):
                        aliases.append(name.get("WHOLE_NAME"))
                
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="EU_CONSOLIDATED",
                    entity_id=person.get("ID", ""),
                    entity_type="individual",
                    primary_name=primary_name,
                    aliases=aliases,
                    sanctions_programs=["EU Sanctions"],
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.85
                )
                
                entries.append(entry)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse EU XML: {e}")
        
        return entries
    
    def _parse_au_xml(self, xml_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse Australia DFAT XML format"""
        entries = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for individual in root.findall(".//Individual"):
                primary_name = individual.find(".//Name").text if individual.find(".//Name") is not None else "Unknown"
                
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="DFAT_CONSOLIDATED",
                    entity_id=individual.get("Id", ""),
                    entity_type="individual",
                    primary_name=primary_name,
                    aliases=[],
                    sanctions_programs=["Australia DFAT"],
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.8
                )
                
                entries.append(entry)
                
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse Australia XML: {e}")
        
        return entries
    
    def _parse_uk_json(self, json_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse UK HMT JSON format"""
        entries = []
        
        try:
            data = json.loads(json_content)
            
            for group in data.get("Groups", []):
                for member in group.get("Members", []):
                    primary_name = member.get("Name", "Unknown")
                    
                    # Extract aliases
                    aliases = []
                    for alias in member.get("Aliases", []):
                        aliases.append(alias.get("Name", ""))
                    
                    entry = SanctionEntry(
                        source=source.source_id,
                        list_type="UK_HMT",
                        entity_id=str(member.get("Id", "")),
                        entity_type="individual" if member.get("Type") == "Individual" else "entity",
                        primary_name=primary_name,
                        aliases=aliases,
                        sanctions_programs=["UK HMT"],
                        designation_date=datetime.now(),
                        last_updated=datetime.now(),
                        risk_score=0.85
                    )
                    
                    entries.append(entry)
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse UK JSON: {e}")
        
        return entries
    
    def _parse_interpol_json(self, json_content: str, source: WatchlistSource) -> List[SanctionEntry]:
        """Parse Interpol Red Notices JSON format"""
        entries = []
        
        try:
            data = json.loads(json_content)
            
            for notice in data.get("_embedded", {}).get("notices", []):
                forename = notice.get("forename", "")
                name = notice.get("name", "")
                primary_name = f"{forename} {name}".strip()
                
                entry = SanctionEntry(
                    source=source.source_id,
                    list_type="INTERPOL_RED",
                    entity_id=notice.get("entity_id", ""),
                    entity_type="individual",
                    primary_name=primary_name,
                    aliases=[],
                    nationality=notice.get("nationalities", []),
                    sanctions_programs=["Interpol Red Notice"],
                    designation_date=datetime.now(),
                    last_updated=datetime.now(),
                    risk_score=0.95,  # Red notices are very high risk
                    additional_data={
                        "charges": notice.get("charge", ""),
                        "wanted_by": notice.get("issuing_country_id", "")
                    }
                )
                
                entries.append(entry)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Interpol JSON: {e}")
        
        return entries
    
    async def _scrape_fatf_jurisdictions(self, source: WatchlistSource) -> List[SanctionEntry]:
        """Scrape FATF high-risk jurisdictions"""
        entries = []
        
        # Simulated FATF high-risk jurisdictions (in production, scrape the actual website)
        high_risk_jurisdictions = [
            "Iran", "North Korea", "Myanmar", "Afghanistan", "Syria"
        ]
        
        for jurisdiction in high_risk_jurisdictions:
            entry = SanctionEntry(
                source=source.source_id,
                list_type="FATF_HIGH_RISK",
                entity_id=jurisdiction.lower().replace(" ", "_"),
                entity_type="jurisdiction",
                primary_name=jurisdiction,
                aliases=[],
                sanctions_programs=["FATF High Risk"],
                designation_date=datetime.now(),
                last_updated=datetime.now(),
                risk_score=0.9,
                additional_data={"jurisdiction_type": "high_risk"}
            )
            
            entries.append(entry)
        
        return entries
    
    def _get_api_key(self, source_id: str) -> Optional[str]:
        """Get API key for source (in production, load from secure config)"""
        # In production, load from secure configuration
        api_keys = {
            "interpol_red": None,  # Requires registration
        }
        
        return api_keys.get(source_id)
    
    async def search_sanctions(self, query: str, source_ids: Optional[List[str]] = None,
                             fuzzy_match: bool = True, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search sanctions data across sources"""
        
        # Fetch data if not cached
        sanctions_data = await self.fetch_sanctions_data()
        
        if source_ids:
            # Filter to specified sources
            filtered_data = {k: v for k, v in sanctions_data.items() if k in source_ids}
        else:
            filtered_data = sanctions_data
        
        matches = []
        query_lower = query.lower()
        
        for source_id, entries in filtered_data.items():
            for entry in entries:
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
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def _name_matches(self, query: str, name: str, fuzzy_match: bool, threshold: float) -> bool:
        """Check if names match based on criteria"""
        
        if not fuzzy_match:
            return query in name or name in query
        
        # Simple fuzzy matching using character overlap
        score = self._calculate_match_score(query, name)
        return score >= threshold
    
    def _calculate_match_score(self, query: str, name: str) -> float:
        """Calculate match score between query and name"""
        
        # Simple character-based similarity
        if not query or not name:
            return 0.0
        
        # Exact match
        if query == name:
            return 1.0
        
        # Substring match
        if query in name or name in query:
            shorter = min(len(query), len(name))
            longer = max(len(query), len(name))
            return shorter / longer
        
        # Character overlap
        query_chars = set(query.replace(" ", ""))
        name_chars = set(name.replace(" ", ""))
        
        if not query_chars or not name_chars:
            return 0.0
        
        overlap = len(query_chars.intersection(name_chars))
        total = len(query_chars.union(name_chars))
        
        return overlap / total if total > 0 else 0.0
    
    async def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all data sources"""
        
        status = {}
        
        for source_id, source in self.sources.items():
            status[source_id] = {
                "name": source.name,
                "jurisdiction": source.jurisdiction,
                "source_type": source.source_type,
                "status": source.status,
                "last_updated": source.last_updated.isoformat() if source.last_updated else None,
                "record_count": source.record_count,
                "update_frequency": source.update_frequency,
                "access_method": source.access_method
            }
        
        return status
    
    async def update_all_sources(self) -> Dict[str, Any]:
        """Update all sanctions sources"""
        
        self.logger.info("Starting update of all sanctions sources")
        
        results = await self.fetch_sanctions_data(force_refresh=True)
        
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
        
        self.logger.info(f"Updated {len(results)} sources with {summary['total_records']} total records")
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        
        total_sources = len(self.sources)
        active_sources = len([s for s in self.sources.values() if s.status == "active"])
        total_records = sum(s.record_count for s in self.sources.values())
        
        # Group by jurisdiction
        by_jurisdiction = {}
        for source in self.sources.values():
            jurisdiction = source.jurisdiction
            if jurisdiction not in by_jurisdiction:
                by_jurisdiction[jurisdiction] = {"sources": 0, "records": 0}
            by_jurisdiction[jurisdiction]["sources"] += 1
            by_jurisdiction[jurisdiction]["records"] += source.record_count
        
        # Group by source type
        by_type = {}
        for source in self.sources.values():
            source_type = source.source_type
            if source_type not in by_type:
                by_type[source_type] = {"sources": 0, "records": 0}
            by_type[source_type]["sources"] += 1
            by_type[source_type]["records"] += source.record_count
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_records": total_records,
            "by_jurisdiction": by_jurisdiction,
            "by_type": by_type,
            "cache_entries": len(self.sanctions_cache),
            "last_cache_update": max([
                entry['timestamp'] for entry in self.sanctions_cache.values()
            ]).isoformat() if self.sanctions_cache else None
        }
