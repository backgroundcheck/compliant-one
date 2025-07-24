"""
Compliant.one Platform Configuration
Core settings for RegTech compliance platform
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class PlatformConfig:
    """Core platform configuration"""
    
    # Platform Info
    PLATFORM_NAME: str = "Compliant.one"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Trusted Third-Party Independent Risk & Compliance Solutions Provider"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/compliant_one")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Service URLs
    IDENTITY_SERVICE_URL: str = os.getenv("IDENTITY_SERVICE_URL", "http://localhost:8001")
    KYC_SERVICE_URL: str = os.getenv("KYC_SERVICE_URL", "http://localhost:8002")
    OSINT_SERVICE_URL: str = os.getenv("OSINT_SERVICE_URL", "http://localhost:8003")
    SANCTIONS_SERVICE_URL: str = os.getenv("SANCTIONS_SERVICE_URL", "http://localhost:8004")
    
    # External APIs
    WORLD_CHECK_API_KEY: str = os.getenv("WORLD_CHECK_API_KEY", "")
    DOWJONES_API_KEY: str = os.getenv("DOWJONES_API_KEY", "")
    LexisNexis_API_KEY: str = os.getenv("LEXISNEXIS_API_KEY", "")
    ACUANT_API_KEY: str = os.getenv("ACUANT_API_KEY", "")
    
    # FATF Compliance
    FATF_RECOMMENDATIONS: List[str] = None
    AML_RISK_CATEGORIES: Dict[str, int] = None
    
    # Monitoring
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MONITORING_ENABLED: bool = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    
    def __post_init__(self):
        """Initialize default values"""
        if self.FATF_RECOMMENDATIONS is None:
            self.FATF_RECOMMENDATIONS = [
                "R.10", "R.11", "R.12", "R.13", "R.14", "R.15", "R.16", "R.17", "R.18", "R.19",
                "R.20", "R.21", "R.22", "R.23", "R.24", "R.25", "R.26", "R.27", "R.28", "R.29",
                "R.30", "R.31", "R.32", "R.33", "R.34", "R.35", "R.36", "R.37", "R.38", "R.39", "R.40"
            ]
        
        if self.AML_RISK_CATEGORIES is None:
            self.AML_RISK_CATEGORIES = {
                "LOW": 1,
                "MEDIUM": 2,
                "HIGH": 3,
                "CRITICAL": 4
            }

def get_config() -> PlatformConfig:
    """Get platform configuration"""
    return PlatformConfig()

# FATF Recommendation Mapping
FATF_SERVICE_MAPPING = {
    "R.10": {
        "name": "Customer Due Diligence",
        "service": "kyc",
        "description": "KYC/EDD customer profiling and verification"
    },
    "R.11": {
        "name": "Record Keeping",
        "service": "reporting",
        "description": "Automated record keeping and audit trails"
    },
    "R.12": {
        "name": "Politically Exposed Persons",
        "service": "sanctions",
        "description": "PEP screening and monitoring"
    },
    "R.13": {
        "name": "Correspondent Banking",
        "service": "kyc",
        "description": "Enhanced due diligence for correspondent relationships"
    },
    "R.14": {
        "name": "Money or Value Transfer Services",
        "service": "transactions",
        "description": "MVTS monitoring and compliance"
    },
    "R.15": {
        "name": "New Technologies",
        "service": "osint",
        "description": "AI-powered OSINT monitoring for new tech risks"
    },
    "R.16": {
        "name": "Wire Transfers",
        "service": "beneficial_ownership",
        "description": "Beneficial ownership validation for wire transfers"
    },
    "R.17": {
        "name": "Reliance on Third Parties",
        "service": "kyc",
        "description": "Third-party reliance validation"
    },
    "R.18": {
        "name": "Internal Controls and Foreign Branches",
        "service": "monitoring",
        "description": "Group-wide monitoring and controls"
    },
    "R.19": {
        "name": "Higher-Risk Countries",
        "service": "osint",
        "description": "Geographic risk assessment"
    },
    "R.20": {
        "name": "Reporting of Suspicious Transactions",
        "service": "transactions",
        "description": "Suspicious transaction reporting"
    },
    "R.21": {
        "name": "Tipping-off and Confidentiality",
        "service": "reporting",
        "description": "Secure reporting mechanisms"
    },
    "R.22": {
        "name": "DNFBPs: Customer Due Diligence",
        "service": "kyc",
        "description": "DNFBP-specific due diligence"
    },
    "R.23": {
        "name": "DNFBPs: Other Measures",
        "service": "kyc",
        "description": "Additional DNFBP compliance measures"
    },
    "R.24": {
        "name": "Transparency of Legal Persons",
        "service": "beneficial_ownership",
        "description": "Corporate registry analysis and BO mapping"
    },
    "R.25": {
        "name": "Transparency of Legal Arrangements",
        "service": "beneficial_ownership",
        "description": "Trust and arrangement transparency"
    }
}

# Risk Categories
RISK_CATEGORIES = {
    "CUSTOMER_RISK": ["PEP", "Sanctions", "Adverse Media", "Geographic"],
    "PRODUCT_RISK": ["Cash Intensive", "Anonymous", "Cross-Border"],
    "CHANNEL_RISK": ["Non-Face-to-Face", "Third Party", "Digital"],
    "GEOGRAPHIC_RISK": ["High Risk Jurisdiction", "Sanctions Country", "FATF Non-Compliant"]
}

# Service Endpoints
SERVICE_ENDPOINTS = {
    "identity": "/api/v1/identity",
    "kyc": "/api/v1/kyc",
    "osint": "/api/v1/osint",
    "beneficial_ownership": "/api/v1/beneficial-ownership",
    "sanctions": "/api/v1/sanctions",
    "monitoring": "/api/v1/monitoring",
    "transactions": "/api/v1/transactions",
    "reporting": "/api/v1/reporting"
}
