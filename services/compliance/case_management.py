"""
Advanced Case Management System for Compliant.one
Investigation and resolution tracking with workflow automation
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class CaseStatus(Enum):
    """Case status options"""
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"

class CasePriority(Enum):
    """Case priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CaseCategory(Enum):
    """Case categories"""
    SANCTIONS_VIOLATION = "sanctions_violation"
    AML_SUSPICIOUS_ACTIVITY = "aml_suspicious_activity"
    ADVERSE_MEDIA = "adverse_media"
    PEP_EXPOSURE = "pep_exposure"
    REGULATORY_BREACH = "regulatory_breach"
    FRAUD_INVESTIGATION = "fraud_investigation"
    COMPLIANCE_REVIEW = "compliance_review"
    RISK_ASSESSMENT = "risk_assessment"
    CUSTOMER_SCREENING = "customer_screening"
    TRANSACTION_MONITORING = "transaction_monitoring"

class ActionType(Enum):
    """Types of case actions"""
    CREATED = "created"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"
    COMMENT_ADDED = "comment_added"
    EVIDENCE_ADDED = "evidence_added"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class CaseAction:
    """Individual action taken on a case"""
    action_id: str
    action_type: ActionType
    timestamp: datetime
    user_id: str
    user_name: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)

@dataclass
class CaseEvidence:
    """Evidence attached to a case"""
    evidence_id: str
    evidence_type: str  # "document", "screenshot", "data", "link"
    title: str
    description: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    uploaded_by: str = ""
    uploaded_at: datetime = field(default_factory=datetime.now)

@dataclass
class CaseTask:
    """Individual task within a case"""
    task_id: str
    title: str
    description: str
    assigned_to: str
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    priority: CasePriority = CasePriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)

@dataclass
class Case:
    """Complete case record"""
    case_id: str
    title: str
    description: str
    category: CaseCategory
    priority: CasePriority
    status: CaseStatus
    
    # Entity information
    entity_name: str
    entity_type: str
    
    # Assignment and tracking
    assigned_to: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    # Optional fields with defaults
    entity_id: Optional[str] = None
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Content
    actions: List[CaseAction] = field(default_factory=list)
    evidence: List[CaseEvidence] = field(default_factory=list)
    tasks: List[CaseTask] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Risk and compliance
    risk_score: float = 0.0
    compliance_impact: str = ""
    regulatory_requirements: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

class CaseWorkflow:
    """Automated workflow for case management"""
    
    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps = []
        self.triggers = []
        self.conditions = {}
        
    def add_step(self, step_id: str, action: str, conditions: Dict[str, Any] = None):
        """Add a workflow step"""
        step = {
            'step_id': step_id,
            'action': action,
            'conditions': conditions or {},
            'auto_execute': conditions is None
        }
        self.steps.append(step)
    
    def can_execute_step(self, step: Dict[str, Any], case: Case) -> bool:
        """Check if a workflow step can be executed"""
        if step['auto_execute']:
            return True
        
        conditions = step.get('conditions', {})
        
        # Check status conditions
        if 'required_status' in conditions:
            if case.status.value != conditions['required_status']:
                return False
        
        # Check priority conditions
        if 'min_priority' in conditions:
            priority_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            if priority_order.get(case.priority.value, 0) < priority_order.get(conditions['min_priority'], 0):
                return False
        
        # Check time conditions
        if 'max_age_hours' in conditions:
            age_hours = (datetime.now() - case.created_at).total_seconds() / 3600
            if age_hours > conditions['max_age_hours']:
                return False
        
        return True

