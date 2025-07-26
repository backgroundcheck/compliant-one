"""
Compliant-One Platform API
Phase 3: Comprehensive API for third-party system integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, Security, status, Query, Path, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import platform services
from services.sanctions.bo_service import BeneficialOwnershipService
from services.identity.identity_service import IdentityVerificationService
from services.kyc.kyc_service import KYCService
from services.osint.osint_service import OSINTService
from services.transactions.enhanced_monitoring import TransactionMonitoringEngine
from services.reporting.regulatory_templates import RegulatoryReportingService
from utils.logger import get_logger

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
            ("reporting", ReportingService)
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
    template_id: str = Path(..., description="Template ID"),
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
    report_id: str = Path(..., description="Report ID"),
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
        # Initialize platform
        await platform.initialize()
        logger.info("Platform initialized successfully")
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
