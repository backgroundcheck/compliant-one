"""
Enhanced Document Processor with RAGFlow Integration
Provides advanced document processing capabilities for compliance documents
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import hashlib

from .ragflow_client import get_ragflow_client, get_knowledge_manager, RAGFlowError
from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DocumentMetadata:
    """Metadata for processed documents"""
    
    document_id: str
    name: str
    file_path: str
    file_type: str
    file_size: int
    checksum: str
    upload_timestamp: datetime
    processing_status: str
    document_type: str  # regulation, policy, template, report
    jurisdiction: Optional[str] = None
    regulation_type: Optional[str] = None  # aml, kyc, sanctions, etc.
    version: Optional[str] = None
    effective_date: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ProcessingResult:
    """Result of document processing"""
    
    success: bool
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    chunks_created: int = 0
    processing_time: float = 0.0
    metadata: Optional[DocumentMetadata] = None

class DocumentProcessor:
    """Enhanced document processor with RAGFlow integration"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.supported_formats = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel'
        }
        
    async def process_document(self, file_path: Union[str, Path], 
                             document_type: str = "regulation",
                             jurisdiction: Optional[str] = None,
                             tags: Optional[List[str]] = None) -> ProcessingResult:
        """Process document and upload to RAGFlow"""
        
        start_time = datetime.now()
        file_path = Path(file_path)
        
        try:
            # Validate file
            if not file_path.exists():
                return ProcessingResult(
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
                
            # Check file format
            file_ext = file_path.suffix.lower()
            if file_ext not in self.supported_formats:
                return ProcessingResult(
                    success=False,
                    error_message=f"Unsupported file format: {file_ext}"
                )
                
            # Generate metadata
            metadata = await self._generate_metadata(
                file_path, document_type, jurisdiction, tags
            )
            
            # Upload to RAGFlow
            client = await get_ragflow_client()
            document_id = await client.upload_document(
                str(file_path),
                metadata.name,
                document_type
            )
            
            metadata.document_id = document_id
            metadata.processing_status = "uploaded"
            
            # Wait for processing completion and get chunk count
            chunks_created = await self._wait_for_processing(client, document_id)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Successfully processed document {metadata.name}: "
                f"{chunks_created} chunks in {processing_time:.2f}s"
            )
            
            return ProcessingResult(
                success=True,
                document_id=document_id,
                chunks_created=chunks_created,
                processing_time=processing_time,
                metadata=metadata
            )
            
        except RAGFlowError as e:
            error_msg = f"RAGFlow processing failed: {e}"
            self.logger.error(error_msg)
            return ProcessingResult(success=False, error_message=error_msg)
            
        except Exception as e:
            error_msg = f"Document processing failed: {e}"
            self.logger.error(error_msg)
            return ProcessingResult(success=False, error_message=error_msg)
            
    async def process_regulatory_batch(self, regulation_directory: Union[str, Path],
                                     jurisdiction: str = "international") -> List[ProcessingResult]:
        """Process a batch of regulatory documents"""
        
        regulation_dir = Path(regulation_directory)
        if not regulation_dir.exists():
            raise ValueError(f"Directory not found: {regulation_dir}")
            
        results = []
        
        # Process all supported files in directory
        for file_path in regulation_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                self.logger.info(f"Processing regulatory document: {file_path.name}")
                
                # Determine regulation type from filename/path
                regulation_type = self._infer_regulation_type(file_path)
                tags = [jurisdiction, regulation_type, "regulation"]
                
                result = await self.process_document(
                    file_path,
                    document_type="regulation",
                    jurisdiction=jurisdiction,
                    tags=tags
                )
                
                results.append(result)
                
                # Small delay to avoid overwhelming the service
                await asyncio.sleep(1)
                
        successful = sum(1 for r in results if r.success)
        total = len(results)
        
        self.logger.info(f"Batch processing complete: {successful}/{total} documents processed")
        return results
        
    async def search_processed_documents(self, query: str, 
                                       document_type: Optional[str] = None,
                                       jurisdiction: Optional[str] = None) -> List[Dict]:
        """Search processed documents"""
        
        try:
            knowledge_manager = await get_knowledge_manager()
            
            # Enhance query with filters
            enhanced_query = query
            if document_type:
                enhanced_query = f"{document_type} {enhanced_query}"
            if jurisdiction:
                enhanced_query = f"{jurisdiction} {enhanced_query}"
                
            results = await knowledge_manager.search_regulations(
                enhanced_query, jurisdiction
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Document search failed: {e}")
            raise
            
    async def get_compliance_insights(self, document_id: str) -> Dict[str, Any]:
        """Extract compliance insights from processed document"""
        
        try:
            client = await get_ragflow_client()
            
            # Get document info
            doc_info = await client.get_document_status(document_id)
            
            # Ask for compliance analysis
            analysis_query = f"""
            Analyze this document for compliance insights:
            
            Document: {doc_info.get('name', 'Unknown')}
            
            Provide:
            1. Key compliance requirements identified
            2. Risk areas highlighted
            3. Relevant FATF recommendations
            4. Implementation guidelines
            5. Monitoring requirements
            
            Focus on actionable compliance insights.
            """
            
            response = await client.ask_question(analysis_query)
            
            return {
                "document_id": document_id,
                "document_name": doc_info.get('name', 'Unknown'),
                "analysis": response.get("answer", ""),
                "key_findings": self._extract_key_findings(response.get("answer", "")),
                "compliance_score": self._calculate_compliance_score(response.get("answer", "")),
                "references": response.get("reference", []),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Compliance insights extraction failed: {e}")
            raise
            
    async def _generate_metadata(self, file_path: Path, document_type: str,
                               jurisdiction: Optional[str], tags: Optional[List[str]]) -> DocumentMetadata:
        """Generate document metadata"""
        
        # Calculate file info
        file_size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        
        # Infer document properties
        regulation_type = self._infer_regulation_type(file_path)
        
        # Prepare tags
        final_tags = tags or []
        final_tags.extend([document_type, regulation_type])
        if jurisdiction:
            final_tags.append(jurisdiction)
            
        return DocumentMetadata(
            document_id="",  # Will be set after upload
            name=file_path.stem,
            file_path=str(file_path),
            file_type=file_path.suffix.lower(),
            file_size=file_size,
            checksum=checksum,
            upload_timestamp=datetime.now(),
            processing_status="pending",
            document_type=document_type,
            jurisdiction=jurisdiction,
            regulation_type=regulation_type,
            tags=list(set(final_tags))  # Remove duplicates
        )
        
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def _infer_regulation_type(self, file_path: Path) -> str:
        """Infer regulation type from file name/path"""
        
        path_str = str(file_path).lower()
        
        if any(term in path_str for term in ['aml', 'anti-money', 'laundering']):
            return 'aml'
        elif any(term in path_str for term in ['kyc', 'know-your-customer', 'customer-due-diligence']):
            return 'kyc'
        elif any(term in path_str for term in ['sanction', 'embargo', 'blacklist']):
            return 'sanctions'
        elif any(term in path_str for term in ['fatf', 'financial-action-task']):
            return 'fatf'
        elif any(term in path_str for term in ['basel', 'banking']):
            return 'basel'
        elif any(term in path_str for term in ['risk', 'assessment']):
            return 'risk_management'
        elif any(term in path_str for term in ['reporting', 'suspicious']):
            return 'reporting'
        else:
            return 'general'
            
    async def _wait_for_processing(self, client, document_id: str, 
                                 max_wait_time: int = 300) -> int:
        """Wait for document processing to complete and return chunk count"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < max_wait_time:
            try:
                doc_status = await client.get_document_status(document_id)
                status = doc_status.get("status", "unknown")
                
                if status == "1":  # Processing complete
                    return doc_status.get("chunk_num", 0)
                elif status == "2":  # Processing failed
                    raise RAGFlowError(f"Document processing failed: {doc_status.get('msg', 'Unknown error')}")
                    
                # Wait before checking again
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.warning(f"Error checking document status: {e}")
                await asyncio.sleep(5)
                
        # Timeout reached
        self.logger.warning(f"Document processing timeout reached for {document_id}")
        return 0
        
    def _extract_key_findings(self, analysis_text: str) -> List[str]:
        """Extract key compliance findings from analysis text"""
        
        findings = []
        lines = analysis_text.split('\n')
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                current_section = line
            elif line.startswith('-') and current_section:
                findings.append(f"{current_section}: {line[1:].strip()}")
                
        return findings[:10]  # Limit to top 10 findings
        
    def _calculate_compliance_score(self, analysis_text: str) -> float:
        """Calculate compliance score based on analysis content"""
        
        # Simple scoring based on compliance keywords presence
        compliance_indicators = [
            'compliant', 'requirement', 'mandatory', 'shall', 'must',
            'regulation', 'standard', 'guideline', 'framework', 'procedure'
        ]
        
        risk_indicators = [
            'risk', 'violation', 'non-compliant', 'deficiency', 'gap',
            'issue', 'concern', 'weakness', 'failure', 'breach'
        ]
        
        text_lower = analysis_text.lower()
        
        compliance_count = sum(1 for indicator in compliance_indicators if indicator in text_lower)
        risk_count = sum(1 for indicator in risk_indicators if indicator in text_lower)
        
        # Score between 0 and 10
        base_score = min(compliance_count * 0.5, 10.0)
        risk_penalty = min(risk_count * 0.3, 3.0)
        
        return max(base_score - risk_penalty, 0.0)

# Service instance
document_processor = DocumentProcessor()

async def process_compliance_document(file_path: Union[str, Path], 
                                    document_type: str = "regulation",
                                    jurisdiction: Optional[str] = None,
                                    tags: Optional[List[str]] = None) -> ProcessingResult:
    """Process a compliance document"""
    return await document_processor.process_document(
        file_path, document_type, jurisdiction, tags
    )

async def process_regulation_directory(directory_path: Union[str, Path],
                                     jurisdiction: str = "international") -> List[ProcessingResult]:
    """Process all regulatory documents in a directory"""
    return await document_processor.process_regulatory_batch(directory_path, jurisdiction)

async def search_compliance_documents(query: str, 
                                    document_type: Optional[str] = None,
                                    jurisdiction: Optional[str] = None) -> List[Dict]:
    """Search processed compliance documents"""
    return await document_processor.search_processed_documents(
        query, document_type, jurisdiction
    )

async def analyze_document_compliance(document_id: str) -> Dict[str, Any]:
    """Get compliance analysis for a processed document"""
    return await document_processor.get_compliance_insights(document_id)
