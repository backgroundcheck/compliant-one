"""
Admin Dashboard Configuration
Centralized configuration for the Compliant.one Admin Dashboard
"""

import os
from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

# Database configuration
ADMIN_DB_PATH = DATABASE_DIR / "data_sources.db"
BACKUP_DIR = DATABASE_DIR / "backups"

# File processing configuration
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
MAX_FILE_SIZE_MB = 100
ALLOWED_FILE_TYPES = {
    'csv': 'text/csv',
    'xml': 'application/xml',
    'json': 'application/json',
    'txt': 'text/plain',
    'html': 'text/html',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls': 'application/vnd.ms-excel',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pdf': 'application/pdf'
}

# Data source categories
DATA_SOURCE_CATEGORIES = [
    "Identity Verification",
    "Sanctions", 
    "PEP",
    "Adverse Media",
    "Beneficial Ownership",
    "Court Records",
    "Regulatory",
    "Transaction Monitoring",
    "OSINT"
]

# Source types
SOURCE_TYPES = [
    "API",
    "File Upload", 
    "Web Scraping",
    "Database",
    "Manual Entry"
]

# Risk scoring configuration
RISK_THRESHOLDS = {
    'high': 0.7,
    'medium': 0.4,
    'low': 0.0
}

# High-risk keywords for entity classification
HIGH_RISK_KEYWORDS = [
    'terror', 'terrorism', 'terrorist',
    'money laundering', 'laundering',
    'fraud', 'fraudulent',
    'corruption', 'corrupt',
    'sanctions', 'sanctioned', 
    'embargo', 'embargoed',
    'prohibited', 'blacklist', 'blacklisted',
    'narcotics', 'drugs',
    'proliferation', 'weapons',
    'organized crime', 'criminal organization'
]

# Medium-risk keywords
MEDIUM_RISK_KEYWORDS = [
    'investigation', 'investigated',
    'suspicious', 'suspect',
    'violation', 'violated',
    'penalty', 'fine', 'fined',
    'enforcement', 'enforced',
    'compliance', 'non-compliant',
    'regulatory', 'regulation',
    'allegation', 'alleged',
    'lawsuit', 'litigation'
]

# Entity type patterns
ENTITY_PATTERNS = {
    'person': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
    'organization': r'\b[A-Z][A-Z\s&]+(?:INC|LLC|LTD|CORP|COMPANY|CORPORATION|LIMITED)\b',
    'location': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2,3}\b',
    'identifier': r'\b[A-Z0-9]{6,}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    'date': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
}

# Sample data sources for initialization
SAMPLE_DATA_SOURCES = [
    {
        'name': 'OFAC SDN List',
        'type': 'API',
        'category': 'Sanctions',
        'source_url': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
        'api_endpoint': 'https://api.treasury.gov/ofac/sdn',
        'description': 'US Treasury OFAC Specially Designated Nationals List'
    },
    {
        'name': 'UN Consolidated List',
        'type': 'API', 
        'category': 'Sanctions',
        'source_url': 'https://www.un.org/securitycouncil/content/un-sc-consolidated-list',
        'api_endpoint': 'https://scsanctions.un.org/resources/xml/en/consolidated.xml',
        'description': 'UN Security Council Consolidated List'
    },
    {
        'name': 'World-Check Database',
        'type': 'API',
        'category': 'PEP',
        'source_url': 'https://www.refinitiv.com/en/products/world-check-kyc-screening',
        'api_endpoint': 'https://api.worldcheck.com/v1',
        'description': 'Refinitiv World-Check API for PEP and sanctions screening'
    },
    {
        'name': 'Companies House UK',
        'type': 'API',
        'category': 'Beneficial Ownership',
        'source_url': 'https://find-and-update.company-information.service.gov.uk/',
        'api_endpoint': 'https://api.company-information.service.gov.uk',
        'description': 'UK Companies House API for corporate information'
    },
    {
        'name': 'Google News API',
        'type': 'API',
        'category': 'Adverse Media',
        'source_url': 'https://newsapi.org/',
        'api_endpoint': 'https://newsapi.org/v2/everything',
        'description': 'News aggregation API for adverse media monitoring'
    },
    {
        'name': 'Dow Jones Risk & Compliance',
        'type': 'API',
        'category': 'PEP',
        'source_url': 'https://www.dowjones.com/professional/risk/',
        'api_endpoint': 'https://api.dowjones.com/v1',
        'description': 'Dow Jones comprehensive risk and compliance database'
    }
]

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'Compliant.one Admin Dashboard',
    'page_icon': '🔧',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Processing configuration
