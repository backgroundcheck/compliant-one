"""
RAGFlow Integration Configuration
Central configuration management for RAGFlow services
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class RAGFlowIntegrationConfig:
    """Complete RAGFlow integration configuration"""
    
    # Core RAGFlow Settings
    api_url: str = field(default_factory=lambda: os.getenv("RAGFLOW_API_URL", "http://localhost:9380"))
    api_key: str = field(default_factory=lambda: os.getenv("RAGFLOW_API_KEY", ""))
    enabled: bool = field(default_factory=lambda: os.getenv("RAGFLOW_ENABLED", "true").lower() == "true")
    
    # Knowledge Base Configuration
    kb_name: str = field(default_factory=lambda: os.getenv("RAGFLOW_KB_NAME", "compliant_one_regulations"))
    kb_description: str = "Compliant-One Regulatory Knowledge Base"
    kb_language: str = "English"
    
    # Document Engine Settings
    doc_engine: str = field(default_factory=lambda: os.getenv("RAGFLOW_DOC_ENGINE", "elasticsearch"))
    enable_gpu: bool = field(default_factory=lambda: os.getenv("RAGFLOW_ENABLE_GPU", "false").lower() == "true")
    
    # Processing Configuration
    chunk_size: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_CHUNK_SIZE", "1024")))
    max_chunk_size: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_MAX_CHUNK_SIZE", "1024")))
    overlap_size: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_OVERLAP_SIZE", "200")))
    
    # Search and Retrieval Settings
    similarity_threshold: float = field(default_factory=lambda: float(os.getenv("RAGFLOW_SIMILARITY_THRESHOLD", "0.8")))
    top_k_results: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_TOP_K", "10")))
    vector_similarity_weight: float = field(default_factory=lambda: float(os.getenv("RAGFLOW_VECTOR_WEIGHT", "0.3")))
    
    # Sync and Performance Settings
    sync_interval: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_SYNC_INTERVAL", "3600")))
    batch_size: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_BATCH_SIZE", "10")))
    max_concurrent_uploads: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_MAX_CONCURRENT", "5")))
    
    # Timeout Settings
    connection_timeout: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_CONN_TIMEOUT", "30")))
    request_timeout: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_REQ_TIMEOUT", "120")))
    processing_timeout: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_PROC_TIMEOUT", "300")))
    
    # Parser Configuration
    default_parser: str = field(default_factory=lambda: os.getenv("RAGFLOW_DEFAULT_PARSER", "naive"))
    layout_recognition: bool = field(default_factory=lambda: os.getenv("RAGFLOW_LAYOUT_RECOGNITION", "true").lower() == "true")
    table_recognition: bool = field(default_factory=lambda: os.getenv("RAGFLOW_TABLE_RECOGNITION", "true").lower() == "true")
    
    # Compliance-Specific Settings
    compliance_parsers: Dict[str, str] = field(default_factory=lambda: {
        "regulation": "laws",
        "policy": "manual", 
        "procedure": "manual",
        "template": "naive",
        "report": "paper"
    })
    
    # Document Type Templates
    document_templates: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "regulation": {
            "parser_id": "laws",
            "parser_config": {
                "chunk_token_num": 1024,
                "layout_recognize": True,
                "delimiter": "\n",
                "task_page_size": 12
            },
            "tags": ["regulation", "compliance", "legal"]
        },
        "policy": {
            "parser_id": "manual", 
            "parser_config": {
                "chunk_token_num": 512,
                "layout_recognize": True,
                "delimiter": "\n"
            },
            "tags": ["policy", "internal", "procedures"]
        },
        "fatf_recommendation": {
            "parser_id": "laws",
            "parser_config": {
                "chunk_token_num": 1024,
                "layout_recognize": True,
                "delimiter": "\n",
                "task_page_size": 8
            },
            "tags": ["fatf", "international", "aml", "cft"]
        },
        "basel_standard": {
            "parser_id": "laws",
            "parser_config": {
                "chunk_token_num": 1024,
                "layout_recognize": True,
                "delimiter": "\n",
                "task_page_size": 10
            },
            "tags": ["basel", "banking", "risk", "capital"]
        }
    })
    
    # Health Check Settings
    health_check_interval: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_HEALTH_CHECK", "60")))
    max_retry_attempts: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_MAX_RETRIES", "3")))
    retry_delay: int = field(default_factory=lambda: int(os.getenv("RAGFLOW_RETRY_DELAY", "5")))

# Global configuration instance
ragflow_config = RAGFlowIntegrationConfig()

def get_ragflow_config() -> RAGFlowIntegrationConfig:
    """Get RAGFlow configuration"""
    return ragflow_config

def update_ragflow_config(**kwargs) -> None:
    """Update RAGFlow configuration"""
    global ragflow_config
    
    for key, value in kwargs.items():
        if hasattr(ragflow_config, key):
            setattr(ragflow_config, key, value)

def validate_ragflow_config() -> List[str]:
    """Validate RAGFlow configuration and return any issues"""
    
    issues = []
    config = get_ragflow_config()
    
    # Check required settings
    if not config.api_url:
        issues.append("RAGFLOW_API_URL is required")
        
    if not config.api_key and config.enabled:
        issues.append("RAGFLOW_API_KEY is required when RAGFlow is enabled")
        
    if config.chunk_size <= 0:
        issues.append("Chunk size must be positive")
        
    if config.similarity_threshold < 0 or config.similarity_threshold > 1:
        issues.append("Similarity threshold must be between 0 and 1")
        
    if config.top_k_results <= 0:
        issues.append("Top K results must be positive")
        
    # Check timeout values
    if config.connection_timeout <= 0:
        issues.append("Connection timeout must be positive")
        
    if config.request_timeout <= 0:
        issues.append("Request timeout must be positive")
        
    return issues

def get_parser_config(document_type: str) -> Dict[str, Any]:
    """Get parser configuration for document type"""
    
    config = get_ragflow_config()
    template = config.document_templates.get(document_type, config.document_templates["regulation"])
    
    return {
        "parser_id": template["parser_id"],
        "parser_config": template["parser_config"].copy()
    }

def get_document_tags(document_type: str, jurisdiction: Optional[str] = None) -> List[str]:
    """Get default tags for document type"""
    
    config = get_ragflow_config()
    template = config.document_templates.get(document_type, config.document_templates["regulation"])
    
    tags = template["tags"].copy()
    
    if jurisdiction:
        tags.append(jurisdiction.lower())
        
    return tags

def create_docker_config() -> Dict[str, Any]:
    """Create Docker configuration for RAGFlow deployment"""
    
    config = get_ragflow_config()
    
    return {
        "version": "3.8",
        "services": {
            "ragflow": {
                "image": "infiniflow/ragflow:v0.19.1-slim",
                "container_name": "compliant-one-ragflow",
                "ports": [
                    f"9380:80"
                ],
                "environment": {
                    "RAGFLOW_API_KEY": config.api_key,
                    "DOC_ENGINE": config.doc_engine,
                    "LIGHTEN": "1" if not config.enable_gpu else "0"
                },
                "volumes": [
                    "ragflow_data:/ragflow",
                    "ragflow_logs:/ragflow/logs"
                ],
                "depends_on": [
                    "elasticsearch",
                    "mysql",
                    "redis",
                    "minio"
                ],
                "restart": "unless-stopped",
                "networks": [
                    "compliant-one-network"
                ]
            },
            "elasticsearch": {
                "image": "docker.elastic.co/elasticsearch/elasticsearch:8.11.0",
                "container_name": "compliant-one-elasticsearch",
                "environment": {
                    "discovery.type": "single-node",
                    "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
                    "xpack.security.enabled": "false"
                },
                "volumes": [
                    "es_data:/usr/share/elasticsearch/data"
                ],
                "ports": [
                    "9200:9200"
                ],
                "restart": "unless-stopped",
                "networks": [
                    "compliant-one-network"
                ]
            },
            "mysql": {
                "image": "mysql:8.0",
                "container_name": "compliant-one-mysql",
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "ragflow123",
                    "MYSQL_DATABASE": "ragflow",
                    "MYSQL_USER": "ragflow",
                    "MYSQL_PASSWORD": "ragflow123"
                },
                "volumes": [
                    "mysql_data:/var/lib/mysql"
                ],
                "ports": [
                    "3306:3306"
                ],
                "restart": "unless-stopped",
                "networks": [
                    "compliant-one-network"
                ]
            },
            "redis": {
                "image": "redis:7.0-alpine",
                "container_name": "compliant-one-redis", 
                "ports": [
                    "6379:6379"
                ],
                "volumes": [
                    "redis_data:/data"
                ],
                "restart": "unless-stopped",
                "networks": [
                    "compliant-one-network"
                ]
            },
            "minio": {
                "image": "quay.io/minio/minio:latest",
                "container_name": "compliant-one-minio",
                "command": "server /data --console-address ':9001'",
                "environment": {
                    "MINIO_ROOT_USER": "minioadmin",
                    "MINIO_ROOT_PASSWORD": "minioadmin123"
                },
                "ports": [
                    "9000:9000",
                    "9001:9001"
                ],
                "volumes": [
                    "minio_data:/data"
                ],
                "restart": "unless-stopped",
                "networks": [
                    "compliant-one-network"
                ]
            }
        },
        "networks": {
            "compliant-one-network": {
                "driver": "bridge"
            }
        },
        "volumes": {
            "ragflow_data": {},
            "ragflow_logs": {},
            "es_data": {},
            "mysql_data": {},
            "redis_data": {},
            "minio_data": {}
        }
    }

def get_environment_template() -> str:
    """Get environment template for RAGFlow integration"""
    
    return """
