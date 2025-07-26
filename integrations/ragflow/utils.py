"""
RAGFlow Integration Utilities
Helper functions and utilities for RAGFlow integration
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
import aiofiles
import hashlib
import re

from .config import get_ragflow_config
from ...utils.logger import get_logger

logger = get_logger(__name__)

class DocumentClassifier:
    """Classify documents for optimal RAGFlow processing"""
    
    def __init__(self):
        self.classification_rules = {
            'fatf_recommendation': {
                'keywords': ['fatf', 'financial action task force', 'recommendation', 'aml', 'cft'],
                'file_patterns': [r'fatf.*recommendation', r'recommendation.*\d+'],
                'document_type': 'fatf_recommendation'
            },
            'basel_standard': {
                'keywords': ['basel', 'bcbs', 'banking supervision', 'capital', 'liquidity'],
                'file_patterns': [r'basel.*\d+', r'bcbs\d+'],
                'document_type': 'basel_standard'
            },
            'aml_regulation': {
                'keywords': ['anti-money laundering', 'aml', 'suspicious activity', 'money laundering'],
                'file_patterns': [r'aml.*law', r'anti.*money.*laundering'],
                'document_type': 'regulation'
            },
            'kyc_regulation': {
                'keywords': ['know your customer', 'kyc', 'customer due diligence', 'cdd'],
                'file_patterns': [r'kyc.*regulation', r'customer.*due.*diligence'],
                'document_type': 'regulation'
            },
            'sanctions_list': {
                'keywords': ['sanctions', 'embargo', 'blacklist', 'designated persons'],
                'file_patterns': [r'sanctions.*list', r'sdn.*list', r'consolidated.*list'],
                'document_type': 'regulation'
            },
            'internal_policy': {
                'keywords': ['policy', 'procedure', 'guideline', 'manual'],
                'file_patterns': [r'policy.*\d+', r'procedure.*manual'],
                'document_type': 'policy'
            }
        }
        
    def classify_document(self, file_path: Union[str, Path], 
                         content_sample: Optional[str] = None) -> Dict[str, Any]:
        """Classify document based on filename and content"""
        
        file_path = Path(file_path)
        filename = file_path.name.lower()
        
        scores = {}
        
        for classification, rules in self.classification_rules.items():
            score = 0
            
            # Check filename patterns
            for pattern in rules['file_patterns']:
                if re.search(pattern, filename, re.IGNORECASE):
                    score += 3
                    
            # Check keywords in filename
            for keyword in rules['keywords']:
                if keyword.lower() in filename:
                    score += 1
                    
            # Check content if available
            if content_sample:
                content_lower = content_sample.lower()
                for keyword in rules['keywords']:
                    if keyword.lower() in content_lower:
                        score += 0.5
                        
            scores[classification] = score
            
        # Find best match
        best_match = max(scores, key=scores.get) if scores else 'regulation'
        confidence = scores.get(best_match, 0) / 10  # Normalize to 0-1
        
        return {
            'classification': best_match,
            'document_type': self.classification_rules[best_match]['document_type'],
            'confidence': min(confidence, 1.0),
            'scores': scores
        }

class MetadataExtractor:
    """Extract metadata from compliance documents"""
    
    def __init__(self):
        self.metadata_patterns = {
            'effective_date': [
                r'effective date:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'effective\s+(\d{1,2}\s+\w+\s+\d{4})',
                r'comes into force on\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
            ],
            'version': [
                r'version\s*:?\s*(\d+\.?\d*)',
                r'v(\d+\.?\d*)',
                r'revision\s*:?\s*(\d+\.?\d*)'
            ],
            'jurisdiction': [
                r'jurisdiction\s*:?\s*([A-Za-z\s]+)',
                r'applicable in\s+([A-Za-z\s]+)',
                r'([A-Z]{2,3})\s+regulation'
            ],
            'regulation_number': [
                r'regulation\s+(?:no\.?\s*)?(\d+[\/\-]\d+)',
                r'directive\s+(\d+[\/\-]\d+)',
                r'recommendation\s+(\d+)'
            ]
        }
        
    async def extract_metadata(self, file_path: Union[str, Path], 
                             max_chars: int = 5000) -> Dict[str, Any]:
        """Extract metadata from document"""
        
        file_path = Path(file_path)
        metadata = {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'file_extension': file_path.suffix.lower(),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Read beginning of file for metadata extraction
            if file_path.suffix.lower() == '.txt':
                content = await self._read_text_content(file_path, max_chars)
            elif file_path.suffix.lower() == '.md':
                content = await self._read_text_content(file_path, max_chars)
            else:
                # For other formats, would need specialized extractors
                content = ""
                
            if content:
                # Extract metadata using patterns
                for field, patterns in self.metadata_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            metadata[field] = match.group(1).strip()
                            break
                            
                # Extract additional context
                metadata['content_sample'] = content[:500]
                metadata['estimated_pages'] = len(content) // 2000  # Rough estimate
                
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {e}")
            
        return metadata
        
    async def _read_text_content(self, file_path: Path, max_chars: int) -> str:
        """Read text content from file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read(max_chars)
                return content
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return ""

