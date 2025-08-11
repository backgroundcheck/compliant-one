"""
SECURE API CONFIGURATION FOR COMPLIANT-ONE
Environment-Based API Key Management
"""

import os
from typing import Dict, Any, Optional

class SecureAPIConfiguration:
    """Secure API configuration using environment variables"""
    
    def __init__(self):
        self.api_keys = self._load_from_environment()
        self.endpoints = self._get_api_endpoints()
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load API keys from environment variables"""
        return {
            # Search & Intelligence
            'builtwith': os.getenv('BUILTWITH_API_KEY'),
            'shodan': os.getenv('SHODAN_API_KEY'),
            'censys': {
                'api_id': os.getenv('CENSYS_API_ID'),
                'secret': os.getenv('CENSYS_SECRET')
            },
            
            # Threat Intelligence
            'virus_total': os.getenv('VIRUSTOTAL_API_KEY'),
            'otx': os.getenv('OTX_API_KEY'),
            'ibm_xforce': {
                'key': os.getenv('IBM_XFORCE_KEY'),
                'password': os.getenv('IBM_XFORCE_PASSWORD')
            },
            'abuse_ip_db': os.getenv('ABUSEIPDB_API_KEY'),
            
            # OSINT & Investigation
            'hunter': os.getenv('HUNTER_API_KEY'),
            'ip_info': os.getenv('IPINFO_API_KEY'),
            'whois_xml': os.getenv('WHOISXML_API_KEY'),
            'numverify': os.getenv('NUMVERIFY_API_KEY'),
            'botscout': os.getenv('BOTSCOUT_API_KEY'),
            'project_honeypot': os.getenv('PROJECTHONEYPOT_API_KEY'),
            
            # Social Media & News
            'twitter': {
                'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
                'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
                'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            },
            'news_api': os.getenv('NEWSAPI_KEY'),
            'linkedin': {
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            },
            
            # Blockchain Analysis
            'breadcrumbs': {
                'api_key': os.getenv('BREADCRUMBS_API_KEY'),
                'enabled': True
            },
            
            # Additional OSINT Services
            'flickr': {
                'key': os.getenv('FLICKR_API_KEY'),
                'secret': os.getenv('FLICKR_SECRET')
            },
            'fraudguard': {
                'username': os.getenv('FRAUDGUARD_USERNAME'),
                'password': os.getenv('FRAUDGUARD_PASSWORD')
            },
            'google_custom_search': {
                'cx': os.getenv('GOOGLE_CUSTOM_SEARCH_CX'),
                'api_key': os.getenv('GOOGLE_API_KEY')
            },
            
            # AI & Analysis
            'huggingface': os.getenv('HUGGINGFACE_TOKEN'),
            'tavily': os.getenv('TAVILY_API_KEY'),
            
            # Maps & Location
            'google_maps': os.getenv('GOOGLE_MAPS_API_KEY'),
            
            # Additional Services
            'aviationstack': os.getenv('AVIATIONSTACK_API_KEY'),
            'firecrawl': os.getenv('FIRECRAWL_API_KEY'),
            'pastebin': os.getenv('PASTEBIN_API_KEY')
        }
    
    def _get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoints configuration"""
        return {
            'builtwith': 'https://api.builtwith.com/v21/api.json',
            'shodan': 'https://api.shodan.io',
            'censys': 'https://search.censys.io/api/v2',
            'virus_total': 'https://www.virustotal.com/vtapi/v2',
            'otx': 'https://otx.alienvault.com/api/v1',
            'ibm_xforce': 'https://api.xforce.ibmcloud.com',
            'abuse_ip_db': 'https://api.abuseipdb.com/api/v2',
            'hunter': 'https://api.hunter.io/v2',
            'ip_info': 'https://ipinfo.io',
            'whois_xml': 'https://www.whoisxmlapi.com/whoisserver/WhoisService',
            'twitter': 'https://api.twitter.com/2',
            'news_api': 'https://newsapi.org/v2',
            'huggingface': 'https://api-inference.huggingface.co',
            'tavily': 'https://api.tavily.com',
            'flickr': 'https://api.flickr.com/services/rest/',
            'linkedin': 'https://api.linkedin.com/v2',
            'numverify': 'http://apilayer.net/api/validate',
            'botscout': 'http://botscout.com/test/',
            'project_honeypot': 'http://www.projecthoneypot.org/api/',
            'fraudguard': 'https://api.fraudguard.io/v2',
            'aviationstack': 'http://api.aviationstack.com/v1',
            'firecrawl': 'https://api.firecrawl.dev/v1',
            'pastebin': 'https://pastebin.com/api',
            'breadcrumbs': {
                'pathfinder': 'https://api.breadcrumbs.app/v1/pathfinder',
                'address_risk': 'https://api.breadcrumbs.app/v1/address-risk',
                'transaction_risk': 'https://api.breadcrumbs.app/v1/transaction-risk',
                'node': 'https://api.breadcrumbs.app/v1/node',
                'sanctions': 'https://api.breadcrumbs.app/v1/sanctions'
            },
            'kev_rss_feed': 'https://kevin.gtfkd.com/rss'
        }
    
    def get_api_key(self, service: str) -> Optional[Any]:
        """Get API key for a specific service"""
        return self.api_keys.get(service)
    
    def get_endpoint(self, service: str) -> Optional[str]:
        """Get endpoint for a specific service"""
        return self.endpoints.get(service)
    
    def is_service_available(self, service: str) -> bool:
        """Check if a service is available (has API key)"""
        key = self.get_api_key(service)
        if isinstance(key, dict):
            return any(v for v in key.values() if v)
        return key is not None and key != ''
    
    def get_available_services(self) -> list:
        """Get list of all available services"""
        return [service for service in self.api_keys.keys() if self.is_service_available(service)]