# RAGFlow Integration Configuration for Compliant-One

# Core RAGFlow Settings
RAGFLOW_API_URL=http://localhost:9380
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_ENABLED=true

# Knowledge Base Settings
RAGFLOW_KB_NAME=compliant_one_regulations
RAGFLOW_DOC_ENGINE=elasticsearch

# Processing Configuration
RAGFLOW_CHUNK_SIZE=1024
RAGFLOW_MAX_CHUNK_SIZE=1024
RAGFLOW_OVERLAP_SIZE=200

# Search and Retrieval
RAGFLOW_SIMILARITY_THRESHOLD=0.8
RAGFLOW_TOP_K=10
RAGFLOW_VECTOR_WEIGHT=0.3

# Performance Settings
RAGFLOW_SYNC_INTERVAL=3600
RAGFLOW_BATCH_SIZE=10
RAGFLOW_MAX_CONCURRENT=5

# Timeout Settings
RAGFLOW_CONN_TIMEOUT=30
RAGFLOW_REQ_TIMEOUT=120
RAGFLOW_PROC_TIMEOUT=300

# Processing Options
RAGFLOW_DEFAULT_PARSER=naive
RAGFLOW_LAYOUT_RECOGNITION=true
RAGFLOW_TABLE_RECOGNITION=true
RAGFLOW_ENABLE_GPU=false

# Health Check Settings
RAGFLOW_HEALTH_CHECK=60
RAGFLOW_MAX_RETRIES=3
RAGFLOW_RETRY_DELAY=5
""".strip()

def export_config_to_file(file_path: str) -> None:
    """Export configuration to file"""
    
    config_content = get_environment_template()
    
    with open(file_path, 'w') as f:
        f.write(config_content)
        
def load_config_from_file(file_path: str) -> None:
    """Load configuration from environment file"""
    
    if not Path(file_path).exists():
        return
        
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                
    # Reinitialize global config
    global ragflow_config
    ragflow_config = RAGFlowIntegrationConfig()
