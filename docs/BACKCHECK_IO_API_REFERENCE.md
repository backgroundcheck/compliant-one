# Backcheck.io API Reference Guide

## API Overview

The Backcheck.io API provides comprehensive RegTech services through RESTful endpoints, enabling seamless integration with banking systems, compliance tools, and third-party applications.

**Base URL**: `https://api.backcheck.io/v1`  
**Authentication**: API Key or OAuth 2.0  
**Content Type**: `application/json`  
**Rate Limiting**: 1000 requests/minute per API key

## Authentication

### API Key Authentication

```bash
curl -H "Authorization: Bearer compliant-your-api-key" \
     -H "Content-Type: application/json" \
     https://api.backcheck.io/v1/sanctions/screen
```

### OAuth 2.0 Authentication

```bash
# Get access token
curl -X POST https://api.backcheck.io/oauth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Use access token
curl -H "Authorization: Bearer ACCESS_TOKEN" \
     https://api.backcheck.io/v1/kyc/verify
```

## Core Compliance Endpoints

### 1. Sanctions Screening

**Endpoint**: `POST /api/v1/sanctions/screen`

**Description**: Screen individuals and entities against global sanctions lists including OFAC, EU, UN, and custom watchlists.

**Request Body**:
```json
{
  "entity_name": "John Doe",
  "entity_type": "person",
  "date_of_birth": "1980-01-01",
  "nationality": "US",
  "additional_identifiers": {
    "passport_number": "123456789",
    "national_id": "987654321"
  },
  "threshold": 0.8
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "screening_id": "SCR_001",
    "entity_name": "John Doe",
    "matches": [
      {
        "list_name": "OFAC_SDN",
        "match_name": "John DOE",
        "match_score": 0.95,
        "match_type": "exact",
        "list_entry_id": "12345",
        "sanctions_details": {
          "program": "UKRAINE-EO13662",
          "date_added": "2022-02-26",
          "sanctions_type": "blocking"
        }
      }
    ],
    "overall_risk_score": 0.95,
    "recommendation": "BLOCK",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### 2. KYC Verification

**Endpoint**: `POST /api/v1/kyc/verify`

**Description**: Perform comprehensive Know Your Customer verification with risk-based assessment.

**Request Body**:
```json
{
  "customer_id": "CUST_001",
  "verification_level": "enhanced",
  "customer_data": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-01",
    "nationality": "US",
    "address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "US"
    }
  },
  "documents": [
    {
      "document_type": "passport",
      "document_number": "123456789",
      "expiry_date": "2030-01-01",
      "issuing_country": "US"
    }
  ],
  "risk_appetite": "medium"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "verification_id": "KYC_001",
    "customer_id": "CUST_001",
    "verification_status": "VERIFIED",
    "risk_category": "MEDIUM",
    "risk_score": 0.45,
    "verification_results": {
      "identity_verification": {
        "status": "PASS",
        "confidence": 0.98,
        "methods_used": ["document_verification", "biometric_match"]
      },
      "address_verification": {
        "status": "PASS",
        "confidence": 0.92,
        "verification_method": "utility_bill_match"
      },
      "sanctions_screening": {
        "status": "CLEAR",
        "matches_found": 0
      },
      "pep_screening": {
        "status": "CLEAR",
        "pep_matches": 0
      }
    },
    "recommendations": [
      "Proceed with standard monitoring",
      "Review annually"
    ],
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### 3. OSINT Intelligence Search

**Endpoint**: `POST /api/v1/osint/search`

**Description**: Perform open-source intelligence gathering and analysis.