PROCESSING_CONFIG = {
    'max_entities_per_file': 10000,
    'batch_size': 1000,
    'enable_entity_classification': True,
    'enable_risk_scoring': True,
    'enable_duplicate_detection': True,
    'auto_backup_frequency': 'daily'  # daily, weekly, monthly
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': LOGS_DIR / 'admin_dashboard.log',
    'max_file_size': '10MB',
    'backup_count': 5
}

# Security configuration
SECURITY_CONFIG = {
    'enable_authentication': False,  # Set to True for production
    'session_timeout': 3600,  # seconds
    'max_login_attempts': 3,
    'password_min_length': 8,
    'require_https': False  # Set to True for production
}

# Feature flags
FEATURE_FLAGS = {
    'enable_file_upload': True,
    'enable_api_sources': True,
    'enable_web_scraping': True,
    'enable_source_validation': True,
    'enable_data_export': True,
    'enable_backup_restore': True,
    'enable_advanced_search': True,
    'enable_bulk_operations': True
}

# API rate limiting
API_RATE_LIMITS = {
    'requests_per_minute': 60,
    'requests_per_hour': 1000,
    'requests_per_day': 10000
}

# Data retention policies
DATA_RETENTION = {
    'uploaded_files_days': 90,
    'processed_data_days': 365,
    'log_files_days': 30,
    'backup_files_days': 180
}

def get_config(section: str = None):
    """Get configuration settings"""
    config = {
        'base': {
            'BASE_DIR': BASE_DIR,
            'DATA_DIR': DATA_DIR,
            'DATABASE_DIR': DATABASE_DIR,
            'LOGS_DIR': LOGS_DIR
        },
        'database': {
            'ADMIN_DB_PATH': ADMIN_DB_PATH,
            'BACKUP_DIR': BACKUP_DIR
        },
        'files': {
            'UPLOAD_DIR': UPLOAD_DIR,
            'PROCESSED_DIR': PROCESSED_DIR,
            'MAX_FILE_SIZE_MB': MAX_FILE_SIZE_MB,
            'ALLOWED_FILE_TYPES': ALLOWED_FILE_TYPES
        },
        'sources': {
            'DATA_SOURCE_CATEGORIES': DATA_SOURCE_CATEGORIES,
            'SOURCE_TYPES': SOURCE_TYPES,
            'SAMPLE_DATA_SOURCES': SAMPLE_DATA_SOURCES
        },
        'risk': {
            'RISK_THRESHOLDS': RISK_THRESHOLDS,
            'HIGH_RISK_KEYWORDS': HIGH_RISK_KEYWORDS,
            'MEDIUM_RISK_KEYWORDS': MEDIUM_RISK_KEYWORDS,
            'ENTITY_PATTERNS': ENTITY_PATTERNS
        },
        'streamlit': STREAMLIT_CONFIG,
        'processing': PROCESSING_CONFIG,
        'logging': LOGGING_CONFIG,
        'security': SECURITY_CONFIG,
        'features': FEATURE_FLAGS,
        'api': API_RATE_LIMITS,
        'retention': DATA_RETENTION
    }
    
    if section:
        return config.get(section, {})
    
    return config

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        DATA_DIR,
        DATABASE_DIR,
        LOGS_DIR,
        UPLOAD_DIR,
        PROCESSED_DIR,
        BACKUP_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def validate_environment():
    """Validate the admin environment"""
    issues = []
    
    # Check directory permissions
    for directory in [DATA_DIR, DATABASE_DIR, LOGS_DIR]:
        if not os.access(directory, os.W_OK):
            issues.append(f"No write permission for {directory}")
    
    # Check disk space (minimum 1GB)
    import shutil
    total, used, free = shutil.disk_usage(BASE_DIR)
    if free < 1024**3:  # 1GB
        issues.append(f"Low disk space: {free / 1024**3:.1f}GB available")
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version}")
    
    return issues
