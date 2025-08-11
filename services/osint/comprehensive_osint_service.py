"""
Comprehensive OSINT Integration Service for Compliant-One
Multi-Source Intelligence Gathering and Analysis
"""

import asyncio
import aiohttp
import requests
import json
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
try:
    from config.secure_api_config import SecureAPIConfiguration
except Exception:
    # Fallback to the legacy APIServiceManager only if needed, but avoid importing secrets by default
    SecureAPIConfiguration = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveOSINTService:
    """Comprehensive OSINT service integrating all available APIs"""
    
    def __init__(self):
        # Prefer secure environment-based configuration
        if SecureAPIConfiguration is not None:
            self.api_manager = SecureAPIConfiguration()
        else:
            raise RuntimeError("Secure configuration not available. Please use config/secure_api_config.py and environment variables.")
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    # Threat Intelligence Services
    async def analyze_ip_comprehensive(self, ip_address: str) -> Dict[str, Any]:
        """Comprehensive IP analysis using multiple threat intelligence sources"""
        results = {
            'ip_address': ip_address,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # VirusTotal Analysis
        if self.api_manager.is_service_available('virus_total'):
            try:
                vt_result = await self._virustotal_ip_analysis(ip_address)
                results['analysis']['virus_total'] = vt_result
            except Exception as e:
                logger.error(f"VirusTotal analysis failed: {e}")
                
        # AbuseIPDB Analysis
        if self.api_manager.is_service_available('abuse_ip_db'):
            try:
                abuse_result = await self._abuseipdb_analysis(ip_address)
                results['analysis']['abuse_ip_db'] = abuse_result
            except Exception as e:
                logger.error(f"AbuseIPDB analysis failed: {e}")
                
        # Shodan Analysis
        if self.api_manager.is_service_available('shodan'):
            try:
                shodan_result = await self._shodan_analysis(ip_address)
                results['analysis']['shodan'] = shodan_result
            except Exception as e:
                logger.error(f"Shodan analysis failed: {e}")
                
        # OTX Analysis
        if self.api_manager.is_service_available('otx'):
            try:
                otx_result = await self._otx_analysis(ip_address)
                results['analysis']['otx'] = otx_result
            except Exception as e:
                logger.error(f"OTX analysis failed: {e}")
                
        # IBM X-Force Analysis
        if self.api_manager.is_service_available('ibm_xforce'):
            try:
                xforce_result = await self._ibm_xforce_analysis(ip_address)
                results['analysis']['ibm_xforce'] = xforce_result
            except Exception as e:
                logger.error(f"IBM X-Force analysis failed: {e}")
                
        # Bot Detection
        if self.api_manager.is_service_available('botscout'):
            try:
                bot_result = await self._botscout_analysis(ip_address)
                results['analysis']['bot_detection'] = bot_result
            except Exception as e:
                logger.error(f"Bot detection failed: {e}")
                
        # Fraud Detection
        if self.api_manager.is_service_available('fraudguard'):
            try:
                fraud_result = await self._fraudguard_analysis(ip_address)
                results['analysis']['fraud_detection'] = fraud_result
            except Exception as e:
                logger.error(f"Fraud detection failed: {e}")
                
        # IP Info Analysis
        if self.api_manager.is_service_available('ip_info'):
            try:
                ipinfo_result = await self._ipinfo_analysis(ip_address)
                results['analysis']['ip_info'] = ipinfo_result
            except Exception as e:
                logger.error(f"IPInfo analysis failed: {e}")
        
        # Calculate overall risk score
        results['risk_assessment'] = self._calculate_risk_score(results['analysis'])
        
        return results

    async def analyze_domain_comprehensive(self, domain: str) -> Dict[str, Any]:
        """Comprehensive domain analysis"""
        results = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # WHOIS Analysis
        if self.api_manager.is_service_available('whois_xml'):
            try:
                whois_result = await self._whois_analysis(domain)
                results['analysis']['whois'] = whois_result
            except Exception as e:
                logger.error(f"WHOIS analysis failed: {e}")
                
        # BuiltWith Analysis
        if self.api_manager.is_service_available('builtwith'):
            try:
                builtwith_result = await self._builtwith_analysis(domain)
                results['analysis']['builtwith'] = builtwith_result
            except Exception as e:
                logger.error(f"BuiltWith analysis failed: {e}")
                
        # VirusTotal Domain Analysis
        if self.api_manager.is_service_available('virus_total'):
            try:
                vt_result = await self._virustotal_domain_analysis(domain)
                results['analysis']['virus_total'] = vt_result
            except Exception as e:
                logger.error(f"VirusTotal domain analysis failed: {e}")
        
        return results

    async def analyze_email_comprehensive(self, email: str) -> Dict[str, Any]:
        """Comprehensive email analysis"""
        results = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # Hunter.io Analysis
        if self.api_manager.is_service_available('hunter'):
            try:
                hunter_result = await self._hunter_email_analysis(email)
                results['analysis']['hunter'] = hunter_result
            except Exception as e:
                logger.error(f"Hunter.io analysis failed: {e}")
        
        return results

    async def analyze_phone_comprehensive(self, phone: str, country_code: str = 'US') -> Dict[str, Any]:
        """Comprehensive phone number analysis"""
        results = {
            'phone': phone,
            'country_code': country_code,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # Numverify Analysis
        if self.api_manager.is_service_available('numverify'):
            try:
                numverify_result = await self._numverify_analysis(phone, country_code)
                results['analysis']['numverify'] = numverify_result
            except Exception as e:
                logger.error(f"Numverify analysis failed: {e}")
        
        return results

    async def analyze_blockchain_address(self, address: str, chain: str = 'ETH') -> Dict[str, Any]:
        """Blockchain address analysis using Breadcrumbs"""
        results = {
            'address': address,
            'chain': chain,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        if self.api_manager.is_service_available('breadcrumbs'):
            try:
                # Address Risk Analysis
                risk_result = await self._breadcrumbs_address_risk(address, chain)
                results['analysis']['risk_assessment'] = risk_result
                
                # Sanctions Check
                sanctions_result = await self._breadcrumbs_sanctions_check(address, chain)
                results['analysis']['sanctions'] = sanctions_result
                
                # Node Analysis
                node_result = await self._breadcrumbs_node_analysis(address, chain)
                results['analysis']['node_analysis'] = node_result
                
            except Exception as e:
                logger.error(f"Blockchain analysis failed: {e}")
        
        return results

    async def search_news_intelligence(self, query: str, days_back: int = 7) -> Dict[str, Any]:
        """News intelligence gathering"""
        results = {
            'query': query,
            'timeframe': f'{days_back} days',
            'timestamp': datetime.now().isoformat(),
            'articles': []
        }
        
        if self.api_manager.is_service_available('news_api'):
            try:
                from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                news_result = await self._news_api_search(query, from_date)
                results['articles'] = news_result
            except Exception as e:
                logger.error(f"News API search failed: {e}")
        
        return results

    async def track_flight(self, flight_number: str = None) -> Dict[str, Any]:
        """Aviation intelligence tracking"""
        results = {
            'flight_number': flight_number,
            'timestamp': datetime.now().isoformat(),
            'flight_data': {}
        }
        
        if self.api_manager.is_service_available('aviationstack'):
            try:
                flight_result = await self._aviationstack_analysis(flight_number)
                results['flight_data'] = flight_result
            except Exception as e:
                logger.error(f"Flight tracking failed: {e}")
        
        return results

    # Individual API Implementation Methods
    async def _virustotal_ip_analysis(self, ip: str) -> Dict[str, Any]:
        """VirusTotal IP analysis"""
        api_key = self.api_manager.get_api_key('virus_total')
        url = f"https://www.virustotal.com/vtapi/v2/ip-address/report"
        
        params = {
            'apikey': api_key,
            'ip': ip
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _abuseipdb_analysis(self, ip: str) -> Dict[str, Any]:
        """AbuseIPDB analysis"""
        api_key = self.api_manager.get_api_key('abuse_ip_db')
        url = f"https://api.abuseipdb.com/api/v2/check"
        
        headers = {
            'Key': api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'ipAddress': ip,
            'maxAgeInDays': 90,
            'verbose': ''
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            return await response.json()

    async def _shodan_analysis(self, ip: str) -> Dict[str, Any]:
        """Shodan analysis"""
        api_key = self.api_manager.get_api_key('shodan')
        url = f"https://api.shodan.io/shodan/host/{ip}"
        
        params = {'key': api_key}
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _otx_analysis(self, ip: str) -> Dict[str, Any]:
        """AlienVault OTX analysis"""
        api_key = self.api_manager.get_api_key('otx')
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        
        headers = {'X-OTX-API-KEY': api_key}
        
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def _ibm_xforce_analysis(self, ip: str) -> Dict[str, Any]:
        """IBM X-Force analysis"""
        credentials = self.api_manager.get_api_key('ibm_xforce')
        auth_string = base64.b64encode(f"{credentials['key']}:{credentials['password']}".encode()).decode()
        
        url = f"https://api.xforce.ibmcloud.com/ipr/{ip}"
        headers = {'Authorization': f'Basic {auth_string}'}
        
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def _botscout_analysis(self, ip: str) -> Dict[str, Any]:
        """BotScout analysis"""
        api_key = self.api_manager.get_api_key('botscout')
        url = f"http://botscout.com/test/?ip={ip}&key={api_key}"
        
        async with self.session.get(url) as response:
            text_result = await response.text()
            return {'result': text_result, 'is_bot': 'Y' in text_result}

    async def _fraudguard_analysis(self, ip: str) -> Dict[str, Any]:
        """FraudGuard analysis"""
        credentials = self.api_manager.get_api_key('fraudguard')
        auth_string = base64.b64encode(f"{credentials['username']}:{credentials['password']}".encode()).decode()
        
        url = f"https://api.fraudguard.io/v2/ip/{ip}"
        headers = {'Authorization': f'Basic {auth_string}'}
        
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def _ipinfo_analysis(self, ip: str) -> Dict[str, Any]:
        """IPInfo analysis"""
        api_key = self.api_manager.get_api_key('ip_info')
        url = f"https://ipinfo.io/{ip}?token={api_key}"
        
        async with self.session.get(url) as response:
            return await response.json()

    async def _whois_analysis(self, domain: str) -> Dict[str, Any]:
        """WHOIS analysis"""
        api_key = self.api_manager.get_api_key('whois_xml')
        url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService"
        
        params = {
            'apiKey': api_key,
            'domainName': domain,
            'outputFormat': 'JSON'
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _builtwith_analysis(self, domain: str) -> Dict[str, Any]:
        """BuiltWith analysis"""
        api_key = self.api_manager.get_api_key('builtwith')
        url = f"https://api.builtwith.com/v21/api.json"
        
        params = {
            'KEY': api_key,
            'LOOKUP': domain
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _virustotal_domain_analysis(self, domain: str) -> Dict[str, Any]:
        """VirusTotal domain analysis"""
        api_key = self.api_manager.get_api_key('virus_total')
        url = f"https://www.virustotal.com/vtapi/v2/domain/report"
        
        params = {
            'apikey': api_key,
            'domain': domain
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _hunter_email_analysis(self, email: str) -> Dict[str, Any]:
        """Hunter.io email analysis"""
        api_key = self.api_manager.get_api_key('hunter')
        url = f"https://api.hunter.io/v2/email-verifier"
        
        params = {
            'email': email,
            'api_key': api_key
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _numverify_analysis(self, phone: str, country_code: str) -> Dict[str, Any]:
        """Numverify phone analysis"""
        api_key = self.api_manager.get_api_key('numverify')
        url = f"http://apilayer.net/api/validate"
        
        params = {
            'access_key': api_key,
            'number': phone,
            'country_code': country_code
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _breadcrumbs_address_risk(self, address: str, chain: str) -> Dict[str, Any]:
        """Breadcrumbs address risk analysis"""
        url = "https://api.breadcrumbs.app/v1/address-risk"
        data = [{
            'address': address,
            'chain': chain,
            'include_exposure': True
        }]
        
        async with self.session.post(url, json=data) as response:
            return await response.json()

    async def _breadcrumbs_sanctions_check(self, address: str, chain: str) -> Dict[str, Any]:
        """Breadcrumbs sanctions check"""
        url = "https://api.breadcrumbs.app/v1/sanctions"
        data = [{'address': address, 'chain': chain}]
        
        async with self.session.post(url, json=data) as response:
            return await response.json()

    async def _breadcrumbs_node_analysis(self, address: str, chain: str) -> Dict[str, Any]:
        """Breadcrumbs node analysis"""
        url = "https://api.breadcrumbs.app/v1/node"
        data = [{'address': address, 'chain': chain}]
        
        async with self.session.post(url, json=data) as response:
            return await response.json()

    async def _news_api_search(self, query: str, from_date: str) -> List[Dict[str, Any]]:
        """News API search"""
        api_key = self.api_manager.get_api_key('news_api')
        url = f"https://newsapi.org/v2/everything"
        
        params = {
            'q': query,
            'apiKey': api_key,
            'from': from_date,
            'language': 'en',
            'sortBy': 'publishedAt'
        }
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('articles', [])

    async def _aviationstack_analysis(self, flight_number: str = None) -> Dict[str, Any]:
        """Aviationstack flight analysis"""
        api_key = self.api_manager.get_api_key('aviationstack')
        url = f"http://api.aviationstack.com/v1/flights"
        
        params = {'access_key': api_key}
        if flight_number:
            params['flight_iata'] = flight_number
        
        async with self.session.get(url, params=params) as response:
            return await response.json()

    def _calculate_risk_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall risk score based on all analyses"""
        risk_factors = []
        
        # VirusTotal risk
        if 'virus_total' in analysis and analysis['virus_total'].get('positives', 0) > 0:
            risk_factors.append('virus_total_detection')
        
        # AbuseIPDB risk
        if 'abuse_ip_db' in analysis and analysis['abuse_ip_db'].get('data', {}).get('abuseConfidencePercentage', 0) > 50:
            risk_factors.append('abuse_reports')
        
        # Bot detection
        if 'bot_detection' in analysis and analysis['bot_detection'].get('is_bot'):
            risk_factors.append('bot_detected')
        
        # Fraud detection
        if 'fraud_detection' in analysis and analysis['fraud_detection'].get('risk_level') == 'high':
            risk_factors.append('fraud_risk')
        
        # Calculate risk level
        risk_count = len(risk_factors)
        if risk_count >= 3:
            risk_level = 'HIGH'
        elif risk_count >= 1:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'risk_count': risk_count,
            'assessment_timestamp': datetime.now().isoformat()
        }

# Usage Example and Testing Function
async def run_comprehensive_analysis():
    """Example usage of the comprehensive OSINT service"""
    
    async with ComprehensiveOSINTService() as osint:
        # Test IP analysis
        print("🔍 Running comprehensive IP analysis...")
        ip_result = await osint.analyze_ip_comprehensive("8.8.8.8")
        print(f"IP Analysis Result: {json.dumps(ip_result, indent=2)}")
        
        # Test domain analysis
        print("\n🌐 Running domain analysis...")
        domain_result = await osint.analyze_domain_comprehensive("google.com")
        print(f"Domain Analysis Result: {json.dumps(domain_result, indent=2)}")
        
        # Test news intelligence
        print("\n📰 Running news intelligence...")
        news_result = await osint.search_news_intelligence("cybersecurity threat", 3)
        print(f"News Intelligence Result: {json.dumps(news_result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_analysis())