**Request Body**:
```json
{
  "entity_name": "ABC Corporation",
  "entity_type": "organization",
  "search_depth": "comprehensive",
  "sources": ["news", "social_media", "corporate_records", "government_data"],
  "max_results": 100,
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2025-01-15"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "search_id": "OSINT_001",
    "entity_name": "ABC Corporation",
    "search_summary": {
      "total_results": 87,
      "sources_searched": 12,
      "risk_indicators_found": 3,
      "overall_sentiment": "NEUTRAL"
    },
    "risk_assessment": {
      "overall_risk_score": 0.35,
      "risk_level": "MEDIUM",
      "risk_factors": [
        "Regulatory investigation mentioned",
        "Leadership changes",
        "Financial performance concerns"
      ]
    },
    "intelligence_summary": {
      "news_articles": 45,
      "social_media_mentions": 23,
      "regulatory_filings": 12,
      "corporate_announcements": 7
    },
    "adverse_media": [
      {
        "title": "ABC Corp Under Regulatory Investigation",
        "source": "Financial Times",
        "date": "2024-12-15",
        "sentiment": "NEGATIVE",
        "relevance_score": 0.89,
        "summary": "Regulatory authorities investigating potential compliance violations..."
      }
    ],
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### 4. Beneficial Ownership Analysis

**Endpoint**: `POST /api/v1/beneficial-ownership/analyze`

**Description**: Analyze corporate structures to identify Ultimate Beneficial Owners (UBOs).

**Request Body**:
```json
{
  "entity_id": "CORP_001",
  "entity_name": "ABC Holdings Ltd",
  "jurisdiction": "BVI",
  "analysis_depth": "comprehensive",
  "ownership_threshold": 0.25,
  "include_nominees": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "UBO_001",
    "entity_name": "ABC Holdings Ltd",
    "ownership_structure": {
      "total_layers": 4,
      "complexity_score": 0.78,
      "jurisdiction_count": 3,
      "nominee_arrangements": 2
    },
    "ultimate_beneficial_owners": [
      {
        "name": "John Smith",
        "ownership_percentage": 45.5,
        "control_type": "direct_ownership",
        "verification_status": "VERIFIED",
        "risk_indicators": [],
        "pep_status": false,
        "sanctions_status": "CLEAR"
      },
      {
        "name": "Jane Doe",
        "ownership_percentage": 30.0,
        "control_type": "indirect_ownership",
        "ownership_path": [
          "ABC Holdings Ltd -> XYZ Trust -> Jane Doe"
        ],
        "verification_status": "PENDING",
        "risk_indicators": ["High-risk jurisdiction"],
        "pep_status": true,
        "sanctions_status": "CLEAR"
      }
    ],
    "risk_assessment": {
      "overall_risk_score": 0.65,
      "risk_level": "HIGH",
      "risk_factors": [
        "Complex ownership structure",
        "Multiple jurisdictions",
        "PEP involvement",
        "Nominee arrangements"
      ]
    },
    "recommendations": [
      "Enhanced due diligence required",
      "Verify nominee arrangements",
      "Monitor PEP status changes"
    ],
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### 5. Comprehensive Compliance Check

**Endpoint**: `POST /api/v1/compliance/check`

**Description**: Perform comprehensive compliance assessment across all FATF recommendations.

**Request Body**:
```json
{
  "customer_id": "CUST_001",
  "customer_data": {
    "name": "John Doe",
    "customer_type": "INDIVIDUAL",
    "jurisdiction": "US",
    "risk_category": "MEDIUM"
  },
  "check_types": [
    "sanctions_screening",
    "pep_screening",
    "kyc_verification",
    "beneficial_ownership",
    "adverse_media",
    "transaction_monitoring"
  ],
  "fatf_recommendations": ["R10", "R12", "R15", "R16"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "compliance_id": "COMP_001",
    "customer_id": "CUST_001",
    "overall_compliance_score": 0.87,
    "overall_risk_level": "MEDIUM",
    "fatf_compliance": {
      "R10": {
        "status": "PASS",
        "score": 0.92,
        "service": "kyc",
        "details": "Customer due diligence completed successfully"
      },
      "R12": {
        "status": "PASS",
        "score": 0.88,
        "service": "sanctions",
        "details": "PEP screening completed, no matches found"
      },
      "R15": {
        "status": "WARNING",
        "score": 0.75,
        "service": "osint",
        "details": "Minor adverse media detected"
      },
      "R16": {
        "status": "PASS",
        "score": 0.95,
        "service": "beneficial_ownership",
        "details": "Wire transfer compliance verified"
      }
    },
    "service_results": {
      "sanctions_screening": {
        "status": "CLEAR",
        "matches": 0,
        "risk_score": 0.05
      },
      "pep_screening": {
        "status": "CLEAR",
        "matches": 0,
        "risk_score": 0.02
      },
      "adverse_media": {
        "status": "MINOR_CONCERNS",
        "articles_found": 2,
        "risk_score": 0.35
      }
    },
    "recommendations": [
      "Continue standard monitoring",
      "Review adverse media findings",
      "Schedule annual review"
    ],
    "next_review_date": "2026-01-15",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Transaction Monitoring Endpoints

### 6. Transaction Screening

**Endpoint**: `POST /api/v1/transactions/screen`

**Description**: Screen transactions for suspicious activity and compliance violations.

**Request Body**:
```json
{
  "transaction_id": "TXN_001",
  "customer_id": "CUST_001",
  "transaction_data": {
    "amount": 50000.00,
    "currency": "USD",
    "transaction_type": "wire_transfer",
    "counterparty": {
      "name": "XYZ Corp",
      "account_number": "123456789",
      "bank": "ABC Bank",
      "country": "US"
    },
    "purpose": "Business payment",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "monitoring_rules": ["threshold", "velocity", "geographic", "counterparty"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "screening_id": "TXN_SCR_001",
    "transaction_id": "TXN_001",
    "risk_score": 0.45,
    "risk_level": "MEDIUM",
    "alerts_generated": [
      {
        "alert_id": "ALERT_001",
        "rule_name": "High Value Transaction",
        "severity": "MEDIUM",
        "description": "Transaction exceeds daily threshold",
        "triggered_conditions": ["amount > 25000"]
      }
    ],
    "screening_results": {
      "sanctions_check": "CLEAR",
      "counterparty_screening": "CLEAR",
      "geographic_risk": "LOW",
      "velocity_check": "MEDIUM"
    },
    "recommendations": [
      "Enhanced monitoring for 30 days",
      "Document business purpose"
    ],
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Regulatory Reporting Endpoints

### 7. Get Report Templates

**Endpoint**: `GET /api/v1/reports/templates`

**Description**: Retrieve available regulatory report templates.

**Query Parameters**:
- `jurisdiction`: Filter by jurisdiction (optional)
- `report_type`: Filter by report type (optional)

**Response**:
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "template_id": "fincen_sar",
        "template_name": "FinCEN Suspicious Activity Report",
        "jurisdiction": "US",
        "report_type": "SAR",
        "version": "2024.1",
        "description": "US FinCEN Form 111 - Suspicious Activity Report",
        "required_fields": [
          "reporting_institution",
          "suspect_information",
          "suspicious_activity",
          "narrative"
        ],
        "output_formats": ["PDF", "XML", "JSON"]
      },
      {
        "template_id": "eu_str",
        "template_name": "EU Suspicious Transaction Report",
        "jurisdiction": "EU",
        "report_type": "STR",
        "version": "2024.1",
        "description": "European Union Suspicious Transaction Report",
        "required_fields": [
          "reporting_entity",
          "transaction_details",
          "suspicion_indicators",
          "supporting_documentation"
        ],
        "output_formats": ["PDF", "XML"]
      }
    ],
    "total_templates": 7,
    "supported_jurisdictions": ["US", "EU", "UK", "AU", "CA"]
  }
}
```

### 8. Generate Report

**Endpoint**: `POST /api/v1/reports/generate`

**Description**: Generate regulatory compliance reports.

**Request Body**:
```json
{
  "template_id": "fincen_sar",
  "report_data": {
    "reporting_institution": {
      "name": "ABC Bank",
      "ein": "12-3456789",
      "address": "123 Banking St, New York, NY 10001"
    },
    "suspect_information": {
      "name": "John Doe",
      "ssn": "XXX-XX-1234",
      "date_of_birth": "1980-01-01",
      "address": "456 Suspect Ave, Miami, FL 33101"
    },
    "suspicious_activity": {
      "activity_type": "Money Laundering",
      "transaction_amount": 100000.00,
      "transaction_date": "2025-01-10",
      "description": "Unusual cash deposit patterns"
    },
    "narrative": "Customer made multiple large cash deposits in amounts just below reporting thresholds..."
  },
  "output_format": "PDF",
  "include_attachments": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "RPT_001",
    "template_name": "FinCEN Suspicious Activity Report",
    "status": "GENERATED",
    "output_format": "PDF",
    "file_size": "2.3 MB",
    "generated_at": "2025-01-15T10:30:00Z",
    "download_url": "https://api.backcheck.io/v1/reports/download/RPT_001",
    "expiry_date": "2025-01-22T10:30:00Z",
    "validation_results": {
      "valid": true,
      "errors": [],
      "warnings": [
        "Consider adding additional supporting documentation"
      ]
    }
  }
}
```

## Monitoring & Analytics Endpoints

### 9. System Health Check

**Endpoint**: `GET /api/v1/health`

**Description**: Check system health and service availability.

**Response**:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "services": {
    "identity": "operational",
    "kyc": "operational",
    "sanctions": "operational",
    "osint": "operational",
    "beneficial_ownership": "operational",
    "transaction_monitoring": "operational",
    "reporting": "operational",
    "database": "operational",
    "ai_engine": "operational"
  },
  "performance_metrics": {
    "avg_response_time": "145ms",
    "requests_per_minute": 847,
    "error_rate": "0.02%",
    "uptime": "99.98%"
  }
}
```