class CaseManagementSystem:
    """Advanced case management system with workflow automation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cases: Dict[str, Case] = {}
        self.workflows: Dict[str, CaseWorkflow] = {}
        self.templates = self._create_default_templates()
        self.auto_assignment_rules = []
        self.escalation_rules = []
        self._initialize_default_workflows()
    
    def _create_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create default case templates"""
        return {
            "sanctions_screening": {
                "title": "Sanctions Screening Alert",
                "category": CaseCategory.SANCTIONS_VIOLATION,
                "priority": CasePriority.CRITICAL,
                "description": "Potential sanctions list match requiring immediate investigation",
                "default_tasks": [
                    {
                        "title": "Verify Entity Identity",
                        "description": "Confirm the identity of the flagged entity"
                    },
                    {
                        "title": "Review Sanctions Match",
                        "description": "Analyze the sanctions list match details"
                    },
                    {
                        "title": "Document Decision",
                        "description": "Record the final screening decision and rationale"
                    }
                ],
                "regulatory_requirements": ["OFAC Compliance", "EU Sanctions"],
                "due_days": 1
            },
            "aml_investigation": {
                "title": "AML Suspicious Activity Investigation",
                "category": CaseCategory.AML_SUSPICIOUS_ACTIVITY,
                "priority": CasePriority.HIGH,
                "description": "Investigation of suspicious transaction patterns",
                "default_tasks": [
                    {
                        "title": "Analyze Transaction Patterns",
                        "description": "Review suspicious transaction activity"
                    },
                    {
                        "title": "Customer Due Diligence",
                        "description": "Conduct enhanced due diligence on customer"
                    },
                    {
                        "title": "Determine SAR Filing",
                        "description": "Decide if Suspicious Activity Report is required"
                    }
                ],
                "regulatory_requirements": ["BSA/AML", "FinCEN Requirements"],
                "due_days": 5
            },
            "adverse_media_review": {
                "title": "Adverse Media Review",
                "category": CaseCategory.ADVERSE_MEDIA,
                "priority": CasePriority.MEDIUM,
                "description": "Review and assess adverse media findings",
                "default_tasks": [
                    {
                        "title": "Verify Media Reports",
                        "description": "Confirm accuracy of adverse media findings"
                    },
                    {
                        "title": "Assess Risk Impact",
                        "description": "Evaluate reputational and compliance risk"
                    },
                    {
                        "title": "Update Risk Profile",
                        "description": "Update entity risk assessment based on findings"
                    }
                ],
                "regulatory_requirements": ["Enhanced Due Diligence"],
                "due_days": 10
            }
        }
    
    def _initialize_default_workflows(self):
        """Initialize default workflows"""
        # High-priority case workflow
        high_priority_workflow = CaseWorkflow("high_priority", "High Priority Case Workflow")
        high_priority_workflow.add_step("immediate_assignment", "auto_assign")
        high_priority_workflow.add_step("notification", "send_alert")
        high_priority_workflow.add_step("escalation_check", "check_escalation", 
                                      {"max_age_hours": 24})
        self.workflows["high_priority"] = high_priority_workflow
        
        # Standard investigation workflow
        standard_workflow = CaseWorkflow("standard", "Standard Investigation Workflow")
        standard_workflow.add_step("assignment", "auto_assign")
        standard_workflow.add_step("initial_review", "schedule_review", 
                                 {"required_status": "open"})
        standard_workflow.add_step("escalation_check", "check_escalation", 
                                 {"max_age_hours": 72})
        self.workflows["standard"] = standard_workflow
    
    def create_case_from_template(self, template_name: str, entity_name: str, 
                                entity_type: str, assigned_to: str, 
                                created_by: str, **kwargs) -> Case:
        """Create a case from a predefined template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        case_id = str(uuid.uuid4())
        
        # Calculate due date
        due_date = None
        if 'due_days' in template:
            due_date = datetime.now() + timedelta(days=template['due_days'])
        
        # Create case
        case = Case(
            case_id=case_id,
            title=template['title'],
            description=template['description'],
            category=template['category'],
            priority=template['priority'],
            status=CaseStatus.OPEN,
            entity_name=entity_name,
            entity_type=entity_type,
            assigned_to=assigned_to,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=due_date,
            regulatory_requirements=template.get('regulatory_requirements', [])
        )
        
        # Apply any additional parameters
        for key, value in kwargs.items():
            if hasattr(case, key):
                setattr(case, key, value)
        
        # Create initial action
        initial_action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.CREATED,
            timestamp=datetime.now(),
            user_id=created_by,
            user_name=created_by,
            description=f"Case created from template: {template_name}"
        )
        case.actions.append(initial_action)
        
        # Create default tasks
        for task_template in template.get('default_tasks', []):
            task = CaseTask(
                task_id=str(uuid.uuid4()),
                title=task_template['title'],
                description=task_template['description'],
                assigned_to=assigned_to,
                priority=case.priority
            )
            case.tasks.append(task)
        
        self.cases[case_id] = case
        
        # Execute workflow if applicable
        self._execute_workflow_for_case(case)
        
        logger.info(f"Created case {case_id} from template {template_name}")
        return case
    
    def create_custom_case(self, case_data: Dict[str, Any]) -> Case:
        """Create a custom case"""
        case_id = str(uuid.uuid4())
        
        case = Case(
            case_id=case_id,
            title=case_data['title'],
            description=case_data['description'],
            category=CaseCategory(case_data['category']),
            priority=CasePriority(case_data['priority']),
            status=CaseStatus.OPEN,
            entity_name=case_data['entity_name'],
            entity_type=case_data['entity_type'],
            assigned_to=case_data['assigned_to'],
            created_by=case_data['created_by'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=case_data.get('due_date'),
            tags=case_data.get('tags', []),
            risk_score=case_data.get('risk_score', 0.0),
            compliance_impact=case_data.get('compliance_impact', ''),
            regulatory_requirements=case_data.get('regulatory_requirements', [])
        )
        
        # Create initial action
        initial_action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.CREATED,
            timestamp=datetime.now(),
            user_id=case_data['created_by'],
            user_name=case_data['created_by'],
            description="Custom case created"
        )
        case.actions.append(initial_action)
        
        self.cases[case_id] = case
        self._execute_workflow_for_case(case)
        
        logger.info(f"Created custom case {case_id}")
        return case
    
    def update_case_status(self, case_id: str, new_status: CaseStatus, 
                          user_id: str, user_name: str, notes: str = "") -> bool:
        """Update case status"""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        old_status = case.status
        case.status = new_status
        case.updated_at = datetime.now()
        
        # Set resolution/close timestamps
        if new_status == CaseStatus.RESOLVED and not case.resolved_at:
            case.resolved_at = datetime.now()
        elif new_status == CaseStatus.CLOSED and not case.closed_at:
            case.closed_at = datetime.now()
        
        # Create action record
        action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.STATUS_CHANGED,
            timestamp=datetime.now(),
            user_id=user_id,
            user_name=user_name,
            description=f"Status changed from {old_status.value} to {new_status.value}",
            details={"old_status": old_status.value, "new_status": new_status.value, "notes": notes}
        )
        case.actions.append(action)
        
        # Execute workflow steps
        self._execute_workflow_for_case(case)
        
        logger.info(f"Updated case {case_id} status to {new_status.value}")
        return True
    
    def assign_case(self, case_id: str, assigned_to: str, 
                   assigned_by: str, notes: str = "") -> bool:
        """Assign case to a user"""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        old_assignee = case.assigned_to
        case.assigned_to = assigned_to
        case.updated_at = datetime.now()
        
        # Create action record
        action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.ASSIGNED,
            timestamp=datetime.now(),
            user_id=assigned_by,
            user_name=assigned_by,
            description=f"Case assigned from {old_assignee} to {assigned_to}",
            details={"old_assignee": old_assignee, "new_assignee": assigned_to, "notes": notes}
        )
        case.actions.append(action)
        
        logger.info(f"Assigned case {case_id} to {assigned_to}")
        return True
    
    def add_case_comment(self, case_id: str, user_id: str, user_name: str, 
                        comment: str, attachments: List[str] = None) -> bool:
        """Add comment to case"""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        case.updated_at = datetime.now()
        
        action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.COMMENT_ADDED,
            timestamp=datetime.now(),
            user_id=user_id,
            user_name=user_name,
            description=comment,
            attachments=attachments or []
        )
        case.actions.append(action)
        
        logger.info(f"Added comment to case {case_id}")
        return True
    
    def add_evidence(self, case_id: str, evidence: CaseEvidence) -> bool:
        """Add evidence to case"""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        case.evidence.append(evidence)
        case.updated_at = datetime.now()
        
        action = CaseAction(
            action_id=str(uuid.uuid4()),
            action_type=ActionType.EVIDENCE_ADDED,
            timestamp=datetime.now(),
            user_id=evidence.uploaded_by,
            user_name=evidence.uploaded_by,
            description=f"Evidence added: {evidence.title}",
            details={"evidence_id": evidence.evidence_id, "evidence_type": evidence.evidence_type}
        )
        case.actions.append(action)
        
        logger.info(f"Added evidence to case {case_id}")
        return True
    
    def complete_task(self, case_id: str, task_id: str, 
                     completed_by: str, notes: str = "") -> bool:
        """Mark a task as completed"""
        if case_id not in self.cases:
            return False
        
        case = self.cases[case_id]
        
        for task in case.tasks:
            if task.task_id == task_id:
                task.completed = True
                task.completed_at = datetime.now()
                task.completed_by = completed_by
                case.updated_at = datetime.now()
                
                action = CaseAction(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.REVIEWED,
                    timestamp=datetime.now(),
                    user_id=completed_by,
                    user_name=completed_by,
                    description=f"Task completed: {task.title}",
                    details={"task_id": task_id, "notes": notes}
                )
                case.actions.append(action)
                
                logger.info(f"Completed task {task_id} in case {case_id}")
                return True
        
        return False
    
    def get_case(self, case_id: str) -> Optional[Case]:
        """Get case by ID"""
        return self.cases.get(case_id)
    
    def search_cases(self, filters: Dict[str, Any] = None, 
                    limit: int = 100) -> List[Case]:
        """Search cases with filters"""
        cases = list(self.cases.values())
        
        if filters:
            if 'status' in filters:
                cases = [c for c in cases if c.status.value == filters['status']]
            
            if 'priority' in filters:
                cases = [c for c in cases if c.priority.value == filters['priority']]
            
            if 'category' in filters:
                cases = [c for c in cases if c.category.value == filters['category']]
            
            if 'assigned_to' in filters:
                cases = [c for c in cases if c.assigned_to == filters['assigned_to']]
            
            if 'entity_name' in filters:
                entity_filter = filters['entity_name'].lower()
                cases = [c for c in cases if entity_filter in c.entity_name.lower()]
            
            if 'created_after' in filters:
                after_date = filters['created_after']
                cases = [c for c in cases if c.created_at >= after_date]
            
            if 'due_before' in filters:
                before_date = filters['due_before']
                cases = [c for c in cases if c.due_date and c.due_date <= before_date]
        
        # Sort by priority and creation date
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        cases.sort(key=lambda x: (priority_order.get(x.priority.value, 0), x.created_at), 
                  reverse=True)
        
        return cases[:limit]
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """Get comprehensive case statistics"""
        total_cases = len(self.cases)
        
        # Status breakdown
        status_counts = {}
        for case in self.cases.values():
            status = case.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Priority breakdown
        priority_counts = {}
        for case in self.cases.values():
            priority = case.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Category breakdown
        category_counts = {}
        for case in self.cases.values():
            category = case.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Overdue cases
        now = datetime.now()
        overdue_cases = [c for c in self.cases.values() 
                        if c.due_date and c.due_date < now and c.status not in [CaseStatus.RESOLVED, CaseStatus.CLOSED]]
        
        # Average resolution time
        resolved_cases = [c for c in self.cases.values() if c.resolved_at]
        avg_resolution_time = None
        if resolved_cases:
            total_time = sum((c.resolved_at - c.created_at).total_seconds() for c in resolved_cases)
            avg_resolution_time = total_time / len(resolved_cases) / 3600  # hours
        
        return {
            'total_cases': total_cases,
            'status_breakdown': status_counts,
            'priority_breakdown': priority_counts,
            'category_breakdown': category_counts,
            'overdue_cases': len(overdue_cases),
            'resolved_cases': len(resolved_cases),
            'average_resolution_hours': avg_resolution_time,
            'statistics_timestamp': datetime.now().isoformat()
        }
    
    def _execute_workflow_for_case(self, case: Case):
        """Execute applicable workflows for a case"""
        try:
            # Determine which workflow to use
            workflow_id = "high_priority" if case.priority in [CasePriority.CRITICAL, CasePriority.HIGH] else "standard"
            
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                
                for step in workflow.steps:
                    if workflow.can_execute_step(step, case):
                        self._execute_workflow_step(step, case)
                        
        except Exception as e:
            logger.error(f"Error executing workflow for case {case.case_id}: {e}")
    
    def _execute_workflow_step(self, step: Dict[str, Any], case: Case):
        """Execute a single workflow step"""
        action = step['action']
        
        if action == "auto_assign":
            # Auto-assignment logic would go here
            logger.info(f"Auto-assignment triggered for case {case.case_id}")
        
        elif action == "send_alert":
            # Alert sending logic would go here
            logger.info(f"Alert sent for case {case.case_id}")
        
        elif action == "check_escalation":
            # Escalation checking logic would go here
            logger.info(f"Escalation check performed for case {case.case_id}")
        
        elif action == "schedule_review":
            # Review scheduling logic would go here
            logger.info(f"Review scheduled for case {case.case_id}")
    
    def export_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Export case data"""
        if case_id not in self.cases:
            return None
        
        case = self.cases[case_id]
        
        # Convert case to dictionary format
        case_dict = {
            'case_id': case.case_id,
            'title': case.title,
            'description': case.description,
            'category': case.category.value,
            'priority': case.priority.value,
            'status': case.status.value,
            'entity_name': case.entity_name,
            'entity_type': case.entity_type,
            'entity_id': case.entity_id,
            'assigned_to': case.assigned_to,
            'created_by': case.created_by,
            'created_at': case.created_at.isoformat(),
            'updated_at': case.updated_at.isoformat(),
            'due_date': case.due_date.isoformat() if case.due_date else None,
            'resolved_at': case.resolved_at.isoformat() if case.resolved_at else None,
            'closed_at': case.closed_at.isoformat() if case.closed_at else None,
            'risk_score': case.risk_score,
            'compliance_impact': case.compliance_impact,
            'regulatory_requirements': case.regulatory_requirements,
            'tags': case.tags,
            'actions': [
                {
                    'action_id': action.action_id,
                    'action_type': action.action_type.value,
                    'timestamp': action.timestamp.isoformat(),
                    'user_id': action.user_id,
                    'user_name': action.user_name,
                    'description': action.description,
                    'details': action.details,
                    'attachments': action.attachments
                }
                for action in case.actions
            ],
            'evidence': [
                {
                    'evidence_id': evidence.evidence_id,
                    'evidence_type': evidence.evidence_type,
                    'title': evidence.title,
                    'description': evidence.description,
                    'file_path': evidence.file_path,
                    'content': evidence.content,
                    'metadata': evidence.metadata,
                    'uploaded_by': evidence.uploaded_by,
                    'uploaded_at': evidence.uploaded_at.isoformat()
                }
                for evidence in case.evidence
            ],
            'tasks': [
                {
                    'task_id': task.task_id,
                    'title': task.title,
                    'description': task.description,
                    'assigned_to': task.assigned_to,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'completed': task.completed,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'completed_by': task.completed_by,
                    'priority': task.priority.value,
                    'dependencies': task.dependencies
                }
                for task in case.tasks
            ],
            'metadata': case.metadata
        }
        
        return case_dict
