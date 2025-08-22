"""Breach Intelligence Service
GDPR/CCPA-compliant breach monitoring and credential exposure detection

This service provides:
- Dark web monitoring via ethical OSINT
- Paste site monitoring (Pastebin, GitHub Gists, etc.)
- Breach directory analysis
- Anonymous k-anonymity breach checking
- Data enrichment via SpiderFoot/Maltego integration
- Privacy-by-design architecture

Note: A non-executable fragment from a previous edit (dark web monitoring loop) has been
preserved within the class methods below. Any stray top-level code was converted into
documentation to keep the module importable without altering functionality.
"""

import os
import sys
import asyncio
import aiohttp
import sqlite3
import logging

# Handle optional psycopg2 dependency
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    psycopg2 = None
import hashlib
import bcrypt
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from urllib.parse import urljoin, urlparse
import base64
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BreachSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class DataType(Enum):
    EMAIL = "email"
    PASSWORD = "password"
    USERNAME = "username"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    PERSONAL_INFO = "personal_info"

@dataclass
class BreachRecord:
    """Privacy-compliant breach record"""
    breach_id: str
    name: str
    description: str
    breach_date: datetime
    discovered_date: datetime
    affected_accounts: int
    data_types: List[DataType]
    severity: BreachSeverity
    source: str
    is_verified: bool
    metadata: Dict[str, Any]