### 10. Analytics Dashboard

**Endpoint**: `GET /api/v1/analytics/dashboard`

**Description**: Get compliance analytics and metrics.

**Query Parameters**:
- `date_range`: Date range for analytics (e.g., "30d", "7d", "1d")
- `metrics`: Specific metrics to include

**Response**:
```json
{
  "success": true,
  "data": {
    "period": "30d",
    "summary": {
      "total_screenings": 15420,
      "high_risk_alerts": 234,
      "compliance_cases": 45,
      "reports_generated": 78
    },
    "risk_distribution": {
      "MINIMAL": 8234,
      "LOW": 4521,
      "MEDIUM": 2145,
      "HIGH": 456,
      "CRITICAL": 64
    },
    "service_usage": {
      "sanctions_screening": 15420,
      "kyc_verification": 3456,
      "osint_searches": 1234,
      "transaction_monitoring": 45678,
      "report_generation": 78
    },
    "compliance_metrics": {
      "fatf_coverage": "98.5%",
      "false_positive_rate": "2.3%",
      "average_processing_time": "1.2s",
      "sla_compliance": "99.7%"
    }
  }
}
```

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "entity_name",
      "issue": "Field is required"
    },
    "request_id": "req_123456789",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_FAILED` | Invalid API key or token | 401 |
| `AUTHORIZATION_DENIED` | Insufficient permissions | 403 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `RESOURCE_NOT_FOUND` | Requested resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

## Rate Limiting

**Default Limits**:
- 1000 requests per minute per API key
- 10,000 requests per hour per API key
- 100,000 requests per day per API key

**Rate Limit Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Webhooks

### Webhook Configuration

**Endpoint**: `POST /api/v1/webhooks/configure`

**Request Body**:
```json
{
  "webhook_url": "https://your-system.com/webhooks/backcheck",
  "events": [
    "compliance.high_risk_detected",
    "transaction.suspicious_activity",
    "report.generation_complete"
  ],
  "secret": "your_webhook_secret"
}
```

### Webhook Events

**High Risk Detection**:
```json
{
  "event": "compliance.high_risk_detected",
  "data": {
    "customer_id": "CUST_001",
    "risk_score": 0.89,
    "risk_level": "HIGH",
    "triggered_rules": ["sanctions_match", "adverse_media"]
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## SDK Examples

### Python SDK

```python
import backcheck

# Initialize client
client = backcheck.Client(api_key="compliant-your-api-key")

# Sanctions screening
result = client.sanctions.screen(
    entity_name="John Doe",
    entity_type="person",
    threshold=0.8
)

# KYC verification
kyc_result = client.kyc.verify(
    customer_id="CUST_001",
    verification_level="enhanced",
    customer_data={...}
)

# Generate report
report = client.reports.generate(
    template_id="fincen_sar",
    report_data={...},
    output_format="PDF"
)
```

### JavaScript SDK

```javascript
const Backcheck = require('@backcheck/api-client');

const client = new Backcheck({
  apiKey: 'compliant-your-api-key'
});

// Sanctions screening
const screeningResult = await client.sanctions.screen({
  entityName: 'John Doe',
  entityType: 'person',
  threshold: 0.8
});

// OSINT search
const osintResult = await client.osint.search({
  entityName: 'ABC Corporation',
  entityType: 'organization',
  searchDepth: 'comprehensive'
});
```

---

*API Reference Version: 1.0*  
*Last Updated: January 2025*  
*For technical support: api-support@backcheck.io*