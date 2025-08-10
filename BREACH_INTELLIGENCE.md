# 🔐 Breach Intelligence Service

## Privacy-Compliant Alternative to Paid HIBP APIs

A comprehensive breach monitoring and intelligence platform that provides ethical dark web monitoring, paste site scraping, and k-anonymity credential checking without relying on paid third-party services.

## 🌟 Key Features

### 🛡️ Privacy-by-Design Architecture

- **K-Anonymity Protection**: Credential checking using hash prefixes with minimum 1000-record anonymity sets
- **GDPR/CCPA Compliant**: Minimal data retention with automatic cleanup
- **Hash-Based Storage**: No plaintext credentials stored in database
- **Differential Privacy**: Statistical noise added to prevent data correlation

### 🕸️ Ethical OSINT Monitoring

- **Paste Site Monitoring**: Ethical scraping of Pastebin, GitHub Gists, Slexy with robots.txt compliance
- **Dark Web Monitoring**: Tor-based monitoring of breach disclosure forums (not illegal marketplaces)
- **Rate Limiting**: Respectful crawling with appropriate delays
- **Source Attribution**: Proper crediting of data sources

### 🔍 Intelligence Enrichment

- **SpiderFoot Integration**: Automated IOC extraction and correlation
- **Maltego Integration**: Visual threat actor attribution and network analysis
- **Threat Actor Profiling**: Behavioral analysis and attribution scoring
- **IOC Extraction**: Automatic extraction of IPs, domains, hashes from breach data

### 📊 Comprehensive Analytics

- **Breach Impact Assessment**: Risk scoring based on data types and exposure
- **Temporal Analysis**: Breach timeline and trend analysis
- **Geographic Mapping**: Location-based breach intelligence
- **Sector Analysis**: Industry-specific breach patterns

## 🚀 Quick Start

### 1. Start the API Server

```bash
python start_breach_api.py
```

### 2. Test the API

```bash
python test_breach_api.py
```

### 3. Access API Documentation

Open your browser to: <http://localhost:8000/docs>

## 📋 API Endpoints

### Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer compliant-your-api-key
```

### Core Endpoints

#### 🔍 Credential Breach Check (K-Anonymity)

```http
POST /api/v1/breach-intel/check-credential
Content-Type: application/json

{
    "credential": "user@example.com",
    "type": "email"
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "credential_hash_prefix": "a665a4",
        "breach_found": false,
        "k_anonymity_set_size": 1247,
        "privacy_compliant": true,
        "last_checked": "2024-12-19T10:30:00Z"
    },
    "message": "Credential breach check completed (privacy-compliant)"
}
```

#### 📡 Add Monitoring Target

```http
POST /api/v1/breach-intel/add-monitoring
Content-Type: application/json

{
    "credential": "user@example.com",
    "type": "email",
    "alert_email": "alerts@company.com"
}
```

#### 📰 Start Paste Site Monitoring

```http
POST /api/v1/breach-intel/monitor-paste-sites
```

Monitors:

- Pastebin (respects robots.txt)
- GitHub Gists
- Slexy
- Justpaste.it
- Dpaste

#### 🕸️ Start Dark Web Monitoring

```http
POST /api/v1/breach-intel/monitor-darkweb
```

Ethical monitoring of:

- Breach disclosure forums
- Security researcher communities
- Public vulnerability databases
- **Note**: Does NOT monitor illegal marketplaces

#### 📈 Get Statistics

```http
GET /api/v1/breach-intel/statistics
```

**Response:**

```json
{
    "success": true,
    "data": {
        "total_breaches": 1247,
        "monitored_credentials": 523,
        "paste_sites_monitored": 5,
        "darkweb_sources": 12,
        "privacy_compliant": true,
        "last_cleanup": "2024-12-19T06:00:00Z"
    }
}
```

#### 🧹 Privacy Compliance Cleanup

```http
POST /api/v1/breach-intel/cleanup-expired
```

Automatically removes:

- Expired breach data (90-day retention)
- Orphaned hash records
- Temporary monitoring data

## 🔧 Technical Architecture

### Database Schema (Privacy-Compliant)

```sql
-- Breach records with minimal data retention
CREATE TABLE breach_records (
    id UUID PRIMARY KEY,
    breach_hash VARCHAR(64) NOT NULL,  -- SHA-256 of breach identifier
    data_types TEXT[],                 -- Types of data exposed
    breach_date TIMESTAMP,
    severity_score INTEGER,
    source_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '90 days'
);

-- Monitoring targets (hash-based)
CREATE TABLE monitoring_targets (
    id UUID PRIMARY KEY,
    credential_hash_prefix VARCHAR(10),  -- First 10 chars of hash
    credential_type VARCHAR(20),
    alert_config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_checked TIMESTAMP
);

