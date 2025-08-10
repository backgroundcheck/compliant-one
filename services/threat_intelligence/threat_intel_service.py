"""
Threat Intelligence and OSINT Service
Monitors legitimate threat intelligence sources, breach databases, and security forums
for compliance and risk management purposes
"""

import os
import sys
import asyncio
import aiohttp
import sqlite3
import logging
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use standard Python logging instead of Streamlit logger to avoid warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatIntelligenceService:
    """
    Legitimate threat intelligence and OSINT monitoring service
    Focuses on publicly available security information sources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Database and data paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_folder = self.project_root / "data" / "threat_intelligence"
        self.db_path = self.data_folder / "threat_intel.db"
        
        # Create directories
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Production Configuration
        self.config = {
            'user_agent': 'CompliantOne-ThreatIntel/1.0 (Financial Compliance Platform)',
            'request_timeout': 60,
            'rate_limit_delay': 2.0,  # seconds between requests
            'max_concurrent_requests': 5,
            'retry_attempts': 3,
            'enabled_sources': {
                'haveibeenpwned': bool(os.getenv('HIBP_API_KEY')),
                'virustotal': bool(os.getenv('VIRUSTOTAL_API_KEY')),
                'shodan': bool(os.getenv('SHODAN_API_KEY')),
                'greynoise': bool(os.getenv('GREYNOISE_API_KEY')),
                'abuse_ch': True,  # Public feed
                'cybercrime_tracker': True,  # Public feed
                'threatfox': True,  # Public API
                'urlhaus': True,  # Public API
                'feodotracker': True,  # Public feed
                'sslbl': True,  # Public feed
                'misp': bool(os.getenv('MISP_URL') and os.getenv('MISP_API_KEY')),
                'opencti': bool(os.getenv('OPENCTI_URL') and os.getenv('OPENCTI_API_KEY'))
            },
            'api_keys': {
                'haveibeenpwned': os.getenv('HIBP_API_KEY'),
                'virustotal': os.getenv('VIRUSTOTAL_API_KEY'),
                'shodan': os.getenv('SHODAN_API_KEY'),
                'greynoise': os.getenv('GREYNOISE_API_KEY'),
                'misp': os.getenv('MISP_API_KEY'),
                'opencti': os.getenv('OPENCTI_API_KEY')
            },
            'misp_url': os.getenv('MISP_URL'),
            'opencti_url': os.getenv('OPENCTI_URL')
        }
        
        # Production threat intelligence sources
        self.sources = {
            'breach_databases': {
                'haveibeenpwned': 'https://haveibeenpwned.com/api/v3',
                'dehashed': 'https://api.dehashed.com/search',
                'leakcheck': 'https://leakcheck.io/api'
            },
            'threat_feeds': {
                'feodotracker_ip': 'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
                'feodotracker_domains': 'https://feodotracker.abuse.ch/downloads/domainblocklist.csv',
                'sslbl_ips': 'https://sslbl.abuse.ch/blacklist/sslipblacklist.csv',
                'urlhaus_urls': 'https://urlhaus.abuse.ch/downloads/csv/',
                'threatfox_iocs': 'https://threatfox.abuse.ch/export/csv/recent/',
                'cybercrime_tracker': 'https://cybercrime-tracker.net/ccam.php',
                'malwaredomainlist': 'https://www.malwaredomainlist.com/hostslist/hosts.txt',
                'emergingthreats_compromised': 'https://rules.emergingthreats.net/blockrules/compromised-ips.txt',
                'emergingthreats_botcc': 'https://rules.emergingthreats.net/fwrules/emerging-botcc.rules'
            },
            'vulnerability_feeds': {
                'cve_recent': 'https://cve.mitre.org/data/downloads/allitems-cvrf.xml',
                'nvd_recent': 'https://services.nvd.nist.gov/rest/json/cves/1.0',
                'exploitdb': 'https://www.exploit-db.com/rss.xml'
            },
            'reputation_feeds': {
                'alienvault_reputation': 'https://reputation.alienvault.com/reputation.data',
                'talos_ip_blacklist': 'https://talosintelligence.com/documents/ip-blacklist',
                'spamhaus_drop': 'https://www.spamhaus.org/drop/drop.txt',
                'spamhaus_edrop': 'https://www.spamhaus.org/drop/edrop.txt'
            }
        }
        
        # Setup database
        self._setup_database()
        
        self.logger.info("Threat Intelligence Service initialized")
    
    def _setup_database(self):
        """Setup threat intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threat indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_type TEXT NOT NULL,
                indicator_value TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                threat_type TEXT,
                description TEXT,
                tags TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(indicator_type, indicator_value, source)
            )
        ''')
        
        # Breach data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breach_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                breach_name TEXT NOT NULL,
                domain TEXT,
                breach_date DATE,
                added_date TIMESTAMP,
                modified_date TIMESTAMP,
                pwn_count INTEGER,
                description TEXT,
                data_classes TEXT,
                is_verified BOOLEAN,
                is_fabricated BOOLEAN,
                is_sensitive BOOLEAN,
                is_retired BOOLEAN,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(breach_name, source)
            )
        ''')
        
        # Monitoring targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type TEXT NOT NULL,
                target_value TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 5,
                alert_threshold REAL DEFAULT 0.7,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP,
                UNIQUE(target_type, target_value)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                indicator_id INTEGER,
                target_id INTEGER,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (indicator_id) REFERENCES threat_indicators (id),
                FOREIGN KEY (target_id) REFERENCES monitoring_targets (id)
            )
        ''')
        
        # Configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_type ON threat_indicators(threat_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicator_value ON threat_indicators(indicator_value)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_breach_domain ON breach_data(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_severity ON threat_alerts(severity)')
        
        conn.commit()
        conn.close()
        
        # Run database migrations for existing databases
        self._run_migrations()
        
        self.logger.info("Threat intelligence database setup completed")
    
    def _run_migrations(self):
        """Run database migrations for schema updates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if alert_threshold column exists in monitoring_targets
            cursor.execute("PRAGMA table_info(monitoring_targets)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'alert_threshold' not in columns:
                cursor.execute('ALTER TABLE monitoring_targets ADD COLUMN alert_threshold REAL DEFAULT 0.7')
                self.logger.info("Added alert_threshold column to monitoring_targets table")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.warning(f"Migration warning (likely safe to ignore): {e}")
    
    async def collect_breach_data(self) -> Dict[str, Any]:
        """Collect data from legitimate breach databases"""
        results = {
            'success': True,
            'sources_checked': 0,
            'new_breaches': 0,
            'updated_breaches': 0,
            'errors': []
        }
        
        try:
            # Check Have I Been Pwned (requires API key for detailed access)
            if self.config['enabled_sources']['haveibeenpwned']:
                hibp_result = await self._collect_hibp_breaches()
                results['sources_checked'] += 1
                results['new_breaches'] += hibp_result.get('new_breaches', 0)
                
            # Check other legitimate breach databases
            # Note: Most require API keys and proper authorization
            
            self.logger.info(f"Breach data collection completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Breach data collection failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    async def _collect_hibp_breaches(self) -> Dict[str, Any]:
        """Collect real breach data from Have I Been Pwned API"""
        result = {'new_breaches': 0, 'updated_breaches': 0, 'errors': []}
        
        api_key = self.config['api_keys'].get('haveibeenpwned')
        if not api_key:
            result['errors'].append('HIBP API key not configured')
            return result
        
        try:
            headers = {
                'hibp-api-key': api_key,
                'User-Agent': self.config['user_agent']
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                # Get all breaches
                async with session.get('https://haveibeenpwned.com/api/v3/breaches') as response:
                    if response.status == 200:
                        breaches = await response.json()
                        
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        
                        for breach in breaches:
                            try:
                                cursor.execute('''
                                    INSERT OR REPLACE INTO breach_data 
                                    (breach_name, domain, breach_date, added_date, modified_date,
                                     pwn_count, description, data_classes, is_verified, 
                                     is_fabricated, is_sensitive, is_retired, source)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    breach['Name'],
                                    breach.get('Domain'),
                                    breach.get('BreachDate'),
                                    breach.get('AddedDate'),
                                    breach.get('ModifiedDate'),
                                    breach.get('PwnCount', 0),
                                    breach.get('Description', ''),
                                    ','.join(breach.get('DataClasses', [])),
                                    breach.get('IsVerified', False),
                                    breach.get('IsFabricated', False),
                                    breach.get('IsSensitive', False),
                                    breach.get('IsRetired', False),
                                    'haveibeenpwned'
                                ))
                                
                                if cursor.rowcount > 0:
                                    result['new_breaches'] += 1
                                
                            except Exception as e:
                                self.logger.warning(f"Error inserting breach {breach['Name']}: {e}")
                                result['errors'].append(f"Error inserting {breach['Name']}: {str(e)}")
                        
                        conn.commit()
                        conn.close()
                        
                    elif response.status == 401:
                        result['errors'].append('HIBP API key is invalid')
                    elif response.status == 429:
                        result['errors'].append('HIBP rate limit exceeded')
                    else:
                        result['errors'].append(f'HIBP API returned status {response.status}')
                        
                # Rate limiting for HIBP
                await asyncio.sleep(self.config['rate_limit_delay'])
                
        except Exception as e:
            self.logger.error(f"HIBP collection failed: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def collect_threat_feeds(self) -> Dict[str, Any]:
        """Collect data from legitimate threat intelligence feeds"""
        results = {
            'success': True,
            'feeds_processed': 0,
            'new_indicators': 0,
            'errors': []
        }
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config['request_timeout']),
                headers={'User-Agent': self.config['user_agent']}
            ) as session:
                
                # Process each category of feeds
                for category, feeds in self.sources['threat_feeds'].items():
                    if isinstance(feeds, dict):
                        for feed_name, feed_url in feeds.items():
                            try:
                                await self._process_threat_feed(session, feed_url, feed_name)
                                results['feeds_processed'] += 1
                                await asyncio.sleep(self.config['rate_limit_delay'])
                            except Exception as e:
                                self.logger.warning(f"Error processing feed {feed_name}: {e}")
                                results['errors'].append(f"{feed_name}: {str(e)}")
                    else:
                        # Handle legacy format
                        try:
                            await self._process_threat_feed(session, feeds, category)
                            results['feeds_processed'] += 1
                            await asyncio.sleep(self.config['rate_limit_delay'])
                        except Exception as e:
                            self.logger.warning(f"Error processing feed {category}: {e}")
                            results['errors'].append(f"{category}: {str(e)}")
                
                # Process reputation feeds
                for feed_name, feed_url in self.sources['reputation_feeds'].items():
                    try:
                        await self._process_reputation_feed(session, feed_url, feed_name)
                        results['feeds_processed'] += 1
                        await asyncio.sleep(self.config['rate_limit_delay'])
                    except Exception as e:
                        self.logger.warning(f"Error processing reputation feed {feed_name}: {e}")
                        results['errors'].append(f"{feed_name}: {str(e)}")
            
            self.logger.info(f"Threat feed collection completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Threat feed collection failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    async def _process_threat_feed(self, session: aiohttp.ClientSession, feed_url: str, feed_name: str = None):
        """Process a single threat intelligence feed"""
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Determine feed type and parse accordingly
                    if 'abuse.ch' in feed_url:
                        await self._parse_abuse_ch_feed(content, feed_name or feed_url)
                    elif 'cybercrime-tracker.net' in feed_url:
                        await self._parse_cybercrime_tracker_feed(content, feed_name or feed_url)
                    elif 'emergingthreats.net' in feed_url:
                        await self._parse_emerging_threats_feed(content, feed_name or feed_url)
                    elif 'malwaredomainlist.com' in feed_url:
                        await self._parse_malware_domain_list(content, feed_name or feed_url)
                    elif 'spamhaus.org' in feed_url:
                        await self._parse_spamhaus_feed(content, feed_name or feed_url)
                    else:
                        await self._parse_generic_feed(content, feed_name or feed_url)
                        
                else:
                    self.logger.warning(f"Feed {feed_url} returned status {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error processing feed {feed_url}: {e}")
            raise
    
    async def _process_reputation_feed(self, session: aiohttp.ClientSession, feed_url: str, feed_name: str):
        """Process reputation-based feeds"""
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    lines = content.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#') or line.startswith(';'):
                            continue
                        
                        # Parse different reputation feed formats
                        if 'alienvault' in feed_url:
                            # AlienVault format: IP#Reliability#Risk#Activity#Country#City#Latitude#Longitude
                            parts = line.split('#')
                            if len(parts) >= 3 and self._is_valid_ip(parts[0]):
                                cursor.execute('''
                                    INSERT OR REPLACE INTO threat_indicators 
                                    (indicator_type, indicator_value, source, confidence, threat_type, description)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', ('ip', parts[0], feed_name, min(float(parts[1])/10.0, 1.0), 'reputation', f'Risk: {parts[2]}, Activity: {parts[3]}'))
                        
                        elif 'spamhaus' in feed_url:
                            # Spamhaus DROP format: CIDR ; SBL ID
                            if ';' in line:
                                cidr = line.split(';')[0].strip()
                                if '/' in cidr:
                                    ip = cidr.split('/')[0]
                                    if self._is_valid_ip(ip):
                                        cursor.execute('''
                                            INSERT OR REPLACE INTO threat_indicators 
                                            (indicator_type, indicator_value, source, confidence, threat_type)
                                            VALUES (?, ?, ?, ?, ?)
                                        ''', ('ip', ip, feed_name, 0.9, 'spam'))
                        
                        else:
                            # Generic IP list
                            if self._is_valid_ip(line):
                                cursor.execute('''
                                    INSERT OR REPLACE INTO threat_indicators 
                                    (indicator_type, indicator_value, source, confidence, threat_type)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', ('ip', line, feed_name, 0.7, 'reputation'))
                    
                    conn.commit()
                    conn.close()
                    
        except Exception as e:
            self.logger.error(f"Error processing reputation feed {feed_url}: {e}")
            raise
    
    async def _parse_abuse_ch_feed(self, content: str, source: str):
        """Parse Abuse.ch threat feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            lines = content.strip().split('\n')
            for line in lines:
                if line.startswith('#') or not line.strip():
                    continue
                
                # Parse IP addresses or domains
                if self._is_valid_ip(line.strip()):
                    indicator_type = 'ip'
                    indicator_value = line.strip()
                elif self._is_valid_domain(line.strip()):
                    indicator_type = 'domain'
                    indicator_value = line.strip()
                else:
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO threat_indicators 
                    (indicator_type, indicator_value, source, confidence, threat_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (indicator_type, indicator_value, source, 0.8, 'malware'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing abuse.ch feed: {e}")
            raise
    
    async def _parse_cybercrime_tracker_feed(self, content: str, source: str):
        """Parse Cybercrime Tracker feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Parse HTML or CSV content based on format
            # This is a simplified parser
            lines = content.strip().split('\n')
            for line in lines:
                # Extract URLs or IPs from the content
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
                ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                
                for url in urls:
                    cursor.execute('''
                        INSERT OR REPLACE INTO threat_indicators 
                        (indicator_type, indicator_value, source, confidence, threat_type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('url', url, source, 0.7, 'cybercrime'))
                
                for ip in ips:
                    if self._is_valid_ip(ip):
                        cursor.execute('''
                            INSERT OR REPLACE INTO threat_indicators 
                            (indicator_type, indicator_value, source, confidence, threat_type)
                            VALUES (?, ?, ?, ?, ?)
                        ''', ('ip', ip, source, 0.7, 'cybercrime'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing cybercrime tracker feed: {e}")
            raise
    
    async def _parse_generic_feed(self, content: str, source: str):
        """Parse generic threat feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract common indicators
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Try to identify indicator type
                if self._is_valid_ip(line):
                    indicator_type = 'ip'
                elif self._is_valid_domain(line):
                    indicator_type = 'domain'
                elif self._is_valid_hash(line):
                    indicator_type = 'hash'
                else:
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO threat_indicators 
                    (indicator_type, indicator_value, source, confidence, threat_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (indicator_type, line, source, 0.6, 'unknown'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing generic feed: {e}")
            raise
    
    async def _parse_emerging_threats_feed(self, content: str, source: str):
        """Parse Emerging Threats feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Emerging Threats format: IP or CIDR
                if '/' in line:  # CIDR notation
                    ip = line.split('/')[0]
                else:
                    ip = line
                
                if self._is_valid_ip(ip):
                    cursor.execute('''
                        INSERT OR REPLACE INTO threat_indicators 
                        (indicator_type, indicator_value, source, confidence, threat_type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('ip', ip, source, 0.8, 'emerging_threat'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing Emerging Threats feed: {e}")
            raise
    
    async def _parse_malware_domain_list(self, content: str, source: str):
        """Parse Malware Domain List feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract domain/URL from line
                domain = line
                if domain.startswith('http'):
                    domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
                
                if self._is_valid_domain(domain):
                    cursor.execute('''
                        INSERT OR REPLACE INTO threat_indicators 
                        (indicator_type, indicator_value, source, confidence, threat_type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('domain', domain, source, 0.8, 'malware'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing Malware Domain List: {e}")
            raise
    
    async def _parse_spamhaus_feed(self, content: str, source: str):
        """Parse Spamhaus feeds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith(';') or line.startswith('#'):
                    continue
                
                # Spamhaus format: CIDR ; SBL ID
                if ';' in line:
                    cidr = line.split(';')[0].strip()
                    sbl_id = line.split(';')[1].strip() if len(line.split(';')) > 1 else ''
                else:
                    cidr = line
                    sbl_id = ''
                
                if '/' in cidr:
                    ip = cidr.split('/')[0]
                else:
                    ip = cidr
                
                if self._is_valid_ip(ip):
                    cursor.execute('''
                        INSERT OR REPLACE INTO threat_indicators 
                        (indicator_type, indicator_value, source, confidence, threat_type, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', ('ip', ip, source, 0.9, 'spam', f'SBL ID: {sbl_id}' if sbl_id else ''))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error parsing Spamhaus feed: {e}")
            raise

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        try:
            # Basic domain validation
            return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', domain) is not None
        except:
            return False
    
    def _is_valid_hash(self, hash_str: str) -> bool:
        """Validate hash format (MD5, SHA1, SHA256)"""
        try:
            if len(hash_str) == 32:  # MD5
                return all(c in '0123456789abcdefABCDEF' for c in hash_str)
            elif len(hash_str) == 40:  # SHA1
                return all(c in '0123456789abcdefABCDEF' for c in hash_str)
            elif len(hash_str) == 64:  # SHA256
                return all(c in '0123456789abcdefABCDEF' for c in hash_str)
            return False
        except:
            return False
    
    async def monitor_targets(self, targets: List[Dict[str, str]]) -> Dict[str, Any]:
        """Monitor specific targets against threat intelligence"""
        results = {
            'success': True,
            'targets_checked': 0,
            'alerts_generated': 0,
            'matches_found': []
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for target in targets:
                target_type = target.get('type')
                target_value = target.get('value')
                
                if not target_type or not target_value:
                    continue
                
                # Check against threat indicators
                cursor.execute('''
                    SELECT * FROM threat_indicators 
                    WHERE indicator_type = ? AND indicator_value = ? AND is_active = 1
                ''', (target_type, target_value))
                
                matches = cursor.fetchall()
                if matches:
                    for match in matches:
                        # Generate alert
                        alert_id = self._generate_alert(
                            cursor,
                            'threat_match',
                            'high',
                            f'{target_type.upper()} {target_value} found in threat intelligence',
                            f'Target {target_value} matches threat indicator from {match[3]}',
                            match[0]
                        )
                        
                        results['matches_found'].append({
                            'target': target_value,
                            'source': match[3],
                            'threat_type': match[5],
                            'confidence': match[4],
                            'alert_id': alert_id
                        })
                        
                        results['alerts_generated'] += 1
                
                results['targets_checked'] += 1
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Target monitoring completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Target monitoring failed: {e}")
            results['success'] = False
            return results
    
    def _generate_alert(self, cursor, alert_type: str, severity: str, title: str, 
                       description: str, indicator_id: int = None, target_id: int = None) -> int:
        """Generate a threat alert"""
        cursor.execute('''
            INSERT INTO threat_alerts 
            (alert_type, severity, title, description, indicator_id, target_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_type, severity, title, description, indicator_id, target_id))
        
        return cursor.lastrowid
    
    def add_monitoring_target(self, target_type: str, target_value: str, 
                            description: str = None, priority: int = 5) -> Dict[str, Any]:
        """Add a new monitoring target"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO monitoring_targets 
                (target_type, target_value, description, priority)
                VALUES (?, ?, ?, ?)
            ''', (target_type, target_value, description, priority))
            
            target_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'target_id': target_id,
                'message': f'Added monitoring target: {target_type} {target_value}'
            }
            
        except Exception as e:
            self.logger.error(f"Error adding monitoring target: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alerts(self, status: str = None, severity: str = None, 
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Get threat alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM threat_alerts WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            alerts = []
            
            for row in cursor.fetchall():
                alerts.append(dict(zip(columns, row)))
            
            conn.close()
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Threat indicators stats
            cursor.execute("SELECT COUNT(*) FROM threat_indicators WHERE is_active = 1")
            active_indicators = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT threat_type, COUNT(*) 
                FROM threat_indicators 
                WHERE is_active = 1 
                GROUP BY threat_type
            ''')
            threat_types = dict(cursor.fetchall())
            
            # Breach data stats
            cursor.execute("SELECT COUNT(*) FROM breach_data")
            total_breaches = cursor.fetchone()[0]
            
            # Alert stats
            cursor.execute("SELECT COUNT(*) FROM threat_alerts WHERE status = 'new'")
            new_alerts = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM threat_alerts 
                WHERE status = 'new' 
                GROUP BY severity
            ''')
            alert_severity = dict(cursor.fetchall())
            
            # Monitoring targets
            cursor.execute("SELECT COUNT(*) FROM monitoring_targets WHERE is_active = 1")
            active_targets = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'data': {
                    'total_indicators': active_indicators,
                    'threat_types': threat_types,
                    'total_breaches': total_breaches,
                    'active_alerts': new_alerts,
                    'alert_severity': alert_severity,
                    'active_targets': active_targets,
                    'database_path': str(self.db_path)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update service configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for key, value in config_updates.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO threat_config 
                    (config_key, config_value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, json.dumps(value), datetime.now()))
                
                # Update in-memory config
                if key in self.config:
                    self.config[key] = value
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Updated {len(config_updates)} configuration items'
            }
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current service configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT config_key, config_value FROM threat_config')
            config_rows = cursor.fetchall()
            
            config_data = {}
            for key, value in config_rows:
                try:
                    config_data[key] = json.loads(value)
                except:
                    config_data[key] = value
            
            conn.close()
            
            return {
                'success': True,
                'data': config_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting configuration: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the threat intelligence service"""
        try:
            health_status = {
                'database': False,
                'configuration': False,
                'api_sources': {}
            }
            
            # Check database connectivity
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM threat_indicators')
                conn.close()
                health_status['database'] = True
            except Exception as e:
                self.logger.error(f"Database health check failed: {e}")
            
            # Check configuration
            try:
                config = self.get_config()
                health_status['configuration'] = config['success']
            except Exception as e:
                self.logger.error(f"Configuration health check failed: {e}")
            
            # Check API sources
            api_keys = {
                'HIBP': os.getenv('HIBP_API_KEY'),
                'VirusTotal': os.getenv('VIRUSTOTAL_API_KEY'),
                'Shodan': os.getenv('SHODAN_API_KEY')
            }
            
            for source, key in api_keys.items():
                health_status['api_sources'][source] = 'configured' if key and key != f'your_{source.lower()}_api_key_here' else 'not_configured'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'database': False,
                'configuration': False,
                'api_sources': {},
                'error': str(e)
            }
    
    async def get_monitoring_targets(self) -> Dict[str, Any]:
        """Get all monitoring targets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, target_type, target_value, alert_threshold, 
                       is_active, created_at, last_checked
                FROM monitoring_targets
                ORDER BY created_at DESC
            ''')
            
            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'id': row[0],
                    'target_type': row[1],
                    'target_value': row[2],
                    'alert_threshold': row[3],
                    'is_active': bool(row[4]),
                    'created_at': row[5],
                    'last_checked': row[6]
                })
            
            conn.close()
            
            return {
                'success': True,
                'targets': targets
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring targets: {e}")
            return {
                'success': False,
                'error': str(e),
                'targets': []
            }
    
    async def add_monitoring_target(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new monitoring target"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_targets 
                (target_type, target_value, alert_threshold, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                target_data['target_type'],
                target_data['target_value'],
                target_data.get('alert_threshold', 0.7),
                True,
                datetime.now()
            ))
            
            target_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'target_id': target_id,
                'message': 'Monitoring target added successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error adding monitoring target: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_virustotal(self, indicators: List[str]) -> Dict[str, Any]:
        """Check indicators against VirusTotal API"""
        vt_api_key = os.getenv('VIRUSTOTAL_API_KEY')
        if not vt_api_key:
            self.logger.warning("VirusTotal API key not configured")
            return {
                'success': False,
                'error': 'VirusTotal API key not configured',
                'results': []
            }
        
        results = []
        headers = {
            'x-apikey': vt_api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                for indicator in indicators:
                    try:
                        # Determine indicator type and appropriate API endpoint
                        if self._is_valid_ip(indicator):
                            url = f"https://www.virustotal.com/vtapi/v2/ip-address/report"
                            params = {'apikey': vt_api_key, 'ip': indicator}
                        elif self._is_valid_domain(indicator):
                            url = f"https://www.virustotal.com/vtapi/v2/domain/report"
                            params = {'apikey': vt_api_key, 'domain': indicator}
                        elif self._is_valid_hash(indicator):
                            url = f"https://www.virustotal.com/vtapi/v2/file/report"
                            params = {'apikey': vt_api_key, 'resource': indicator}
                        else:
                            continue
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Parse VirusTotal response
                                if data.get('response_code') == 1:
                                    result = {
                                        'indicator': indicator,
                                        'scanned': True,
                                        'positives': data.get('positives', 0),
                                        'total': data.get('total', 0),
                                        'scan_date': data.get('scan_date'),
                                        'permalink': data.get('permalink')
                                    }
                                    
                                    # Store in database if malicious
                                    if data.get('positives', 0) > 0:
                                        await self._store_virustotal_result(indicator, data)
                                    
                                    results.append(result)
                                else:
                                    results.append({
                                        'indicator': indicator,
                                        'scanned': False,
                                        'message': 'Not found in VirusTotal'
                                    })
                            
                            elif response.status == 204:
                                # Rate limit exceeded
                                self.logger.warning("VirusTotal rate limit exceeded")
                                await asyncio.sleep(60)  # Wait 1 minute
                                
                            elif response.status == 403:
                                self.logger.error("VirusTotal API key invalid or expired")
                                break
                            
                            # Respect rate limits
                            await asyncio.sleep(15)  # Free API allows 4 requests per minute
                    
                    except Exception as e:
                        self.logger.error(f"Error checking {indicator} with VirusTotal: {e}")
                        results.append({
                            'indicator': indicator,
                            'scanned': False,
                            'error': str(e)
                        })
            
            return {
                'success': True,
                'results': results,
                'total_checked': len(indicators),
                'malicious_found': sum(1 for r in results if r.get('positives', 0) > 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error in VirusTotal check: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': results
            }
    
    async def _store_virustotal_result(self, indicator: str, vt_data: Dict[str, Any]):
        """Store VirusTotal results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine indicator type
            if self._is_valid_ip(indicator):
                indicator_type = 'ip'
            elif self._is_valid_domain(indicator):
                indicator_type = 'domain'
            elif self._is_valid_hash(indicator):
                indicator_type = 'hash'
            else:
                return
            
            # Calculate confidence based on detection ratio
            positives = vt_data.get('positives', 0)
            total = vt_data.get('total', 1)
            confidence = min(positives / total, 1.0) if total > 0 else 0.0
            
            description = f"VirusTotal: {positives}/{total} engines detected this as malicious"
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_type, indicator_value, source, confidence, threat_type, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                indicator_type, 
                indicator, 
                'VirusTotal', 
                confidence, 
                'malware', 
                description,
                json.dumps({
                    'vt_positives': positives,
                    'vt_total': total,
                    'scan_date': vt_data.get('scan_date'),
                    'permalink': vt_data.get('permalink')
                })
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing VirusTotal result: {e}")
    
    async def check_shodan(self, ips: List[str]) -> Dict[str, Any]:
        """Check IPs against Shodan API"""
        shodan_api_key = os.getenv('SHODAN_API_KEY')
        if not shodan_api_key:
            self.logger.warning("Shodan API key not configured")
            return {
                'success': False,
                'error': 'Shodan API key not configured',
                'results': []
            }
        
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for ip in ips:
                    if not self._is_valid_ip(ip):
                        continue
                    
                    try:
                        url = f"https://api.shodan.io/shodan/host/{ip}"
                        params = {'key': shodan_api_key}
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                result = {
                                    'ip': ip,
                                    'found': True,
                                    'ports': data.get('ports', []),
                                    'hostnames': data.get('hostnames', []),
                                    'country': data.get('country_name'),
                                    'organization': data.get('org'),
                                    'last_update': data.get('last_update'),
                                    'vulnerabilities': data.get('vulns', [])
                                }
                                
                                # Store interesting findings
                                if data.get('vulns') or len(data.get('ports', [])) > 10:
                                    await self._store_shodan_result(ip, data)
                                
                                results.append(result)
                                
                            elif response.status == 404:
                                results.append({
                                    'ip': ip,
                                    'found': False,
                                    'message': 'IP not found in Shodan'
                                })
                            
                            elif response.status == 401:
                                self.logger.error("Shodan API key invalid")
                                break
                            
                            # Respect rate limits
                            await asyncio.sleep(1)  # Shodan allows 1 request per second
                    
                    except Exception as e:
                        self.logger.error(f"Error checking {ip} with Shodan: {e}")
                        results.append({
                            'ip': ip,
                            'found': False,
                            'error': str(e)
                        })
            
            return {
                'success': True,
                'results': results,
                'total_checked': len(ips),
                'vulnerable_found': sum(1 for r in results if r.get('vulnerabilities'))
            }
            
        except Exception as e:
            self.logger.error(f"Error in Shodan check: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': results
            }
    
    async def _store_shodan_result(self, ip: str, shodan_data: Dict[str, Any]):
        """Store Shodan results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate confidence based on vulnerabilities and exposed services
            vulns = shodan_data.get('vulns', [])
            ports = shodan_data.get('ports', [])
            
            confidence = 0.5  # Base confidence
            if vulns:
                confidence += 0.4  # High confidence if vulnerabilities found
            if len(ports) > 10:
                confidence += 0.1  # Slightly higher if many ports exposed
            
            confidence = min(confidence, 1.0)
            
            description = f"Shodan: {len(ports)} open ports"
            if vulns:
                description += f", {len(vulns)} vulnerabilities"
            
            threat_type = 'vulnerability' if vulns else 'exposure'
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_type, indicator_value, source, confidence, threat_type, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'ip', 
                ip, 
                'Shodan', 
                confidence, 
                threat_type, 
                description,
                json.dumps({
                    'ports': ports,
                    'hostnames': shodan_data.get('hostnames', []),
                    'vulnerabilities': vulns,
                    'country': shodan_data.get('country_name'),
                    'organization': shodan_data.get('org'),
                    'last_update': shodan_data.get('last_update')
                })
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing Shodan result: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for threat intelligence service"""
        try:
            # Check database connectivity
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM threat_indicators")
            indicator_count = cursor.fetchone()[0]
            conn.close()
            
            # Check enabled sources
            enabled_sources = [k for k, v in self.config['enabled_sources'].items() if v]
            
            return {
                'status': 'healthy',
                'database_accessible': True,
                'total_indicators': indicator_count,
                'enabled_sources': enabled_sources,
                'data_folder': str(self.data_folder),
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

async def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Threat Intelligence Service")
    parser.add_argument("--collect-breaches", action="store_true", help="Collect breach data")
    parser.add_argument("--collect-feeds", action="store_true", help="Collect threat feeds")
    parser.add_argument("--monitor", action="store_true", help="Run monitoring checks")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--add-target", nargs=3, metavar=('TYPE', 'VALUE', 'DESC'), help="Add monitoring target")
    parser.add_argument("--alerts", action="store_true", help="Show alerts")
    
    args = parser.parse_args()
    
    service = ThreatIntelligenceService()
    
    if args.collect_breaches:
        print("📥 Collecting breach data...")
        result = await service.collect_breach_data()
        print(f"✅ Collection completed: {result}")
    
    elif args.collect_feeds:
        print("📡 Collecting threat feeds...")
        result = await service.collect_threat_feeds()
        print(f"✅ Collection completed: {result}")
    
    elif args.monitor:
        print("🔍 Running monitoring checks...")
        # Get monitoring targets from database
        conn = sqlite3.connect(service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT target_type, target_value FROM monitoring_targets WHERE is_active = 1")
        targets = [{'type': row[0], 'value': row[1]} for row in cursor.fetchall()]
        conn.close()
        
        if targets:
            result = await service.monitor_targets(targets)
            print(f"🚨 Monitoring completed: {result}")
        else:
            print("No monitoring targets configured")
    
    elif args.add_target:
        target_type, target_value, description = args.add_target
        result = service.add_monitoring_target(target_type, target_value, description)
        print(f"➕ Add target result: {result}")
    
    elif args.alerts:
        alerts = service.get_alerts(limit=20)
        print(f"🚨 Recent Alerts ({len(alerts)}):")
        for alert in alerts:
            print(f"  {alert['severity'].upper()}: {alert['title']}")
            print(f"    Created: {alert['created_at']}")
            print(f"    Status: {alert['status']}")
            print()
    
    elif args.stats:
        stats = service.get_statistics()
        print("📊 Threat Intelligence Statistics:")
        print(f"  🎯 Active indicators: {stats['indicators']['total_active']}")
        print(f"  💥 Total breaches: {stats['breaches']['total']}")
        print(f"  🚨 New alerts: {stats['alerts']['new']}")
        print(f"  👁️  Active targets: {stats['monitoring']['active_targets']}")
        
        print("\n  Threat types:")
        for threat_type, count in stats['indicators']['by_threat_type'].items():
            print(f"    {threat_type}: {count}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
