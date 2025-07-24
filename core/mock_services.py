"""
Mock Services for Compliant.one Platform
Provides demo implementations of all compliance services
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from utils.logger import ComplianceLogger

class MockService:
    """Base mock service for demonstration purposes"""
    
    def __init__(self, service_name: str, config: Any):
        self.service_name = service_name
        self.config = config
        self.logger = ComplianceLogger(service_name)
        
        # Mock data for demonstrations
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate mock data for service demonstrations"""
        return {
            "pep_list": [
                {"name": "John Politician", "country": "Country A", "position": "Minister"},
                {"name": "Jane Official", "country": "Country B", "position": "Governor"},
                {"name": "Bob Leader", "country": "Country C", "position": "Mayor"}
            ],
            "sanctions_list": [
                {"name": "Sanctioned Entity 1", "list": "OFAC SDN", "date_added": "2024-01-15"},
                {"name": "Sanctioned Entity 2", "list": "EU Consolidated", "date_added": "2024-02-20"},
                {"name": "Sanctioned Entity 3", "list": "UN Security Council", "date_added": "2024-03-10"}
            ],
            "adverse_media": [
                {"entity": "Risk Corp", "headline": "Investigation into financial irregularities", "date": "2024-07-15", "severity": "HIGH"},
                {"entity": "Concern Ltd", "headline": "Regulatory fine for compliance violations", "date": "2024-07-10", "severity": "MEDIUM"},
                {"entity": "Alert Inc", "headline": "Sanctions violation allegations", "date": "2024-07-05", "severity": "CRITICAL"}
            ],
            "beneficial_owners": [
                {"company": "Shell Corp A", "owner": "Hidden Owner 1", "percentage": 25.5, "jurisdiction": "Offshore"},
                {"company": "Shell Corp B", "owner": "Hidden Owner 2", "percentage": 51.0, "jurisdiction": "Tax Haven"},
                {"company": "Shell Corp C", "owner": "Hidden Owner 3", "percentage": 100.0, "jurisdiction": "Secrecy State"}
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "status": "healthy",
            "uptime": random.randint(100, 10000),
            "last_check": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    async def check_compliance(self, customer: Any, recommendation: str) -> Dict[str, Any]:
        """Mock compliance check"""
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate processing time
        
        # Simulate different outcomes based on customer data
        risk_factors = self._assess_risk_factors(customer, recommendation)
        score = self._calculate_score(risk_factors)
        status = self._determine_status(score)
        
        result = {
            "status": status,
            "score": score,
            "details": {
                "recommendation": recommendation,
                "service": self.service_name,
                "risk_factors": risk_factors,
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": random.randint(50, 500)
            },
            "reference_id": f"{self.service_name}_{recommendation}_{random.randint(10000, 99999)}"
        }
        
        # Log the compliance check
        self.logger.log_compliance_check(
            customer.customer_id, recommendation, status, result["details"]
        )
        
        return result
    
    def _assess_risk_factors(self, customer: Any, recommendation: str) -> List[str]:
        """Assess risk factors for customer"""
        risk_factors = []
        
        # Risk based on customer type
        if customer.customer_type == "CORPORATE":
            risk_factors.append("Corporate entity")
        
        # Risk based on jurisdiction
        high_risk_jurisdictions = ["Country X", "Country Y", "Country Z"]
        if customer.jurisdiction in high_risk_jurisdictions:
            risk_factors.append("High-risk jurisdiction")
        
        # Risk based on customer category
        if customer.risk_category in ["HIGH", "CRITICAL"]:
            risk_factors.append(f"{customer.risk_category} risk customer")
        
        # Service-specific risk factors
        if self.service_name == "sanctions":
            # Check mock sanctions data
            for sanction in self.mock_data["sanctions_list"]:
                if customer.name.lower() in sanction["name"].lower():
                    risk_factors.append("Potential sanctions match")
        
        elif self.service_name == "kyc" and recommendation == "R.12":
            # Check PEP data
            for pep in self.mock_data["pep_list"]:
                if customer.name.lower() in pep["name"].lower():
                    risk_factors.append("PEP match found")
        
        elif self.service_name == "osint":
            # Check adverse media
            for media in self.mock_data["adverse_media"]:
                if customer.name.lower() in media["entity"].lower():
                    risk_factors.append(f"Adverse media: {media['severity']}")
        
        return risk_factors
    
    def _calculate_score(self, risk_factors: List[str]) -> float:
        """Calculate compliance score based on risk factors"""
        base_score = 1.0
        
        # Deduct score for each risk factor
        for factor in risk_factors:
            if "CRITICAL" in factor:
                base_score -= 0.4
            elif "HIGH" in factor:
                base_score -= 0.3
            elif "MEDIUM" in factor:
                base_score -= 0.2
            elif "sanctions" in factor.lower():
                base_score -= 0.5
            elif "pep" in factor.lower():
                base_score -= 0.3
            else:
                base_score -= 0.1
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, base_score))
    
    def _determine_status(self, score: float) -> str:
        """Determine compliance status based on score"""
        if score >= 0.8:
            return "PASS"
        elif score >= 0.6:
            return "WARNING"
        else:
            return "FAIL"

class MockIdentityService(MockService):
    """Mock Identity Verification Service"""
    
    async def verify_identity(self, customer: Any, documents: List[Dict]) -> Dict[str, Any]:
        """Mock identity verification"""
        await asyncio.sleep(0.3)
        
        verification_score = random.uniform(0.7, 1.0)
        
        return {
            "verified": verification_score > 0.8,
            "score": verification_score,
            "details": {
                "document_authenticity": verification_score,
                "biometric_match": random.uniform(0.8, 1.0),
                "data_consistency": random.uniform(0.9, 1.0),
                "documents_processed": len(documents)
            }
        }

class MockKYCService(MockService):
    """Mock KYC/CDD/EDD Service"""
    
    async def perform_kyc(self, customer: Any, level: str = "CDD") -> Dict[str, Any]:
        """Mock KYC check"""
        await asyncio.sleep(0.4)
        
        kyc_score = random.uniform(0.6, 1.0)
        
        return {
            "kyc_level": level,
            "passed": kyc_score > 0.7,
            "score": kyc_score,
            "details": {
                "identity_verification": random.uniform(0.8, 1.0),
                "address_verification": random.uniform(0.7, 1.0),
                "document_verification": random.uniform(0.8, 1.0),
                "pep_screening": random.uniform(0.9, 1.0)
            }
        }

class MockSanctionsService(MockService):
    """Mock Sanctions Screening Service"""
    
    async def screen_sanctions(self, entity_name: str) -> Dict[str, Any]:
        """Mock sanctions screening"""
        await asyncio.sleep(0.2)
        
        # Check against mock sanctions list
        matches = []
        for sanction in self.mock_data["sanctions_list"]:
            if entity_name.lower() in sanction["name"].lower():
                matches.append({
                    "name": sanction["name"],
                    "list": sanction["list"],
                    "match_score": random.uniform(0.8, 1.0),
                    "date_added": sanction["date_added"]
                })
        
        return {
            "has_matches": len(matches) > 0,
            "match_count": len(matches),
            "matches": matches,
            "screening_timestamp": datetime.now().isoformat()
        }
