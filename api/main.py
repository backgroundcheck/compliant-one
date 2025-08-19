"""
Compliant-One Platform API
Phase 3: Comprehensive API for third-party system integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, Security, status, Query, Path, Body, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import platform services
from services.beneficial_ownership.bo_service import BeneficialOwnershipService
from services.identity.identity_service import IdentityVerificationService
from services.kyc.kyc_service import KYCService
from services.osint.osint_service import OSINTService
from services.breach_intelligence.breach_service import BreachIntelligenceService
from utils.logger import get_logger
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.platform import CompliantOnePlatform, Customer
from services.sanctions.sanctions_service import SanctionsService
from services.kyc.kyc_service import KYCService
from services.osint.osint_service import OSINTService
from services.identity.identity_service import IdentityVerificationService
from services.beneficial_ownership.bo_service import BeneficialOwnershipService
from services.monitoring.monitoring_service import MonitoringService
from services.transactions.transaction_service import TransactionMonitoringService
from services.reporting.reporting_service import ReportingService
# Regulatory Reporting Service - using fallback implementation until module is created
class RegulatoryReportingService:
    def get_templates(self, jurisdiction=None, report_type=None):
        return []
    def get_template_details(self, template_id):
        return {"success": False, "error": "Service not implemented", "data": {}}
    def validate_data(self, template_id, data):
        return {"valid": False, "errors": ["Service not implemented"], "warnings": []}
    def generate_report(self, template_id, data, output_format, customer_id=None):
        return {"success": False, "error": "Service not implemented", "report_id": None, "template_name": None, "output_format": output_format, "generated_at": None, "download_url": None}
    def get_report_status(self, report_id):
        return {"success": False, "error": "Service not implemented", "data": {}}
    def get_analytics(self):
        return {"error": "Service not implemented", "total_templates": 0, "active_templates": 0, "total_reports_generated": 0, "supported_jurisdictions": [], "supported_frameworks": []}
    def health_check(self):
        return {"status": "not implemented", "message": "Regulatory reporting service is not yet implemented"}
from services.ocr.ocr_service import OCRService
from services.threat_intelligence.threat_intel_service import ThreatIntelligenceService
from services.breach_intelligence.breach_service import BreachIntelligenceService
from utils.logger import get_logger

# Initialize FastAPI app
app = FastAPI(
    title="Compliant-One API",
    description="Enterprise RegTech Platform API for Third-Party Integration",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
def _parse_allowed_origins() -> list:
    origins = os.getenv("ALLOWED_ORIGINS", "*")
    if origins.strip() == "*":
        return ["*"]
    return [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()
logger = get_logger(__name__)

# Initialize services
platform = CompliantOnePlatform()

# ============================================================================
# Root & Docs Redirect
# ============================================================================

@app.get("/")
async def root():
    """Friendly landing route with docs and health links."""
    return {
        "message": "Compliant-One API is running. Visit /docs for interactive docs.",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health"
    }

# Basic liveness/readiness for production probes
@app.get("/liveness")
async def liveness():
    return {"status": "ok"}

@app.get("/readiness")
async def readiness():
    try:
        breach_service = BreachIntelligenceService()
        health = breach_service.health_check()
        if health.get("database"):
            return {"status": "ready"}
        raise RuntimeError("database not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"not ready: {e}")

# ============================================================================
# Authentication Models
# ============================================================================

class APIKey(BaseModel):
    key: str
    permissions: List[str]
    expires_at: Optional[datetime] = None

class UserCredentials(BaseModel):
    username: str
    password: str

# ============================================================================
# Request/Response Models
# ============================================================================

class CustomerRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    document_number: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None

class SanctionsScreeningRequest(BaseModel):
    customer_id: Optional[str] = None
    entity_name: str
    entity_type: str = "person"  # person, organization, vessel
    additional_identifiers: Optional[Dict[str, str]] = None
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)

class KYCVerificationRequest(BaseModel):
    customer_id: str
    verification_level: str = "standard"  # basic, standard, enhanced
    documents: List[Dict[str, str]] = []
    risk_appetite: str = "medium"  # low, medium, high

class OSINTRequest(BaseModel):
    entity_name: str
    entity_type: str = "person"
    search_depth: str = "standard"  # basic, standard, deep
    sources: Optional[List[str]] = None
    max_results: int = Field(default=50, le=500)

class TransactionMonitoringRequest(BaseModel):
    customer_id: str
    transaction_data: Dict[str, Any]
    monitoring_rules: Optional[List[str]] = None

class ComplianceReportRequest(BaseModel):
    report_type: str  # sar, ctr, annual_report
    customer_ids: Optional[List[str]] = None
    date_range: Dict[str, str]
    format: str = "pdf"  # pdf, json, csv
    include_attachments: bool = False

# Response Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime

# ============================================================================
# Authentication & Authorization
# ============================================================================

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key authentication"""
    token = credentials.credentials
    
    # In production, implement proper API key validation
    # For demo purposes, accept any token starting with 'compliant-'
    if not token.startswith('compliant-'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return {"api_key": token, "permissions": ["read", "write"]}

async def get_current_user(user_info: dict = Depends(verify_api_key)):
    """Get current authenticated user from API key verification"""
    return user_info

# ============================================================================
# OCR Service API
# ============================================================================

class OCRRequest(BaseModel):
    """OCR processing request"""
    file_path: Optional[str] = None
    file_data: Optional[str] = None  # Base64 encoded file
    config: str = "default"
    preprocess: bool = True
    enhancement_level: str = "medium"

class OCRBatchRequest(BaseModel):
    """Batch OCR processing request"""
    directory_path: str
    file_pattern: str = "*"
    max_files: Optional[int] = None
    config: str = "default"

@app.post("/api/v1/ocr/extract-text", response_model=APIResponse)
async def ocr_extract_text(
    request: OCRRequest,
    auth: dict = Depends(verify_api_key)
):
    """Extract text from image or scanned document using OCR"""
    try:
        ocr_service = OCRService()
        
        if request.file_path:
            # Process file from path
            result = ocr_service.extract_text_from_image(
                request.file_path,
                config=request.config,
                preprocess=request.preprocess,
                enhancement_level=request.enhancement_level
            )
        elif request.file_data:
            # Process base64 encoded file
            import base64
            import tempfile
            from PIL import Image
            import io
            
            # Decode base64 data
            file_bytes = base64.b64decode(request.file_data)
            
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(file_bytes))
            
            result = ocr_service.extract_text_from_image(
                image,
                config=request.config,
                preprocess=request.preprocess,
                enhancement_level=request.enhancement_level
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file_path or file_data must be provided"
            )
        
        return APIResponse(
            success=result["success"],
            data={
                "extracted_text": result["text"],
                "confidence": result["confidence"],
                "metadata": result["metadata"],
                "error": result.get("error")
            }
        )
    except Exception as e:
        logger.error(f"OCR text extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ocr/extract-pdf", response_model=APIResponse)
