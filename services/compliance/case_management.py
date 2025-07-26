"""
Advanced Case Management System - Phase 2
📋 Intelligent Case Workflow, AI-powered Investigation Tools, Compliance Tracking
Comprehensive Investigation Management with Automated Compliance Reporting
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
import asyncio

from utils.logger import ComplianceLogger

class CaseStatus(Enum):
    """Case status enumeration"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    ARCHIVED = "archived"

class CasePriority(Enum):
    """Case priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class CaseType(Enum):
    """Types of compliance cases"""
    AML_INVESTIGATION = "aml_investigation"
    SANCTIONS_VIOLATION = "sanctions_violation"
    PEP_REVIEW = "pep_review"
    ADVERSE_MEDIA = "adverse_media"
    TRANSACTION_MONITORING = "transaction_monitoring"
    CUSTOMER_DUE_DILIGENCE = "customer_due_diligence"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    REGULATORY_INQUIRY = "regulatory_inquiry"
    INTERNAL_AUDIT = "internal_audit"
    POLICY_VIOLATION = "policy_violation"

class ActionType(Enum):
    """Types of case actions"""
    CREATED = "created"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"
    COMMENT_ADDED = "comment_added"
    DOCUMENT_ATTACHED = "document_attached"
    EVIDENCE_ADDED = "evidence_added"
    REVIEW_COMPLETED = "review_completed"
    ESCALATED = "escalated"
    CLOSED = "closed"
    REOPENED = "reopened"

class RiskRating(Enum):
    """Risk rating for cases"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CaseAction:
    """Individual action/event in case history"""
    action_id: str
    action_type: ActionType
    performed_by: str
    timestamp: datetime
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)

@dataclass
class CaseEvidence:
    """Evidence item for a case"""
    evidence_id: str
    evidence_type: str  # document, screenshot, data_export, etc.
    title: str
    description: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_by: str = "system"
    collected_at: datetime = field(default_factory=datetime.now)
    hash_value: Optional[str] = None  # For integrity verification

@dataclass
class CaseTask:
    """Task within a case"""
    task_id: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    priority: CasePriority = CasePriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)  # Other task IDs
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

@dataclass
class ComplianceCase:
    """Main case entity"""
    case_id: str
    case_number: str  # Human-readable case number
    title: str
    description: str
    case_type: CaseType
    status: CaseStatus
    priority: CasePriority
    risk_rating: RiskRating
    
    # Parties involved
    created_by: str
    assigned_to: Optional[str] = None
    entity_id: Optional[str] = None  # Customer/entity being investigated
    entity_name: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Case content
    actions: List[CaseAction] = field(default_factory=list)
    evidence: List[CaseEvidence] = field(default_factory=list)
    tasks: List[CaseTask] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Compliance tracking
    regulatory_refs: List[str] = field(default_factory=list)  # FATF R.10, etc.
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Analysis results
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    investigation_findings: Dict[str, Any] = field(default_factory=dict)
    final_determination: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CaseTemplate:
    """Template for creating standard cases"""
    template_id: str
    name: str
    description: str
    case_type: CaseType
    default_priority: CasePriority
    default_tasks: List[Dict[str, Any]] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    estimated_duration_days: Optional[int] = None

