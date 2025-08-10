# Threat Intelligence System - Production Setup Guide

## Overview

The Threat Intelligence System provides comprehensive monitoring and analysis using legitimate security data sources including Have I Been Pwned, VirusTotal, Shodan, and various threat feeds.

## Required API Keys

### 1. Have I Been Pwned (HIBP)

- **Purpose**: Check for email addresses in data breaches
- **Get API Key**: <https://haveibeenpwned.com/API/Key>
- **Cost**: $3.50/month for up to 10,000 queries
- **Rate Limit**: 1 request per 1.5 seconds
- **Configuration**: Set `HIBP_API_KEY` in .env file

### 2. VirusTotal

- **Purpose**: Check files, URLs, IPs, and domains for malware
- **Get API Key**: <https://www.virustotal.com/gui/my-apikey>
- **Free Tier**: 4 requests/minute, 500 requests/day
- **Premium**: Higher rate limits and additional features
- **Configuration**: Set `VIRUSTOTAL_API_KEY` in .env file

### 3. Shodan

- **Purpose**: Check IP addresses for exposed services and vulnerabilities
- **Get API Key**: <https://account.shodan.io/>
- **Free Tier**: Limited queries
- **Paid Plans**: Start at $59/month for more queries
- **Configuration**: Set `SHODAN_API_KEY` in .env file

### 4. Optional Sources

#### AlienVault OTX (Open Threat Exchange)

- **Purpose**: Additional threat intelligence feeds
- **Get API Key**: <https://otx.alienvault.com/settings>
- **Cost**: Free
- **Configuration**: Set `OTX_API_KEY` in .env file

#### GreyNoise

- **Purpose**: Internet background noise analysis
- **Get API Key**: <https://viz.greynoise.io/account/api-key>
- **Free Tier**: 10,000 queries/month
- **Configuration**: Set `GREYNOISE_API_KEY` in .env file

## Quick Setup

1. **Copy Environment File**:

   ```bash
   cp .env.example .env
   ```

2. **Configure API Keys** in `.env` file:

   ```bash
   HIBP_API_KEY=your_actual_hibp_api_key
   VIRUSTOTAL_API_KEY=your_actual_virustotal_api_key
   SHODAN_API_KEY=your_actual_shodan_api_key
   ```

3. **Start the Service**:

   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

4. **Access Admin Panel**:
   - Navigate to `http://localhost:8000/threat-intel/admin`
   - Configure sources and monitoring targets

## Production Configuration

### Database Setup

The system uses SQLite by default for simplicity. For production:

```bash
# Create data directory
mkdir -p ./data

# Database will be created automatically at:
./data/threat_intelligence.db
```

### Logging Configuration

```bash
# Create logs directory
mkdir -p ./logs

# Set log level in .env
LOG_LEVEL=INFO
LOG_FILE=./logs/threat_intelligence.log
```

### Security Configuration

```bash
# Generate secure secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Add to .env file
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

## API Endpoints

### Authentication

All endpoints require authentication. Use the `/auth/login` endpoint to get a token.

### Core Endpoints

#### Collect Threat Intelligence

```bash
POST /api/v1/threat-intel/collect
```

#### Check Have I Been Pwned

```bash
POST /api/v1/threat-intel/hibp/check
Content-Type: application/json

{
  "emails": ["test@example.com", "user@domain.com"]
}
```

#### Check VirusTotal

```bash
POST /api/v1/threat-intel/virustotal/check
Content-Type: application/json

{
  "indicators": ["malicious.com", "192.168.1.1", "hash123..."]
}
```

#### Check Shodan

```bash
POST /api/v1/threat-intel/shodan/check
Content-Type: application/json

{
  "ips": ["8.8.8.8", "1.1.1.1"]
}
```

#### Comprehensive Check

```bash
POST /api/v1/threat-intel/comprehensive-check
Content-Type: application/json

{
  "emails": ["test@example.com"],
  "indicators": ["malicious.com"],
  "ips": ["8.8.8.8"],
  "collect_feeds": true
}
```

### Monitoring Endpoints

#### Add Monitoring Target

```bash
POST /api/v1/threat-intel/targets
Content-Type: application/json

{
  "target_type": "domain",
  "target_value": "yourcompany.com",
  "alert_threshold": 0.7
}
```

#### Get Alerts

```bash
GET /api/v1/threat-intel/alerts?status=active&severity=high
```

## Admin Panel Features

Access the admin panel at `http://localhost:8000/threat-intel/admin` for:

- **Dashboard**: Real-time statistics and threat overview
- **Source Management**: Configure and test threat intelligence sources
- **Target Monitoring**: Set up monitoring for domains, IPs, emails
- **Alert Management**: View and manage security alerts
- **Data Export**: Export threat data for analysis

## Rate Limiting

The system respects API rate limits:

- **HIBP**: 1 request per 1.5 seconds
- **VirusTotal**: 4 requests per minute (free tier)
- **Shodan**: 1 request per second

Configure delays in `.env`:

```bash
HIBP_RATE_LIMIT_DELAY=1.5
VIRUSTOTAL_RATE_LIMIT_DELAY=15
SHODAN_RATE_LIMIT_DELAY=1
```

## Threat Feeds

The system automatically collects from these free sources:

- **Abuse.ch**: Malware and botnet indicators
- **Cybercrime Tracker**: Active cybercrime infrastructure
- **Emerging Threats**: Known malicious IPs
- **Spamhaus**: Spam and malware sources
- **Malware Domain List**: Malicious domains

Feeds update every hour by default. Configure in `.env`:

```bash
THREAT_FEED_UPDATE_INTERVAL=3600
```

## Monitoring Setup

### Email Alerts

Configure email notifications for high-priority threats:

```bash
THREAT_ALERT_EMAIL_ENABLED=true
THREAT_ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
THREAT_ALERT_EMAIL_SMTP_PORT=587
THREAT_ALERT_EMAIL_USERNAME=your_email@gmail.com
THREAT_ALERT_EMAIL_PASSWORD=your_app_password
THREAT_ALERT_EMAIL_FROM=alerts@yourcompany.com
THREAT_ALERT_EMAIL_TO=security@yourcompany.com
```

### Continuous Monitoring

```bash
THREAT_MONITORING_ENABLED=true
THREAT_MONITORING_INTERVAL=300  # Check every 5 minutes
```

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify keys are correctly set in `.env`
   - Check key validity on provider websites
   - Ensure sufficient quota/credits

2. **Rate Limit Exceeded**:
   - Increase delay settings in `.env`
   - Consider upgrading to paid API tiers

3. **Database Issues**:
   - Ensure `./data` directory exists and is writable
   - Check disk space for database growth

4. **Network Issues**:
   - Verify outbound internet connectivity
   - Check firewall rules for API endpoints

### Support

For issues or questions:

- Check logs in `./logs/threat_intelligence.log`
- Review API responses in debug mode
- Consult provider documentation for API-specific issues

## Compliance Notes

This system:

- Uses only legitimate, publicly available threat intelligence sources
- Respects all API terms of service and rate limits
- Does not access or interact with illegal content
- Maintains audit logs of all activities
- Provides data export for compliance reporting

The system is designed to help organizations:

- Monitor their digital assets for security threats
- Detect compromised credentials or systems
- Maintain situational awareness of cyber threats
- Meet regulatory requirements for threat monitoring