# Create environment template
def create_env_template() -> str:
    """Create .env template with all required environment variables"""
    template = """# OSINT and Threat Intelligence API Configuration
# Copy this file to .env and fill in your actual API keys

# Search & Intelligence APIs
BUILTWITH_API_KEY=your_builtwith_api_key_here
SHODAN_API_KEY=your_shodan_api_key_here
CENSYS_API_ID=your_censys_api_id_here
CENSYS_SECRET=your_censys_secret_here

# Threat Intelligence APIs
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
OTX_API_KEY=your_otx_api_key_here
IBM_XFORCE_KEY=your_ibm_xforce_key_here
IBM_XFORCE_PASSWORD=your_ibm_xforce_password_here
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here

# OSINT & Investigation APIs
HUNTER_API_KEY=your_hunter_api_key_here
IPINFO_API_KEY=your_ipinfo_api_key_here
WHOISXML_API_KEY=your_whoisxml_api_key_here
NUMVERIFY_API_KEY=your_numverify_api_key_here
BOTSCOUT_API_KEY=your_botscout_api_key_here
PROJECTHONEYPOT_API_KEY=your_projecthoneypot_api_key_here

# Social Media & News APIs
TWITTER_CONSUMER_KEY=your_twitter_consumer_key_here
TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
NEWSAPI_KEY=your_newsapi_key_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here

# Blockchain Analysis APIs
BREADCRUMBS_API_KEY=your_breadcrumbs_api_key_here

# Additional OSINT Services
FLICKR_API_KEY=your_flickr_api_key_here
FLICKR_SECRET=your_flickr_secret_here
FRAUDGUARD_USERNAME=your_fraudguard_username_here
FRAUDGUARD_PASSWORD=your_fraudguard_password_here
GOOGLE_CUSTOM_SEARCH_CX=your_google_custom_search_cx_here
GOOGLE_API_KEY=your_google_api_key_here

# AI & Analysis APIs
HUGGINGFACE_TOKEN=your_huggingface_token_here
TAVILY_API_KEY=your_tavily_api_key_here

# Maps & Location APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Additional Services
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
PASTEBIN_API_KEY=your_pastebin_api_key_here
"""
    return template

# Usage
if __name__ == "__main__":
    # Create .env template
    with open('.env.template', 'w') as f:
        f.write(create_env_template())
    print("Created .env.template file. Copy to .env and fill in your API keys.")
    
    # Test configuration
    config = SecureAPIConfiguration()
    print(f"Available services: {len(config.get_available_services())}")
    for service in config.get_available_services():
        print(f"✅ {service} - Available")