class CaseWorkflowEngine:
    """Engine for managing case workflows and automation"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("case_workflow_engine")
        
        # Workflow rules
        self.status_transitions = self._define_status_transitions()
        self.auto_assignment_rules = self._define_assignment_rules()
        self.escalation_rules = self._define_escalation_rules()
        
        # SLA configurations
        self.sla_config = self._define_sla_config()
    
    def _define_status_transitions(self) -> Dict[CaseStatus, List[CaseStatus]]:
        """Define allowed status transitions"""
        return {
            CaseStatus.NEW: [CaseStatus.ASSIGNED, CaseStatus.IN_PROGRESS, CaseStatus.CLOSED],
            CaseStatus.ASSIGNED: [CaseStatus.IN_PROGRESS, CaseStatus.UNDER_REVIEW, CaseStatus.ESCALATED],
            CaseStatus.IN_PROGRESS: [CaseStatus.UNDER_REVIEW, CaseStatus.PENDING_APPROVAL, CaseStatus.ESCALATED, CaseStatus.RESOLVED],
            CaseStatus.UNDER_REVIEW: [CaseStatus.IN_PROGRESS, CaseStatus.PENDING_APPROVAL, CaseStatus.RESOLVED, CaseStatus.ESCALATED],
            CaseStatus.PENDING_APPROVAL: [CaseStatus.RESOLVED, CaseStatus.IN_PROGRESS, CaseStatus.ESCALATED],
            CaseStatus.ESCALATED: [CaseStatus.IN_PROGRESS, CaseStatus.UNDER_REVIEW, CaseStatus.RESOLVED],
            CaseStatus.RESOLVED: [CaseStatus.CLOSED, CaseStatus.REOPENED],
            CaseStatus.CLOSED: [CaseStatus.REOPENED, CaseStatus.ARCHIVED],
            CaseStatus.ARCHIVED: []  # Final state
        }
    
    def _define_assignment_rules(self) -> Dict[str, Any]:
        """Define automatic assignment rules"""
        return {
            CaseType.SANCTIONS_VIOLATION: {
                'queue': 'sanctions_team',
                'auto_assign': True,
                'priority_boost': True
            },
            CaseType.PEP_REVIEW: {
                'queue': 'pep_team',
                'auto_assign': True,
                'priority_boost': False
            },
            CaseType.AML_INVESTIGATION: {
                'queue': 'aml_investigators',
                'auto_assign': False,
                'priority_boost': True
            },
            CaseType.TRANSACTION_MONITORING: {
                'queue': 'transaction_analysts',
                'auto_assign': True,
                'priority_boost': False
            }
        }
    
    def _define_escalation_rules(self) -> List[Dict[str, Any]]:
        """Define escalation rules"""
        return [
            {
                'name': 'High Priority Overdue',
                'condition': {
                    'priority': [CasePriority.HIGH, CasePriority.CRITICAL, CasePriority.URGENT],
                    'overdue_hours': 24
                },
                'action': 'escalate_to_manager'
            },
            {
                'name': 'Critical Case Stale',
                'condition': {
                    'priority': [CasePriority.CRITICAL, CasePriority.URGENT],
                    'inactive_hours': 4
                },
                'action': 'alert_senior_management'
            },
            {
                'name': 'Sanctions Case Overdue',
                'condition': {
                    'case_type': [CaseType.SANCTIONS_VIOLATION],
                    'overdue_hours': 2
                },
                'action': 'immediate_escalation'
            }
        ]
    
    def _define_sla_config(self) -> Dict[str, Dict[str, int]]:
        """Define SLA configurations (hours)"""
        return {
            CaseType.SANCTIONS_VIOLATION.value: {
                'initial_response': 1,
                'investigation': 24,
                'resolution': 72
            },
            CaseType.PEP_REVIEW.value: {
                'initial_response': 4,
                'investigation': 48,
                'resolution': 120
            },
            CaseType.AML_INVESTIGATION.value: {
                'initial_response': 8,
                'investigation': 72,
                'resolution': 240
            },
            CaseType.TRANSACTION_MONITORING.value: {
                'initial_response': 2,
                'investigation': 24,
                'resolution': 96
            },
            CaseType.ADVERSE_MEDIA.value: {
                'initial_response': 8,
                'investigation': 48,
                'resolution': 168
            }
        }
    
    def validate_status_transition(self, current_status: CaseStatus, new_status: CaseStatus) -> bool:
        """Validate if status transition is allowed"""
        allowed_transitions = self.status_transitions.get(current_status, [])
        return new_status in allowed_transitions
    
    def get_auto_assignment(self, case_type: CaseType) -> Optional[Dict[str, Any]]:
        """Get auto-assignment configuration for case type"""
        return self.auto_assignment_rules.get(case_type)
    
    def check_escalation_rules(self, case: ComplianceCase) -> List[str]:
        """Check if case meets escalation criteria"""
        triggered_rules = []
        now = datetime.now()
        
        for rule in self.escalation_rules:
            condition = rule['condition']
            
            # Check priority condition
            if 'priority' in condition and case.priority not in condition['priority']:
                continue
            
            # Check case type condition
            if 'case_type' in condition and case.case_type not in condition['case_type']:
                continue
            
            # Check overdue condition
            if 'overdue_hours' in condition and case.due_date:
                if now > case.due_date + timedelta(hours=condition['overdue_hours']):
                    triggered_rules.append(rule['name'])
                    continue
            
            # Check inactive condition
            if 'inactive_hours' in condition:
                last_action_time = case.updated_at
                if case.actions:
                    last_action_time = max(action.timestamp for action in case.actions)
                
                if now > last_action_time + timedelta(hours=condition['inactive_hours']):
                    triggered_rules.append(rule['name'])
        
        return triggered_rules
    
    def calculate_sla_deadlines(self, case: ComplianceCase) -> Dict[str, datetime]:
        """Calculate SLA deadlines for case"""
        sla_config = self.sla_config.get(case.case_type.value, {})
        deadlines = {}
        
        for milestone, hours in sla_config.items():
            deadline = case.created_at + timedelta(hours=hours)
            deadlines[milestone] = deadline
        
        return deadlines

class CaseAnalyticsEngine:
    """AI-powered analytics engine for case insights"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("case_analytics_engine")
    
    async def analyze_case(self, case: ComplianceCase) -> Dict[str, Any]:
        """Perform AI analysis on case"""
        analysis = {
            'case_id': case.case_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'risk_assessment': await self._assess_case_risk(case),
            'pattern_analysis': await self._analyze_patterns(case),
            'entity_analysis': await self._analyze_entity(case),
            'timeline_analysis': await self._analyze_timeline(case),
            'recommendations': await self._generate_recommendations(case),
            'confidence_score': 0.0
        }
        
        # Calculate overall confidence
        analysis['confidence_score'] = self._calculate_confidence(analysis)
        
        return analysis
    
    async def _assess_case_risk(self, case: ComplianceCase) -> Dict[str, Any]:
        """Assess risk level and factors for case"""
        risk_factors = []
        risk_score = 0.0
        
        # Case type risk weighting
        type_risk_weights = {
            CaseType.SANCTIONS_VIOLATION: 0.9,
            CaseType.AML_INVESTIGATION: 0.8,
            CaseType.PEP_REVIEW: 0.7,
            CaseType.SUSPICIOUS_ACTIVITY: 0.8,
            CaseType.ADVERSE_MEDIA: 0.6,
            CaseType.TRANSACTION_MONITORING: 0.5
        }
        
        base_risk = type_risk_weights.get(case.case_type, 0.5)
        risk_score += base_risk * 0.4
        
        # Priority impact
        priority_weights = {
            CasePriority.CRITICAL: 0.9,
            CasePriority.URGENT: 0.8,
            CasePriority.HIGH: 0.7,
            CasePriority.MEDIUM: 0.5,
            CasePriority.LOW: 0.3
        }
        
        priority_impact = priority_weights.get(case.priority, 0.5)
        risk_score += priority_impact * 0.3
        
        # Evidence analysis
        if case.evidence:
            high_risk_evidence = len([e for e in case.evidence if 'high_risk' in e.metadata.get('tags', [])])
            evidence_impact = min(0.3, high_risk_evidence * 0.1)
            risk_score += evidence_impact
            
            if high_risk_evidence > 0:
                risk_factors.append(f"{high_risk_evidence} high-risk evidence items")
        
        # Timeline factors
        if case.due_date and datetime.now() > case.due_date:
            risk_factors.append("Case overdue")
            risk_score += 0.2
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskRating.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskRating.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskRating.MEDIUM
        elif risk_score >= 0.2:
            risk_level = RiskRating.LOW
        else:
            risk_level = RiskRating.MINIMAL
        
        return {
            'risk_level': risk_level.value,
            'risk_score': round(risk_score, 3),
            'risk_factors': risk_factors,
            'type_based_risk': base_risk,
            'priority_impact': priority_impact
        }
    
    async def _analyze_patterns(self, case: ComplianceCase) -> Dict[str, Any]:
        """Analyze patterns in case data"""
        patterns = {
            'temporal_patterns': [],
            'behavioral_patterns': [],
            'network_patterns': [],
            'anomalies': []
        }
        
        # Analyze action patterns
        if case.actions:
            action_intervals = []
            for i in range(1, len(case.actions)):
                interval = (case.actions[i].timestamp - case.actions[i-1].timestamp).total_seconds() / 3600
                action_intervals.append(interval)
            
            if action_intervals:
                avg_interval = sum(action_intervals) / len(action_intervals)
                patterns['temporal_patterns'].append(f"Average action interval: {avg_interval:.1f} hours")
                
                # Detect unusual gaps
                long_gaps = [interval for interval in action_intervals if interval > avg_interval * 3]
                if long_gaps:
                    patterns['anomalies'].append(f"{len(long_gaps)} unusually long gaps between actions")
        
        # Analyze evidence patterns
        if case.evidence:
            evidence_types = {}
            for evidence in case.evidence:
                evidence_types[evidence.evidence_type] = evidence_types.get(evidence.evidence_type, 0) + 1
            
            patterns['behavioral_patterns'].append(f"Evidence distribution: {evidence_types}")
        
        return patterns
    
    async def _analyze_entity(self, case: ComplianceCase) -> Dict[str, Any]:
        """Analyze entity involved in case"""
        entity_analysis = {
            'entity_id': case.entity_id,
            'entity_name': case.entity_name,
            'risk_indicators': [],
            'historical_cases': 0,
            'relationship_analysis': {}
        }
        
        if case.entity_id:
            # Mock historical case analysis
            entity_analysis['historical_cases'] = 2  # Would query actual case history
            entity_analysis['risk_indicators'] = ['previous_investigations', 'geographic_risk']
        
        return entity_analysis
    
    async def _analyze_timeline(self, case: ComplianceCase) -> Dict[str, Any]:
        """Analyze case timeline and milestones"""
        timeline_analysis = {
            'case_age_days': (datetime.now() - case.created_at).days,
            'action_frequency': 0.0,
            'milestone_compliance': {},
            'predicted_resolution_date': None
        }
        
        # Calculate action frequency
        if case.actions:
            case_duration_hours = (datetime.now() - case.created_at).total_seconds() / 3600
            timeline_analysis['action_frequency'] = len(case.actions) / max(case_duration_hours, 1)
        
        # Predict resolution date based on case type and current progress
        case_type_avg_days = {
            CaseType.SANCTIONS_VIOLATION: 3,
            CaseType.PEP_REVIEW: 5,
            CaseType.AML_INVESTIGATION: 10,
            CaseType.TRANSACTION_MONITORING: 4,
            CaseType.ADVERSE_MEDIA: 7
        }
        
        avg_duration = case_type_avg_days.get(case.case_type, 7)
        predicted_date = case.created_at + timedelta(days=avg_duration)
        timeline_analysis['predicted_resolution_date'] = predicted_date.isoformat()
        
        return timeline_analysis
    
    async def _generate_recommendations(self, case: ComplianceCase) -> List[str]:
        """Generate AI-powered recommendations for case"""
        recommendations = []
        
        # Status-based recommendations
        if case.status == CaseStatus.NEW:
            recommendations.append("Assign case to appropriate investigator")
            recommendations.append("Conduct initial risk assessment")
        
        elif case.status == CaseStatus.IN_PROGRESS:
            if not case.evidence:
                recommendations.append("Collect supporting evidence")
            
            if len(case.actions) < 3:
                recommendations.append("Document investigation steps")
        
        # Type-specific recommendations
        if case.case_type == CaseType.SANCTIONS_VIOLATION:
            recommendations.append("Verify sanctions list matches")
            recommendations.append("Document compliance remediation steps")
        
        elif case.case_type == CaseType.PEP_REVIEW:
            recommendations.append("Conduct enhanced due diligence")
            recommendations.append("Review source of wealth documentation")
        
        # Priority-based recommendations
        if case.priority in [CasePriority.CRITICAL, CasePriority.URGENT]:
            recommendations.append("Escalate to senior management")
            recommendations.append("Consider immediate risk mitigation")
        
        # Timeline recommendations
        if case.due_date and datetime.now() > case.due_date:
            recommendations.append("Address overdue status")
            recommendations.append("Update timeline estimates")
        
        return recommendations
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""
        confidence_factors = []
        
        # Risk assessment confidence
        risk_assessment = analysis.get('risk_assessment', {})
        if risk_assessment.get('risk_factors'):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Pattern analysis confidence
        patterns = analysis.get('pattern_analysis', {})
        pattern_count = sum(len(patterns.get(key, [])) for key in patterns)
        pattern_confidence = min(0.9, 0.3 + pattern_count * 0.1)
        confidence_factors.append(pattern_confidence)
        
        # Entity analysis confidence
        entity_analysis = analysis.get('entity_analysis', {})
        if entity_analysis.get('entity_id'):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors)