-- K-Anonymity sets for privacy protection
CREATE TABLE k_anonymity_sets (
    hash_prefix VARCHAR(10) PRIMARY KEY,
    set_size INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

### Privacy Protection Mechanisms

#### K-Anonymity Implementation

```python
async def check_credential_breach(self, credential: str, credential_type: str):
    """Check credential using k-anonymity protection"""
    
    # 1. Hash the credential
    credential_hash = hashlib.sha256(credential.encode()).hexdigest()
    hash_prefix = credential_hash[:10]  # Use 10-char prefix
    
    # 2. Ensure k-anonymity set size >= 1000
    anonymity_set = await self.get_k_anonymity_set(hash_prefix)
    if anonymity_set['size'] < 1000:
        return {
            'privacy_compliant': False,
            'message': 'Insufficient anonymity set size'
        }
    
    # 3. Check breaches for entire anonymity set
    # Only return aggregated statistics, not individual matches
    breach_stats = await self.check_anonymity_set_breaches(hash_prefix)
    
    return {
        'credential_hash_prefix': hash_prefix,
        'k_anonymity_set_size': anonymity_set['size'],
        'breach_probability': breach_stats['probability'],
        'privacy_compliant': True
    }
```

## 🔒 Security & Compliance

### GDPR/CCPA Compliance

- **Data Minimization**: Only collect necessary breach metadata
- **Purpose Limitation**: Data used only for breach intelligence
- **Storage Limitation**: 90-day automatic data retention
- **Right to Erasure**: Immediate data deletion on request
- **Privacy by Design**: Hash-based architecture prevents data exposure

### Ethical Monitoring Guidelines

- **Robots.txt Compliance**: Respect website crawling policies
- **Rate Limiting**: Non-aggressive crawling (max 1 req/10 seconds)
- **Legal Boundaries**: No monitoring of illegal marketplaces
- **Source Attribution**: Proper crediting of breach disclosure sources
- **Responsible Disclosure**: Report vulnerabilities to affected parties

### Security Measures

- **TLS Encryption**: All API communications encrypted
- **API Key Authentication**: Secure token-based access
- **Input Validation**: Comprehensive sanitization
- **Audit Logging**: Complete activity tracking
- **Access Controls**: Role-based permissions

## 🛠️ Integration Examples

### Python Client

```python

```

import httpx

class BreachIntelClient:
    def **init**(self, api_key: str, base_url: str = "<http://localhost:8000>"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def check_credential(self, credential: str, credential_type: str = "email"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/breach-intel/check-credential",
                headers=self.headers,
                json={"credential": credential, "type": credential_type}
            )
            return response.json()

## Usage

client = BreachIntelClient("compliant-your-api-key")
result = await client.check_credential("<user@example.com>")

```

### JavaScript Client
```javascript
class BreachIntelClient {
    constructor(apiKey, baseUrl = 'http://localhost:8000') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async checkCredential(credential, type = 'email') {
        const response = await fetch(`${this.baseUrl}/api/v1/breach-intel/check-credential`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ credential, type })
        });
        return response.json();
    }
}

// Usage
const client = new BreachIntelClient('compliant-your-api-key');
const result = await client.checkCredential('user@example.com');
```

## 📊 Monitoring Dashboard

### Key Metrics

- **Breach Detection Rate**: Number of new breaches detected per day
- **False Positive Rate**: Accuracy of breach detection algorithms
- **Privacy Compliance Score**: GDPR/CCPA adherence metrics
- **API Response Times**: Performance monitoring
- **Data Retention Compliance**: Automatic cleanup effectiveness

### Alerting

- **Real-time Notifications**: Immediate alerts for monitored credentials
- **Weekly Summaries**: Comprehensive breach intelligence reports
- **Compliance Reports**: Privacy regulation adherence summaries
- **Performance Alerts**: API health and response time monitoring

## 🔄 Continuous Improvement

### Machine Learning Enhancement

- **Breach Pattern Recognition**: ML models for improved detection
- **False Positive Reduction**: Continuous algorithm refinement
- **Threat Actor Attribution**: Behavioral analysis improvements
- **Predictive Analytics**: Forecast breach trends and risks

### Community Integration

- **Threat Intelligence Sharing**: Responsible disclosure to security community
- **Open Source Contributions**: Share privacy-preserving techniques
- **Research Collaboration**: Academic partnerships for advancement
- **Industry Standards**: Contribute to breach intelligence standards

## 📞 Support & Contributing

### Getting Help

- **Documentation**: Comprehensive API documentation at `/docs`
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Community**: Join our security research community discussions

### Contributing

- **Code Contributions**: Follow our secure coding guidelines
- **Privacy Reviews**: Help improve privacy protection mechanisms
- **Ethical Guidelines**: Contribute to responsible disclosure policies
- **Testing**: Help expand our privacy-compliant testing suite

## 📄 License & Legal

### Privacy Compliance

This system is designed to comply with:

- **GDPR** (General Data Protection Regulation)
- **CCPA** (California Consumer Privacy Act)
- **SOX** (Sarbanes-Oxley Act)
- **HIPAA** (Health Insurance Portability and Accountability Act)

### Ethical Use

This platform is intended for:

- ✅ Legitimate security research
- ✅ Corporate security monitoring
- ✅ Privacy-compliant breach detection
- ✅ Responsible vulnerability disclosure

**NOT intended for:**

- ❌ Illegal data acquisition
- ❌ Privacy violations
- ❌ Unauthorized access attempts
- ❌ Criminal marketplace monitoring

### Disclaimer

This tool is provided for legitimate security research and corporate protection purposes only. Users are responsible for ensuring compliance with applicable laws and regulations in their jurisdiction.

---

**🔐 Built with Privacy-by-Design Architecture**  
**⚖️ GDPR/CCPA Compliant**  
**🛡️ Ethical OSINT Focused**  
**🔬 Research-Grade Security Intelligence**
