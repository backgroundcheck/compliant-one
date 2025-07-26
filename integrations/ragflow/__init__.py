"""
RAGFlow Integration Main Module
Main entry point for RAGFlow integration with Compliant-One platform
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from .config import get_ragflow_config, validate_ragflow_config
from .utils import (
    classify_compliance_document,
    extract_document_metadata, 
    validate_compliance_document,
    check_integration_health,
    get_sync_status,
    sync_manager
)
from ...services.ai.ragflow_client import get_ragflow_client, get_knowledge_manager, cleanup_ragflow_services
from ...services.ai.document_processor import process_compliance_document, process_regulation_directory
from ...services.ai.compliance_chat import create_chat_session, send_chat_message, QuestionType, UrgencyLevel
from ...utils.logger import get_logger

logger = get_logger(__name__)

class RAGFlowIntegration:
    """Main RAGFlow integration manager"""
    
    def __init__(self):
        self.config = get_ragflow_config()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize RAGFlow integration"""
        
        if self._initialized:
            return
            
        try:
            # Validate configuration
            issues = validate_ragflow_config()
            if issues:
                raise RuntimeError(f"Configuration issues: {', '.join(issues)}")
                
            if not self.config.enabled:
                self.logger.info("RAGFlow integration is disabled")
                return
                
            # Test connection
            health_status = await check_integration_health()
            if health_status['status'] != 'healthy':
                self.logger.warning(f"RAGFlow health check failed: {health_status}")
                
            self._initialized = True
            self.logger.info("RAGFlow integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAGFlow integration: {e}")
            raise
            
    async def cleanup(self) -> None:
        """Cleanup RAGFlow integration"""
        try:
            await cleanup_ragflow_services()
            self._initialized = False
            self.logger.info("RAGFlow integration cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    async def upload_regulation(self, file_path: Union[str, Path], 
                              jurisdiction: Optional[str] = None,
                              tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upload regulatory document to RAGFlow"""
        
        if not self._initialized:
            await self.initialize()
            
        file_path = Path(file_path)
        
        try:
            # Pre-processing: classification and validation
            classification = await classify_compliance_document(file_path)
            metadata = await extract_document_metadata(file_path)
            validation = await validate_compliance_document(file_path)
            
            if not validation['is_valid']:
                return {
                    'success': False,
                    'error': f"Document validation failed: {', '.join(validation['issues'])}",
                    'metadata': metadata
                }
                
            # Process document
            result = await process_compliance_document(
                file_path,
                classification['document_type'],
                jurisdiction,
                tags
            )
            
            if result.success:
                # Track sync status
                checksum = metadata.get('checksum', '')
                await sync_manager.track_document_sync(
                    str(file_path), 
                    result.document_id, 
                    checksum
                )
                
            return {
                'success': result.success,
                'document_id': result.document_id,
                'classification': classification,
                'metadata': metadata,
                'validation': validation,
                'processing_time': result.processing_time,
                'chunks_created': result.chunks_created,
                'error': result.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to upload regulation {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
            
    async def upload_regulation_batch(self, directory_path: Union[str, Path],
                                    jurisdiction: str = "international") -> Dict[str, Any]:
        """Upload batch of regulatory documents"""
        
        if not self._initialized:
            await self.initialize()
            
        directory_path = Path(directory_path)
        
        try:
            results = await process_regulation_directory(directory_path, jurisdiction)
            
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            return {
                'total_processed': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) if results else 0,
                'results': results,
                'jurisdiction': jurisdiction,
                'directory': str(directory_path)
            }
            
        except Exception as e:
            self.logger.error(f"Batch upload failed for {directory_path}: {e}")
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 1,
                'success_rate': 0,
                'error': str(e),
                'directory': str(directory_path)
            }
            
    async def search_regulations(self, query: str, 
                               jurisdiction: Optional[str] = None,
                               document_type: Optional[str] = None) -> Dict[str, Any]:
        """Search regulatory documents"""
        
        if not self._initialized:
            await self.initialize()
            
        try:
            knowledge_manager = await get_knowledge_manager()
            results = await knowledge_manager.search_regulations(query, jurisdiction)
            
            # Filter by document type if specified
            if document_type:
                results = [r for r in results if document_type.lower() in r.get('content_with_weight', '').lower()]
                
            return {
                'success': True,
                'query': query,
                'jurisdiction': jurisdiction,
                'document_type': document_type,
                'results_count': len(results),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
            
    async def get_compliance_guidance(self, scenario: str, 
                                    risk_level: str = "medium",
                                    question_type: Optional[QuestionType] = None) -> Dict[str, Any]:
        """Get AI-powered compliance guidance"""
        
        if not self._initialized:
            await self.initialize()
            
        try:
            # Create chat session for this guidance request
            session_id = await create_chat_session(title=f"Guidance: {scenario[:50]}...")
            
            # Determine urgency based on risk level
            urgency_mapping = {
                "low": UrgencyLevel.LOW,
                "medium": UrgencyLevel.MEDIUM,
                "high": UrgencyLevel.HIGH,
                "critical": UrgencyLevel.CRITICAL
            }
            urgency = urgency_mapping.get(risk_level.lower(), UrgencyLevel.MEDIUM)
            
            # Send message to get guidance
            response = await send_chat_message(
                session_id,
                scenario,
                question_type or QuestionType.GENERAL_COMPLIANCE,
                urgency
            )
            
            return {
                'success': True,
                'scenario': scenario,
                'risk_level': risk_level,
                'guidance': response.content,
                'sources': response.sources,
                'confidence_score': response.confidence_score,
                'processing_time': response.processing_time,
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Compliance guidance failed for scenario '{scenario}': {e}")
            return {
                'success': False,
                'error': str(e),
                'scenario': scenario
            }
            
    async def analyze_compliance_document(self, document_id: str) -> Dict[str, Any]:
        """Analyze document for compliance insights"""
        
        if not self._initialized:
            await self.initialize()
            
        try:
            from ...services.ai.document_processor import analyze_document_compliance
            
            analysis = await analyze_document_compliance(document_id)
            
            return {
                'success': True,
                'document_id': document_id,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Document analysis failed for {document_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_id': document_id
            }
            
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        
        try:
            # Get health status
            health_status = await check_integration_health()
            
            # Get sync statistics
            sync_stats = await get_sync_status()
            
            # Get configuration info
            config_info = {
                'enabled': self.config.enabled,
                'api_url': self.config.api_url,
                'knowledge_base': self.config.kb_name,
                'doc_engine': self.config.doc_engine,
                'chunk_size': self.config.chunk_size
            }
            
            return {
                'initialized': self._initialized,
                'configuration': config_info,
                'health': health_status,
                'synchronization': sync_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get integration status: {e}")
            return {
                'initialized': self._initialized,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Global integration instance
_ragflow_integration: Optional[RAGFlowIntegration] = None

async def get_ragflow_integration() -> RAGFlowIntegration:
    """Get initialized RAGFlow integration"""
    global _ragflow_integration
    
    if _ragflow_integration is None:
        _ragflow_integration = RAGFlowIntegration()
        await _ragflow_integration.initialize()
        
    return _ragflow_integration

# Convenience functions
async def upload_regulation_document(file_path: Union[str, Path], 
                                   jurisdiction: Optional[str] = None,
                                   tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Upload regulatory document"""
    integration = await get_ragflow_integration()
    return await integration.upload_regulation(file_path, jurisdiction, tags)

async def upload_regulation_directory(directory_path: Union[str, Path],
                                    jurisdiction: str = "international") -> Dict[str, Any]:
    """Upload directory of regulatory documents"""
    integration = await get_ragflow_integration()
    return await integration.upload_regulation_batch(directory_path, jurisdiction)

async def search_compliance_regulations(query: str, 
                                      jurisdiction: Optional[str] = None,
                                      document_type: Optional[str] = None) -> Dict[str, Any]:
    """Search compliance regulations"""
    integration = await get_ragflow_integration()
    return await integration.search_regulations(query, jurisdiction, document_type)

async def get_ai_compliance_guidance(scenario: str, 
                                   risk_level: str = "medium",
                                   question_type: Optional[QuestionType] = None) -> Dict[str, Any]:
    """Get AI compliance guidance"""
    integration = await get_ragflow_integration()
    return await integration.get_compliance_guidance(scenario, risk_level, question_type)

async def analyze_uploaded_document(document_id: str) -> Dict[str, Any]:
    """Analyze uploaded document"""
    integration = await get_ragflow_integration()
    return await integration.analyze_compliance_document(document_id)

async def get_ragflow_status() -> Dict[str, Any]:
    """Get RAGFlow integration status"""
    integration = await get_ragflow_integration()
    return await integration.get_integration_status()

async def cleanup_ragflow_integration() -> None:
    """Cleanup RAGFlow integration"""
    global _ragflow_integration
    
    if _ragflow_integration:
        await _ragflow_integration.cleanup()
        _ragflow_integration = None