class ContentValidator:
    """Validate document content for compliance processing"""
    
    def __init__(self):
        self.min_content_length = 100
        self.max_content_length = 10_000_000  # 10MB
        self.required_compliance_indicators = [
            'regulation', 'compliance', 'requirement', 'shall', 'must',
            'obligation', 'standard', 'guideline', 'procedure'
        ]
        
    def validate_document(self, file_path: Union[str, Path], 
                         content_sample: Optional[str] = None) -> Dict[str, Any]:
        """Validate document for compliance processing"""
        
        file_path = Path(file_path)
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'compliance_score': 0.0
        }
        
        # Check file existence
        if not file_path.exists():
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"File not found: {file_path}")
            return validation_result
            
        # Check file size
        file_size = file_path.stat().st_size
        if file_size < self.min_content_length:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"File too small: {file_size} bytes")
        elif file_size > self.max_content_length:
            validation_result['warnings'].append(f"Large file: {file_size} bytes")
            
        # Check content if available
        if content_sample:
            compliance_score = self._calculate_compliance_score(content_sample)
            validation_result['compliance_score'] = compliance_score
            
            if compliance_score < 0.1:
                validation_result['warnings'].append("Low compliance content detected")
                
        return validation_result
        
    def _calculate_compliance_score(self, content: str) -> float:
        """Calculate compliance relevance score"""
        
        content_lower = content.lower()
        matches = 0
        
        for indicator in self.required_compliance_indicators:
            if indicator in content_lower:
                matches += 1
                
        # Additional scoring for compliance-specific terms
        compliance_terms = [
            'fatf', 'basel', 'aml', 'kyc', 'sanctions', 'due diligence',
            'risk assessment', 'suspicious activity', 'money laundering'
        ]
        
        for term in compliance_terms:
            if term in content_lower:
                matches += 0.5
                
        # Normalize score
        max_possible = len(self.required_compliance_indicators) + len(compliance_terms) * 0.5
        return min(matches / max_possible, 1.0) if max_possible > 0 else 0.0