class CaseManagementSystem:
    """Comprehensive case management system"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("case_management_system")
        
        # Storage
        self.cases: Dict[str, ComplianceCase] = {}
        self.templates: Dict[str, CaseTemplate] = {}
        
        # Configuration with safe access
        self.config = config or {}
        
        # Engines
        workflow_config = self.config.get('workflow', {}) if self.config else {}
        analytics_config = self.config.get('analytics', {}) if self.config else {}
        
        self.workflow_engine = CaseWorkflowEngine(workflow_config)
        self.analytics_engine = CaseAnalyticsEngine(analytics_config)
        
        # Configuration
        self.auto_save = self.config.get('auto_save', True)
        self.cases_file = self.config.get('cases_file', 'data/cases.json')
        self.templates_file = self.config.get('templates_file', 'data/case_templates.json')
        
        # Counters for case numbering
        self.case_counter = 1
        
        # Load existing data
        self._load_data()
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _load_data(self):
        """Load cases and templates from storage"""
        try:
            # Load cases
            cases_path = Path(self.cases_file)
            if cases_path.exists():
                with open(cases_path, 'r') as f:
                    cases_data = json.load(f)
                    
                for case_data in cases_data:
                    case = self._deserialize_case(case_data)
                    self.cases[case.case_id] = case
                
                # Update counter
                if self.cases:
                    max_number = max(int(case.case_number.split('-')[1]) for case in self.cases.values() if '-' in case.case_number)
                    self.case_counter = max_number + 1
                
                self.logger.logger.info(f"Loaded {len(self.cases)} cases from {self.cases_file}")
            
            # Load templates
            templates_path = Path(self.templates_file)
            if templates_path.exists():
                with open(templates_path, 'r') as f:
                    templates_data = json.load(f)
                    
                for template_data in templates_data:
                    template = self._deserialize_template(template_data)
                    self.templates[template.template_id] = template
                
                self.logger.logger.info(f"Loaded {len(self.templates)} templates from {self.templates_file}")
        
        except Exception as e:
            self.logger.logger.error(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save cases and templates to storage"""
        if not self.auto_save:
            return
        
        try:
            # Save cases
            cases_path = Path(self.cases_file)
            cases_path.parent.mkdir(parents=True, exist_ok=True)
            
            cases_data = [self._serialize_case(case) for case in self.cases.values()]
            
            with open(cases_path, 'w') as f:
                json.dump(cases_data, f, indent=2, default=str)
            
            # Save templates
            templates_path = Path(self.templates_file)
            templates_path.parent.mkdir(parents=True, exist_ok=True)
            
            templates_data = [asdict(template) for template in self.templates.values()]
            
            with open(templates_path, 'w') as f:
                json.dump(templates_data, f, indent=2, default=str)
            
            self.logger.logger.info("Saved cases and templates to storage")
        
        except Exception as e:
            self.logger.logger.error(f"Error saving data: {e}")
    
    def _serialize_case(self, case: ComplianceCase) -> Dict[str, Any]:
        """Serialize case to dictionary"""
        case_dict = asdict(case)
        
        # Convert enums to strings
        case_dict['case_type'] = case.case_type.value
        case_dict['status'] = case.status.value
        case_dict['priority'] = case.priority.value
        case_dict['risk_rating'] = case.risk_rating.value
        
        # Convert action enums
        for action in case_dict['actions']:
            action['action_type'] = action['action_type']
        
        # Convert task enums
        for task in case_dict['tasks']:
            task['priority'] = task['priority']
        
        return case_dict
    
    def _parse_enum_value(self, enum_class, value_str: str):
        """Parse enum value handling both 'EnumClass.VALUE' and 'value' formats"""
        if isinstance(value_str, str):
            # Handle 'EnumClass.VALUE' format
            if '.' in value_str:
                value_str = value_str.split('.')[-1]
            
            # Convert to lowercase for enum lookup
            if enum_class == CaseType:
                case_map = {
                    'AML_INVESTIGATION': 'aml_investigation',
                    'SANCTIONS_VIOLATION': 'sanctions_violation',
                    'PEP_REVIEW': 'pep_review',
                    'ADVERSE_MEDIA': 'adverse_media',
                    'TRANSACTION_MONITORING': 'transaction_monitoring',
                    'CUSTOMER_DUE_DILIGENCE': 'customer_due_diligence',
                    'SUSPICIOUS_ACTIVITY': 'suspicious_activity',
                    'REGULATORY_INQUIRY': 'regulatory_inquiry',
                    'INTERNAL_AUDIT': 'internal_audit',
                    'POLICY_VIOLATION': 'policy_violation'
                }
                value_str = case_map.get(value_str, value_str.lower())
            elif enum_class == CasePriority:
                priority_map = {
                    'URGENT': 'urgent',
                    'CRITICAL': 'critical',
                    'HIGH': 'high',
                    'MEDIUM': 'medium',
                    'LOW': 'low'
                }
                value_str = priority_map.get(value_str, value_str.lower())
            elif enum_class == CaseStatus:
                status_map = {
                    'OPEN': 'open',
                    'IN_PROGRESS': 'in_progress',
                    'PENDING_REVIEW': 'pending_review',
                    'ESCALATED': 'escalated',
                    'RESOLVED': 'resolved',
                    'CLOSED': 'closed',
                    'ARCHIVED': 'archived'
                }
                value_str = status_map.get(value_str, value_str.lower())
            elif enum_class == RiskRating:
                risk_map = {
                    'MINIMAL': 'minimal',
                    'LOW': 'low',
                    'MEDIUM': 'medium',
                    'HIGH': 'high',
                    'CRITICAL': 'critical'
                }
                value_str = risk_map.get(value_str, value_str.lower())
        
        return enum_class(value_str)
    
    def _deserialize_case(self, case_data: Dict[str, Any]) -> ComplianceCase:
        """Deserialize case from dictionary"""
        try:
            # Convert enum strings back to enums
            case_data['case_type'] = self._parse_enum_value(CaseType, case_data['case_type'])
            case_data['status'] = self._parse_enum_value(CaseStatus, case_data['status'])
            case_data['priority'] = self._parse_enum_value(CasePriority, case_data['priority'])
            case_data['risk_rating'] = self._parse_enum_value(RiskRating, case_data['risk_rating'])
            
            # Convert datetime strings
            datetime_fields = ['created_at', 'updated_at', 'due_date', 'closed_at']
            for field in datetime_fields:
                if case_data.get(field) and isinstance(case_data[field], str):
                    case_data[field] = datetime.fromisoformat(case_data[field])
            
            # Convert actions
            actions = []
            for action_data in case_data.get('actions', []):
                action_data['action_type'] = ActionType(action_data['action_type'])
                action_data['timestamp'] = datetime.fromisoformat(action_data['timestamp'])
                actions.append(CaseAction(**action_data))
            case_data['actions'] = actions
            
            # Convert evidence
            evidence = []
            for evidence_data in case_data.get('evidence', []):
                if evidence_data.get('collected_at') and isinstance(evidence_data['collected_at'], str):
                    evidence_data['collected_at'] = datetime.fromisoformat(evidence_data['collected_at'])
                evidence.append(CaseEvidence(**evidence_data))
            case_data['evidence'] = evidence
            
            # Convert tasks
            tasks = []
            for task_data in case_data.get('tasks', []):
                task_data['priority'] = CasePriority(task_data['priority'])
                datetime_fields = ['due_date', 'completed_at']
                for field in datetime_fields:
                    if task_data.get(field) and isinstance(task_data[field], str):
                        task_data[field] = datetime.fromisoformat(task_data[field])
                tasks.append(CaseTask(**task_data))
            case_data['tasks'] = tasks
            
            return ComplianceCase(**case_data)
        except Exception as e:
            self.logger.logger.error(f"Error deserializing case {case_data.get('case_id', 'unknown')}: {e}")
            raise
    
    def _deserialize_template(self, template_data: Dict[str, Any]) -> CaseTemplate:
        """Deserialize template from dictionary"""
        try:
            template_data['case_type'] = self._parse_enum_value(CaseType, template_data['case_type'])
            template_data['default_priority'] = self._parse_enum_value(CasePriority, template_data['default_priority'])
            return CaseTemplate(**template_data)
        except Exception as e:
            self.logger.logger.error(f"Error deserializing template {template_data.get('template_id', 'unknown')}: {e}")
            raise
    
    def _initialize_default_templates(self):
        """Initialize default case templates"""
        if self.templates:
            return  # Templates already loaded
        
        default_templates = [
            CaseTemplate(
                template_id="TMPL_SANCTIONS",
                name="Sanctions Screening Investigation",
                description="Template for sanctions screening violations",
                case_type=CaseType.SANCTIONS_VIOLATION,
                default_priority=CasePriority.CRITICAL,
                default_tasks=[
                    {
                        'title': 'Verify sanctions match',
                        'description': 'Confirm entity match against sanctions lists',
                        'estimated_hours': 2
                    },
                    {
                        'title': 'Document compliance measures',
                        'description': 'Record all compliance and remediation actions',
                        'estimated_hours': 4
                    },
                    {
                        'title': 'Report to authorities',
                        'description': 'File required regulatory reports',
                        'estimated_hours': 2
                    }
                ],
                required_evidence=['sanctions_list_match', 'entity_verification', 'compliance_documentation'],
                compliance_requirements=['FATF_R.6', 'FATF_R.7'],
                estimated_duration_days=3
            ),
            
            CaseTemplate(
                template_id="TMPL_PEP",
                name="PEP Enhanced Due Diligence",
                description="Template for PEP customer review",
                case_type=CaseType.PEP_REVIEW,
                default_priority=CasePriority.HIGH,
                default_tasks=[
                    {
                        'title': 'Verify PEP status',
                        'description': 'Confirm politically exposed person classification',
                        'estimated_hours': 3
                    },
                    {
                        'title': 'Enhanced due diligence',
                        'description': 'Conduct comprehensive background review',
                        'estimated_hours': 8
                    },
                    {
                        'title': 'Source of wealth verification',
                        'description': 'Verify and document source of wealth',
                        'estimated_hours': 6
                    },
                    {
                        'title': 'Risk assessment',
                        'description': 'Complete risk rating and approval process',
                        'estimated_hours': 2
                    }
                ],
                required_evidence=['pep_verification', 'source_of_wealth', 'enhanced_due_diligence'],
                compliance_requirements=['FATF_R.12'],
                estimated_duration_days=5
            ),
            
            CaseTemplate(
                template_id="TMPL_AML",
                name="AML Investigation",
                description="Template for anti-money laundering investigations",
                case_type=CaseType.AML_INVESTIGATION,
                default_priority=CasePriority.HIGH,
                default_tasks=[
                    {
                        'title': 'Transaction analysis',
                        'description': 'Analyze suspicious transaction patterns',
                        'estimated_hours': 6
                    },
                    {
                        'title': 'Customer background review',
                        'description': 'Review customer history and profile',
                        'estimated_hours': 4
                    },
                    {
                        'title': 'External data gathering',
                        'description': 'Collect external intelligence and verification',
                        'estimated_hours': 8
                    },
                    {
                        'title': 'Determination and reporting',
                        'description': 'Make final determination and file reports',
                        'estimated_hours': 4
                    }
                ],
                required_evidence=['transaction_records', 'customer_profile', 'external_intelligence'],
                compliance_requirements=['FATF_R.20', 'FATF_R.29'],
                estimated_duration_days=10
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
            
        self._save_data()
        self.logger.logger.info(f"Initialized {len(default_templates)} default templates")
    
    def create_case(self, title: str, description: str, case_type: CaseType,
                   created_by: str, entity_id: Optional[str] = None,
                   entity_name: Optional[str] = None, template_id: Optional[str] = None,
                   priority: Optional[CasePriority] = None) -> ComplianceCase:
        """Create a new case"""
        
        # Generate case ID and number
        case_id = str(uuid.uuid4())
        case_number = f"CASE-{self.case_counter:06d}"
        self.case_counter += 1
        
        # Use template if specified
        template = None
        if template_id:
            template = self.templates.get(template_id)
        
        # Determine priority
        if priority is None:
            priority = template.default_priority if template else CasePriority.MEDIUM
        
        # Create case
        case = ComplianceCase(
            case_id=case_id,
            case_number=case_number,
            title=title,
            description=description,
            case_type=case_type,
            status=CaseStatus.NEW,
            priority=priority,
            risk_rating=RiskRating.MEDIUM,  # Will be updated by analytics
            created_by=created_by,
            entity_id=entity_id,
            entity_name=entity_name
        )
        
        # Apply template
        if template:
            self._apply_template(case, template)
        
        # Calculate SLA deadlines
        sla_deadlines = self.workflow_engine.calculate_sla_deadlines(case)
        if 'resolution' in sla_deadlines:
            case.due_date = sla_deadlines['resolution']
        
        # Add creation action
        creation_action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.CREATED,
            performed_by=created_by,
            timestamp=datetime.now(),
            description=f"Case created: {title}"
        )
        case.actions.append(creation_action)
        
        # Store case
        self.cases[case_id] = case
        self._save_data()
        
        self.logger.logger.info(f"Created case {case_number} ({case_id})")
        
        return case
    
    def _apply_template(self, case: ComplianceCase, template: CaseTemplate):
        """Apply template to case"""
        # Add default tasks
        for task_data in template.default_tasks:
            task = CaseTask(
                task_id=str(uuid.uuid4()),
                title=task_data['title'],
                description=task_data['description'],
                priority=case.priority,
                estimated_hours=task_data.get('estimated_hours')
            )
            case.tasks.append(task)
        
        # Set compliance requirements
        case.compliance_requirements = template.compliance_requirements.copy()
        
        # Set metadata
        case.metadata['template_id'] = template.template_id
        case.metadata['required_evidence'] = template.required_evidence
    
    def update_case_status(self, case_id: str, new_status: CaseStatus, 
                          performed_by: str, comment: Optional[str] = None) -> bool:
        """Update case status"""
        try:
            case = self.cases.get(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            # Validate status transition
            if not self.workflow_engine.validate_status_transition(case.status, new_status):
                raise ValueError(f"Invalid status transition from {case.status.value} to {new_status.value}")
            
            old_status = case.status
            case.status = new_status
            case.updated_at = datetime.now()
            
            # Handle status-specific logic
            if new_status == CaseStatus.CLOSED:
                case.closed_at = datetime.now()
            elif new_status == CaseStatus.REOPENED:
                case.status = CaseStatus.IN_PROGRESS  # Reopened cases go to in progress
                case.closed_at = None
            
            # Add status change action
            description = f"Status changed from {old_status.value} to {new_status.value}"
            if comment:
                description += f": {comment}"
            
            action = CaseAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.STATUS_CHANGED,
                performed_by=performed_by,
                timestamp=datetime.now(),
                description=description,
                details={'old_status': old_status.value, 'new_status': new_status.value, 'comment': comment}
            )
            case.actions.append(action)
            
            self._save_data()
            self.logger.logger.info(f"Updated case {case.case_number} status to {new_status.value}")
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error updating case status: {e}")
            return False
    
    def assign_case(self, case_id: str, assigned_to: str, assigned_by: str) -> bool:
        """Assign case to user"""
        try:
            case = self.cases.get(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            old_assignee = case.assigned_to
            case.assigned_to = assigned_to
            case.updated_at = datetime.now()
            
            # Update status if case is new
            if case.status == CaseStatus.NEW:
                case.status = CaseStatus.ASSIGNED
            
            # Add assignment action
            description = f"Case assigned to {assigned_to}"
            if old_assignee:
                description = f"Case reassigned from {old_assignee} to {assigned_to}"
            
            action = CaseAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.ASSIGNED,
                performed_by=assigned_by,
                timestamp=datetime.now(),
                description=description,
                details={'old_assignee': old_assignee, 'new_assignee': assigned_to}
            )
            case.actions.append(action)
            
            self._save_data()
            self.logger.logger.info(f"Assigned case {case.case_number} to {assigned_to}")
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error assigning case: {e}")
            return False
    
    def add_comment(self, case_id: str, comment: str, author: str) -> bool:
        """Add comment to case"""
        try:
            case = self.cases.get(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            action = CaseAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.COMMENT_ADDED,
                performed_by=author,
                timestamp=datetime.now(),
                description=comment
            )
            case.actions.append(action)
            case.updated_at = datetime.now()
            
            self._save_data()
            self.logger.logger.info(f"Added comment to case {case.case_number}")
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error adding comment: {e}")
            return False
    
    def add_evidence(self, case_id: str, evidence: CaseEvidence) -> bool:
        """Add evidence to case"""
        try:
            case = self.cases.get(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            case.evidence.append(evidence)
            case.updated_at = datetime.now()
            
            # Add evidence action
            action = CaseAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.EVIDENCE_ADDED,
                performed_by=evidence.collected_by,
                timestamp=datetime.now(),
                description=f"Added evidence: {evidence.title}",
                details={'evidence_id': evidence.evidence_id, 'evidence_type': evidence.evidence_type}
            )
            case.actions.append(action)
            
            self._save_data()
            self.logger.logger.info(f"Added evidence to case {case.case_number}")
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error adding evidence: {e}")
            return False
    
    async def analyze_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Perform AI analysis on case"""
        try:
            case = self.cases.get(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            analysis = await self.analytics_engine.analyze_case(case)
            
            # Store analysis in case
            case.ai_analysis = analysis
            case.updated_at = datetime.now()
            
            # Update risk rating based on analysis
            risk_assessment = analysis.get('risk_assessment', {})
            risk_level = risk_assessment.get('risk_level', 'medium')
            case.risk_rating = RiskRating(risk_level)
            
            self._save_data()
            self.logger.logger.info(f"Completed AI analysis for case {case.case_number}")
            
            return analysis
            
        except Exception as e:
            self.logger.logger.error(f"Error analyzing case: {e}")
            return None
    
    def get_case(self, case_id: str) -> Optional[ComplianceCase]:
        """Get case by ID"""
        return self.cases.get(case_id)
    
    def get_case_by_number(self, case_number: str) -> Optional[ComplianceCase]:
        """Get case by case number"""
        for case in self.cases.values():
            if case.case_number == case_number:
                return case
        return None
    
    def list_cases(self, filters: Optional[Dict[str, Any]] = None) -> List[ComplianceCase]:
        """List cases with optional filters"""
        cases = list(self.cases.values())
        
        if not filters:
            return cases
        
        # Apply filters
        if 'status' in filters:
            cases = [c for c in cases if c.status == filters['status']]
        
        if 'case_type' in filters:
            cases = [c for c in cases if c.case_type == filters['case_type']]
        
        if 'assigned_to' in filters:
            cases = [c for c in cases if c.assigned_to == filters['assigned_to']]
        
        if 'priority' in filters:
            cases = [c for c in cases if c.priority == filters['priority']]
        
        if 'created_by' in filters:
            cases = [c for c in cases if c.created_by == filters['created_by']]
        
        # Sort by creation date (newest first)
        cases.sort(key=lambda c: c.created_at, reverse=True)
        
        return cases
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """Get case management statistics"""
        stats = {
            'total_cases': len(self.cases),
            'cases_by_status': {},
            'cases_by_type': {},
            'cases_by_priority': {},
            'average_resolution_time': 0.0,
            'overdue_cases': 0,
            'sla_compliance': 0.0
        }
        
        resolution_times = []
        overdue_count = 0
        sla_met = 0
        total_closed = 0
        
        for case in self.cases.values():
            # Count by status
            status_key = case.status.value
            stats['cases_by_status'][status_key] = stats['cases_by_status'].get(status_key, 0) + 1
            
            # Count by type
            type_key = case.case_type.value
            stats['cases_by_type'][type_key] = stats['cases_by_type'].get(type_key, 0) + 1
            
            # Count by priority
            priority_key = case.priority.value
            stats['cases_by_priority'][priority_key] = stats['cases_by_priority'].get(priority_key, 0) + 1
            
            # Calculate resolution time for closed cases
            if case.status == CaseStatus.CLOSED and case.closed_at:
                resolution_time = (case.closed_at - case.created_at).total_seconds() / 86400  # days
                resolution_times.append(resolution_time)
                total_closed += 1
                
                # Check SLA compliance
                if case.due_date and case.closed_at <= case.due_date:
                    sla_met += 1
            
            # Check overdue
            if case.due_date and datetime.now() > case.due_date and case.status not in [CaseStatus.CLOSED, CaseStatus.ARCHIVED]:
                overdue_count += 1
        
        # Calculate averages
        if resolution_times:
            stats['average_resolution_time'] = sum(resolution_times) / len(resolution_times)
        
        stats['overdue_cases'] = overdue_count
        
        if total_closed > 0:
            stats['sla_compliance'] = (sla_met / total_closed) * 100
        
        return stats

# Global case management system with default config
case_management_system = CaseManagementSystem(config={})

def get_case_management_system() -> CaseManagementSystem:
    """Get the global case management system"""
    return case_management_system
