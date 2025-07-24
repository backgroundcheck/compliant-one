"""
Compliant.one Core Platform
Main platform orchestrator and service manager
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from config.settings import get_config, FATF_SERVICE_MAPPING
from utils.logger import get_logger

@dataclass
class ComplianceResult:
    """Standard compliance result format"""
    service: str
    recommendation: str
    status: str  # PASS, FAIL, WARNING, PENDING
    score: float
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    reference_id: str = ""

@dataclass
class Customer:
    """Customer entity for compliance checking"""
    customer_id: str
    name: str
    customer_type: str  # INDIVIDUAL, CORPORATE, GOVERNMENT
    jurisdiction: str
    risk_category: str = "MEDIUM"
    metadata: Dict[str, Any] = field(default_factory=dict)

class CompliantOnePlatform:
    """
    Main Compliant.one Platform
    Orchestrates all compliance services and FATF recommendation coverage
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.services = {}
        self.active_sessions = {}
        
        # Initialize service registry
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all platform services"""
        try:
            # Import all service modules
            from services.identity.identity_service import IdentityVerificationService
            from services.kyc.kyc_service import KYCService
            from services.osint.osint_service import OSINTService
            from services.beneficial_ownership.bo_service import BeneficialOwnershipService
            from services.sanctions.sanctions_service import SanctionsService
            from services.monitoring.monitoring_service import MonitoringService
            from services.transactions.transaction_service import TransactionMonitoringService
            from services.reporting.reporting_service import ReportingService
            
            # Phase 2 Advanced Services
            try:
                from services.ai.ai_service import get_ai_service_manager
                from services.osint.adverse_media_service import get_adverse_media_manager
                from services.compliance.risk_rules_engine import get_risk_rules_manager
                from services.compliance.case_management import get_case_management_system
                
                # Initialize Phase 2 services
                self.ai_service_manager = get_ai_service_manager()
                self.adverse_media_manager = get_adverse_media_manager()
                self.risk_rules_manager = get_risk_rules_manager()
                self.case_management_system = get_case_management_system()
                
                self.phase2_enabled = True
                self.logger.info("Phase 2 Advanced AI & Compliance Automation services initialized")
                
            except ImportError as e:
                self.logger.warning(f"Phase 2 services not available: {e}")
                self.phase2_enabled = False
            
            # Register core services
            self.services = {
                'identity': IdentityVerificationService(self.config),
                'kyc': KYCService(self.config),
                'osint': OSINTService(self.config),
                'beneficial_ownership': BeneficialOwnershipService(self.config),
                'sanctions': SanctionsService(self.config),
                'monitoring': MonitoringService(self.config),
                'transactions': TransactionMonitoringService(self.config),
                'reporting': ReportingService(self.config)
            }
            
            # Add Phase 2 services to registry if available
            if self.phase2_enabled:
                self.services.update({
                    'ai_analytics': self.ai_service_manager,
                    'adverse_media': self.adverse_media_manager,
                    'risk_rules': self.risk_rules_manager,
                    'case_management': self.case_management_system
                })
            
            self.logger.info(f"Initialized {len(self.services)} compliance services")
            
        except ImportError as e:
            self.logger.warning(f"Some services not available: {e}")
            # Initialize with mock services for demonstration
            self._initialize_mock_services()
    
    def _initialize_mock_services(self):
        """Initialize mock services for demonstration"""
        from core.mock_services import MockService
        
        service_names = ['identity', 'kyc', 'osint', 'beneficial_ownership', 
                        'sanctions', 'monitoring', 'transactions', 'reporting']
        
        self.services = {name: MockService(name, self.config) for name in service_names}
        self.logger.info("Initialized with mock services for demonstration")
    
    async def comprehensive_compliance_check(self, customer: Customer, 
                                           recommendations: Optional[List[str]] = None) -> Dict[str, ComplianceResult]:
        """
        Perform comprehensive compliance check across all FATF recommendations
        """
        if recommendations is None:
            recommendations = self.config.FATF_RECOMMENDATIONS
        
        self.logger.info(f"Starting comprehensive compliance check for customer {customer.customer_id}")
        
        results = {}
        tasks = []
        
        # Create tasks for each relevant recommendation
        for recommendation in recommendations:
            if recommendation in FATF_SERVICE_MAPPING:
                service_info = FATF_SERVICE_MAPPING[recommendation]
                service_name = service_info['service']
                
                if service_name in self.services:
                    task = self._execute_recommendation_check(
                        recommendation, service_name, customer
                    )
                    tasks.append((recommendation, task))
        
        # Execute all checks concurrently
        if tasks:
            task_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            # Process results
            for i, (recommendation, _) in enumerate(tasks):
                result = task_results[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Error in {recommendation}: {result}")
                    results[recommendation] = ComplianceResult(
                        service=FATF_SERVICE_MAPPING[recommendation]['service'],
                        recommendation=recommendation,
                        status="FAIL",
                        score=0.0,
                        details={"error": str(result)}
                    )
                else:
                    results[recommendation] = result
        
        # Calculate overall compliance score
        overall_score = self._calculate_overall_score(results)
        self.logger.info(f"Compliance check completed. Overall score: {overall_score}")
        
        return results
    
    async def _execute_recommendation_check(self, recommendation: str, 
                                          service_name: str, customer: Customer) -> ComplianceResult:
        """Execute compliance check for specific FATF recommendation"""
        service = self.services[service_name]
        service_info = FATF_SERVICE_MAPPING[recommendation]
        
        try:
            # Call the appropriate service method
            if hasattr(service, 'check_compliance'):
                result = await service.check_compliance(customer, recommendation)
            else:
                # Fallback to generic check
                result = await self._generic_compliance_check(service, customer, recommendation)
            
            return ComplianceResult(
                service=service_name,
                recommendation=recommendation,
                status=result.get('status', 'PASS'),
                score=result.get('score', 1.0),
                details=result.get('details', {}),
                reference_id=result.get('reference_id', '')
            )
            
        except Exception as e:
            self.logger.error(f"Error executing {recommendation} check: {e}")
            return ComplianceResult(
                service=service_name,
                recommendation=recommendation,
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    async def _generic_compliance_check(self, service: Any, customer: Customer, 
                                      recommendation: str) -> Dict[str, Any]:
        """Generic compliance check fallback"""
        # This would be service-specific implementation
        return {
            'status': 'PASS',
            'score': 0.85,
            'details': {
                'message': f'Mock compliance check for {recommendation}',
                'customer_id': customer.customer_id,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _calculate_overall_score(self, results: Dict[str, ComplianceResult]) -> float:
        """Calculate overall compliance score"""
        if not results:
            return 0.0
        
        total_score = sum(result.score for result in results.values())
        return total_score / len(results)
    
    async def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all platform services"""
        status = {}
        
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    health = await service.health_check()
                else:
                    health = {"status": "unknown", "message": "Health check not implemented"}
                
                status[service_name] = {
                    "available": True,
                    "health": health,
                    "fatf_coverage": [
                        rec for rec, info in FATF_SERVICE_MAPPING.items() 
                        if info['service'] == service_name
                    ]
                }
            except Exception as e:
                status[service_name] = {
                    "available": False,
                    "error": str(e),
                    "fatf_coverage": []
                }
        
        return status
    
    async def get_fatf_coverage(self) -> Dict[str, Any]:
        """Get FATF recommendation coverage analysis"""
        coverage = {
            "total_recommendations": len(self.config.FATF_RECOMMENDATIONS),
            "covered_recommendations": 0,
            "coverage_by_service": {},
            "uncovered_recommendations": []
        }
        
        for recommendation in self.config.FATF_RECOMMENDATIONS:
            if recommendation in FATF_SERVICE_MAPPING:
                service_name = FATF_SERVICE_MAPPING[recommendation]['service']
                if service_name in self.services:
                    coverage["covered_recommendations"] += 1
                    if service_name not in coverage["coverage_by_service"]:
                        coverage["coverage_by_service"][service_name] = []
                    coverage["coverage_by_service"][service_name].append(recommendation)
                else:
                    coverage["uncovered_recommendations"].append(recommendation)
            else:
                coverage["uncovered_recommendations"].append(recommendation)
        
        coverage["coverage_percentage"] = (
            coverage["covered_recommendations"] / coverage["total_recommendations"] * 100
        )
        
        return coverage
    
    # Phase 2: Advanced AI & Compliance Automation Methods
    
    async def ai_risk_analysis(self, customer: Customer, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform AI-powered risk analysis"""
        if not hasattr(self, 'phase2_enabled') or not self.phase2_enabled:
            return {"error": "Phase 2 AI services not available"}
        
        try:
            self.logger.info(f"Starting AI risk analysis for customer {customer.customer_id}")
            
            # Prepare data for AI analysis
            customer_data = {
                'customer_id': customer.customer_id,
                'name': customer.name,
                'customer_type': customer.customer_type,
                'jurisdiction': customer.jurisdiction,
                'risk_category': customer.risk_category,
                'metadata': customer.metadata
            }
            
            # Perform different types of AI analysis
            analysis_results = {}
            
            if analysis_type in ["comprehensive", "anomaly"]:
                anomaly_result = await self.ai_service_manager.anomaly_detection_service.detect_anomalies(
                    customer_data, 'customer_profile'
                )
                analysis_results['anomaly_detection'] = anomaly_result
            
            if analysis_type in ["comprehensive", "predictive"]:
                prediction_result = await self.ai_service_manager.predictive_analytics_service.predict_risk(
                    customer_data, 'customer_risk'
                )
                analysis_results['risk_prediction'] = prediction_result
            
            if analysis_type in ["comprehensive", "network"]:
                network_result = await self.ai_service_manager.network_analysis_service.analyze_relationships(
                    customer.customer_id, customer_data
                )
                analysis_results['network_analysis'] = network_result
            
            # Generate comprehensive insights
            insights = {
                'customer_id': customer.customer_id,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'ai_analysis_results': analysis_results,
                'overall_risk_score': self._calculate_ai_risk_score(analysis_results),
                'recommendations': self._generate_ai_recommendations(analysis_results)
            }
            
            self.logger.info(f"AI risk analysis completed for customer {customer.customer_id}")
            return insights
            
        except Exception as e:
            self.logger.error(f"AI risk analysis failed: {e}")
            return {"error": str(e)}
    
    async def adverse_media_monitoring(self, entity_name: str, monitoring_config: Dict = None) -> Dict[str, Any]:
        """Perform comprehensive adverse media monitoring"""
        if not hasattr(self, 'phase2_enabled') or not self.phase2_enabled:
            return {"error": "Phase 2 adverse media services not available"}
        
        try:
            self.logger.info(f"Starting adverse media monitoring for: {entity_name}")
            
            # Perform comprehensive adverse media scan
            scan_results = await self.adverse_media_manager.comprehensive_adverse_media_scan(
                entity_name, monitoring_config or {}
            )
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Adverse media monitoring failed: {e}")
            return {"error": str(e)}
    
    async def evaluate_risk_rules(self, customer: Customer, transaction_data: Dict = None) -> Dict[str, Any]:
        """Evaluate risk rules against customer and transaction data"""
        if not hasattr(self, 'phase2_enabled') or not self.phase2_enabled:
            return {"error": "Phase 2 risk rules engine not available"}
        
        try:
            # Prepare data for rule evaluation
            evaluation_data = {
                'customer': {
                    'customer_id': customer.customer_id,
                    'name': customer.name,
                    'customer_type': customer.customer_type,
                    'jurisdiction': customer.jurisdiction,
                    'risk_category': customer.risk_category,
                    'pep_status': customer.metadata.get('pep_status', False),
                    'country': customer.jurisdiction
                },
                'screening': {
                    'sanctions_match': customer.metadata.get('sanctions_score', 0.0),
                    'adverse_media_score': customer.metadata.get('adverse_media_score', 0.0)
                }
            }
            
            # Add transaction data if provided
            if transaction_data:
                evaluation_data['transaction'] = transaction_data
            
            # Evaluate rules
            rule_results = await self.risk_rules_manager.evaluate_rules(evaluation_data)
            
            # Process results
            triggered_rules = [r for r in rule_results if r.triggered]
            
            return {
                'customer_id': customer.customer_id,
                'evaluation_timestamp': datetime.now().isoformat(),
                'rules_evaluated': len(rule_results),
                'rules_triggered': len(triggered_rules),
                'triggered_rules': [
                    {
                        'rule_id': r.rule_id,
                        'rule_name': r.rule_name,
                        'risk_level': r.risk_level.value,
                        'confidence_score': r.confidence_score,
                        'matched_conditions': r.matched_conditions,
                        'actions_executed': r.actions_executed
                    }
                    for r in triggered_rules
                ],
                'overall_risk_level': self._determine_overall_risk_level(triggered_rules),
                'recommendations': self._generate_rule_recommendations(triggered_rules)
            }
            
        except Exception as e:
            self.logger.error(f"Risk rules evaluation failed: {e}")
            return {"error": str(e)}
    
    async def create_compliance_case(self, title: str, description: str, case_type: str,
                                   created_by: str, entity_id: str = None, 
                                   entity_name: str = None) -> Dict[str, Any]:
        """Create a new compliance case"""
        if not hasattr(self, 'phase2_enabled') or not self.phase2_enabled:
            return {"error": "Phase 2 case management not available"}
        
        try:
            # Import case types
            from services.compliance.case_management import CaseType
            
            # Convert string to enum
            case_type_enum = CaseType(case_type)
            
            # Create case
            case = self.case_management_system.create_case(
                title=title,
                description=description,
                case_type=case_type_enum,
                created_by=created_by,
                entity_id=entity_id,
                entity_name=entity_name
            )
            
            # Perform initial AI analysis
            analysis = await self.case_management_system.analyze_case(case.case_id)
            
            return {
                'case_id': case.case_id,
                'case_number': case.case_number,
                'status': case.status.value,
                'priority': case.priority.value,
                'created_at': case.created_at.isoformat(),
                'due_date': case.due_date.isoformat() if case.due_date else None,
                'ai_analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Case creation failed: {e}")
            return {"error": str(e)}
    
    async def comprehensive_compliance_assessment(self, customer: Customer) -> Dict[str, Any]:
        """Perform comprehensive compliance assessment using all Phase 2 capabilities"""
        if not hasattr(self, 'phase2_enabled') or not self.phase2_enabled:
            return {"error": "Phase 2 services not available"}
        
        self.logger.info(f"Starting comprehensive Phase 2 compliance assessment for {customer.customer_id}")
        
        assessment_results = {
            'customer_id': customer.customer_id,
            'assessment_timestamp': datetime.now().isoformat(),
            'phase': 'Phase 2 - Advanced AI & Compliance Automation'
        }
        
        try:
            # 1. Core compliance checks
            core_results = await self.comprehensive_compliance_check(customer)
            assessment_results['core_compliance'] = core_results
            
            # 2. AI risk analysis
            ai_analysis = await self.ai_risk_analysis(customer, "comprehensive")
            assessment_results['ai_risk_analysis'] = ai_analysis
            
            # 3. Adverse media monitoring
            adverse_media = await self.adverse_media_monitoring(
                customer.name, 
                {'entity_type': customer.customer_type.lower()}
            )
            assessment_results['adverse_media'] = adverse_media
            
            # 4. Risk rules evaluation
            rules_evaluation = await self.evaluate_risk_rules(customer)
            assessment_results['risk_rules_evaluation'] = rules_evaluation
            
            # 5. Generate overall assessment
            overall_assessment = self._generate_overall_assessment(assessment_results)
            assessment_results['overall_assessment'] = overall_assessment
            
            # 6. Create case if high risk detected
            if overall_assessment['risk_level'] in ['HIGH', 'CRITICAL']:
                case_result = await self.create_compliance_case(
                    title=f"High Risk Assessment - {customer.name}",
                    description=f"Automated high risk detection for customer {customer.customer_id}",
                    case_type="customer_due_diligence",
                    created_by="system",
                    entity_id=customer.customer_id,
                    entity_name=customer.name
                )
                assessment_results['case_created'] = case_result
            
            self.logger.info(f"Comprehensive assessment completed for {customer.customer_id}")
            return assessment_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive assessment failed: {e}")
            assessment_results['error'] = str(e)
            return assessment_results
    
    def _calculate_ai_risk_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall AI risk score"""
        scores = []
        
        if 'anomaly_detection' in analysis_results:
            anomaly_score = analysis_results['anomaly_detection'].get('anomaly_score', 0.0)
            scores.append(anomaly_score)
        
        if 'risk_prediction' in analysis_results:
            risk_score = analysis_results['risk_prediction'].get('risk_score', 0.0)
            scores.append(risk_score)
        
        if 'network_analysis' in analysis_results:
            network_risk = analysis_results['network_analysis'].get('risk_score', 0.0)
            scores.append(network_risk)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_ai_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on AI analysis"""
        recommendations = []
        
        # Check anomaly detection results
        if 'anomaly_detection' in analysis_results:
            anomalies = analysis_results['anomaly_detection'].get('detected_anomalies', [])
            if anomalies:
                recommendations.append("Investigate detected anomalies in customer profile")
        
        # Check risk prediction results
        if 'risk_prediction' in analysis_results:
            risk_score = analysis_results['risk_prediction'].get('risk_score', 0.0)
            if risk_score > 0.7:
                recommendations.append("Implement enhanced monitoring due to high predicted risk")
        
        # Check network analysis results
        if 'network_analysis' in analysis_results:
            suspicious_connections = analysis_results['network_analysis'].get('suspicious_connections', [])
            if suspicious_connections:
                recommendations.append("Review suspicious network connections")
        
        return recommendations
    
    def _determine_overall_risk_level(self, triggered_rules) -> str:
        """Determine overall risk level from triggered rules"""
        if not triggered_rules:
            return "MINIMAL"
        
        # Get highest risk level
        risk_levels = ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        max_risk_index = 0
        
        for rule in triggered_rules:
            risk_level = rule.risk_level.value.upper()
            if risk_level in risk_levels:
                risk_index = risk_levels.index(risk_level)
                max_risk_index = max(max_risk_index, risk_index)
        
        return risk_levels[max_risk_index]
    
    def _generate_rule_recommendations(self, triggered_rules) -> List[str]:
        """Generate recommendations based on triggered rules"""
        recommendations = []
        
        for rule in triggered_rules:
            if rule.rule_name == "Sanctions List Match":
                recommendations.append("Immediate sanctions verification required")
            elif rule.rule_name == "PEP Screening Alert":
                recommendations.append("Conduct enhanced due diligence for PEP")
            elif rule.rule_name == "High Value Transaction Alert":
                recommendations.append("Review transaction for suspicious activity")
            elif rule.rule_name == "High Risk Country Alert":
                recommendations.append("Apply enhanced monitoring for geographic risk")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_overall_assessment(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall compliance assessment"""
        risk_indicators = []
        risk_scores = []
        
        # Analyze core compliance results
        core_compliance = assessment_results.get('core_compliance', {})
        failed_checks = [rec for rec, result in core_compliance.items() if result.status == 'FAIL']
        if failed_checks:
            risk_indicators.append(f"Failed {len(failed_checks)} core compliance checks")
        
        # Analyze AI risk analysis
        ai_analysis = assessment_results.get('ai_risk_analysis', {})
        if not ai_analysis.get('error'):
            ai_risk_score = ai_analysis.get('overall_risk_score', 0.0)
            risk_scores.append(ai_risk_score)
            if ai_risk_score > 0.7:
                risk_indicators.append("High AI-detected risk score")
        
        # Analyze adverse media
        adverse_media = assessment_results.get('adverse_media', {})
        if not adverse_media.get('error'):
            overall_assessment = adverse_media.get('overall_assessment', {})
            media_risk_level = overall_assessment.get('overall_risk_level', 'MINIMAL')
            if media_risk_level in ['HIGH', 'CRITICAL']:
                risk_indicators.append("Significant adverse media detected")
        
        # Analyze risk rules
        rules_evaluation = assessment_results.get('risk_rules_evaluation', {})
        if not rules_evaluation.get('error'):
            triggered_count = rules_evaluation.get('rules_triggered', 0)
            if triggered_count > 0:
                risk_indicators.append(f"{triggered_count} risk rules triggered")
        
        # Calculate overall risk score
        overall_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Determine risk level
        if overall_score >= 0.8 or len(risk_indicators) >= 3:
            risk_level = 'CRITICAL'
        elif overall_score >= 0.6 or len(risk_indicators) >= 2:
            risk_level = 'HIGH'
        elif overall_score >= 0.4 or len(risk_indicators) >= 1:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'overall_risk_score': round(overall_score, 3),
            'risk_indicators': risk_indicators,
            'recommendation': self._get_risk_level_recommendation(risk_level),
            'next_actions': self._get_next_actions(risk_level, risk_indicators)
        }
    
    def _get_risk_level_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'CRITICAL': 'IMMEDIATE ACTION REQUIRED: Escalate to senior management and consider relationship termination',
            'HIGH': 'URGENT REVIEW: Implement enhanced monitoring and additional due diligence',
            'MEDIUM': 'ENHANCED MONITORING: Increase transaction monitoring and periodic reviews',
            'LOW': 'STANDARD MONITORING: Continue regular monitoring procedures'
        }
        return recommendations.get(risk_level, 'No specific recommendation')
    
    def _get_next_actions(self, risk_level: str, risk_indicators: List[str]) -> List[str]:
        """Get next actions based on risk assessment"""
        actions = []
        
        if risk_level in ['CRITICAL', 'HIGH']:
            actions.extend([
                'Create compliance case for investigation',
                'Notify compliance team immediately',
                'Implement enhanced monitoring',
                'Review and update customer risk rating'
            ])
        
        if risk_level == 'MEDIUM':
            actions.extend([
                'Schedule enhanced due diligence review',
                'Increase transaction monitoring frequency',
                'Document findings in customer file'
            ])
        
        # Add specific actions based on risk indicators
        for indicator in risk_indicators:
            if 'sanctions' in indicator.lower():
                actions.append('Verify sanctions list compliance')
            elif 'adverse media' in indicator.lower():
                actions.append('Review adverse media findings')
            elif 'ai-detected' in indicator.lower():
                actions.append('Investigate AI-identified anomalies')
        
        return list(set(actions))  # Remove duplicates

# Global platform instance
platform = CompliantOnePlatform()

async def initialize_platform():
    """Initialize the platform"""
    logger = get_logger(__name__)
    logger.info("Initializing Compliant.one Platform...")
    
    # Platform is initialized in constructor
    status = await platform.get_service_status()
    coverage = await platform.get_fatf_coverage()
    
    logger.info(f"Platform initialized with {len(platform.services)} services")
    logger.info(f"FATF Coverage: {coverage['coverage_percentage']:.1f}%")
    
    return platform

# Export main functions
__all__ = [
    'CompliantOnePlatform',
    'Customer',
    'ComplianceResult',
    'platform',
    'initialize_platform'
]