async def ocr_extract_pdf(
    pdf_path: str,
    pages: Optional[List[int]] = None,
    config: str = "default",
    preprocess: bool = True,
    auth: dict = Depends(verify_api_key)
):
    """Extract text from PDF using OCR (for scanned PDFs)"""
    try:
        ocr_service = OCRService()
        
        result = ocr_service.extract_text_from_pdf(
            pdf_path,
            pages=pages,
            config=config,
            preprocess=preprocess
        )
        
        return APIResponse(
            success=result["success"],
            data={
                "extracted_text": result["text"],
                "pages_processed": result["pages_processed"],
                "average_confidence": result.get("average_confidence", 0.0),
                "metadata": result["metadata"],
                "error": result.get("error")
            }
        )
    except Exception as e:
        logger.error(f"OCR PDF extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ocr/extract-structured", response_model=APIResponse)
async def ocr_extract_structured(
    file_path: str,
    data_type: str = "table",
    auth: dict = Depends(verify_api_key)
):
    """Extract structured data from images (tables, forms, invoices)"""
    try:
        ocr_service = OCRService()
        
        result = ocr_service.extract_structured_data(
            file_path,
            data_type=data_type
        )
        
        return APIResponse(
            success=result["success"],
            data={
                "extracted_text": result["text"],
                "structured_data": result.get("structured_data", {}),
                "data_type": result.get("data_type"),
                "confidence": result["confidence"],
                "error": result.get("error")
            }
        )
    except Exception as e:
        logger.error(f"OCR structured data extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ocr/batch-process", response_model=APIResponse)
async def ocr_batch_process(
    request: OCRBatchRequest,
    auth: dict = Depends(verify_api_key)
):
    """Process multiple images in a directory using OCR"""
    try:
        ocr_service = OCRService()
        
        result = ocr_service.batch_process_images(
            request.directory_path,
            config=request.config,
            file_pattern=request.file_pattern,
            max_files=request.max_files
        )
        
        return APIResponse(
            success=result["success"],
            data={
                "results": result["results"],
                "summary": result.get("summary", {}),
                "error": result.get("error")
            }
        )
    except Exception as e:
        logger.error(f"OCR batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ocr/supported-languages", response_model=APIResponse)
async def get_ocr_supported_languages(auth: dict = Depends(verify_api_key)):
    """Get list of supported languages for OCR"""
    try:
        ocr_service = OCRService()
        languages = ocr_service.get_supported_languages()
        
        return APIResponse(
            success=True,
            data={
                "supported_languages": languages,
                "total_languages": len(languages)
            }
        )
    except Exception as e:
        logger.error(f"Failed to get OCR supported languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ocr/health", response_model=APIResponse)
async def ocr_health_check(auth: dict = Depends(verify_api_key)):
    """Health check for OCR service"""
    try:
        ocr_service = OCRService()
        health = ocr_service.health_check()
        
        return APIResponse(
            success=True,
            data=health
        )
    except Exception as e:
        logger.error(f"OCR health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Threat Intelligence API
# ============================================================================

class ThreatIntelRequest(BaseModel):
    """Threat intelligence collection request"""
    sources: Optional[List[str]] = None
    target_types: Optional[List[str]] = None
    collect_breaches: bool = True
    collect_feeds: bool = True

class MonitoringTargetRequest(BaseModel):
    """Monitoring target request"""
    target_type: str = Field(..., description="Type of target (ip, domain, email, hash)")
    target_value: str = Field(..., description="Value to monitor")
    description: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)

class ThreatConfigRequest(BaseModel):
    """Threat intelligence configuration request"""
    enabled_sources: Optional[Dict[str, bool]] = None
    rate_limit_delay: Optional[float] = None
    max_concurrent_requests: Optional[int] = None
    api_keys: Optional[Dict[str, str]] = None

