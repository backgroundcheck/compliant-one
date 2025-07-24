"""
Advanced Risk Rules Engine - Phase 2
🎯 Customizable Risk Rules, Dynamic Policy Engine, Compliance Automation
Real-time Rule Evaluation with AI-powered Decision Making
"""

import json
import yaml
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import logging
from pathlib import Path
import asyncio

# Optional dependencies
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from utils.logger import ComplianceLogger

class RiskLevel(Enum):
    """Risk levels for rule evaluation"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RuleType(Enum):
    """Types of risk rules"""
    CUSTOMER_SCREENING = "customer_screening"
    TRANSACTION_MONITORING = "transaction_monitoring"
    SANCTIONS_SCREENING = "sanctions_screening"
    PEP_SCREENING = "pep_screening"
    ADVERSE_MEDIA = "adverse_media"
    GEOGRAPHIC_RISK = "geographic_risk"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    COMPLIANCE_VALIDATION = "compliance_validation"
    CUSTOM = "custom"

class RuleOperator(Enum):
    """Operators for rule conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX_MATCH = "regex_match"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    BETWEEN = "between"

class ActionType(Enum):
    """Types of actions to take when rule triggers"""
    ALERT = "alert"
    BLOCK = "block"
    REVIEW = "review"
    ESCALATE = "escalate"
    LOG = "log"
    NOTIFY = "notify"
    CUSTOM_FUNCTION = "custom_function"
    API_CALL = "api_call"
    EMAIL = "email"

@dataclass
class RuleCondition:
    """Individual condition within a rule"""
    field_path: str  # e.g., "customer.risk_score", "transaction.amount"
    operator: RuleOperator
    value: Any
    condition_id: str = None
    description: str = ""
    
    def __post_init__(self):
        if self.condition_id is None:
            self.condition_id = f"cond_{hash(f'{self.field_path}_{self.operator.value}_{self.value}')}"

@dataclass
class RuleAction:
    """Action to execute when rule triggers"""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    delay_seconds: int = 0
    action_id: str = None
    
    def __post_init__(self):
        if self.action_id is None:
            self.action_id = f"action_{hash(f'{self.action_type.value}_{str(self.parameters)}')}"

@dataclass
class RiskRule:
    """Risk rule definition"""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    logic_operator: str = "AND"  # AND, OR
    enabled: bool = True
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    compliance_refs: List[str] = field(default_factory=list)  # FATF R.10, etc.