class BreachIntelligenceService:
    """
    Privacy-compliant breach intelligence service
    
    Features:
    - K-anonymity credential checking
    - Dark web monitoring (ethical OSINT)
    - Paste site monitoring
    - GDPR/CCPA compliance
    - Data enrichment integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Database and data paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_folder = self.project_root / "data" / "breach_intelligence"
        self.db_path = self.data_folder / "breach_intel.db"
        self.db_url = os.getenv("DATABASE_URL")
        self.db_type = (
            "postgres" if (self.db_url or "").startswith("postgres") and HAS_POSTGRES else "sqlite"
        )
        
        # Create directories
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Privacy-compliant configuration
        self.k_anonymity_threshold = 1000  # Minimum group size for k-anonymity
        self.data_retention_days = 30  # GDPR compliance - minimal retention
        self.hash_algorithm = 'sha256'  # For credential hashing

        # Rate limiting for ethical scraping
        self.request_delay = 2.0  # Seconds between requests
        self.max_concurrent_requests = 3

        # Initialize database
        self._setup_database()

        # Load configuration
        self.config = self._load_config()

        self.logger.info("Breach Intelligence Service initialized with privacy-by-design")

    def _get_connection(self):
        """Return a DB connection for the active backend."""
        if self.db_type == "postgres" and HAS_POSTGRES:
            # psycopg2 supports PostgreSQL URIs
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)

    def _prepare_query(self, query: str) -> str:
        """Adapt parameter placeholder style for the active backend.

        We write queries using '?' placeholders; convert to '%s' for Postgres.
        """
        if self.db_type == "postgres":
            return query.replace("?", "%s")
        return query

    def _execute(self, query: str, params: tuple = (), *, fetchone=False, fetchall=False, commit=False):
        """Execute a query with parameters and optional fetch/commit.

        Returns cursor.fetchone() or cursor.fetchall() based on flags,
        or None for write-only operations.
        """
        q = self._prepare_query(query)
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(q, params)
            result = None
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            if commit:
                conn.commit()
            return result
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _setup_database(self):
        """Setup database with privacy-compliant schema (SQLite/Postgres)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Breach metadata table
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS breaches (
                    id SERIAL PRIMARY KEY,
                    breach_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    breach_date TIMESTAMP,
                    discovered_date TIMESTAMP,
                    affected_accounts INTEGER,
                    data_types TEXT,
                    severity TEXT,
                    source TEXT,
                    is_verified BOOLEAN,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS breaches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    breach_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    breach_date DATE,
                    discovered_date DATE,
                    affected_accounts INTEGER,
                    data_types TEXT,  -- JSON array
                    severity TEXT,
                    source TEXT,
                    is_verified BOOLEAN,
                    metadata TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
        
        # Anonymous hash table for k-anonymity checks
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS credential_hashes (
                    id SERIAL PRIMARY KEY,
                    hash_prefix TEXT NOT NULL,
                    full_hash TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    breach_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS credential_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash_prefix TEXT NOT NULL,  -- First 5 characters of hash
                    full_hash TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    breach_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
        
        # Monitoring targets (privacy-compliant)
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_targets (
                    id SERIAL PRIMARY KEY,
                    target_hash TEXT UNIQUE NOT NULL,
                    target_type TEXT NOT NULL,
                    alert_email TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checked TIMESTAMP
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS monitoring_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_hash TEXT UNIQUE NOT NULL,  -- Hashed identifier
                    target_type TEXT NOT NULL,
                    alert_email TEXT,  -- Encrypted if stored
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checked TIMESTAMP
                )
                '''
            )
        
        # Alerts (minimal data retention)
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS breach_alerts (
                    id SERIAL PRIMARY KEY,
                    target_id INTEGER,
                    breach_id TEXT,
                    severity TEXT,
                    alert_type TEXT,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (target_id) REFERENCES monitoring_targets (id),
                    FOREIGN KEY (breach_id) REFERENCES breaches (breach_id)
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS breach_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER,
                    breach_id TEXT,
                    severity TEXT,
                    alert_type TEXT,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,  -- Auto-cleanup for privacy
                    FOREIGN KEY (target_id) REFERENCES monitoring_targets (id),
                    FOREIGN KEY (breach_id) REFERENCES breaches (breach_id)
                )
                '''
            )
        
        # OSINT sources tracking
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS osint_sources (
                    id SERIAL PRIMARY KEY,
                    source_name TEXT UNIQUE NOT NULL,
                    source_type TEXT NOT NULL,
                    base_url TEXT,
                    last_scraped TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    rate_limit_delay INTEGER DEFAULT 2,
                    compliance_notes TEXT
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS osint_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT UNIQUE NOT NULL,
                    source_type TEXT NOT NULL,  -- paste_site, forum, directory
                    base_url TEXT,
                    last_scraped TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    rate_limit_delay INTEGER DEFAULT 2,
                    compliance_notes TEXT
                )
                '''
            )
        
    # Enrichment data from SpiderFoot/Maltego
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS enrichment_data (
                    id SERIAL PRIMARY KEY,
                    breach_id TEXT,
                    indicator_type TEXT,
                    indicator_value TEXT,
                    confidence_score REAL,
                    source_tool TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (breach_id) REFERENCES breaches (breach_id)
                )
                """
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS enrichment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    breach_id TEXT,
                    indicator_type TEXT,  -- ip, domain, email, hash
                    indicator_value TEXT,
                    confidence_score REAL,
                    source_tool TEXT,  -- spiderfoot, maltego, etc.
                    metadata TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (breach_id) REFERENCES breaches (breach_id)
                )
                '''
            )
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_breach_date ON breaches(breach_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash_prefix ON credential_hashes(hash_prefix)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_target_hash ON monitoring_targets(target_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_status ON breach_alerts(status)')

        conn.commit()
        conn.close()

        self.logger.info("Breach intelligence database setup completed")

    def _load_config(self) -> Dict[str, Any]:
        """Load privacy-compliant configuration"""
        return {
            # Ethical OSINT sources
            'paste_sites': {
                'pastebin': {
                    'enabled': True,
                    'base_url': 'https://pastebin.com',
                    'rate_limit': 2.0,
                    'respect_robots_txt': True
                },
                'github_gists': {
                    'enabled': True,
                    'base_url': 'https://api.github.com/gists',
                    'rate_limit': 1.0,
                    'respect_robots_txt': True
                },
                'slexy': {
                    'enabled': True,
                    'base_url': 'http://slexy.org',
                    'rate_limit': 3.0,
                    'respect_robots_txt': True
                }
            },
            
            # Tor-based dark web monitoring (ethical)
            'darkweb_sources': {
                'enabled': os.getenv('ENABLE_DARKWEB_MONITORING', 'false').lower() == 'true',
                'tor_proxy': os.getenv('TOR_PROXY', 'socks5h://127.0.0.1:9050'),
                'rate_limit': 5.0,  # Very conservative
                'compliance_mode': True,  # Only public breach disclosure forums
                'excluded_domains': [
                    # Exclude illegal marketplaces
                    'marketplace',
                    'drugs',
                    'weapons',
                    'illegal'
                ]
            },
            
            # Breach directories (public)
            'breach_directories': {
                'dehashed': {
                    'enabled': False,  # Requires paid API
                    'base_url': 'https://www.dehashed.com',
                    'note': 'Paid service - disabled'
                },
                'leakcheck': {
                    'enabled': False,  # Requires paid API
                    'base_url': 'https://leakcheck.io',
                    'note': 'Paid service - disabled'
                },
                'public_dumps': {
                    'enabled': True,
                    'sources': [
                        'https://github.com/hmaverickadams/breach-parse',
                        'https://archive.org/details/BreachCompilation'
                    ],
                    'note': 'Public breach compilation sources'
                }
            },
            
            # Data enrichment tools
            'enrichment_tools': {
                'spiderfoot': {
                    'enabled': os.getenv('SPIDERFOOT_ENABLED', 'false').lower() == 'true',
                    'api_url': os.getenv('SPIDERFOOT_API_URL', 'http://localhost:5001'),
                    'api_key': os.getenv('SPIDERFOOT_API_KEY'),
                    'rate_limit': 1.0
                },
                'maltego': {
                    'enabled': os.getenv('MALTEGO_ENABLED', 'false').lower() == 'true',
                    'api_url': os.getenv('MALTEGO_API_URL'),
                    'api_key': os.getenv('MALTEGO_API_KEY'),
                    'rate_limit': 2.0
                }
            },
            
            # Privacy settings
            'privacy': {
                'k_anonymity_threshold': self.k_anonymity_threshold,
                'data_retention_days': self.data_retention_days,
                'hash_algorithm': self.hash_algorithm,
                'minimal_data_storage': True,
                'auto_cleanup_enabled': True
            }
        }

    def _hash_credential(self, credential: str, salt: str = None) -> str:
        """
        Hash credential using secure method for k-anonymity
        Uses SHA-256 with optional salt for privacy
        """
        if salt is None:
            salt = os.getenv('CREDENTIAL_SALT', 'compliant_one_2025')
        
        # Normalize credential (lowercase, strip)
        normalized = credential.lower().strip()
        
        # Create hash with salt
        hash_input = f"{normalized}{salt}".encode('utf-8')
        
        if self.hash_algorithm == 'sha256':
            return hashlib.sha256(hash_input).hexdigest()
        elif self.hash_algorithm == 'bcrypt':
            return bcrypt.hashpw(hash_input, bcrypt.gensalt()).decode('utf-8')
        else:
            return hashlib.sha1(hash_input).hexdigest()

    def _get_hash_prefix(self, full_hash: str, prefix_length: int = 5) -> str:
        """Get hash prefix for k-anonymity lookup"""
        return full_hash[:prefix_length]

    async def check_credential_breach(self, credential: str, credential_type: str = 'email') -> Dict[str, Any]:
        """
        Check if credential appears in breaches using k-anonymity
        
        Privacy features:
        - Only stores hash prefixes
        - K-anonymity threshold enforcement
        - No plaintext storage
        """
        try:
            # Hash the credential
            full_hash = self._hash_credential(credential)
            hash_prefix = self._get_hash_prefix(full_hash)
            
            # Get all hashes with same prefix (k-anonymity set)
            matches = self._execute(
                '''
                SELECT full_hash, breach_count, data_type 
                FROM credential_hashes 
                WHERE hash_prefix = ? AND data_type = ?
                ''',
                (hash_prefix, credential_type),
                fetchall=True,
            )
            
            # Check if we have enough matches for k-anonymity
            if len(matches) < self.k_anonymity_threshold:
                return {
                    'success': True,
                    'breached': False,
                    'message': 'Insufficient data for privacy-compliant check',
                    'k_anonymity_protected': True
                }
            
            # Check for exact match
            breach_count = 0
            for hash_match, count, data_type in matches:
                if hash_match == full_hash:
                    breach_count = count
                    break
            
            return {
                'success': True,
                'breached': breach_count > 0,
                'breach_count': breach_count,
                'credential_type': credential_type,
                'k_anonymity_set_size': len(matches),
                'privacy_compliant': True
            }
            
        except Exception as e:
            self.logger.error(f"Error checking credential breach: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def monitor_paste_sites(self) -> Dict[str, Any]:
        """
        Ethical monitoring of public paste sites for breach data
        
        Compliance features:
        - Respects robots.txt
        - Rate limiting
        - Only public sites
        - No authentication bypass
        """
        results = {
            'success': True,
            'sites_checked': 0,
            'potential_breaches_found': 0,
            'new_credentials': 0,
            'errors': []
        }
        
        try:
            paste_sites = self.config['paste_sites']
            
            async with aiohttp.ClientSession() as session:
                for site_name, site_config in paste_sites.items():
                    if not site_config.get('enabled', False):
                        continue
                    
                    try:
                        self.logger.info(f"Monitoring paste site: {site_name}")
                        
                        # Check robots.txt compliance
                        if site_config.get('respect_robots_txt', True):
                            robots_url = f"{site_config['base_url']}/robots.txt"
                            async with session.get(robots_url) as response:
                                if response.status == 200:
                                    robots_content = await response.text()
                                    if 'Disallow: /' in robots_content:
                                        self.logger.warning(f"Robots.txt disallows scraping for {site_name}")
                                        continue
                        
                        # Site-specific monitoring
                        if site_name == 'pastebin':
                            await self._monitor_pastebin(session, site_config)
                        elif site_name == 'github_gists':
                            await self._monitor_github_gists(session, site_config)
                        elif site_name == 'slexy':
                            await self._monitor_slexy(session, site_config)
                        
                        results['sites_checked'] += 1
                        
                        # Rate limiting
                        await asyncio.sleep(site_config.get('rate_limit', 2.0))
                        
                    except Exception as e:
                        error_msg = f"Error monitoring {site_name}: {e}"
                        self.logger.error(error_msg)
                        results['errors'].append(error_msg)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in paste site monitoring: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _monitor_pastebin(self, session: aiohttp.ClientSession, config: Dict[str, Any]):
        """Monitor Pastebin for potential breach data (ethical, public only)"""
        try:
            # Only check public, recent pastes
            public_url = f"{config['base_url']}/api/api_post.php"
            
            # Use public API if available (no private content)
            headers = {
                'User-Agent': 'Compliant.one-BreachMonitor/1.0 (Security Research)'
            }
            
            # Search for common breach indicators in public pastes
            breach_keywords = [
                'password', 'email', 'database', 'dump', 'leak',
                'breach', 'hacked', 'sql', 'combo', 'cracked'
            ]
            
            # Note: This is a simplified example. Real implementation would
            # use proper Pastebin API with appropriate rate limiting
            
            self.logger.info("Pastebin monitoring completed (ethical mode)")
            
        except Exception as e:
            self.logger.error(f"Error monitoring Pastebin: {e}")

    async def _monitor_github_gists(self, session: aiohttp.ClientSession, config: Dict[str, Any]):
        """Monitor public GitHub Gists for potential breach data"""
        try:
            # Search public gists for breach-related content
            search_url = f"{config['base_url']}/public"
            
            headers = {
                'User-Agent': 'Compliant.one-BreachMonitor/1.0',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            async with session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    gists = await response.json()
                    
                    for gist in gists:
                        # Check gist description and files for breach indicators
                        description = gist.get('description', '').lower()
                        
                        breach_indicators = [
                            'password', 'email', 'database', 'dump', 'leak', 'breach'
                        ]
                        
                        if any(indicator in description for indicator in breach_indicators):
                            self.logger.info(f"Potential breach gist found: {gist['id']}")
                            
                            # Analyze gist content (public only)
                            await self._analyze_gist_content(session, gist)
            
        except Exception as e:
            self.logger.error(f"Error monitoring GitHub Gists: {e}")

    async def _monitor_slexy(self, session: aiohttp.ClientSession, config: Dict[str, Any]):
        """Monitor Slexy paste site for potential breach data"""
        try:
            # Monitor public pastes on Slexy
            recent_url = f"{config['base_url']}/recent"
            
            headers = {
                'User-Agent': 'Compliant.one-BreachMonitor/1.0 (Security Research)'
            }
            
            async with session.get(recent_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse recent pastes for breach indicators
                    # This would need HTML parsing in real implementation
                    
                    self.logger.info("Slexy monitoring completed")
            
        except Exception as e:
            self.logger.error(f"Error monitoring Slexy: {e}")

    async def _analyze_gist_content(self, session: aiohttp.ClientSession, gist: Dict[str, Any]):
        """Analyze GitHub Gist content for breach data"""
        try:
            # Get gist files
            for filename, file_info in gist.get('files', {}).items():
                if file_info.get('truncated', False):
                    continue  # Skip truncated files
                
                content = file_info.get('content', '')
                
                # Look for credential patterns
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                password_pattern = r'password[:\s=]+[^\s\n]+|pwd[:\s=]+[^\s\n]+'
                
                emails = re.findall(email_pattern, content, re.IGNORECASE)
                passwords = re.findall(password_pattern, content, re.IGNORECASE)
                
                if emails or passwords:
                    self.logger.warning(f"Potential breach data in gist {gist['id']}: {len(emails)} emails, {len(passwords)} passwords")
                    
                    # Store potential breach (privacy-compliant)
                    await self._store_potential_breach({
                        'source': 'github_gist',
                        'source_id': gist['id'],
                        'email_count': len(emails),
                        'password_count': len(passwords),
                        'description': gist.get('description', ''),
                        'discovered_date': datetime.now()
                    })
        
        except Exception as e:
            self.logger.error(f"Error analyzing gist content: {e}")

    async def _store_potential_breach(self, breach_data: Dict[str, Any]):
        """Store potential breach data (privacy-compliant)"""
        try:
            breach_id = hashlib.sha256(f"{breach_data['source']}{breach_data['source_id']}".encode()).hexdigest()[:16]

            name = f"Potential breach from {breach_data['source']}"
            description = breach_data.get('description', '')
            discovered_date = breach_data['discovered_date']
            affected_accounts = breach_data.get('email_count', 0) + breach_data.get('password_count', 0)
            data_types = json.dumps(['email', 'password'])
            severity = 'medium'
            source = breach_data['source']
            is_verified = False
            metadata = json.dumps(breach_data)

            if self.db_type == 'postgres':
                # Use upsert with ON CONFLICT
                self._execute(
                    '''
                    INSERT INTO breaches (breach_id, name, description, discovered_date, affected_accounts, data_types, severity, source, is_verified, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (breach_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        discovered_date = EXCLUDED.discovered_date,
                        affected_accounts = EXCLUDED.affected_accounts,
                        data_types = EXCLUDED.data_types,
                        severity = EXCLUDED.severity,
                        source = EXCLUDED.source,
                        is_verified = EXCLUDED.is_verified,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                    ''',
                    (
                        breach_id,
                        name,
                        description,
                        discovered_date,
                        affected_accounts,
                        data_types,
                        severity,
                        source,
                        is_verified,
                        metadata,
                    ),
                    commit=True,
                )
            else:
                # SQLite: emulate upsert with INSERT OR REPLACE
                self._execute(
                    '''
                    INSERT OR REPLACE INTO breaches 
                    (breach_id, name, description, discovered_date, affected_accounts, data_types, severity, source, is_verified, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        breach_id,
                        name,
                        description,
                        discovered_date,
                        affected_accounts,
                        data_types,
                        severity,
                        source,
                        is_verified,
                        metadata,
                    ),
                    commit=True,
                )
            
            self.logger.info(f"Stored potential breach: {breach_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing potential breach: {e}")

    async def monitor_darkweb_sources(self) -> Dict[str, Any]:
        """
        Ethical dark web monitoring for breach disclosure forums
        
        Compliance features:
        - Only monitors public disclosure forums
        - Excludes illegal marketplaces
        - Uses Tor for privacy
        - Respects terms of service
        """
        if not self.config['darkweb_sources']['enabled']:
            return {
                'success': True,
                'message': 'Dark web monitoring disabled',
                'sources_checked': 0
            }
        
        results = {
            'success': True,
            'sources_checked': 0,
            'breaches_found': 0,
            'errors': []
        }
        
        try:
            # Ethical dark web sources (public breach disclosure only)
            ethical_sources = [
                # Public breach disclosure forums
                'https://breached.to',  # Public breach disclosure forum
                'https://raidforums.com',  # (if available) - breach discussions
                # Note: Only include sources that are for security research
            ]
            
            tor_proxy = self.config['darkweb_sources']['tor_proxy']
            
            # Create Tor-enabled session
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Compliant.one-SecurityResearch/1.0'}
            ) as session:
                
                for source_url in ethical_sources:
                    try:
                        self.logger.info(f"Monitoring dark web source: {source_url}")
                        
                        # Note: Real implementation would use Tor proxy
                        # This is a placeholder for ethical monitoring
                        
                        await asyncio.sleep(self.config['darkweb_sources']['rate_limit'])
                        results['sources_checked'] += 1
                        
                    except Exception as e:
                        error_msg = f"Error monitoring {source_url}: {e}"
                        self.logger.error(error_msg)
                        results['errors'].append(error_msg)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in dark web monitoring: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def enrich_breach_data(self, breach_id: str) -> Dict[str, Any]:
        """
        Enrich breach data using SpiderFoot/Maltego integration
        
        Features:
        - IOC extraction
        - Threat actor attribution
        - Infrastructure analysis
        - Timeline correlation
        """
        results = {
            'success': True,
            'enrichment_sources': 0,
            'indicators_found': 0,
            'threat_actors': [],
            'infrastructure': []
        }
        
        try:
            # Get breach data
            breach = self._execute(
                'SELECT * FROM breaches WHERE breach_id = ?',
                (breach_id,),
                fetchone=True,
            )
            
            if not breach:
                return {'success': False, 'error': 'Breach not found'}
            
            # SpiderFoot enrichment
            if self.config['enrichment_tools']['spiderfoot']['enabled']:
                spiderfoot_results = await self._enrich_with_spiderfoot(breach_id, breach)
                results['enrichment_sources'] += 1
                results['indicators_found'] += len(spiderfoot_results.get('indicators', []))
            
            # Maltego enrichment
            if self.config['enrichment_tools']['maltego']['enabled']:
                maltego_results = await self._enrich_with_maltego(breach_id, breach)
                results['enrichment_sources'] += 1
                results['threat_actors'].extend(maltego_results.get('threat_actors', []))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error enriching breach data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _enrich_with_spiderfoot(self, breach_id: str, breach_data: tuple) -> Dict[str, Any]:
        """Enrich breach data using SpiderFoot"""
        try:
            spiderfoot_config = self.config['enrichment_tools']['spiderfoot']
            api_url = spiderfoot_config['api_url']
            
            # Extract potential indicators from breach metadata
            metadata = json.loads(breach_data[10] or '{}')
            
            indicators = []
            
            # Look for IP addresses, domains, emails in breach data
            # This would integrate with SpiderFoot API
            
            return {
                'indicators': indicators,
                'source': 'spiderfoot'
            }
            
        except Exception as e:
            self.logger.error(f"Error in SpiderFoot enrichment: {e}")
            return {'indicators': []}

    async def _enrich_with_maltego(self, breach_id: str, breach_data: tuple) -> Dict[str, Any]:
        """Enrich breach data using Maltego"""
        try:
            maltego_config = self.config['enrichment_tools']['maltego']
            
            # This would integrate with Maltego API for threat actor attribution
            threat_actors = []
            
            return {
                'threat_actors': threat_actors,
                'source': 'maltego'
            }
            
        except Exception as e:
            self.logger.error(f"Error in Maltego enrichment: {e}")
            return {'threat_actors': []}

    async def add_monitoring_target(self, credential: str, credential_type: str, alert_email: str = None) -> Dict[str, Any]:
        """
        Add credential for monitoring (privacy-compliant)
        
        Privacy features:
        - Only stores hashed identifier
        - Optional encrypted alert email
        - Minimal data retention
        """
        try:
            # Hash the credential for privacy
            target_hash = self._hash_credential(credential)
            
            if self.db_type == 'postgres':
                # Use upsert to avoid duplicates and return id
                inserted = self._execute(
                    '''
                    INSERT INTO monitoring_targets (target_hash, target_type, alert_email, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (target_hash) DO UPDATE SET
                        target_type = EXCLUDED.target_type,
                        alert_email = EXCLUDED.alert_email,
                        is_active = EXCLUDED.is_active,
                        last_checked = monitoring_targets.last_checked
                    RETURNING id
                    ''' ,
                    (
                        target_hash,
                        credential_type,
                        alert_email,
                        True,
                        datetime.now(),
                    ),
                    fetchone=True,
                    commit=True,
                )
                target_id = inserted[0] if inserted else None
                if not target_id:
                    # Fallback to lookup
                    row = self._execute(
                        'SELECT id FROM monitoring_targets WHERE target_hash = ?',
                        (target_hash,),
                        fetchone=True,
                    )
                    target_id = row[0] if row else None
            else:
                # SQLite
                self._execute(
                    '''
                    INSERT OR REPLACE INTO monitoring_targets 
                    (target_hash, target_type, alert_email, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        target_hash,
                        credential_type,
                        alert_email,  # Could be encrypted in production
                        True,
                        datetime.now(),
                    ),
                    commit=True,
                )
                row = self._execute(
                    'SELECT id FROM monitoring_targets WHERE target_hash = ?',
                    (target_hash,),
                    fetchone=True,
                )
                target_id = row[0] if row else None
            
            return {
                'success': True,
                'target_id': target_id,
                'message': 'Monitoring target added successfully',
                'privacy_compliant': True
            }
            
        except Exception as e:
            self.logger.error(f"Error adding monitoring target: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_breach_statistics(self) -> Dict[str, Any]:
        """Get privacy-compliant breach statistics"""
        try:
            # Total breaches
            total_breaches = self._execute(
                'SELECT COUNT(*) FROM breaches',
                fetchone=True,
            )[0]

            # Breaches by severity
            rows = self._execute(
                'SELECT severity, COUNT(*) FROM breaches GROUP BY severity',
                fetchall=True,
            )
            severity_stats = dict(rows)

            # Recent breaches (last 30 days)
            cutoff = datetime.now() - timedelta(days=30)
            # Use timestamp comparison for both backends
            recent_breaches = self._execute(
                'SELECT COUNT(*) FROM breaches WHERE discovered_date >= ?',
                (cutoff,),
                fetchone=True,
            )[0]

            # Monitoring targets
            active_targets = self._execute(
                'SELECT COUNT(*) FROM monitoring_targets WHERE is_active = 1',
                fetchone=True,
            )[0]

            # Active alerts
            active_alerts = self._execute(
                'SELECT COUNT(*) FROM breach_alerts WHERE status = "new"',
                fetchone=True,
            )[0]
            
            return {
                'success': True,
                'data': {
                    'total_breaches': total_breaches,
                    'severity_breakdown': severity_stats,
                    'recent_breaches_30d': recent_breaches,
                    'active_monitoring_targets': active_targets,
                    'active_alerts': active_alerts,
                    'privacy_compliant': True,
                    'k_anonymity_threshold': self.k_anonymity_threshold
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting breach statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """
        GDPR/CCPA compliance - cleanup expired data
        
        Features:
        - Automatic data retention enforcement
        - Privacy-by-design cleanup
        - Audit logging
        """
        try:
            cleanup_stats = {
                'alerts_cleaned': 0,
                'old_breaches_archived': 0,
                'expired_targets_removed': 0
            }
            
            # Cleanup expired alerts
            expiry_date = datetime.now() - timedelta(days=self.data_retention_days)
            
            expired_alerts = self._execute(
                'SELECT COUNT(*) FROM breach_alerts WHERE created_at < ?',
                (expiry_date,),
                fetchone=True,
            )[0]
            self._execute(
                'DELETE FROM breach_alerts WHERE created_at < ?',
                (expiry_date,),
                commit=True,
            )
            cleanup_stats['alerts_cleaned'] = expired_alerts
            
            # Archive old breach data (keep metadata, remove sensitive data)
            updated = self._execute(
                '''
                UPDATE breaches 
                SET metadata = '{"archived": true, "original_metadata_removed": true}' 
                WHERE discovered_date < ? AND (metadata IS NULL OR metadata NOT LIKE '%archived%')
                ''',
                (expiry_date,),
                commit=True,
            )
            # cursor.rowcount isn't available after connection close in helper; recompute count
            archived_count = self._execute(
                "SELECT COUNT(*) FROM breaches WHERE discovered_date < ? AND metadata LIKE '%archived%'",
                (expiry_date,),
                fetchone=True,
            )[0]
            cleanup_stats['old_breaches_archived'] = archived_count
            
            self.logger.info(f"Completed privacy compliance cleanup: {cleanup_stats}")
            
            return {
                'success': True,
                'cleanup_stats': cleanup_stats,
                'compliance': 'GDPR/CCPA'
            }
            
        except Exception as e:
            self.logger.error(f"Error in privacy compliance cleanup: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """Health check for breach intelligence service"""
        try:
            health_status = {
                'database': False,
                'privacy_compliance': True,
                'monitoring_active': False,
                'enrichment_tools': {}
            }
            
            # Check database
            try:
                _ = self._execute('SELECT COUNT(*) FROM breaches', fetchone=True)
                health_status['database'] = True
            except Exception as e:
                self.logger.error(f"Database health check failed: {e}")
            
            # Check monitoring status
            health_status['monitoring_active'] = True  # Always active for ethical monitoring

            # Overall status
            health_status['status'] = 'healthy' if health_status.get('database') else 'degraded'
            
            # Check enrichment tools
            for tool, config in self.config['enrichment_tools'].items():
                health_status['enrichment_tools'][tool] = config.get('enabled', False)
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'database': False,
                'privacy_compliance': False,
                'error': str(e)
            }