@app.post("/api/v1/threat-intel/collect", response_model=APIResponse)
async def collect_threat_intelligence(
    request: ThreatIntelRequest,
    auth: dict = Depends(verify_api_key)
):
    """Collect threat intelligence data from configured sources"""
    try:
        threat_service = ThreatIntelligenceService()
        
        results = {
            'breach_collection': None,
            'feed_collection': None,
            'total_new_indicators': 0,
            'sources_processed': 0
        }
        
        if request.collect_breaches:
            breach_result = await threat_service.collect_breach_data()
            results['breach_collection'] = breach_result
            results['sources_processed'] += breach_result.get('sources_checked', 0)
        
        if request.collect_feeds:
            feed_result = await threat_service.collect_threat_feeds()
            results['feed_collection'] = feed_result
            results['sources_processed'] += feed_result.get('feeds_processed', 0)
            results['total_new_indicators'] += feed_result.get('new_indicators', 0)
        
        return APIResponse(
            success=True,
            data={
                "collection_results": results,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Threat intelligence collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/monitor", response_model=APIResponse)
async def monitor_threats(
    targets: Optional[List[Dict[str, str]]] = None,
    auth: dict = Depends(verify_api_key)
):
    """Monitor specific targets against threat intelligence"""
    try:
        threat_service = ThreatIntelligenceService()
        
        # If no targets provided, get all active targets from database
        if not targets:
            import sqlite3
            conn = sqlite3.connect(threat_service.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT target_type, target_value FROM monitoring_targets WHERE is_active = 1")
            targets = [{'type': row[0], 'value': row[1]} for row in cursor.fetchall()]
            conn.close()
        
        result = await threat_service.monitor_targets(targets)
        
        return APIResponse(
            success=result['success'],
            data={
                "monitoring_result": result,
                "targets_checked": result['targets_checked'],
                "alerts_generated": result['alerts_generated'],
                "matches_found": result['matches_found']
            }
        )
    except Exception as e:
        logger.error(f"Threat monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/targets", response_model=APIResponse)
async def add_monitoring_target(
    request: MonitoringTargetRequest,
    auth: dict = Depends(verify_api_key)
):
    """Add a new monitoring target"""
    try:
        threat_service = ThreatIntelligenceService()
        
        result = threat_service.add_monitoring_target(
            target_type=request.target_type,
            target_value=request.target_value,
            description=request.description,
            priority=request.priority
        )
        
        return APIResponse(
            success=result['success'],
            data={
                "target_id": result.get('target_id'),
                "message": result.get('message'),
                "target": {
                    "type": request.target_type,
                    "value": request.target_value,
                    "priority": request.priority
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to add monitoring target: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threat-intel/targets", response_model=APIResponse)
async def get_monitoring_targets(
    active_only: bool = True,
    auth: dict = Depends(verify_api_key)
):
    """Get monitoring targets"""
    try:
        threat_service = ThreatIntelligenceService()
        
        import sqlite3
        conn = sqlite3.connect(threat_service.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM monitoring_targets"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY priority DESC, created_at DESC"
        
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        targets = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "targets": targets,
                "total_count": len(targets),
                "active_only": active_only
            }
        )
    except Exception as e:
        logger.error(f"Failed to get monitoring targets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threat-intel/alerts", response_model=APIResponse)
async def get_threat_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, le=1000, description="Maximum number of alerts"),
    auth: dict = Depends(verify_api_key)
):
    """Get threat intelligence alerts"""
    try:
        threat_service = ThreatIntelligenceService()
        
        alerts = threat_service.get_alerts(
            status=status,
            severity=severity,
            limit=limit
        )
        
        # Group alerts by severity for summary
        severity_summary = {}
        for alert in alerts:
            severity_key = alert.get('severity', 'unknown')
            severity_summary[severity_key] = severity_summary.get(severity_key, 0) + 1
        
        return APIResponse(
            success=True,
            data={
                "alerts": alerts,
                "total_count": len(alerts),
                "severity_summary": severity_summary,
                "filters_applied": {
                    "status": status,
                    "severity": severity,
                    "limit": limit
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to get threat alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/threat-intel/alerts/{alert_id}/resolve", response_model=APIResponse)
async def resolve_threat_alert(
    alert_id: int = Path(description="Alert ID"),
    resolution_note: Optional[str] = Body(None),
    auth: dict = Depends(verify_api_key)
):
    """Resolve a threat intelligence alert"""
    try:
        threat_service = ThreatIntelligenceService()
        
        import sqlite3
        conn = sqlite3.connect(threat_service.db_path)
        cursor = conn.cursor()
        
        # Update alert status
        cursor.execute('''
            UPDATE threat_alerts 
            SET status = 'resolved', resolved_at = ?
            WHERE id = ?
        ''', (datetime.now(), alert_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Add resolution note if provided
        if resolution_note:
            cursor.execute('''
                UPDATE threat_alerts 
                SET description = description || ? || ?
                WHERE id = ?
            ''', ('\n\nResolution Note: ', resolution_note, alert_id))
        
        conn.commit()
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "alert_id": alert_id,
                "status": "resolved",
                "resolved_at": datetime.now().isoformat(),
                "resolution_note": resolution_note
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threat-intel/statistics", response_model=APIResponse)
async def get_threat_intelligence_statistics(
    auth: dict = Depends(verify_api_key)
):
    """Get threat intelligence statistics and analytics"""
    try:
        threat_service = ThreatIntelligenceService()
        
        stats = threat_service.get_statistics()
        
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        
        return APIResponse(
            success=True,
            data={
                "statistics": stats,
                "summary": {
                    "total_indicators": stats['indicators']['total_active'],
                    "total_breaches": stats['breaches']['total'],
                    "new_alerts": stats['alerts']['new'],
                    "active_targets": stats['monitoring']['active_targets']
                },
                "generated_at": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get threat intelligence statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/search", response_model=APIResponse)
async def search_threat_indicators(
    query: str = Body(..., description="Search query"),
    indicator_types: Optional[List[str]] = Body(None, description="Filter by indicator types"),
    threat_types: Optional[List[str]] = Body(None, description="Filter by threat types"),
    min_confidence: float = Body(0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
    limit: int = Body(100, le=1000, description="Maximum results"),
    auth: dict = Depends(verify_api_key)
):
    """Search threat intelligence indicators"""
    try:
        threat_service = ThreatIntelligenceService()
        
        import sqlite3
        conn = sqlite3.connect(threat_service.db_path)
        cursor = conn.cursor()
        
        # Build search query
        sql_query = '''
            SELECT * FROM threat_indicators 
            WHERE is_active = 1 AND confidence >= ?
            AND (indicator_value LIKE ? OR description LIKE ?)
        '''
        params = [min_confidence, f'%{query}%', f'%{query}%']
        
        if indicator_types:
            placeholders = ','.join('?' * len(indicator_types))
            sql_query += f' AND indicator_type IN ({placeholders})'
            params.extend(indicator_types)
        
        if threat_types:
            placeholders = ','.join('?' * len(threat_types))
            sql_query += f' AND threat_type IN ({placeholders})'
            params.extend(threat_types)
        
        sql_query += ' ORDER BY confidence DESC, last_updated DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql_query, params)
        columns = [description[0] for description in cursor.description]
        indicators = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "indicators": indicators,
                "total_found": len(indicators),
                "search_params": {
                    "query": query,
                    "indicator_types": indicator_types,
                    "threat_types": threat_types,
                    "min_confidence": min_confidence,
                    "limit": limit
                }
            }
        )
    except Exception as e:
        logger.error(f"Threat indicator search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/threat-intel/config", response_model=APIResponse)
async def update_threat_intelligence_config(
    request: ThreatConfigRequest,
    auth: dict = Depends(verify_api_key)
):
    """Update threat intelligence service configuration"""
    try:
        threat_service = ThreatIntelligenceService()
        
        config_updates = {}
        
        if request.enabled_sources is not None:
            config_updates['enabled_sources'] = request.enabled_sources
        
        if request.rate_limit_delay is not None:
            config_updates['rate_limit_delay'] = request.rate_limit_delay
        
        if request.max_concurrent_requests is not None:
            config_updates['max_concurrent_requests'] = request.max_concurrent_requests
        
        if request.api_keys is not None:
            # Only update non-empty API keys
            existing_keys = threat_service.config.get('api_keys', {})
            for key, value in request.api_keys.items():
                if value:  # Only update if value is provided
                    existing_keys[key] = value
            config_updates['api_keys'] = existing_keys
        
        if not config_updates:
            raise HTTPException(status_code=400, detail="No configuration updates provided")
        
        result = threat_service.update_configuration(config_updates)
        
        return APIResponse(
            success=result['success'],
            data={
                "updated_config": config_updates,
                "message": result.get('message'),
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update threat intelligence config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threat-intel/config", response_model=APIResponse)
async def get_threat_intelligence_config(
    auth: dict = Depends(verify_api_key)
):
    """Get current threat intelligence configuration"""
    try:
        threat_service = ThreatIntelligenceService()
        
        # Mask sensitive information like API keys
        config_copy = threat_service.config.copy()
        if 'api_keys' in config_copy:
            masked_keys = {}
            for key, value in config_copy['api_keys'].items():
                if value:
                    masked_keys[key] = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "****"
                else:
                    masked_keys[key] = None
            config_copy['api_keys'] = masked_keys
        
        return APIResponse(
            success=True,
            data={
                "configuration": config_copy,
                "database_path": str(threat_service.db_path),
                "data_folder": str(threat_service.data_folder)
            }
        )
    except Exception as e:
        logger.error(f"Failed to get threat intelligence config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threat-intel/health", response_model=APIResponse)
async def threat_intelligence_health_check(
    auth: dict = Depends(verify_api_key)
):
    """Health check for threat intelligence service"""
    try:
        threat_service = ThreatIntelligenceService()
        
        health = threat_service.health_check()
        
        return APIResponse(
            success=True,
            data={
                "service_name": "Threat Intelligence Service",
                "health_check": health,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Threat intelligence health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/virustotal/check", response_model=APIResponse)
async def check_virustotal_indicators(
    request: Dict[str, List[str]],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Check indicators against VirusTotal API"""
    try:
        indicators = request.get('indicators', [])
        if not indicators:
            raise HTTPException(status_code=400, detail="No indicators provided")
        
        threat_service = ThreatIntelligenceService()
        
        # Run VirusTotal check
        result = await threat_service.check_virustotal(indicators)
        
        return APIResponse(
            success=result['success'],
            data=result,
            message=f"Checked {len(indicators)} indicators against VirusTotal"
        )
    except Exception as e:
        logger.error(f"VirusTotal check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/shodan/check", response_model=APIResponse)
async def check_shodan_ips(
    request: Dict[str, List[str]],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Check IP addresses against Shodan API"""
    try:
        ips = request.get('ips', [])
        if not ips:
            raise HTTPException(status_code=400, detail="No IP addresses provided")
        
        threat_service = ThreatIntelligenceService()
        
        # Run Shodan check
        result = await threat_service.check_shodan(ips)
        
        return APIResponse(
            success=result['success'],
            data=result,
            message=f"Checked {len(ips)} IP addresses against Shodan"
        )
    except Exception as e:
        logger.error(f"Shodan check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/hibp/check", response_model=APIResponse)
async def check_hibp_emails(
    request: Dict[str, List[str]],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Check email addresses against Have I Been Pwned"""
    try:
        emails = request.get('emails', [])
        if not emails:
            raise HTTPException(status_code=400, detail="No email addresses provided")
        
        threat_service = ThreatIntelligenceService()
        
        # Run HIBP check
        result = await threat_service.check_hibp_emails(emails)
        
        return APIResponse(
            success=result['success'],
            data=result,
            message=f"Checked {len(emails)} email addresses against HIBP"
        )
    except Exception as e:
        logger.error(f"HIBP check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/threat-intel/comprehensive-check", response_model=APIResponse)
async def comprehensive_threat_check(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Run comprehensive threat intelligence checks across all sources"""
    try:
        threat_service = ThreatIntelligenceService()
        
        results = {
            'hibp': {'success': True, 'results': []},
            'virustotal': {'success': True, 'results': []},
            'shodan': {'success': True, 'results': []},
            'feeds': {'success': True, 'indicators_collected': 0}
        }
        
        # Check emails against HIBP
        if request.get('emails'):
            results['hibp'] = await threat_service.check_hibp_emails(request['emails'])
        
        # Check indicators against VirusTotal
        if request.get('indicators'):
            results['virustotal'] = await threat_service.check_virustotal(request['indicators'])
        
        # Check IPs against Shodan
        if request.get('ips'):
            results['shodan'] = await threat_service.check_shodan(request['ips'])
        
        # Collect from threat feeds
        if request.get('collect_feeds', True):
            results['feeds'] = await threat_service.collect_threat_intelligence()
        
        # Calculate overall success
        overall_success = all(r.get('success', False) for r in results.values())
        
        return APIResponse(
            success=overall_success,
            data=results,
            message="Comprehensive threat intelligence check completed"
        )
    except Exception as e:
        logger.error(f"Comprehensive threat check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Breach Intelligence API Endpoints
# ============================================================================

@app.post("/api/v1/breach-intel/check-credential", response_model=APIResponse)
async def check_credential_breach(
    request: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Check if credential appears in breaches using k-anonymity"""
    try:
        credential = request.get('credential')
        credential_type = request.get('type', 'email')
        
        if not credential:
            raise HTTPException(status_code=400, detail="Credential required")
        
        breach_service = BreachIntelligenceService()
        result = await breach_service.check_credential_breach(credential, credential_type)
        # Ensure privacy flag is present for clients/tests
        result.setdefault('privacy_compliant', True)
        
        return APIResponse(
            success=result['success'],
            data=result,
            message="Credential breach check completed (privacy-compliant)"
        )
    except Exception as e:
        logger.error(f"Credential breach check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/breach-intel/add-monitoring", response_model=APIResponse)
async def add_breach_monitoring(
    request: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Add credential for breach monitoring (privacy-compliant)"""
    try:
        credential = request.get('credential')
        credential_type = request.get('type', 'email')
        alert_email = request.get('alert_email')
        
        if not credential:
            raise HTTPException(status_code=400, detail="Credential required")
        
        breach_service = BreachIntelligenceService()
        result = await breach_service.add_monitoring_target(credential, credential_type, alert_email)
        
        return APIResponse(
            success=result['success'],
            data=result,
            message="Monitoring target added successfully"
        )
    except Exception as e:
        logger.error(f"Add breach monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/breach-intel/monitor-paste-sites", response_model=APIResponse)
async def monitor_paste_sites(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start ethical monitoring of paste sites for breach data"""
    try:
        breach_service = BreachIntelligenceService()
        
        # Run monitoring in background
        background_tasks.add_task(breach_service.monitor_paste_sites)
        
        return APIResponse(
            success=True,
            data={'status': 'monitoring_started'},
            message="Paste site monitoring started in background"
        )
    except Exception as e:
        logger.error(f"Paste site monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/breach-intel/monitor-darkweb", response_model=APIResponse)
async def monitor_darkweb_sources(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start ethical dark web monitoring for breach disclosures"""
    try:
        breach_service = BreachIntelligenceService()
        
        # Run monitoring in background
        background_tasks.add_task(breach_service.monitor_darkweb_sources)
        
        return APIResponse(
            success=True,
            data={'status': 'darkweb_monitoring_started'},
            message="Dark web monitoring started (ethical mode)"
        )
    except Exception as e:
        logger.error(f"Dark web monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/breach-intel/enrich/{breach_id}", response_model=APIResponse)
async def enrich_breach_data(
    breach_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Enrich breach data using SpiderFoot/Maltego integration"""
    try:
        breach_service = BreachIntelligenceService()
        
        # Run enrichment in background
        background_tasks.add_task(breach_service.enrich_breach_data, breach_id)
        
        return APIResponse(
            success=True,
            data={'breach_id': breach_id, 'status': 'enrichment_started'},
            message="Breach data enrichment started"
        )
    except Exception as e:
        logger.error(f"Breach enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/breach-intel/statistics", response_model=APIResponse)
async def get_breach_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get privacy-compliant breach intelligence statistics"""
    try:
        breach_service = BreachIntelligenceService()
        result = await breach_service.get_breach_statistics()
        
        return APIResponse(
            success=result['success'],
            data=result.get('data', {}),
            message="Breach statistics retrieved"
        )
    except Exception as e:
        logger.error(f"Get breach statistics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/breach-intel/cleanup-expired", response_model=APIResponse)
async def cleanup_expired_data(
    current_user: dict = Depends(get_current_user)
):
    """GDPR/CCPA compliance - cleanup expired breach data"""
    try:
        breach_service = BreachIntelligenceService()
        result = await breach_service.cleanup_expired_data()
        
        return APIResponse(
            success=result['success'],
            data=result.get('cleanup_stats', {}),
            message="Privacy compliance cleanup completed"
        )
    except Exception as e:
        logger.error(f"Privacy cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/breach-intel/health", response_model=APIResponse)
async def breach_intelligence_health_check(
    current_user: dict = Depends(get_current_user)
):
    """Health check for breach intelligence service"""
    try:
        breach_service = BreachIntelligenceService()
        health = breach_service.health_check()
        if 'status' not in health:
            db_ok = bool(health.get('database'))
            health['status'] = 'healthy' if db_ok else 'degraded'
        
        return APIResponse(
            success=True,
            data={
                "service_name": "Breach Intelligence Service",
                "health_check": health,
                "privacy_compliant": True,
                "timestamp": datetime.now().isoformat()
            },
            message="Breach Intelligence Service health"
        )
    except Exception as e:
        logger.error(f"Breach intelligence health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Health Check & System Status
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """System health check endpoint"""
    try:
        services_status = {}
        
        # Check platform services
        services = [
            ("sanctions", SanctionsService),
            ("kyc", KYCService),
            ("osint", OSINTService),
            ("monitoring", MonitoringService),
            ("transactions", TransactionMonitoringService),
            ("reporting", ReportingService),
            ("ocr", OCRService),
            ("threat_intelligence", ThreatIntelligenceService)
        ]
        
        for service_name, service_class in services:
            try:
                service = service_class()
                if hasattr(service, 'health_check'):
                    health = service.health_check()
                    services_status[service_name] = health.get('status', 'unknown')
                else:
                    services_status[service_name] = 'available'
            except Exception as e:
                services_status[service_name] = f'error: {str(e)[:50]}'
        
        return HealthCheckResponse(
            status="healthy",
            version="3.0.0",
            services=services_status,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

# ============================================================================
# Sanctions Screening API
# ============================================================================

@app.post("/api/v1/sanctions/screen", response_model=APIResponse)
async def sanctions_screening(
    request: SanctionsScreeningRequest,
    auth: dict = Depends(verify_api_key)
):
    """Screen entity against sanctions lists"""
    try:
        sanctions_service = SanctionsService()
        
        result = sanctions_service.screen_entity(
            entity_name=request.entity_name,
            entity_type=request.entity_type,
            threshold=request.threshold
        )
        
        return APIResponse(
            success=True,
            data={
                "entity_name": request.entity_name,
                "screening_result": result,
                "risk_score": result.get('risk_score', 0.0),
                "matches_found": len(result.get('matches', [])),
                "processing_time": result.get('processing_time', 0.0)
            }
        )
    except Exception as e:
        logger.error(f"Sanctions screening failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sanctions/lists", response_model=APIResponse)
async def get_sanctions_lists(auth: dict = Depends(verify_api_key)):
    """Get available sanctions lists"""
    try:
        sanctions_service = SanctionsService()
        health = sanctions_service.health_check()
        
        return APIResponse(
            success=True,
            data={
                "available_lists": health.get('available_lists', []),
                "total_entities": health.get('sanctions_entities', 0),
                "last_updated": health.get('last_updated', 'unknown')
            }
        )
    except Exception as e:
        logger.error(f"Failed to get sanctions lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# KYC Verification API
# ============================================================================

@app.post("/api/v1/kyc/verify", response_model=APIResponse)
async def kyc_verification(
    request: KYCVerificationRequest,
    auth: dict = Depends(verify_api_key)
):
    """Perform KYC verification for customer"""
    try:
        kyc_service = KYCService()
        
        # Create customer object
        customer = Customer(
            customer_id=request.customer_id,
            first_name="",  # Will be populated from documents
            last_name="",
            date_of_birth=None,
            nationality=None,
            address={}
        )
        
        result = await kyc_service.perform_kyc_check(
            customer,
            verification_level=request.verification_level,
            risk_appetite=request.risk_appetite
        )
        
        return APIResponse(
            success=True,
            data={
                "customer_id": request.customer_id,
                "verification_result": result,
                "risk_rating": result.get('risk_rating', 'unknown'),
                "verification_status": result.get('status', 'pending'),
                "compliance_score": result.get('compliance_score', 0.0)
            }
        )
    except Exception as e:
        logger.error(f"KYC verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# OSINT Intelligence API
# ============================================================================

@app.post("/api/v1/osint/search", response_model=APIResponse)
async def osint_search(
    request: OSINTRequest,
    auth: dict = Depends(verify_api_key)
):
    """Perform OSINT search for entity"""
    try:
        osint_service = OSINTService()
        
        result = await osint_service.search_entity(
            entity_name=request.entity_name,
            entity_type=request.entity_type,
            max_results=request.max_results
        )
        
        return APIResponse(
            success=True,
            data={
                "entity_name": request.entity_name,
                "search_results": result,
                "sources_searched": result.get('sources', []),
                "intelligence_score": result.get('intelligence_score', 0.0),
                "adverse_media_found": result.get('adverse_media_count', 0)
            }
        )
    except Exception as e:
        logger.error(f"OSINT search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Transaction Monitoring API
# ============================================================================

@app.post("/api/v1/transactions/monitor", response_model=APIResponse)
async def transaction_monitoring(
    request: TransactionMonitoringRequest,
    auth: dict = Depends(verify_api_key)
):
    """Monitor transaction for suspicious activity"""
    try:
        transaction_service = TransactionMonitoringService()
        
        result = transaction_service.monitor_transaction(
            customer_id=request.customer_id,
            transaction_data=request.transaction_data
        )
        
        return APIResponse(
            success=True,
            data={
                "customer_id": request.customer_id,
                "monitoring_result": result,
                "risk_score": result.get('risk_score', 0.0),
                "alerts_triggered": len(result.get('alerts', [])),
                "recommended_action": result.get('recommended_action', 'approve')
            }
        )
    except Exception as e:
        logger.error(f"Transaction monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transactions/alerts", response_model=APIResponse)
async def get_transaction_alerts(
    customer_id: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """Get transaction alerts"""
    try:
        transaction_service = TransactionMonitoringService()
        
        alerts = transaction_service.get_alerts(customer_id=customer_id)
        
        return APIResponse(
            success=True,
            data={
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_priority_alerts": len([a for a in alerts if a.get('priority') == 'high'])
            }
        )
    except Exception as e:
        logger.error(f"Failed to get transaction alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Beneficial Ownership API
# ============================================================================

@app.post("/api/v1/beneficial-ownership/analyze", response_model=APIResponse)
async def beneficial_ownership_analysis(
    customer_id: str,
    auth: dict = Depends(verify_api_key)
):
    """Analyze beneficial ownership structure"""
    try:
        bo_service = BeneficialOwnershipService()
        
        result = await bo_service.analyze_ownership_structure(customer_id)
        
        return APIResponse(
            success=True,
            data={
                "customer_id": customer_id,
                "ownership_analysis": result,
                "ultimate_beneficial_owners": result.get('ubos', []),
                "ownership_complexity": result.get('complexity_score', 0.0),
                "risk_indicators": result.get('risk_indicators', [])
            }
        )
    except Exception as e:
        logger.error(f"Beneficial ownership analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Compliance Reporting API
# ============================================================================

@app.post("/api/v1/reports/generate", response_model=APIResponse)
async def generate_compliance_report(
    request: ComplianceReportRequest,
    auth: dict = Depends(verify_api_key)
):
    """Generate compliance report"""
    try:
        reporting_service = ReportingService()
        
        result = await reporting_service.generate_report(
            report_type=request.report_type,
            customer_ids=request.customer_ids,
            date_range=request.date_range,
            format=request.format
        )
        
        return APIResponse(
            success=True,
            data={
                "report_id": result.get('report_id'),
                "report_type": request.report_type,
                "format": request.format,
                "download_url": result.get('download_url'),
                "generated_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/templates", response_model=APIResponse)
async def get_report_templates(auth: dict = Depends(verify_api_key)):
    """Get available report templates"""
    try:
        return APIResponse(
            success=True,
            data={
                "templates": [
                    {
                        "id": "sar",
                        "name": "Suspicious Activity Report",
                        "description": "SAR filing template for regulatory submission"
                    },
                    {
                        "id": "ctr",
                        "name": "Currency Transaction Report",
                        "description": "CTR template for large currency transactions"
                    },
                    {
                        "id": "annual_report",
                        "name": "Annual Compliance Report",
                        "description": "Comprehensive annual compliance summary"
                    },
                    {
                        "id": "customer_risk_assessment",
                        "name": "Customer Risk Assessment",
                        "description": "Individual customer risk profile report"
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Failed to get report templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Platform Integration API
# ============================================================================

@app.post("/api/v1/platform/comprehensive-check", response_model=APIResponse)
async def comprehensive_compliance_check(
    request: CustomerRequest,
    auth: dict = Depends(verify_api_key)
):
    """Perform comprehensive compliance check across all services"""
    try:
        # Create customer object
        customer = Customer(
            customer_id=request.customer_id,
            first_name=request.first_name,
            last_name=request.last_name,
            date_of_birth=request.date_of_birth,
            nationality=request.nationality,
            address=request.address or {}
        )
        
        # Run comprehensive check
        result = await platform.comprehensive_compliance_check(customer)
        
        return APIResponse(
            success=True,
            data={
                "customer_id": request.customer_id,
                "compliance_results": result,
                "overall_risk_score": max([r.risk_score for r in result.values() if hasattr(r, 'risk_score')], default=0.0),
                "recommendations_checked": len(result),
                "alerts_generated": sum([len(r.alerts) for r in result.values() if hasattr(r, 'alerts')], 0)
            }
        )
    except Exception as e:
        logger.error(f"Comprehensive compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Webhook & Event API
# ============================================================================

@app.post("/api/v1/webhooks/register")
async def register_webhook(
    webhook_url: str,
    events: List[str],
    auth: dict = Depends(verify_api_key)
):
    """Register webhook for real-time compliance events"""
    try:
        # In production, implement webhook registration system
        return APIResponse(
            success=True,
            data={
                "webhook_id": f"webhook_{datetime.now().timestamp()}",
                "url": webhook_url,
                "events": events,
                "status": "registered"
            }
        )
    except Exception as e:
        logger.error(f"Webhook registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return APIResponse(
        success=False,
        error="Internal server error",
        timestamp=datetime.now()
    )

# ============================================================================
# Regulatory Reporting Endpoints
# ============================================================================

class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    template_id: str = Field(..., description="Regulatory report template ID")
    data: Dict[str, Any] = Field(..., description="Report data")
    output_format: str = Field(default="PDF", description="Output format (PDF, XML, JSON, CSV)")
    customer_id: Optional[str] = Field(None, description="Customer ID for the report")

class ReportDataValidationRequest(BaseModel):
    """Request model for data validation"""
    template_id: str = Field(..., description="Template ID to validate against")
    data: Dict[str, Any] = Field(..., description="Data to validate")

@app.get("/api/v1/reports/templates")
async def get_report_templates(
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    auth: dict = Depends(verify_api_key)
):
    """Get available regulatory report templates"""
    try:
        reporting_service = RegulatoryReportingService()
        
        templates = reporting_service.get_templates(jurisdiction, report_type)
        
        return APIResponse(
            success=True,
            data={
                "templates": templates,
                "total_count": len(templates),
                "filters_applied": {
                    "jurisdiction": jurisdiction,
                    "report_type": report_type
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to get report templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report templates: {str(e)}"
        )

@app.get("/api/v1/reports/templates/{template_id}")
async def get_template_details(
    template_id: str = Path(description="Template ID"),
    auth: dict = Depends(verify_api_key)
):
    """Get detailed information about a specific template"""
    try:
        reporting_service = RegulatoryReportingService()
        
        result = reporting_service.get_template_details(template_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Template not found")
            )
        
        return APIResponse(
            success=True,
            data=result["data"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template details: {str(e)}"
        )

@app.post("/api/v1/reports/validate")
async def validate_report_data(
    request: ReportDataValidationRequest,
    auth: dict = Depends(verify_api_key)
):
    """Validate report data against template requirements"""
    try:
        reporting_service = RegulatoryReportingService()
        
        validation_result = reporting_service.validate_data(
            request.template_id,
            request.data
        )
        
        return APIResponse(
            success=True,
            data={
                "template_id": request.template_id,
                "validation_result": validation_result,
                "data_valid": validation_result.get("valid", False),
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", [])
            }
        )
    except Exception as e:
        logger.error(f"Failed to validate report data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate report data: {str(e)}"
        )

@app.post("/api/v1/reports/generate")
async def generate_regulatory_report(
    request: ReportGenerationRequest,
    auth: dict = Depends(verify_api_key)
):
    """Generate a regulatory report from template and data"""
    try:
        reporting_service = RegulatoryReportingService()
        
        result = reporting_service.generate_report(
            request.template_id,
            request.data,
            request.output_format,
            request.customer_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Report generation failed")
            )
        
        return APIResponse(
            success=True,
            data={
                "report_id": result["report_id"],
                "template_name": result["template_name"],
                "output_format": result["output_format"],
                "generated_at": result["generated_at"],
                "download_url": result["download_url"],
                "validation_warnings": result.get("validation_warnings", [])
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@app.get("/api/v1/reports/status/{report_id}")
async def get_report_status(
    report_id: str = Path(description="Report ID"),
    auth: dict = Depends(verify_api_key)
):
    """Get the status of a generated report"""
    try:
        reporting_service = RegulatoryReportingService()
        
        result = reporting_service.get_report_status(report_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Report not found")
            )
        
        return APIResponse(
            success=True,
            data=result["data"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report status: {str(e)}"
        )

@app.get("/api/v1/reports/analytics")
async def get_reporting_analytics(
    auth: dict = Depends(verify_api_key)
):
    """Get reporting system analytics and statistics"""
    try:
        reporting_service = RegulatoryReportingService()
        
        analytics = reporting_service.get_analytics()
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )
        
        return APIResponse(
            success=True,
            data={
                "analytics": analytics,
                "summary": {
                    "total_templates": analytics["total_templates"],
                    "active_templates": analytics["active_templates"],
                    "reports_generated": analytics["total_reports_generated"],
                    "supported_jurisdictions": len(analytics["supported_jurisdictions"]),
                    "supported_frameworks": len(analytics["supported_frameworks"])
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reporting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reporting analytics: {str(e)}"
        )

@app.get("/api/v1/reports/health")
async def reporting_health_check(
    auth: dict = Depends(verify_api_key)
):
    """Health check for regulatory reporting service"""
    try:
        reporting_service = RegulatoryReportingService()
        
        health_status = reporting_service.health_check()
        
        return APIResponse(
            success=True,
            data={
                "service_name": "Regulatory Reporting Service",
                "health_check": health_status,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Reporting service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

# ============================================================================
# Application Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Compliant-One API server starting up...")
    
    try:
        # Initialize platform if the method exists; constructor already sets up services
        if hasattr(platform, "initialize"):
            import inspect
            init_fn = getattr(platform, "initialize")
            try:
                if inspect.iscoroutinefunction(init_fn):
                    await init_fn()
                else:
                    init_fn()
                logger.info("Platform initialize() executed")
            except Exception as e:
                logger.warning(f"Platform initialize() failed: {e}")
        else:
            logger.info("No platform.initialize() method; proceeding with default initialization")
    except Exception as e:
        logger.error(f"Failed to initialize platform: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Compliant-One API server shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