class SyncManager:
    """Manage synchronization between Compliant-One and RAGFlow"""
    
    def __init__(self):
        self.sync_status_file = Path("data/ragflow_sync_status.json")
        self.last_sync_file = Path("data/ragflow_last_sync.json")
        
    async def track_document_sync(self, local_path: str, document_id: str, 
                                checksum: str) -> None:
        """Track synchronized document"""
        
        sync_data = await self._load_sync_status()
        
        sync_data[local_path] = {
            'document_id': document_id,
            'checksum': checksum,
            'sync_timestamp': datetime.now().isoformat(),
            'status': 'synced'
        }
        
        await self._save_sync_status(sync_data)
        
    async def check_document_sync(self, local_path: str, 
                                current_checksum: str) -> Optional[str]:
        """Check if document needs sync"""
        
        sync_data = await self._load_sync_status()
        
        if local_path in sync_data:
            stored_info = sync_data[local_path]
            if stored_info.get('checksum') == current_checksum:
                return stored_info.get('document_id')
                
        return None
        
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        
        sync_data = await self._load_sync_status()
        
        total_docs = len(sync_data)
        synced_docs = sum(1 for doc in sync_data.values() if doc.get('status') == 'synced')
        
        # Calculate last sync time
        last_sync_times = [
            datetime.fromisoformat(doc['sync_timestamp']) 
            for doc in sync_data.values() 
            if 'sync_timestamp' in doc
        ]
        
        last_sync = max(last_sync_times) if last_sync_times else None
        
        return {
            'total_documents': total_docs,
            'synced_documents': synced_docs,
            'sync_percentage': (synced_docs / total_docs * 100) if total_docs > 0 else 0,
            'last_sync': last_sync.isoformat() if last_sync else None
        }
        
    async def _load_sync_status(self) -> Dict[str, Any]:
        """Load sync status from file"""
        
        if not self.sync_status_file.exists():
            return {}
            
        try:
            async with aiofiles.open(self.sync_status_file, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except Exception as e:
            logger.warning(f"Failed to load sync status: {e}")
            return {}
            
    async def _save_sync_status(self, sync_data: Dict[str, Any]) -> None:
        """Save sync status to file"""
        
        try:
            # Ensure directory exists
            self.sync_status_file.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(self.sync_status_file, 'w') as f:
                await f.write(json.dumps(sync_data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save sync status: {e}")

class HealthChecker:
    """Health checking for RAGFlow integration"""
    
    def __init__(self):
        self.config = get_ragflow_config()
        
    async def check_ragflow_health(self) -> Dict[str, Any]:
        """Check RAGFlow service health"""
        
        health_status = {
            'status': 'unknown',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            from ...services.ai.ragflow_client import get_ragflow_client
            
            # Test connection
            client = await get_ragflow_client()
            
            # Test basic operations
            health_status['checks']['connection'] = await self._check_connection(client)
            health_status['checks']['knowledge_base'] = await self._check_knowledge_base(client)
            health_status['checks']['search'] = await self._check_search(client)
            
            # Determine overall status
            all_passed = all(check.get('status') == 'ok' for check in health_status['checks'].values())
            health_status['status'] = 'healthy' if all_passed else 'unhealthy'
            
        except Exception as e:
            health_status['status'] = 'error'
            health_status['error'] = str(e)
            
        return health_status
        
    async def _check_connection(self, client) -> Dict[str, Any]:
        """Check connection to RAGFlow"""
        try:
            # Simple test - list knowledge bases
            await client._make_request("POST", "/kb/list", {})
            return {'status': 'ok', 'message': 'Connection successful'}
        except Exception as e:
            return {'status': 'error', 'message': f'Connection failed: {e}'}
            
    async def _check_knowledge_base(self, client) -> Dict[str, Any]:
        """Check knowledge base status"""
        try:
            if client.kb_id:
                return {'status': 'ok', 'message': f'Knowledge base active: {client.kb_id}'}
            else:
                return {'status': 'warning', 'message': 'Knowledge base not initialized'}
        except Exception as e:
            return {'status': 'error', 'message': f'Knowledge base check failed: {e}'}
            
    async def _check_search(self, client) -> Dict[str, Any]:
        """Check search functionality"""
        try:
            results = await client.search_documents("compliance test", top_k=1)
            return {'status': 'ok', 'message': f'Search returned {len(results)} results'}
        except Exception as e:
            return {'status': 'error', 'message': f'Search failed: {e}'}

# Utility instances
document_classifier = DocumentClassifier()
metadata_extractor = MetadataExtractor()
content_validator = ContentValidator()
sync_manager = SyncManager()
health_checker = HealthChecker()

# Utility functions
async def classify_compliance_document(file_path: Union[str, Path], 
                                     content_sample: Optional[str] = None) -> Dict[str, Any]:
    """Classify compliance document"""
    return document_classifier.classify_document(file_path, content_sample)

async def extract_document_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Extract document metadata"""
    return await metadata_extractor.extract_metadata(file_path)

async def validate_compliance_document(file_path: Union[str, Path], 
                                     content_sample: Optional[str] = None) -> Dict[str, Any]:
    """Validate compliance document"""
    return content_validator.validate_document(file_path, content_sample)

async def check_integration_health() -> Dict[str, Any]:
    """Check RAGFlow integration health"""
    return await health_checker.check_ragflow_health()

async def get_sync_status() -> Dict[str, Any]:
    """Get synchronization status"""
    return await sync_manager.get_sync_statistics()

def calculate_file_checksum(file_path: Union[str, Path]) -> str:
    """Calculate file checksum"""
    hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
            
    return hasher.hexdigest()
