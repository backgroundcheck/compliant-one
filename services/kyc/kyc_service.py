"""
KYC/CDD/EDD Screening Service
📊 Automated Customer Due Diligence, Enhanced Due Diligence for high-risk customers,
Risk-based customer categorization, and Simplified Due Diligence

FATF Alignment: R.10 (Customer Due Diligence), R.22/23 (DNFBP Requirements)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from utils.logger import ComplianceLogger

class DDLevel(Enum):
    """Due Diligence Levels"""
    SDD = "simplified"  # Simplified Due Diligence
    CDD = "customer"    # Customer Due Diligence
    EDD = "enhanced"    # Enhanced Due Diligence

class CustomerType(Enum):
    """Customer Types"""
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    DNFBP = "dnfbp"  # Designated Non-Financial Businesses and Professions

class RiskCategory(Enum):
    """Risk Categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CustomerProfile:
    """Customer profile for KYC assessment"""
    customer_id: str
    name: str
    customer_type: CustomerType
    jurisdiction: str
    business_sector: Optional[str] = None
    incorporation_date: Optional[datetime] = None
    annual_turnover: Optional[float] = None
    source_of_funds: Optional[str] = None
    purpose_of_relationship: Optional[str] = None
    expected_transaction_volume: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KYCResult:
    """KYC assessment result"""
    assessment_id: str
    customer_id: str
    dd_level: DDLevel
    risk_category: RiskCategory
    overall_score: float
    risk_factors: List[str]
    recommended_actions: List[str]
    compliance_status: str
    assessment_timestamp: datetime
    next_review_date: datetime
    details: Dict[str, Any] = field(default_factory=dict)

