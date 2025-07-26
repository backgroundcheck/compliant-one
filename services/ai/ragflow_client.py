"""
RAGFlow Integration Service for Compliant-One Platform
Provides document processing, knowledge management, and AI-powered compliance analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import json

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class RAGFlowConfig:
    """RAGFlow service configuration"""
    
    api_url: str = os.getenv("RAGFLOW_API_URL", "http://localhost:9380")
    api_key: str = os.getenv("RAGFLOW_API_KEY", "")
    kb_name: str = os.getenv("RAGFLOW_KB_NAME", "compliant_one_regulations")
    doc_engine: str = os.getenv("RAGFLOW_DOC_ENGINE", "elasticsearch")
    enabled: bool = os.getenv("RAGFLOW_ENABLED", "true").lower() == "true"
    sync_interval: int = int(os.getenv("RAGFLOW_SYNC_INTERVAL", "3600"))
    max_chunk_size: int = int(os.getenv("RAGFLOW_MAX_CHUNK_SIZE", "1024"))
    similarity_threshold: float = float(os.getenv("RAGFLOW_SIMILARITY_THRESHOLD", "0.8"))
    enable_gpu: bool = os.getenv("RAGFLOW_ENABLE_GPU", "false").lower() == "true"
    
class RAGFlowError(Exception):
    """Custom exception for RAGFlow operations"""
    pass

class RAGFlowClient:
    """Client for interacting with RAGFlow API"""
    
    def __init__(self, config: RAGFlowConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.kb_id: Optional[str] = None
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Initialize connection to RAGFlow"""
        if not self.config.enabled:
            self.logger.warning("RAGFlow is disabled in configuration")
            return
            
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Test connection and get/create knowledge base
        try:
            await self._ensure_knowledge_base()
            self.logger.info("Successfully connected to RAGFlow")
        except Exception as e:
            self.logger.error(f"Failed to connect to RAGFlow: {e}")
            raise RAGFlowError(f"Connection failed: {e}")
            
    async def disconnect(self):
        """Close connection to RAGFlow"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to RAGFlow API"""
        if not self.session:
            raise RAGFlowError("Not connected to RAGFlow")
            
        url = f"{self.config.api_url}/api/v1{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get("message", f"HTTP {response.status}")
                    raise RAGFlowError(f"API request failed: {error_msg}")
                    
                return response_data
                
        except aiohttp.ClientError as e:
            raise RAGFlowError(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise RAGFlowError(f"Invalid JSON response: {e}")
            
    async def _ensure_knowledge_base(self):
        """Ensure the knowledge base exists, create if not"""
        try:
            # List existing knowledge bases
            response = await self._make_request("POST", "/kb/list", {})
            kbs = response.get("data", {}).get("kbs", [])
            
            # Look for existing knowledge base
            for kb in kbs:
                if kb.get("name") == self.config.kb_name:
                    self.kb_id = kb.get("id")
                    self.logger.info(f"Found existing knowledge base: {self.kb_id}")
                    return
                    
            # Create new knowledge base
            create_data = {
                "name": self.config.kb_name,
                "description": "Compliant-One Regulatory Knowledge Base",
                "language": "English",
                "permission": "me",
                "doc_num": 0,
                "chunk_num": 0,
                "parser_id": "naive",
                "parser_config": {
                    "chunk_token_num": self.config.max_chunk_size,
                    "layout_recognize": True,
                    "delimiter": "\\n"
                }
            }
            
            response = await self._make_request("POST", "/kb/create", create_data)
            self.kb_id = response.get("data", {}).get("kb_id")
            self.logger.info(f"Created new knowledge base: {self.kb_id}")
            
        except Exception as e:
            raise RAGFlowError(f"Failed to setup knowledge base: {e}")
            
    async def upload_document(self, file_path: str, document_name: str, 
                            document_type: str = "regulatory") -> str:
        """Upload document to RAGFlow knowledge base"""
        if not self.kb_id:
            raise RAGFlowError("Knowledge base not initialized")
            
        try:
            # For this implementation, we'll use the document create endpoint
            # In a full implementation, you'd handle file upload properly
            doc_data = {
                "name": document_name,
                "type": document_type,
                "kb_id": self.kb_id,
                "parser_id": "naive",
                "parser_config": {
                    "chunk_token_num": self.config.max_chunk_size,
                    "layout_recognize": True
                }
            }
            
            response = await self._make_request("POST", "/document/create", doc_data)
            doc_id = response.get("data", {}).get("doc_id")
            
            self.logger.info(f"Uploaded document {document_name} with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            raise RAGFlowError(f"Failed to upload document: {e}")
            
    async def search_documents(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search documents in knowledge base"""
        if not self.kb_id:
            raise RAGFlowError("Knowledge base not initialized")
            
        try:
            search_data = {
                "kb_id": [self.kb_id],
                "question": query,
                "top_k": top_k,
                "similarity_threshold": self.config.similarity_threshold,
                "vector_similarity_weight": 0.3,
                "highlight": True
            }
            
            response = await self._make_request("POST", "/retrieval", search_data)
            return response.get("data", {}).get("chunks", [])
            
        except Exception as e:
            raise RAGFlowError(f"Search failed: {e}")
            
    async def ask_question(self, question: str, conversation_id: Optional[str] = None) -> Dict:
        """Ask question using RAG with compliance context"""
        if not self.kb_id:
            raise RAGFlowError("Knowledge base not initialized")
            
        try:
            # Create conversation if needed
            if not conversation_id:
                conv_response = await self._make_request("GET", "/new_conversation")
                conversation_id = conv_response.get("data", {}).get("id")
                
            # Ask question
            ask_data = {
                "conversation_id": conversation_id,
                "messages": [
                    {
                        "role": "user",
                        "content": f"As a compliance expert, please answer this question based on regulatory knowledge: {question}"
                    }
                ],
                "quote": True,
                "doc_ids": [],
                "kb_ids": [self.kb_id]
            }
            
            response = await self._make_request("POST", "/completion", ask_data)
            return response.get("data", {})
            
        except Exception as e:
            raise RAGFlowError(f"Question answering failed: {e}")
            
    async def get_document_status(self, doc_id: str) -> Dict:
        """Get document processing status"""
        try:
            response = await self._make_request("GET", f"/document/get/{doc_id}")
            return response.get("data", {})
            
        except Exception as e:
            raise RAGFlowError(f"Failed to get document status: {e}")
            
    async def list_documents(self) -> List[Dict]:
        """List all documents in knowledge base"""
        if not self.kb_id:
            raise RAGFlowError("Knowledge base not initialized")
            
        try:
            list_data = {
                "kb_id": self.kb_id,
                "page": 1,
                "page_size": 100,
                "orderby": "create_time",
                "desc": True
            }
            
            response = await self._make_request("POST", "/document/list", list_data)
            return response.get("data", {}).get("docs", [])
            
        except Exception as e:
            raise RAGFlowError(f"Failed to list documents: {e}")

class ComplianceKnowledgeManager:
    """Manages compliance-specific knowledge operations"""
    
    def __init__(self, ragflow_client: RAGFlowClient):
        self.client = ragflow_client
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    async def upload_regulation(self, regulation_file: str, regulation_name: str, 
                              jurisdiction: str = "international") -> str:
        """Upload regulatory document with compliance metadata"""
        document_name = f"{jurisdiction}_{regulation_name}_{datetime.now().strftime('%Y%m%d')}"
        
        try:
            doc_id = await self.client.upload_document(
                regulation_file, 
                document_name, 
                "regulation"
            )
            
            self.logger.info(f"Uploaded regulation: {regulation_name} ({jurisdiction})")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to upload regulation {regulation_name}: {e}")
            raise
            
    async def search_regulations(self, compliance_query: str, 
                               jurisdiction: Optional[str] = None) -> List[Dict]:
        """Search regulations with compliance context"""
        
        # Enhance query with compliance context
        enhanced_query = f"compliance regulation {compliance_query}"
        if jurisdiction:
            enhanced_query = f"{jurisdiction} {enhanced_query}"
            
        try:
            results = await self.client.search_documents(enhanced_query, top_k=10)
            
            # Filter and rank results for compliance relevance
            compliance_results = []
            for result in results:
                if self._is_compliance_relevant(result):
                    compliance_results.append({
                        **result,
                        "compliance_score": self._calculate_compliance_score(result, compliance_query)
                    })
                    
            # Sort by compliance score
            compliance_results.sort(key=lambda x: x.get("compliance_score", 0), reverse=True)
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Regulation search failed: {e}")
            raise
            
    async def get_compliance_guidance(self, scenario: str, 
                                    risk_level: str = "medium") -> Dict:
        """Get AI-powered compliance guidance for specific scenarios"""
        
        guidance_prompt = f"""
        As a compliance expert, provide guidance for the following scenario:
        
        Scenario: {scenario}
        Risk Level: {risk_level}
        
        Please provide:
        1. Applicable regulations and standards
        2. Required compliance actions
        3. Risk mitigation strategies
        4. Documentation requirements
        5. Recommended next steps
        
        Base your response on current regulatory requirements and best practices.
        """
        
        try:
            response = await self.client.ask_question(guidance_prompt)
            
            return {
                "scenario": scenario,
                "risk_level": risk_level,
                "guidance": response.get("answer", ""),
                "sources": response.get("reference", []),
                "timestamp": datetime.now().isoformat(),
                "confidence": response.get("prompt_tokens", 0) / 1000  # Simple confidence metric
            }
            
        except Exception as e:
            self.logger.error(f"Compliance guidance generation failed: {e}")
            raise
            
    def _is_compliance_relevant(self, search_result: Dict) -> bool:
        """Check if search result is relevant for compliance"""
        content = search_result.get("content_with_weight", "").lower()
        
        compliance_keywords = [
            "regulation", "compliance", "aml", "kyc", "fatf", "basel",
            "sanctions", "due diligence", "risk", "monitoring", "reporting"
        ]
        
        return any(keyword in content for keyword in compliance_keywords)
        
    def _calculate_compliance_score(self, search_result: Dict, query: str) -> float:
        """Calculate compliance relevance score"""
        content = search_result.get("content_with_weight", "").lower()
        query_terms = query.lower().split()
        
        # Simple scoring based on keyword matches
        score = 0.0
        for term in query_terms:
            if term in content:
                score += 1.0
                
        # Boost score for compliance-specific terms
        compliance_terms = ["regulation", "compliance", "aml", "kyc"]
        for term in compliance_terms:
            if term in content:
                score += 0.5
                
        # Normalize by content length
        content_length = len(content.split())
        if content_length > 0:
            score = score / (content_length / 100)  # Normalize per 100 words
            
        return min(score, 10.0)  # Cap at 10.0

# Service initialization
_ragflow_client: Optional[RAGFlowClient] = None
_knowledge_manager: Optional[ComplianceKnowledgeManager] = None

async def get_ragflow_client() -> RAGFlowClient:
    """Get initialized RAGFlow client"""
    global _ragflow_client
    
    if _ragflow_client is None:
        config = RAGFlowConfig()
        _ragflow_client = RAGFlowClient(config)
        await _ragflow_client.connect()
        
    return _ragflow_client

async def get_knowledge_manager() -> ComplianceKnowledgeManager:
    """Get initialized compliance knowledge manager"""
    global _knowledge_manager
    
    if _knowledge_manager is None:
        client = await get_ragflow_client()
        _knowledge_manager = ComplianceKnowledgeManager(client)
        
    return _knowledge_manager

async def cleanup_ragflow_services():
    """Cleanup RAGFlow services"""
    global _ragflow_client, _knowledge_manager
    
    if _ragflow_client:
        await _ragflow_client.disconnect()
        _ragflow_client = None
        
    _knowledge_manager = None