@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation"""
    rule_id: str
    rule_name: str
    triggered: bool
    risk_level: RiskLevel
    confidence_score: float
    matched_conditions: List[str]
    actions_executed: List[str]
    evaluation_time_ms: float
    evaluation_timestamp: datetime
    data_snapshot: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicySet:
    """Collection of related rules forming a policy"""
    policy_id: str
    name: str
    description: str
    rules: List[str]  # Rule IDs
    policy_type: str
    enabled: bool = True
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    compliance_framework: str = "FATF"
    jurisdiction: str = "global"

class RuleEvaluationEngine:
    """Core engine for evaluating risk rules"""
    
    def __init__(self):
        self.logger = ComplianceLogger("rule_evaluation_engine")
        self.custom_functions = {}
        self.field_extractors = {}
        
        # Performance tracking
        self.evaluation_stats = {
            'total_evaluations': 0,
            'rules_triggered': 0,
            'average_evaluation_time': 0.0,
            'last_reset': datetime.now()
        }
    
    def register_custom_function(self, name: str, function: Callable):
        """Register custom function for rule actions"""
        self.custom_functions[name] = function
        self.logger.logger.info(f"Registered custom function: {name}")
    
    def register_field_extractor(self, field_path: str, extractor: Callable):
        """Register custom field extractor"""
        self.field_extractors[field_path] = extractor
        self.logger.logger.info(f"Registered field extractor: {field_path}")
    
    async def evaluate_rule(self, rule: RiskRule, data: Dict[str, Any]) -> RuleEvaluationResult:
        """Evaluate a single rule against data"""
        start_time = datetime.now()
        
        try:
            # Check if rule is active
            if not self._is_rule_active(rule):
                return RuleEvaluationResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    triggered=False,
                    risk_level=RiskLevel.MINIMAL,
                    confidence_score=0.0,
                    matched_conditions=[],
                    actions_executed=[],
                    evaluation_time_ms=0.0,
                    evaluation_timestamp=start_time,
                    data_snapshot={},
                    metadata={'status': 'inactive'}
                )
            
            # Evaluate conditions
            condition_results = []
            matched_conditions = []
            
            for condition in rule.conditions:
                result = await self._evaluate_condition(condition, data)
                condition_results.append(result)
                if result:
                    matched_conditions.append(condition.condition_id)
            
            # Apply logic operator
            if rule.logic_operator.upper() == "AND":
                rule_triggered = all(condition_results)
            elif rule.logic_operator.upper() == "OR":
                rule_triggered = any(condition_results)
            else:
                raise ValueError(f"Unsupported logic operator: {rule.logic_operator}")
            
            # Calculate confidence and risk level
            confidence_score = self._calculate_confidence(condition_results, rule)
            risk_level = self._determine_risk_level(rule_triggered, rule, confidence_score)
            
            # Execute actions if rule triggered
            actions_executed = []
            if rule_triggered:
                actions_executed = await self._execute_actions(rule.actions, data, rule)
            
            # Calculate evaluation time
            end_time = datetime.now()
            evaluation_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Update statistics
            self._update_stats(evaluation_time_ms, rule_triggered)
            
            return RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                triggered=rule_triggered,
                risk_level=risk_level,
                confidence_score=confidence_score,
                matched_conditions=matched_conditions,
                actions_executed=actions_executed,
                evaluation_time_ms=evaluation_time_ms,
                evaluation_timestamp=start_time,
                data_snapshot=self._create_data_snapshot(data, rule),
                metadata={
                    'conditions_evaluated': len(condition_results),
                    'conditions_matched': len(matched_conditions),
                    'logic_operator': rule.logic_operator,
                    'rule_priority': rule.priority
                }
            )
            
        except Exception as e:
            self.logger.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                triggered=False,
                risk_level=RiskLevel.MINIMAL,
                confidence_score=0.0,
                matched_conditions=[],
                actions_executed=[],
                evaluation_time_ms=0.0,
                evaluation_timestamp=start_time,
                data_snapshot={},
                metadata={'error': str(e)}
            )
    
    def _is_rule_active(self, rule: RiskRule) -> bool:
        """Check if rule is currently active"""
        if not rule.enabled:
            return False
        
        now = datetime.now()
        
        if rule.effective_date and now < rule.effective_date:
            return False
        
        if rule.expiry_date and now > rule.expiry_date:
            return False
        
        return True
    
    async def _evaluate_condition(self, condition: RuleCondition, data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            # Extract field value
            field_value = self._extract_field_value(condition.field_path, data)
            
            # Apply operator
            return self._apply_operator(field_value, condition.operator, condition.value)
            
        except Exception as e:
            self.logger.logger.warning(f"Error evaluating condition {condition.condition_id}: {e}")
            return False
    
    def _extract_field_value(self, field_path: str, data: Dict[str, Any]) -> Any:
        """Extract field value from data using dot notation"""
        
        # Check for custom extractor
        if field_path in self.field_extractors:
            return self.field_extractors[field_path](data)
        
        # Standard dot notation extraction
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                index = int(key)
                value = value[index] if 0 <= index < len(value) else None
            else:
                return None
            
            if value is None:
                break
        
        return value
    
    def _apply_operator(self, field_value: Any, operator: RuleOperator, condition_value: Any) -> bool:
        """Apply operator to compare field value with condition value"""
        
        if operator == RuleOperator.EQUALS:
            return field_value == condition_value
        
        elif operator == RuleOperator.NOT_EQUALS:
            return field_value != condition_value
        
        elif operator == RuleOperator.GREATER_THAN:
            return field_value is not None and field_value > condition_value
        
        elif operator == RuleOperator.LESS_THAN:
            return field_value is not None and field_value < condition_value
        
        elif operator == RuleOperator.GREATER_EQUAL:
            return field_value is not None and field_value >= condition_value
        
        elif operator == RuleOperator.LESS_EQUAL:
            return field_value is not None and field_value <= condition_value
        
        elif operator == RuleOperator.CONTAINS:
            return field_value is not None and str(condition_value) in str(field_value)
        
        elif operator == RuleOperator.NOT_CONTAINS:
            return field_value is None or str(condition_value) not in str(field_value)
        
        elif operator == RuleOperator.STARTS_WITH:
            return field_value is not None and str(field_value).startswith(str(condition_value))
        
        elif operator == RuleOperator.ENDS_WITH:
            return field_value is not None and str(field_value).endswith(str(condition_value))
        
        elif operator == RuleOperator.REGEX_MATCH:
            if field_value is None:
                return False
            try:
                return bool(re.search(str(condition_value), str(field_value)))
            except re.error:
                return False
        
        elif operator == RuleOperator.IN_LIST:
            return field_value in condition_value if isinstance(condition_value, (list, tuple, set)) else False
        
        elif operator == RuleOperator.NOT_IN_LIST:
            return field_value not in condition_value if isinstance(condition_value, (list, tuple, set)) else True
        
        elif operator == RuleOperator.IS_EMPTY:
            return field_value is None or field_value == "" or (isinstance(field_value, (list, dict)) and len(field_value) == 0)
        
        elif operator == RuleOperator.IS_NOT_EMPTY:
            return field_value is not None and field_value != "" and (not isinstance(field_value, (list, dict)) or len(field_value) > 0)
        
        elif operator == RuleOperator.BETWEEN:
            if not isinstance(condition_value, (list, tuple)) or len(condition_value) != 2:
                return False
            return field_value is not None and condition_value[0] <= field_value <= condition_value[1]
        
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    async def _execute_actions(self, actions: List[RuleAction], data: Dict[str, Any], rule: RiskRule) -> List[str]:
        """Execute actions for triggered rule"""
        executed_actions = []
        
        # Sort actions by priority
        sorted_actions = sorted(actions, key=lambda a: a.priority)
        
        for action in sorted_actions:
            try:
                # Apply delay if specified
                if action.delay_seconds > 0:
                    await asyncio.sleep(action.delay_seconds)
                
                # Execute action
                result = await self._execute_action(action, data, rule)
                if result:
                    executed_actions.append(action.action_id)
                
            except Exception as e:
                self.logger.logger.error(f"Error executing action {action.action_id}: {e}")
        
        return executed_actions
    
    async def _execute_action(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute a single action"""
        
        if action.action_type == ActionType.ALERT:
            return await self._execute_alert_action(action, data, rule)
        
        elif action.action_type == ActionType.LOG:
            return await self._execute_log_action(action, data, rule)
        
        elif action.action_type == ActionType.NOTIFY:
            return await self._execute_notify_action(action, data, rule)
        
        elif action.action_type == ActionType.CUSTOM_FUNCTION:
            return await self._execute_custom_function(action, data, rule)
        
        elif action.action_type == ActionType.API_CALL:
            return await self._execute_api_call(action, data, rule)
        
        elif action.action_type == ActionType.EMAIL:
            return await self._execute_email_action(action, data, rule)
        
        else:
            self.logger.logger.warning(f"Unsupported action type: {action.action_type}")
            return False
    
    async def _execute_alert_action(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute alert action"""
        alert_message = action.parameters.get('message', f"Rule {rule.name} triggered")
        severity = action.parameters.get('severity', 'MEDIUM')
        
        self.logger.logger.warning(f"ALERT [{severity}]: {alert_message} (Rule: {rule.rule_id})")
        return True
    
    async def _execute_log_action(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute log action"""
        log_level = action.parameters.get('level', 'INFO')
        message = action.parameters.get('message', f"Rule {rule.name} triggered")
        
        if log_level.upper() == 'ERROR':
            self.logger.logger.error(message)
        elif log_level.upper() == 'WARNING':
            self.logger.logger.warning(message)
        else:
            self.logger.logger.info(message)
        
        return True
    
    async def _execute_notify_action(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute notification action"""
        # Mock notification - would integrate with actual notification system
        recipients = action.parameters.get('recipients', [])
        message = action.parameters.get('message', f"Rule {rule.name} triggered")
        
        self.logger.logger.info(f"NOTIFICATION sent to {recipients}: {message}")
        return True
    
    async def _execute_custom_function(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute custom function"""
        function_name = action.parameters.get('function_name')
        if function_name and function_name in self.custom_functions:
            try:
                result = await self.custom_functions[function_name](data, rule, action.parameters)
                return bool(result)
            except Exception as e:
                self.logger.logger.error(f"Custom function {function_name} failed: {e}")
                return False
        
        return False
    
    async def _execute_api_call(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute API call action"""
        # Mock API call - would use actual HTTP client
        url = action.parameters.get('url')
        method = action.parameters.get('method', 'POST')
        
        self.logger.logger.info(f"API CALL: {method} {url} (Rule: {rule.rule_id})")
        return True
    
    async def _execute_email_action(self, action: RuleAction, data: Dict[str, Any], rule: RiskRule) -> bool:
        """Execute email action"""
        # Mock email - would integrate with actual email service
        to_emails = action.parameters.get('to', [])
        subject = action.parameters.get('subject', f"Rule Alert: {rule.name}")
        
        self.logger.logger.info(f"EMAIL sent to {to_emails}: {subject}")
        return True
    
    def _calculate_confidence(self, condition_results: List[bool], rule: RiskRule) -> float:
        """Calculate confidence score for rule evaluation"""
        if not condition_results:
            return 0.0
        
        # Base confidence on percentage of conditions met
        met_conditions = sum(condition_results)
        total_conditions = len(condition_results)
        
        confidence = met_conditions / total_conditions
        
        # Adjust for rule type and priority
        if rule.rule_type in [RuleType.SANCTIONS_SCREENING, RuleType.PEP_SCREENING]:
            confidence *= 1.2  # Higher confidence for critical screening
        
        if rule.priority >= 3:
            confidence *= 1.1  # Higher confidence for high priority rules
        
        return min(1.0, confidence)
    
    def _determine_risk_level(self, triggered: bool, rule: RiskRule, confidence: float) -> RiskLevel:
        """Determine risk level based on rule evaluation"""
        if not triggered:
            return RiskLevel.MINIMAL
        
        # Base risk level on rule type and priority
        if rule.rule_type in [RuleType.SANCTIONS_SCREENING, RuleType.PEP_SCREENING]:
            base_risk = RiskLevel.HIGH
        elif rule.rule_type in [RuleType.ADVERSE_MEDIA, RuleType.TRANSACTION_MONITORING]:
            base_risk = RiskLevel.MEDIUM
        else:
            base_risk = RiskLevel.LOW
        
        # Adjust based on confidence and priority
        risk_score = 0.0
        
        if base_risk == RiskLevel.HIGH:
            risk_score = 0.7
        elif base_risk == RiskLevel.MEDIUM:
            risk_score = 0.5
        else:
            risk_score = 0.3
        
        # Adjust for confidence
        risk_score *= confidence
        
        # Adjust for priority
        risk_score *= (1.0 + rule.priority * 0.1)
        
        # Determine final risk level
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        elif risk_score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _create_data_snapshot(self, data: Dict[str, Any], rule: RiskRule) -> Dict[str, Any]:
        """Create relevant data snapshot for rule evaluation"""
        snapshot = {}
        
        # Extract fields used in rule conditions
        for condition in rule.conditions:
            field_value = self._extract_field_value(condition.field_path, data)
            snapshot[condition.field_path] = field_value
        
        return snapshot
    
    def _update_stats(self, evaluation_time_ms: float, triggered: bool):
        """Update evaluation statistics"""
        self.evaluation_stats['total_evaluations'] += 1
        
        if triggered:
            self.evaluation_stats['rules_triggered'] += 1
        
        # Update average evaluation time
        current_avg = self.evaluation_stats['average_evaluation_time']
        total_evals = self.evaluation_stats['total_evaluations']
        
        new_avg = ((current_avg * (total_evals - 1)) + evaluation_time_ms) / total_evals
        self.evaluation_stats['average_evaluation_time'] = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get evaluation statistics"""
        return self.evaluation_stats.copy()

class RiskRulesManager:
    """Manager for risk rules and policies"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = ComplianceLogger("risk_rules_manager")
        
        # Storage
        self.rules: Dict[str, RiskRule] = {}
        self.policies: Dict[str, PolicySet] = {}
        
        # Evaluation engine
        self.evaluation_engine = RuleEvaluationEngine()
        
        # Configuration with safe access
        self.config = config or {}
        self.auto_save = self.config.get('auto_save', True)
        self.rules_file = self.config.get('rules_file', 'data/risk_rules.json')
        self.policies_file = self.config.get('policies_file', 'data/risk_policies.json')
        
        # Load existing rules and policies
        self._load_rules_and_policies()
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _load_rules_and_policies(self):
        """Load rules and policies from storage"""
        try:
            # Load rules
            rules_path = Path(self.rules_file)
            if rules_path.exists():
                with open(rules_path, 'r') as f:
                    rules_data = json.load(f)
                    
                for rule_data in rules_data:
                    rule = self._deserialize_rule(rule_data)
                    self.rules[rule.rule_id] = rule
                
                self.logger.logger.info(f"Loaded {len(self.rules)} rules from {self.rules_file}")
            
            # Load policies
            policies_path = Path(self.policies_file)
            if policies_path.exists():
                with open(policies_path, 'r') as f:
                    policies_data = json.load(f)
                    
                for policy_data in policies_data:
                    policy = PolicySet(**policy_data)
                    self.policies[policy.policy_id] = policy
                
                self.logger.logger.info(f"Loaded {len(self.policies)} policies from {self.policies_file}")
        
        except Exception as e:
            self.logger.logger.error(f"Error loading rules and policies: {e}")
    
    def _save_rules_and_policies(self):
        """Save rules and policies to storage"""
        if not self.auto_save:
            return
        
        try:
            # Save rules
            rules_path = Path(self.rules_file)
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            
            rules_data = [self._serialize_rule(rule) for rule in self.rules.values()]
            
            with open(rules_path, 'w') as f:
                json.dump(rules_data, f, indent=2, default=str)
            
            # Save policies
            policies_path = Path(self.policies_file)
            policies_path.parent.mkdir(parents=True, exist_ok=True)
            
            policies_data = [asdict(policy) for policy in self.policies.values()]
            
            with open(policies_path, 'w') as f:
                json.dump(policies_data, f, indent=2, default=str)
            
            self.logger.logger.info("Saved rules and policies to storage")
        
        except Exception as e:
            self.logger.logger.error(f"Error saving rules and policies: {e}")
    
    def _serialize_rule(self, rule: RiskRule) -> Dict[str, Any]:
        """Serialize rule to dictionary"""
        rule_dict = asdict(rule)
        
        # Convert enums to strings
        rule_dict['rule_type'] = rule.rule_type.value
        
        for condition in rule_dict['conditions']:
            condition['operator'] = condition['operator']
        
        for action in rule_dict['actions']:
            action['action_type'] = action['action_type']
        
        return rule_dict
    
    def _deserialize_rule(self, rule_data: Dict[str, Any]) -> RiskRule:
        """Deserialize rule from dictionary"""
        # Convert strings back to enums
        rule_data['rule_type'] = RuleType(rule_data['rule_type'])
        
        # Convert condition operators
        for condition in rule_data['conditions']:
            condition['operator'] = RuleOperator(condition['operator'])
        
        # Convert action types
        for action in rule_data['actions']:
            action['action_type'] = ActionType(action['action_type'])
        
        # Convert datetime strings
        if isinstance(rule_data['created_at'], str):
            rule_data['created_at'] = datetime.fromisoformat(rule_data['created_at'])
        if isinstance(rule_data['updated_at'], str):
            rule_data['updated_at'] = datetime.fromisoformat(rule_data['updated_at'])
        
        # Create condition objects
        conditions = [RuleCondition(**cond) for cond in rule_data['conditions']]
        rule_data['conditions'] = conditions
        
        # Create action objects
        actions = [RuleAction(**action) for action in rule_data['actions']]
        rule_data['actions'] = actions
        
        return RiskRule(**rule_data)
    
    def _initialize_default_rules(self):
        """Initialize default compliance rules"""
        if self.rules:
            return  # Rules already loaded
        
        default_rules = [
            # High-value transaction monitoring
            RiskRule(
                rule_id="RULE_HIGH_VALUE_TXN",
                name="High Value Transaction Alert",
                description="Alert on transactions exceeding threshold",
                rule_type=RuleType.TRANSACTION_MONITORING,
                conditions=[
                    RuleCondition(
                        field_path="transaction.amount",
                        operator=RuleOperator.GREATER_THAN,
                        value=10000,
                        description="Transaction amount > $10,000"
                    )
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.ALERT,
                        parameters={
                            'message': 'High value transaction detected',
                            'severity': 'HIGH'
                        }
                    ),
                    RuleAction(
                        action_type=ActionType.REVIEW,
                        parameters={'queue': 'high_value_review'}
                    )
                ],
                priority=3,
                compliance_refs=["FATF_R.20"]
            ),
            
            # PEP screening rule
            RiskRule(
                rule_id="RULE_PEP_SCREENING",
                name="PEP Screening Alert",
                description="Alert when customer is identified as PEP",
                rule_type=RuleType.PEP_SCREENING,
                conditions=[
                    RuleCondition(
                        field_path="customer.pep_status",
                        operator=RuleOperator.EQUALS,
                        value=True,
                        description="Customer is PEP"
                    )
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.ESCALATE,
                        parameters={'level': 'senior_compliance'}
                    ),
                    RuleAction(
                        action_type=ActionType.NOTIFY,
                        parameters={
                            'recipients': ['compliance@company.com'],
                            'message': 'PEP customer identified'
                        }
                    )
                ],
                priority=5,
                compliance_refs=["FATF_R.12"]
            ),
            
            # Sanctions screening rule
            RiskRule(
                rule_id="RULE_SANCTIONS_MATCH",
                name="Sanctions List Match",
                description="Block transactions for sanctioned entities",
                rule_type=RuleType.SANCTIONS_SCREENING,
                conditions=[
                    RuleCondition(
                        field_path="screening.sanctions_match",
                        operator=RuleOperator.GREATER_THAN,
                        value=0.8,
                        description="High sanctions match score"
                    )
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.BLOCK,
                        parameters={'reason': 'sanctions_match'}
                    ),
                    RuleAction(
                        action_type=ActionType.ALERT,
                        parameters={
                            'message': 'Sanctions match detected',
                            'severity': 'CRITICAL'
                        }
                    )
                ],
                priority=5,
                compliance_refs=["FATF_R.6", "FATF_R.7"]
            ),
            
            # Geographic risk rule
            RiskRule(
                rule_id="RULE_HIGH_RISK_COUNTRY",
                name="High Risk Country Alert",
                description="Enhanced monitoring for high-risk jurisdictions",
                rule_type=RuleType.GEOGRAPHIC_RISK,
                conditions=[
                    RuleCondition(
                        field_path="customer.country",
                        operator=RuleOperator.IN_LIST,
                        value=["AF", "IR", "KP", "SY"],  # Example high-risk countries
                        description="Customer from high-risk country"
                    )
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.REVIEW,
                        parameters={'queue': 'geographic_risk_review'}
                    ),
                    RuleAction(
                        action_type=ActionType.LOG,
                        parameters={
                            'level': 'WARNING',
                            'message': 'Customer from high-risk jurisdiction'
                        }
                    )
                ],
                priority=3,
                compliance_refs=["FATF_R.19"]
            ),
            
            # Adverse media rule
            RiskRule(
                rule_id="RULE_ADVERSE_MEDIA",
                name="Adverse Media Alert",
                description="Alert on negative media coverage",
                rule_type=RuleType.ADVERSE_MEDIA,
                conditions=[
                    RuleCondition(
                        field_path="screening.adverse_media_score",
                        operator=RuleOperator.GREATER_THAN,
                        value=0.7,
                        description="High adverse media score"
                    )
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.REVIEW,
                        parameters={'queue': 'adverse_media_review'}
                    ),
                    RuleAction(
                        action_type=ActionType.NOTIFY,
                        parameters={
                            'recipients': ['risk@company.com'],
                            'message': 'Adverse media detected'
                        }
                    )
                ],
                priority=2,
                compliance_refs=["FATF_R.10"]
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
        
        self.logger.logger.info(f"Initialized {len(default_rules)} default rules")
    
    def add_rule(self, rule: RiskRule) -> bool:
        """Add a new rule"""
        try:
            # Validate rule
            self._validate_rule(rule)
            
            # Add to storage
            self.rules[rule.rule_id] = rule
            
            # Save to disk
            self._save_rules_and_policies()
            
            self.logger.logger.info(f"Added rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error adding rule {rule.rule_id}: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing rule"""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule {rule_id} not found")
            
            rule = self.rules[rule_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            # Update timestamp
            rule.updated_at = datetime.now()
            
            # Validate updated rule
            self._validate_rule(rule)
            
            # Save to disk
            self._save_rules_and_policies()
            
            self.logger.logger.info(f"Updated rule: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error updating rule {rule_id}: {e}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule {rule_id} not found")
            
            del self.rules[rule_id]
            
            # Remove from policies
            for policy in self.policies.values():
                if rule_id in policy.rules:
                    policy.rules.remove(rule_id)
            
            # Save to disk
            self._save_rules_and_policies()
            
            self.logger.logger.info(f"Deleted rule: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error deleting rule {rule_id}: {e}")
            return False
    
    def _validate_rule(self, rule: RiskRule):
        """Validate rule structure and logic"""
        if not rule.rule_id:
            raise ValueError("Rule ID is required")
        
        if not rule.name:
            raise ValueError("Rule name is required")
        
        if not rule.conditions:
            raise ValueError("Rule must have at least one condition")
        
        if not rule.actions:
            raise ValueError("Rule must have at least one action")
        
        # Validate conditions
        for condition in rule.conditions:
            if not condition.field_path:
                raise ValueError("Condition field_path is required")
        
        # Validate actions
        for action in rule.actions:
            if not action.action_type:
                raise ValueError("Action type is required")
    
    async def evaluate_rules(self, data: Dict[str, Any], 
                           rule_filter: Optional[Dict[str, Any]] = None) -> List[RuleEvaluationResult]:
        """Evaluate rules against data"""
        
        # Filter rules if specified
        rules_to_evaluate = self._filter_rules(rule_filter) if rule_filter else list(self.rules.values())
        
        # Sort by priority (highest first)
        rules_to_evaluate.sort(key=lambda r: r.priority, reverse=True)
        
        # Evaluate rules
        results = []
        for rule in rules_to_evaluate:
            result = await self.evaluation_engine.evaluate_rule(rule, data)
            results.append(result)
        
        return results
    
    def _filter_rules(self, rule_filter: Dict[str, Any]) -> List[RiskRule]:
        """Filter rules based on criteria"""
        filtered_rules = []
        
        for rule in self.rules.values():
            # Check enabled status
            if rule_filter.get('enabled_only', True) and not rule.enabled:
                continue
            
            # Check rule type
            if 'rule_types' in rule_filter:
                if rule.rule_type not in rule_filter['rule_types']:
                    continue
            
            # Check tags
            if 'tags' in rule_filter:
                if not any(tag in rule.tags for tag in rule_filter['tags']):
                    continue
            
            # Check priority
            if 'min_priority' in rule_filter:
                if rule.priority < rule_filter['min_priority']:
                    continue
            
            filtered_rules.append(rule)
        
        return filtered_rules
    
    def get_rule(self, rule_id: str) -> Optional[RiskRule]:
        """Get rule by ID"""
        return self.rules.get(rule_id)
    
    def list_rules(self, rule_type: Optional[RuleType] = None) -> List[RiskRule]:
        """List all rules, optionally filtered by type"""
        if rule_type:
            return [rule for rule in self.rules.values() if rule.rule_type == rule_type]
        return list(self.rules.values())
    
    def create_policy(self, policy: PolicySet) -> bool:
        """Create a new policy"""
        try:
            self.policies[policy.policy_id] = policy
            self._save_rules_and_policies()
            
            self.logger.logger.info(f"Created policy: {policy.policy_id}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error creating policy {policy.policy_id}: {e}")
            return False
    
    def get_policy(self, policy_id: str) -> Optional[PolicySet]:
        """Get policy by ID"""
        return self.policies.get(policy_id)
    
    def list_policies(self) -> List[PolicySet]:
        """List all policies"""
        return list(self.policies.values())
    
    async def evaluate_policy(self, policy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all rules in a policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Get rules in policy
        policy_rules = [self.rules[rule_id] for rule_id in policy.rules if rule_id in self.rules]
        
        # Evaluate rules
        results = []
        for rule in policy_rules:
            result = await self.evaluation_engine.evaluate_rule(rule, data)
            results.append(result)
        
        # Calculate policy-level metrics
        triggered_rules = [r for r in results if r.triggered]
        total_risk_score = sum(r.confidence_score for r in triggered_rules)
        
        return {
            'policy_id': policy_id,
            'policy_name': policy.name,
            'evaluation_timestamp': datetime.now().isoformat(),
            'rules_evaluated': len(results),
            'rules_triggered': len(triggered_rules),
            'overall_risk_score': total_risk_score,
            'rule_results': [asdict(r) for r in results]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rules and policies statistics"""
        rule_stats = {
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'rules_by_type': {},
            'rules_by_priority': {}
        }
        
        # Rules by type
        for rule in self.rules.values():
            rule_type = rule.rule_type.value
            rule_stats['rules_by_type'][rule_type] = rule_stats['rules_by_type'].get(rule_type, 0) + 1
        
        # Rules by priority
        for rule in self.rules.values():
            priority = rule.priority
            rule_stats['rules_by_priority'][priority] = rule_stats['rules_by_priority'].get(priority, 0) + 1
        
        policy_stats = {
            'total_policies': len(self.policies),
            'enabled_policies': len([p for p in self.policies.values() if p.enabled])
        }
        
        evaluation_stats = self.evaluation_engine.get_stats()
        
        return {
            'rules': rule_stats,
            'policies': policy_stats,
            'evaluation_engine': evaluation_stats,
            'last_updated': datetime.now().isoformat()
        }

# Global risk rules manager with default config
risk_rules_manager = RiskRulesManager(config={})

def get_risk_rules_manager() -> RiskRulesManager:
    """Get the global risk rules manager"""
    return risk_rules_manager