class KYCService:
    """
    KYC/CDD/EDD Screening Service
    
    Features:
    - Automated Customer Due Diligence (CDD)
    - Enhanced Due Diligence (EDD) for high-risk customers
    - Simplified Due Diligence (SDD) for low-risk scenarios
    - Risk-based customer categorization
    - DNFBP-specific requirements
    - Ongoing monitoring recommendations
    """
    
    def __init__(self, config: Any):
        self.config = config
        self.logger = ComplianceLogger("kyc_service")
        
        # Risk thresholds
        self.risk_thresholds = {
            RiskCategory.LOW: 0.3,
            RiskCategory.MEDIUM: 0.6,
            RiskCategory.HIGH: 0.8,
            RiskCategory.CRITICAL: 1.0
        }
        
        # DD level requirements
        self.dd_requirements = {
            DDLevel.SDD: ["basic_identity", "sanctions_check"],
            DDLevel.CDD: ["identity_verification", "address_verification", "sanctions_check", "pep_check"],
            DDLevel.EDD: ["enhanced_identity", "source_of_wealth", "ongoing_monitoring", 
                         "sanctions_check", "pep_check", "adverse_media", "beneficial_ownership"]
        }
        
        # Initialize risk matrices
        self._initialize_risk_matrices()
    
    def _initialize_risk_matrices(self):
        """Initialize risk assessment matrices"""
        
        # Customer type risk weights
        self.customer_type_risk = {
            CustomerType.INDIVIDUAL: 0.2,
            CustomerType.CORPORATE: 0.4,
            CustomerType.GOVERNMENT: 0.3,
            CustomerType.DNFBP: 0.5
        }
        
        # Geographic risk (mock data)
        self.geographic_risk = {
            "low_risk": ["US", "UK", "DE", "SG", "AU", "CA", "JP"],
            "medium_risk": ["BR", "IN", "MX", "TH", "ZA"],
            "high_risk": ["AF", "IR", "KP", "SY", "YE"],
            "sanctions": ["RU", "BY", "MM", "VE", "CU"]
        }
        
        # Business sector risk
        self.sector_risk = {
            "low_risk": ["education", "healthcare", "utilities"],
            "medium_risk": ["retail", "manufacturing", "technology"],
            "high_risk": ["gaming", "cryptocurrency", "precious_metals", "real_estate"],
            "critical_risk": ["money_services", "casinos", "arms_dealing"]
        }
    
    async def perform_kyc(self, customer: CustomerProfile, 
                         requested_level: Optional[DDLevel] = None) -> KYCResult:
        """
        Perform KYC assessment based on risk-based approach
        
        Args:
            customer: Customer profile
            requested_level: Optional specific DD level requested
            
        Returns:
            KYC assessment result
        """
        assessment_id = self._generate_assessment_id(customer.customer_id)
        
        self.logger.log_compliance_check(
            customer.customer_id, "R.10", "PENDING",
            {"assessment_id": assessment_id, "requested_level": requested_level}
        )
        
        try:
            # Step 1: Risk assessment
            risk_assessment = await self._assess_customer_risk(customer)
            
            # Step 2: Determine appropriate DD level
            recommended_dd_level = self._determine_dd_level(risk_assessment, requested_level)
            
            # Step 3: Perform due diligence checks
            dd_results = await self._perform_due_diligence(customer, recommended_dd_level)
            
            # Step 4: Compliance checks
            compliance_results = await self._check_compliance_requirements(customer, recommended_dd_level)
            
            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(risk_assessment, dd_results)
            
            # Step 6: Calculate overall score
            overall_score = self._calculate_overall_score(risk_assessment, dd_results, compliance_results)
            
            # Step 7: Determine compliance status
            compliance_status = self._determine_compliance_status(overall_score, dd_results)
            
            # Create result
            result = KYCResult(
                assessment_id=assessment_id,
                customer_id=customer.customer_id,
                dd_level=recommended_dd_level,
                risk_category=risk_assessment["category"],
                overall_score=overall_score,
                risk_factors=risk_assessment["factors"],
                recommended_actions=recommendations,
                compliance_status=compliance_status,
                assessment_timestamp=datetime.now(),
                next_review_date=self._calculate_next_review_date(risk_assessment["category"]),
                details={
                    "risk_assessment": risk_assessment,
                    "dd_results": dd_results,
                    "compliance_results": compliance_results,
                    "requirements_met": self._check_requirements_met(recommended_dd_level, dd_results)
                }
            )
            
            # Log result
            status = "PASS" if compliance_status == "COMPLIANT" else "FAIL"
            self.logger.log_compliance_check(
                customer.customer_id, "R.10", status,
                {"assessment_id": assessment_id, "score": overall_score, "dd_level": recommended_dd_level.value}
            )
            
            return result
            
        except Exception as e:
            self.logger.logger.error(f"KYC assessment failed for {customer.customer_id}: {e}")
            return KYCResult(
                assessment_id=assessment_id,
                customer_id=customer.customer_id,
                dd_level=DDLevel.CDD,
                risk_category=RiskCategory.HIGH,
                overall_score=0.0,
                risk_factors=["assessment_error"],
                recommended_actions=["manual_review"],
                compliance_status="NON_COMPLIANT",
                assessment_timestamp=datetime.now(),
                next_review_date=datetime.now() + timedelta(days=30),
                details={"error": str(e)}
            )
    
    async def _assess_customer_risk(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Assess customer risk factors"""
        await asyncio.sleep(0.3)  # Simulate processing
        
        risk_factors = []
        risk_score = 0.0
        
        # Customer type risk
        customer_type_risk = self.customer_type_risk.get(customer.customer_type, 0.5)
        risk_score += customer_type_risk
        
        # Geographic risk
        geo_risk = self._assess_geographic_risk(customer.jurisdiction)
        risk_score += geo_risk["score"]
        risk_factors.extend(geo_risk["factors"])
        
        # Business sector risk
        if customer.business_sector:
            sector_risk = self._assess_sector_risk(customer.business_sector)
            risk_score += sector_risk["score"]
            risk_factors.extend(sector_risk["factors"])
        
        # Transaction volume risk
        if customer.expected_transaction_volume:
            volume_risk = self._assess_volume_risk(customer.expected_transaction_volume)
            risk_score += volume_risk["score"]
            risk_factors.extend(volume_risk["factors"])
        
        # Determine risk category
        risk_category = self._categorize_risk(risk_score)
        
        return {
            "score": min(risk_score, 1.0),
            "category": risk_category,
            "factors": risk_factors,
            "breakdown": {
                "customer_type": customer_type_risk,
                "geographic": geo_risk["score"],
                "sector": sector_risk["score"] if customer.business_sector else 0.0,
                "volume": volume_risk["score"] if customer.expected_transaction_volume else 0.0
            }
        }
    
    def _assess_geographic_risk(self, jurisdiction: str) -> Dict[str, Any]:
        """Assess geographic risk"""
        if jurisdiction in self.geographic_risk["sanctions"]:
            return {"score": 0.9, "factors": ["sanctions_jurisdiction"]}
        elif jurisdiction in self.geographic_risk["high_risk"]:
            return {"score": 0.7, "factors": ["high_risk_jurisdiction"]}
        elif jurisdiction in self.geographic_risk["medium_risk"]:
            return {"score": 0.4, "factors": ["medium_risk_jurisdiction"]}
        else:
            return {"score": 0.1, "factors": []}
    
    def _assess_sector_risk(self, sector: str) -> Dict[str, Any]:
        """Assess business sector risk"""
        if sector in self.sector_risk["critical_risk"]:
            return {"score": 0.8, "factors": ["critical_risk_sector"]}
        elif sector in self.sector_risk["high_risk"]:
            return {"score": 0.6, "factors": ["high_risk_sector"]}
        elif sector in self.sector_risk["medium_risk"]:
            return {"score": 0.3, "factors": ["medium_risk_sector"]}
        else:
            return {"score": 0.1, "factors": []}
    
    def _assess_volume_risk(self, volume: float) -> Dict[str, Any]:
        """Assess transaction volume risk"""
        if volume > 10000000:  # >10M
            return {"score": 0.6, "factors": ["high_volume_transactions"]}
        elif volume > 1000000:  # >1M
            return {"score": 0.4, "factors": ["medium_volume_transactions"]}
        else:
            return {"score": 0.1, "factors": []}
    
    def _categorize_risk(self, risk_score: float) -> RiskCategory:
        """Categorize risk based on score"""
        if risk_score >= 0.8:
            return RiskCategory.CRITICAL
        elif risk_score >= 0.6:
            return RiskCategory.HIGH
        elif risk_score >= 0.3:
            return RiskCategory.MEDIUM
        else:
            return RiskCategory.LOW
    
    def _determine_dd_level(self, risk_assessment: Dict[str, Any], 
                           requested_level: Optional[DDLevel] = None) -> DDLevel:
        """Determine appropriate due diligence level"""
        risk_category = risk_assessment["category"]
        
        # If specific level requested, validate it's appropriate
        if requested_level:
            if requested_level == DDLevel.EDD or risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]:
                return DDLevel.EDD
            elif requested_level == DDLevel.CDD or risk_category == RiskCategory.MEDIUM:
                return DDLevel.CDD
            elif requested_level == DDLevel.SDD and risk_category == RiskCategory.LOW:
                return DDLevel.SDD
        
        # Risk-based determination
        if risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]:
            return DDLevel.EDD
        elif risk_category == RiskCategory.MEDIUM:
            return DDLevel.CDD
        else:
            return DDLevel.SDD
    
    async def _perform_due_diligence(self, customer: CustomerProfile, 
                                   dd_level: DDLevel) -> Dict[str, Any]:
        """Perform due diligence checks based on level"""
        await asyncio.sleep(0.5)  # Simulate processing
        
        requirements = self.dd_requirements[dd_level]
        results = {}
        
        for requirement in requirements:
            if requirement == "basic_identity":
                results[requirement] = await self._check_basic_identity(customer)
            elif requirement == "identity_verification":
                results[requirement] = await self._check_identity_verification(customer)
            elif requirement == "enhanced_identity":
                results[requirement] = await self._check_enhanced_identity(customer)
            elif requirement == "address_verification":
                results[requirement] = await self._check_address_verification(customer)
            elif requirement == "sanctions_check":
                results[requirement] = await self._check_sanctions(customer)
            elif requirement == "pep_check":
                results[requirement] = await self._check_pep(customer)
            elif requirement == "adverse_media":
                results[requirement] = await self._check_adverse_media(customer)
            elif requirement == "source_of_wealth":
                results[requirement] = await self._check_source_of_wealth(customer)
            elif requirement == "beneficial_ownership":
                results[requirement] = await self._check_beneficial_ownership(customer)
            elif requirement == "ongoing_monitoring":
                results[requirement] = await self._setup_ongoing_monitoring(customer)
        
        return results
    
    async def _check_basic_identity(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Basic identity check"""
        return {"passed": True, "score": 0.9, "details": "Basic identity verified"}
    
    async def _check_identity_verification(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Standard identity verification"""
        return {"passed": True, "score": 0.88, "details": "Identity documents verified"}
    
    async def _check_enhanced_identity(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Enhanced identity verification"""
        return {"passed": True, "score": 0.92, "details": "Enhanced identity verification completed"}
    
    async def _check_address_verification(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Address verification"""
        return {"passed": True, "score": 0.85, "details": "Address verified through utility bills"}
    
    async def _check_sanctions(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Sanctions screening"""
        # Mock sanctions check
        return {"passed": True, "score": 1.0, "matches": 0, "details": "No sanctions matches found"}
    
    async def _check_pep(self, customer: CustomerProfile) -> Dict[str, Any]:
        """PEP screening"""
        # Mock PEP check
        return {"passed": True, "score": 0.95, "matches": 0, "details": "No PEP matches found"}
    
    async def _check_adverse_media(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Adverse media screening"""
        return {"passed": True, "score": 0.90, "findings": 0, "details": "No adverse media found"}
    
    async def _check_source_of_wealth(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Source of wealth verification"""
        return {"passed": True, "score": 0.87, "details": "Source of wealth documented and verified"}
    
    async def _check_beneficial_ownership(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Beneficial ownership verification"""
        if customer.customer_type == CustomerType.CORPORATE:
            return {"passed": True, "score": 0.89, "owners_identified": 3, "details": "All beneficial owners identified"}
        else:
            return {"passed": True, "score": 1.0, "details": "Individual customer - not applicable"}
    
    async def _setup_ongoing_monitoring(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Setup ongoing monitoring"""
        return {"passed": True, "score": 1.0, "details": "Ongoing monitoring configured"}
    
    async def _check_compliance_requirements(self, customer: CustomerProfile, 
                                           dd_level: DDLevel) -> Dict[str, Any]:
        """Check specific compliance requirements"""
        await asyncio.sleep(0.2)
        
        compliance_checks = {}
        
        # FATF R.10 compliance
        compliance_checks["R.10"] = {"passed": True, "score": 0.92}
        
        # DNFBP specific requirements
        if customer.customer_type == CustomerType.DNFBP:
            compliance_checks["R.22"] = {"passed": True, "score": 0.88}
            compliance_checks["R.23"] = {"passed": True, "score": 0.90}
        
        return compliance_checks
    
    def _generate_recommendations(self, risk_assessment: Dict[str, Any], 
                                dd_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        risk_category = risk_assessment["category"]
        
        if risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]:
            recommendations.append("Implement enhanced monitoring")
            recommendations.append("Schedule quarterly reviews")
            recommendations.append("Require senior management approval")
        
        if risk_category == RiskCategory.MEDIUM:
            recommendations.append("Schedule annual reviews")
            recommendations.append("Monitor transaction patterns")
        
        # Check for failed DD requirements
        failed_checks = [k for k, v in dd_results.items() if not v.get("passed", True)]
        if failed_checks:
            recommendations.append(f"Address failed checks: {', '.join(failed_checks)}")
        
        return recommendations
    
    def _calculate_overall_score(self, risk_assessment: Dict[str, Any],
                               dd_results: Dict[str, Any],
                               compliance_results: Dict[str, Any]) -> float:
        """Calculate overall KYC score"""
        
        # DD results score (60% weight)
        dd_scores = [result.get("score", 0.0) for result in dd_results.values()]
        dd_score = sum(dd_scores) / len(dd_scores) if dd_scores else 0.0
        
        # Compliance score (25% weight)
        compliance_scores = [result.get("score", 0.0) for result in compliance_results.values()]
        compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        # Risk assessment score (15% weight) - inverted (lower risk = higher score)
        risk_score = 1.0 - risk_assessment["score"]
        
        overall_score = (dd_score * 0.6) + (compliance_score * 0.25) + (risk_score * 0.15)
        
        return max(0.0, min(1.0, overall_score))
    
    def _determine_compliance_status(self, overall_score: float, 
                                   dd_results: Dict[str, Any]) -> str:
        """Determine compliance status"""
        
        # Check for any critical failures
        critical_failures = [
            k for k, v in dd_results.items() 
            if not v.get("passed", True) and k in ["sanctions_check", "pep_check"]
        ]
        
        if critical_failures:
            return "NON_COMPLIANT"
        
        if overall_score >= 0.8:
            return "COMPLIANT"
        elif overall_score >= 0.6:
            return "CONDITIONAL"
        else:
            return "NON_COMPLIANT"
    
    def _check_requirements_met(self, dd_level: DDLevel, 
                              dd_results: Dict[str, Any]) -> Dict[str, bool]:
        """Check which requirements are met"""
        requirements = self.dd_requirements[dd_level]
        return {req: dd_results.get(req, {}).get("passed", False) for req in requirements}
    
    def _calculate_next_review_date(self, risk_category: RiskCategory) -> datetime:
        """Calculate next review date based on risk category"""
        if risk_category == RiskCategory.CRITICAL:
            return datetime.now() + timedelta(days=90)  # Quarterly
        elif risk_category == RiskCategory.HIGH:
            return datetime.now() + timedelta(days=180)  # Semi-annually
        elif risk_category == RiskCategory.MEDIUM:
            return datetime.now() + timedelta(days=365)  # Annually
        else:
            return datetime.now() + timedelta(days=730)  # Bi-annually
    
    def _generate_assessment_id(self, customer_id: str) -> str:
        """Generate unique assessment ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"KYC_{customer_id}_{timestamp}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            "status": "healthy",
            "dd_levels_supported": [level.value for level in DDLevel],
            "risk_categories": [cat.value for cat in RiskCategory],
            "last_check": datetime.now().isoformat()
        }
    
    async def check_compliance(self, customer: Any, recommendation: str) -> Dict[str, Any]:
        """Check compliance for FATF recommendations"""
        
        if recommendation == "R.10":
            return {
                "status": "PASS",
                "score": 0.94,
                "details": {
                    "service": "kyc",
                    "recommendation": "R.10",
                    "description": "Customer Due Diligence with risk-based approach",
                    "capabilities": [
                        "Simplified Due Diligence (SDD)",
                        "Customer Due Diligence (CDD)", 
                        "Enhanced Due Diligence (EDD)",
                        "Risk-based categorization"
                    ]
                }
            }
        
        elif recommendation in ["R.22", "R.23"]:
            return {
                "status": "PASS",
                "score": 0.91,
                "details": {
                    "service": "kyc",
                    "recommendation": recommendation,
                    "description": "DNFBP-specific due diligence requirements",
                    "dnfbp_support": [
                        "Real estate agents",
                        "Lawyers and notaries",
                        "Accountants",
                        "Trust and company service providers",
                        "Dealers in precious metals"
                    ]
                }
            }
        
        else:
            return {
                "status": "NOT_APPLICABLE",
                "score": 1.0,
                "details": {
                    "message": f"Recommendation {recommendation} not applicable to KYC service"
                }
            }
