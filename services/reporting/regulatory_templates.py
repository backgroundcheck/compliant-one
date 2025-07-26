"""
Regulatory Reporting Templates Service
Phase 3: Pre-built templates for common compliance reports
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import io
import base64

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ReportTemplate:
    """Regulatory report template definition"""
    template_id: str
    name: str
    description: str
    regulatory_framework: str  # FATF, FinCEN, EU, AUSTRAC, etc.
    report_type: str  # SAR, CTR, STR, Annual, etc.
    jurisdiction: str
    version: str
    created_date: datetime
    last_updated: datetime
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, Any]
    output_formats: List[str]  # PDF, XML, JSON, CSV
    template_data: Dict[str, Any]
    is_active: bool = True

@dataclass
class ReportInstance:
    """Instance of a generated report"""
    report_id: str
    template_id: str
    customer_id: Optional[str]
    generated_by: str
    generated_at: datetime
    report_period: Dict[str, str]
    data: Dict[str, Any]
    status: str  # draft, submitted, rejected, approved
    file_path: Optional[str] = None
    submission_reference: Optional[str] = None

class RegulatoryReportingEngine:
    """Advanced regulatory reporting engine with pre-built templates"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.templates = {}
        self.report_instances = {}
        
        # Initialize pre-built templates
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize pre-built regulatory report templates"""
        
        # US FinCEN SAR (Suspicious Activity Report)
        sar_template = ReportTemplate(
            template_id="fincen_sar",
            name="FinCEN Suspicious Activity Report",
            description="Form 111 - Suspicious Activity Report for financial institutions",
            regulatory_framework="FinCEN",
            report_type="SAR",
            jurisdiction="United States",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "filing_institution_name", "filing_institution_tin",
                "filing_institution_address", "contact_person",
                "suspect_information", "suspicious_activity_description",
                "activity_date", "activity_amount", "law_enforcement_contacted"
            ],
            optional_fields=[
                "suspect_ssn", "suspect_date_of_birth", "suspect_address",
                "account_number", "transaction_location", "narrative"
            ],
            validation_rules={
                "activity_amount": {"type": "number", "minimum": 0},
                "activity_date": {"type": "date", "format": "YYYY-MM-DD"},
                "suspect_information": {"type": "string", "min_length": 10}
            },
            output_formats=["PDF", "XML"],
            template_data=self._get_sar_template_data()
        )
        
        # US FinCEN CTR (Currency Transaction Report)
        ctr_template = ReportTemplate(
            template_id="fincen_ctr",
            name="FinCEN Currency Transaction Report",
            description="Form 112 - Currency Transaction Report for transactions over $10,000",
            regulatory_framework="FinCEN",
            report_type="CTR",
            jurisdiction="United States",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "filing_institution_name", "filing_institution_tin",
                "transaction_date", "transaction_amount", "currency_type",
                "customer_name", "customer_address", "customer_identification"
            ],
            optional_fields=[
                "customer_ssn", "customer_date_of_birth", "customer_occupation",
                "transaction_purpose", "cash_in_amount", "cash_out_amount"
            ],
            validation_rules={
                "transaction_amount": {"type": "number", "minimum": 10000},
                "transaction_date": {"type": "date", "format": "YYYY-MM-DD"},
                "currency_type": {"type": "string", "enum": ["USD", "EUR", "GBP", "CAD", "OTHER"]}
            },
            output_formats=["PDF", "XML"],
            template_data=self._get_ctr_template_data()
        )
        
        # EU STR (Suspicious Transaction Report)
        eu_str_template = ReportTemplate(
            template_id="eu_str",
            name="EU Suspicious Transaction Report",
            description="EU 4th Anti-Money Laundering Directive STR template",
            regulatory_framework="EU_AMLD",
            report_type="STR",
            jurisdiction="European Union",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "reporting_entity_name", "reporting_entity_identifier",
                "subject_name", "subject_address", "transaction_details",
                "suspicious_behavior_description", "report_date"
            ],
            optional_fields=[
                "subject_date_of_birth", "subject_nationality",
                "beneficial_owner_information", "connected_parties",
                "additional_information"
            ],
            validation_rules={
                "transaction_amount": {"type": "number", "minimum": 0},
                "report_date": {"type": "date", "format": "YYYY-MM-DD"},
                "subject_name": {"type": "string", "min_length": 2}
            },
            output_formats=["PDF", "XML", "JSON"],
            template_data=self._get_eu_str_template_data()
        )
        
        # UK MLRO Annual Report
        uk_mlro_template = ReportTemplate(
            template_id="uk_mlro_annual",
            name="UK MLRO Annual Report",
            description="Money Laundering Reporting Officer Annual Report to Senior Management",
            regulatory_framework="UK_MLR",
            report_type="Annual Report",
            jurisdiction="United Kingdom",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "firm_name", "firm_fca_number", "mlro_name",
                "report_period", "training_summary", "policies_review",
                "suspicious_activity_summary", "risk_assessment_update"
            ],
            optional_fields=[
                "staff_changes", "system_changes", "regulatory_updates",
                "recommendations", "action_plan"
            ],
            validation_rules={
                "report_period": {"type": "string", "pattern": r"\d{4}-\d{4}"},
                "mlro_name": {"type": "string", "min_length": 2}
            },
            output_formats=["PDF", "DOCX"],
            template_data=self._get_uk_mlro_template_data()
        )
        
        # AUSTRAC SMR (Suspicious Matter Report)
        austrac_smr_template = ReportTemplate(
            template_id="austrac_smr",
            name="AUSTRAC Suspicious Matter Report",
            description="Australian Transaction Reports and Analysis Centre SMR",
            regulatory_framework="AUSTRAC",
            report_type="SMR",
            jurisdiction="Australia",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "reporting_entity_abn", "reporting_entity_name",
                "subject_details", "transaction_details",
                "grounds_for_suspicion", "report_date"
            ],
            optional_fields=[
                "subject_alternative_names", "associated_accounts",
                "relevant_documents", "law_enforcement_action"
            ],
            validation_rules={
                "transaction_amount": {"type": "number", "minimum": 0},
                "report_date": {"type": "date", "format": "YYYY-MM-DD"},
                "reporting_entity_abn": {"type": "string", "length": 11}
            },
            output_formats=["PDF", "XML"],
            template_data=self._get_austrac_smr_template_data()
        )
        
        # Customer Risk Assessment Template
        cra_template = ReportTemplate(
            template_id="customer_risk_assessment",
            name="Customer Risk Assessment Report",
            description="Comprehensive customer risk assessment and profiling report",
            regulatory_framework="FATF",
            report_type="Risk Assessment",
            jurisdiction="International",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "customer_id", "customer_name", "assessment_date",
                "risk_factors", "overall_risk_rating", "risk_mitigation_measures"
            ],
            optional_fields=[
                "previous_assessments", "regulatory_changes",
                "monitoring_requirements", "review_schedule"
            ],
            validation_rules={
                "overall_risk_rating": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                "assessment_date": {"type": "date", "format": "YYYY-MM-DD"}
            },
            output_formats=["PDF", "JSON", "CSV"],
            template_data=self._get_cra_template_data()
        )
        
        # Compliance Monitoring Report
        monitoring_template = ReportTemplate(
            template_id="compliance_monitoring",
            name="Compliance Monitoring Report",
            description="Periodic compliance monitoring and effectiveness report",
            regulatory_framework="FATF",
            report_type="Monitoring Report",
            jurisdiction="International",
            version="1.0",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            required_fields=[
                "report_period", "monitoring_activities", "key_findings",
                "compliance_metrics", "recommendations"
            ],
            optional_fields=[
                "training_activities", "policy_updates", "system_enhancements",
                "regulatory_communications"
            ],
            validation_rules={
                "report_period": {"type": "string", "pattern": r"\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}"}
            },
            output_formats=["PDF", "DOCX", "JSON"],
            template_data=self._get_monitoring_template_data()
        )
        
        # Add all templates to the registry
        templates = [
            sar_template, ctr_template, eu_str_template,
            uk_mlro_template, austrac_smr_template,
            cra_template, monitoring_template
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
        
        self.logger.info(f"Initialized {len(self.templates)} regulatory report templates")
    
    def _get_sar_template_data(self) -> Dict[str, Any]:
        """Get SAR template structure"""
        return {
            "sections": [
                {
                    "section": "Filing Institution Information",
                    "fields": [
                        {"name": "filing_institution_name", "type": "text", "required": True},
                        {"name": "filing_institution_tin", "type": "text", "required": True},
                        {"name": "filing_institution_address", "type": "address", "required": True},
                        {"name": "contact_person", "type": "contact", "required": True}
                    ]
                },
                {
                    "section": "Subject Information",
                    "fields": [
                        {"name": "suspect_name", "type": "text", "required": True},
                        {"name": "suspect_ssn", "type": "ssn", "required": False},
                        {"name": "suspect_address", "type": "address", "required": False},
                        {"name": "suspect_phone", "type": "phone", "required": False}
                    ]
                },
                {
                    "section": "Suspicious Activity",
                    "fields": [
                        {"name": "activity_date", "type": "date", "required": True},
                        {"name": "activity_amount", "type": "currency", "required": True},
                        {"name": "suspicious_activity_description", "type": "textarea", "required": True},
                        {"name": "law_enforcement_contacted", "type": "boolean", "required": True}
                    ]
                }
            ],
            "validation": {
                "cross_validation": [
                    {"if": "law_enforcement_contacted == true", "then": "law_enforcement_agency required"}
                ]
            }
        }
    
    def _get_ctr_template_data(self) -> Dict[str, Any]:
        """Get CTR template structure"""
        return {
            "sections": [
                {
                    "section": "Filing Institution",
                    "fields": [
                        {"name": "filing_institution_name", "type": "text", "required": True},
                        {"name": "filing_institution_tin", "type": "text", "required": True},
                        {"name": "filing_institution_address", "type": "address", "required": True}
                    ]
                },
                {
                    "section": "Transaction Information",
                    "fields": [
                        {"name": "transaction_date", "type": "date", "required": True},
                        {"name": "transaction_amount", "type": "currency", "required": True},
                        {"name": "currency_type", "type": "select", "required": True, "options": ["USD", "EUR", "GBP", "OTHER"]},
                        {"name": "cash_in_amount", "type": "currency", "required": False},
                        {"name": "cash_out_amount", "type": "currency", "required": False}
                    ]
                },
                {
                    "section": "Customer Information",
                    "fields": [
                        {"name": "customer_name", "type": "text", "required": True},
                        {"name": "customer_address", "type": "address", "required": True},
                        {"name": "customer_identification", "type": "id_document", "required": True},
                        {"name": "customer_ssn", "type": "ssn", "required": False}
                    ]
                }
            ]
        }
    
    def _get_eu_str_template_data(self) -> Dict[str, Any]:
        """Get EU STR template structure"""
        return {
            "sections": [
                {
                    "section": "Reporting Entity",
                    "fields": [
                        {"name": "reporting_entity_name", "type": "text", "required": True},
                        {"name": "reporting_entity_identifier", "type": "text", "required": True},
                        {"name": "reporting_entity_address", "type": "address", "required": True},
                        {"name": "reporting_entity_country", "type": "country", "required": True}
                    ]
                },
                {
                    "section": "Subject Information",
                    "fields": [
                        {"name": "subject_name", "type": "text", "required": True},
                        {"name": "subject_address", "type": "address", "required": True},
                        {"name": "subject_nationality", "type": "country", "required": False},
                        {"name": "subject_date_of_birth", "type": "date", "required": False}
                    ]
                },
                {
                    "section": "Transaction Details",
                    "fields": [
                        {"name": "transaction_details", "type": "textarea", "required": True},
                        {"name": "transaction_amount", "type": "currency", "required": False},
                        {"name": "transaction_currency", "type": "select", "required": False, "options": ["EUR", "USD", "GBP", "OTHER"]},
                        {"name": "suspicious_behavior_description", "type": "textarea", "required": True}
                    ]
                }
            ]
        }
    
    def _get_uk_mlro_template_data(self) -> Dict[str, Any]:
        """Get UK MLRO annual report template structure"""
        return {
            "sections": [
                {
                    "section": "Executive Summary",
                    "fields": [
                        {"name": "firm_name", "type": "text", "required": True},
                        {"name": "firm_fca_number", "type": "text", "required": True},
                        {"name": "mlro_name", "type": "text", "required": True},
                        {"name": "report_period", "type": "text", "required": True}
                    ]
                },
                {
                    "section": "Training and Awareness",
                    "fields": [
                        {"name": "training_summary", "type": "textarea", "required": True},
                        {"name": "training_attendance", "type": "number", "required": False},
                        {"name": "training_effectiveness", "type": "textarea", "required": False}
                    ]
                },
                {
                    "section": "Policies and Procedures",
                    "fields": [
                        {"name": "policies_review", "type": "textarea", "required": True},
                        {"name": "policy_updates", "type": "textarea", "required": False},
                        {"name": "procedure_effectiveness", "type": "textarea", "required": False}
                    ]
                },
                {
                    "section": "Suspicious Activity",
                    "fields": [
                        {"name": "suspicious_activity_summary", "type": "textarea", "required": True},
                        {"name": "reports_submitted", "type": "number", "required": False},
                        {"name": "investigation_outcomes", "type": "textarea", "required": False}
                    ]
                }
            ]
        }
    
    def _get_austrac_smr_template_data(self) -> Dict[str, Any]:
        """Get AUSTRAC SMR template structure"""
        return {
            "sections": [
                {
                    "section": "Reporting Entity Details",
                    "fields": [
                        {"name": "reporting_entity_abn", "type": "text", "required": True},
                        {"name": "reporting_entity_name", "type": "text", "required": True},
                        {"name": "reporting_entity_address", "type": "address", "required": True}
                    ]
                },
                {
                    "section": "Subject Details",
                    "fields": [
                        {"name": "subject_name", "type": "text", "required": True},
                        {"name": "subject_address", "type": "address", "required": False},
                        {"name": "subject_date_of_birth", "type": "date", "required": False},
                        {"name": "subject_identification", "type": "id_document", "required": False}
                    ]
                },
                {
                    "section": "Transaction and Activity Details",
                    "fields": [
                        {"name": "transaction_details", "type": "textarea", "required": True},
                        {"name": "transaction_amount", "type": "currency", "required": False},
                        {"name": "grounds_for_suspicion", "type": "textarea", "required": True},
                        {"name": "report_date", "type": "date", "required": True}
                    ]
                }
            ]
        }
    
    def _get_cra_template_data(self) -> Dict[str, Any]:
        """Get Customer Risk Assessment template structure"""
        return {
            "sections": [
                {
                    "section": "Customer Information",
                    "fields": [
                        {"name": "customer_id", "type": "text", "required": True},
                        {"name": "customer_name", "type": "text", "required": True},
                        {"name": "customer_type", "type": "select", "required": True, "options": ["Individual", "Corporate", "Trust", "Partnership"]},
                        {"name": "assessment_date", "type": "date", "required": True}
                    ]
                },
                {
                    "section": "Risk Factors Assessment",
                    "fields": [
                        {"name": "customer_risk_factors", "type": "checklist", "required": True},
                        {"name": "product_risk_factors", "type": "checklist", "required": True},
                        {"name": "geographic_risk_factors", "type": "checklist", "required": True},
                        {"name": "delivery_channel_risk_factors", "type": "checklist", "required": True}
                    ]
                },
                {
                    "section": "Risk Rating and Mitigation",
                    "fields": [
                        {"name": "overall_risk_rating", "type": "select", "required": True, "options": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                        {"name": "risk_mitigation_measures", "type": "textarea", "required": True},
                        {"name": "monitoring_requirements", "type": "textarea", "required": False},
                        {"name": "review_schedule", "type": "text", "required": False}
                    ]
                }
            ]
        }
    
    def _get_monitoring_template_data(self) -> Dict[str, Any]:
        """Get Compliance Monitoring template structure"""
        return {
            "sections": [
                {
                    "section": "Report Overview",
                    "fields": [
                        {"name": "report_period", "type": "text", "required": True},
                        {"name": "report_author", "type": "text", "required": True},
                        {"name": "report_date", "type": "date", "required": True}
                    ]
                },
                {
                    "section": "Monitoring Activities",
                    "fields": [
                        {"name": "monitoring_activities", "type": "textarea", "required": True},
                        {"name": "testing_performed", "type": "textarea", "required": False},
                        {"name": "sample_sizes", "type": "text", "required": False}
                    ]
                },
                {
                    "section": "Findings and Recommendations",
                    "fields": [
                        {"name": "key_findings", "type": "textarea", "required": True},
                        {"name": "compliance_metrics", "type": "textarea", "required": True},
                        {"name": "recommendations", "type": "textarea", "required": True},
                        {"name": "action_plan", "type": "textarea", "required": False}
                    ]
                }
            ]
        }
    
    def get_available_templates(self, jurisdiction: Optional[str] = None, 
                              report_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available report templates with optional filtering"""
        filtered_templates = []
        
        for template in self.templates.values():
            if not template.is_active:
                continue
            
            if jurisdiction and template.jurisdiction.lower() != jurisdiction.lower():
                continue
            
            if report_type and template.report_type.lower() != report_type.lower():
                continue
            
            template_summary = {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "regulatory_framework": template.regulatory_framework,
                "report_type": template.report_type,
                "jurisdiction": template.jurisdiction,
                "version": template.version,
                "output_formats": template.output_formats,
                "last_updated": template.last_updated.isoformat()
            }
            
            filtered_templates.append(template_summary)
        
        return filtered_templates
    
    def get_template_details(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed template information"""
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        
        return {
            "template_info": asdict(template),
            "field_definitions": template.template_data,
            "validation_rules": template.validation_rules,
            "sample_data": self._generate_sample_data(template_id)
        }
    
    def _generate_sample_data(self, template_id: str) -> Dict[str, Any]:
        """Generate sample data for template"""
        # This would generate realistic sample data for each template
        # For now, returning basic placeholder data
        
        sample_data = {
            "fincen_sar": {
                "filing_institution_name": "First National Bank",
                "filing_institution_tin": "12-3456789",
                "suspect_name": "John Doe",
                "activity_date": "2024-01-15",
                "activity_amount": 25000.00,
                "suspicious_activity_description": "Multiple structured transactions just below reporting threshold"
            },
            "fincen_ctr": {
                "filing_institution_name": "Community Credit Union",
                "transaction_date": "2024-01-20",
                "transaction_amount": 15000.00,
                "currency_type": "USD",
                "customer_name": "Jane Smith"
            },
            "eu_str": {
                "reporting_entity_name": "European Banking Corporation",
                "subject_name": "Corporate Entity ABC",
                "transaction_amount": 50000.00,
                "suspicious_behavior_description": "Unusual cross-border transactions with high-risk jurisdiction"
            }
        }
        
        return sample_data.get(template_id, {})
    
    def validate_report_data(self, template_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate report data against template requirements"""
        if template_id not in self.templates:
            return {"valid": False, "errors": ["Template not found"]}
        
        template = self.templates[template_id]
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        for required_field in template.required_fields:
            if required_field not in data or not data[required_field]:
                validation_result["errors"].append(f"Required field missing: {required_field}")
                validation_result["valid"] = False
        
        # Apply validation rules
        for field, rules in template.validation_rules.items():
            if field in data:
                field_value = data[field]
                
                # Type validation
                if "type" in rules:
                    if not self._validate_field_type(field_value, rules["type"]):
                        validation_result["errors"].append(f"Invalid type for field {field}: expected {rules['type']}")
                        validation_result["valid"] = False
                
                # Numeric validation
                if "minimum" in rules and isinstance(field_value, (int, float)):
                    if field_value < rules["minimum"]:
                        validation_result["errors"].append(f"Value for {field} below minimum: {rules['minimum']}")
                        validation_result["valid"] = False
                
                # String length validation
                if "min_length" in rules and isinstance(field_value, str):
                    if len(field_value) < rules["min_length"]:
                        validation_result["errors"].append(f"Value for {field} too short: minimum {rules['min_length']} characters")
                        validation_result["valid"] = False
                
                # Enum validation
                if "enum" in rules:
                    if field_value not in rules["enum"]:
                        validation_result["errors"].append(f"Invalid value for {field}: must be one of {rules['enum']}")
                        validation_result["valid"] = False
        
        return validation_result
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)),
            "date": lambda v: isinstance(v, str) and self._is_valid_date(v),
            "boolean": lambda v: isinstance(v, bool),
            "currency": lambda v: isinstance(v, (int, float)) and v >= 0
        }
        
        validator = type_validators.get(expected_type, lambda v: True)
        return validator(value)
    
    def _is_valid_date(self, date_string: str) -> bool:
        """Check if string is valid date"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def generate_report(self, template_id: str, data: Dict[str, Any], 
                       output_format: str = "PDF", customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate regulatory report from template and data"""
        try:
            # Validate template exists
            if template_id not in self.templates:
                return {"success": False, "error": "Template not found"}
            
            template = self.templates[template_id]
            
            # Validate data
            validation_result = self.validate_report_data(template_id, data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Data validation failed",
                    "validation_errors": validation_result["errors"]
                }
            
            # Check output format support
            if output_format not in template.output_formats:
                return {
                    "success": False,
                    "error": f"Output format {output_format} not supported for this template"
                }
            
            # Generate report ID
            report_id = f"report_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create report instance
            report_instance = ReportInstance(
                report_id=report_id,
                template_id=template_id,
                customer_id=customer_id,
                generated_by="system",  # In production, use actual user
                generated_at=datetime.now(),
                report_period=data.get("report_period", {"start": "2024-01-01", "end": "2024-12-31"}),
                data=data,
                status="draft"
            )
            
            # Generate report content
            report_content = self._generate_report_content(template, data, output_format)
            
            # Store report instance
            self.report_instances[report_id] = report_instance
            
            return {
                "success": True,
                "report_id": report_id,
                "template_name": template.name,
                "output_format": output_format,
                "generated_at": report_instance.generated_at.isoformat(),
                "content": report_content,
                "download_url": f"/api/v1/reports/download/{report_id}",
                "validation_warnings": validation_result.get("warnings", [])
            }
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_report_content(self, template: ReportTemplate, data: Dict[str, Any], 
                               output_format: str) -> Dict[str, Any]:
        """Generate report content in specified format"""
        if output_format == "PDF":
            return self._generate_pdf_content(template, data)
        elif output_format == "XML":
            return self._generate_xml_content(template, data)
        elif output_format == "JSON":
            return self._generate_json_content(template, data)
        elif output_format == "CSV":
            return self._generate_csv_content(template, data)
        else:
            return {"content_type": "text", "content": "Unsupported format"}
    
    def _generate_pdf_content(self, template: ReportTemplate, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF report content"""
        # In production, use a proper PDF generation library like ReportLab
        pdf_content = f"""
        {template.name}
        {template.description}
        
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Report Data:
        {json.dumps(data, indent=2)}
        """
        
        return {
            "content_type": "application/pdf",
            "content": base64.b64encode(pdf_content.encode()).decode(),
            "filename": f"{template.template_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    
    def _generate_xml_content(self, template: ReportTemplate, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate XML report content"""
        # Simple XML generation - in production, use proper XML libraries
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<{template.report_type.lower().replace(' ', '_')}>
    <template_id>{template.template_id}</template_id>
    <generated_at>{datetime.now().isoformat()}</generated_at>
    <data>
"""
        
        for key, value in data.items():
            xml_content += f"        <{key}>{value}</{key}>\n"
        
        xml_content += f"""    </data>
</{template.report_type.lower().replace(' ', '_')}>"""
        
        return {
            "content_type": "application/xml",
            "content": xml_content,
            "filename": f"{template.template_id}_{datetime.now().strftime('%Y%m%d')}.xml"
        }
    
    def _generate_json_content(self, template: ReportTemplate, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON report content"""
        json_content = {
            "template_info": {
                "template_id": template.template_id,
                "name": template.name,
                "regulatory_framework": template.regulatory_framework,
                "jurisdiction": template.jurisdiction
            },
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": template.report_type
            },
            "report_data": data
        }
        
        return {
            "content_type": "application/json",
            "content": json.dumps(json_content, indent=2),
            "filename": f"{template.template_id}_{datetime.now().strftime('%Y%m%d')}.json"
        }
    
    def _generate_csv_content(self, template: ReportTemplate, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSV report content"""
        # Simple CSV generation
        csv_lines = ["Field,Value"]
        for key, value in data.items():
            csv_lines.append(f"{key},{value}")
        
        csv_content = "\n".join(csv_lines)
        
        return {
            "content_type": "text/csv",
            "content": csv_content,
            "filename": f"{template.template_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    
    def get_report_status(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report generation status"""
        if report_id not in self.report_instances:
            return None
        
        report = self.report_instances[report_id]
        
        return {
            "report_id": report.report_id,
            "template_id": report.template_id,
            "status": report.status,
            "generated_at": report.generated_at.isoformat(),
            "customer_id": report.customer_id,
            "submission_reference": report.submission_reference
        }
    
    def get_reporting_analytics(self) -> Dict[str, Any]:
        """Get reporting analytics and statistics"""
        total_reports = len(self.report_instances)
        
        # Reports by template
        reports_by_template = {}
        reports_by_status = {}
        
        for report in self.report_instances.values():
            reports_by_template[report.template_id] = reports_by_template.get(report.template_id, 0) + 1
            reports_by_status[report.status] = reports_by_status.get(report.status, 0) + 1
        
        return {
            "total_templates": len(self.templates),
            "active_templates": len([t for t in self.templates.values() if t.is_active]),
            "total_reports_generated": total_reports,
            "reports_by_template": reports_by_template,
            "reports_by_status": reports_by_status,
            "supported_jurisdictions": list(set([t.jurisdiction for t in self.templates.values()])),
            "supported_frameworks": list(set([t.regulatory_framework for t in self.templates.values()]))
        }


class RegulatoryReportingService:
    """Service wrapper for regulatory reporting engine"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.engine = RegulatoryReportingEngine()
        self.service_status = "operational"
    
    def get_templates(self, jurisdiction: Optional[str] = None, 
                     report_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available report templates"""
        try:
            return self.engine.get_available_templates(jurisdiction, report_type)
        except Exception as e:
            self.logger.error(f"Failed to get templates: {e}")
            return []
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """Get template details"""
        try:
            details = self.engine.get_template_details(template_id)
            if details:
                return {"success": True, "data": details}
            else:
                return {"success": False, "error": "Template not found"}
        except Exception as e:
            self.logger.error(f"Failed to get template details: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_report(self, template_id: str, data: Dict[str, Any], 
                       output_format: str = "PDF", customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate regulatory report"""
        try:
            return self.engine.generate_report(template_id, data, output_format, customer_id)
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_data(self, template_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate report data"""
        try:
            return self.engine.validate_report_data(template_id, data)
        except Exception as e:
            self.logger.error(f"Failed to validate data: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get report status"""
        try:
            status = self.engine.get_report_status(report_id)
            if status:
                return {"success": True, "data": status}
            else:
                return {"success": False, "error": "Report not found"}
        except Exception as e:
            self.logger.error(f"Failed to get report status: {e}")
            return {"success": False, "error": str(e)}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get reporting analytics"""
        try:
            return self.engine.get_reporting_analytics()
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for reporting service"""
        try:
            analytics = self.engine.get_reporting_analytics()
            
            return {
                "status": self.service_status,
                "total_templates": analytics["total_templates"],
                "active_templates": analytics["active_templates"],
                "supported_jurisdictions": len(analytics["supported_jurisdictions"]),
                "supported_frameworks": len(analytics["supported_frameworks"]),
                "reports_generated": analytics["total_reports_generated"],
                "capabilities": [
                    "Multi-jurisdiction template support",
                    "Data validation and verification",
                    "Multiple output formats (PDF, XML, JSON, CSV)",
                    "Regulatory compliance checking",
                    "Report tracking and status monitoring"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
