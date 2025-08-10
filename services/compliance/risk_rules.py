"""
Customizable Risk Rules Engine for Compliant.one
Advanced rule-based risk assessment with configurable thresholds and criteria
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re
import operator

logger = logging.getLogger(__name__)

class RuleOperator(Enum):
    """Available operators for rule conditions"""
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
    MATCHES_REGEX = "matches_regex"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

class RiskLevel(Enum):
    """Risk levels for rule outcomes"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertSeverity(Enum):
    """Alert severity levels"""
    IMMEDIATE = "immediate"
    URGENT = "urgent"
    NORMAL = "normal"
    LOW_PRIORITY = "low_priority"

@dataclass
class RuleCondition:
    """Individual condition within a rule"""
    field: str
    operator: RuleOperator
    value: Any
    case_sensitive: bool = True
    
class LogicalOperator(Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"

@dataclass
class RuleAction:
    """Action to take when rule is triggered"""
    action_type: str  # "alert", "score_adjustment", "escalation", "block"
    parameters: Dict[str, Any]
    severity: AlertSeverity = AlertSeverity.NORMAL

@dataclass
class RiskRule:
    """Complete risk rule definition"""
    rule_id: str
    name: str
    description: str
    conditions: List[RuleCondition]
    logical_operator: LogicalOperator
    risk_level: RiskLevel
    risk_score_adjustment: float  # Points to add/subtract from base score
    actions: List[RuleAction]
    enabled: bool = True
    priority: int = 50  # 1-100, higher = more important
    category: str = "general"
    created_by: str = "system"
    created_at: datetime = None
    last_modified: datetime = None
    tags: List[str] = None

class CustomRiskRulesEngine:
    """Advanced customizable risk rules engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.rules: Dict[str, RiskRule] = {}
        self.rule_templates = self._load_default_templates()
        self.execution_stats = {}
        
        # Operator mapping for evaluation
        self.operators = {
            RuleOperator.EQUALS: operator.eq,
            RuleOperator.NOT_EQUALS: operator.ne,
            RuleOperator.GREATER_THAN: operator.gt,
            RuleOperator.LESS_THAN: operator.lt,
            RuleOperator.GREATER_EQUAL: operator.ge,
            RuleOperator.LESS_EQUAL: operator.le,
        }
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load default rule templates for common scenarios"""
        return {
            "high_value_transaction": {
                "name": "High Value Transaction Alert",
                "description": "Alert on transactions above specified threshold",
                "conditions": [
                    {
                        "field": "transaction_amount",
                        "operator": "greater_than",
                        "value": 100000
                    }
                ],
                "risk_level": "high",
                "risk_score_adjustment": 25.0,
                "category": "financial"
            },
            "sanctions_list_match": {
                "name": "Sanctions List Match",
                "description": "Critical alert for sanctions list matches",
                "conditions": [
                    {
                        "field": "sanctions_match_score",
                        "operator": "greater_than",
                        "value": 0.8
                    }
                ],
                "risk_level": "critical",
                "risk_score_adjustment": 50.0,
                "category": "compliance"
            },
            "pep_exposure": {
                "name": "PEP Exposure Detection",
                "description": "Alert for Politically Exposed Person relationships",
                "conditions": [
                    {
                        "field": "pep_status",
                        "operator": "equals",
                        "value": True
                    }
                ],
                "risk_level": "high",
                "risk_score_adjustment": 30.0,
                "category": "compliance"
            },
            "adverse_media_high": {
                "name": "High-Risk Adverse Media",
                "description": "Alert for high-risk adverse media mentions",
                "conditions": [
                    {
                        "field": "adverse_media_score",
                        "operator": "greater_than",
                        "value": 0.7
                    }
                ],
                "risk_level": "high",
                "risk_score_adjustment": 20.0,
                "category": "reputation"
            },
            "geographic_risk": {
                "name": "High-Risk Geography",
                "description": "Alert for high-risk jurisdictions",
                "conditions": [
                    {
                        "field": "country_risk_score",
                        "operator": "greater_than",
                        "value": 8.0
                    }
                ],
                "risk_level": "medium",
                "risk_score_adjustment": 15.0,
                "category": "geographic"
            },
            "anomaly_detection": {
                "name": "Behavioral Anomaly Alert",
                "description": "Alert for anomalous behavior patterns",
                "conditions": [
                    {
                        "field": "anomaly_score",
                        "operator": "greater_than",
                        "value": 0.8
                    }
                ],
                "risk_level": "medium",
                "risk_score_adjustment": 18.0,
                "category": "behavioral"
            }
        }
    
    def create_rule_from_template(self, template_name: str, rule_id: str,
                                 customizations: Dict[str, Any] = None) -> RiskRule:
        """Create a rule from a predefined template"""
        if template_name not in self.rule_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.rule_templates[template_name].copy()
        
        # Apply customizations
        if customizations:
            template.update(customizations)
        
        # Convert conditions to RuleCondition objects
        conditions = []
        for cond_dict in template.get('conditions', []):
            condition = RuleCondition(
                field=cond_dict['field'],
                operator=RuleOperator(cond_dict['operator']),
                value=cond_dict['value'],
                case_sensitive=cond_dict.get('case_sensitive', True)
            )
            conditions.append(condition)
        
        # Create default actions
        actions = template.get('actions', [
            RuleAction(
                action_type="alert",
                parameters={"message": f"Rule triggered: {template['name']}"},
                severity=AlertSeverity.NORMAL
            )
        ])
        
        if isinstance(actions[0], dict):
            actions = [RuleAction(**action) for action in actions]
        
        rule = RiskRule(
            rule_id=rule_id,
            name=template['name'],
            description=template['description'],
            conditions=conditions,
            logical_operator=LogicalOperator(template.get('logical_operator', 'and')),
            risk_level=RiskLevel(template['risk_level']),
            risk_score_adjustment=template['risk_score_adjustment'],
            actions=actions,
            category=template.get('category', 'general'),
            created_at=datetime.now(),
            last_modified=datetime.now(),
            tags=template.get('tags', [])
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Created rule '{rule_id}' from template '{template_name}'")
        return rule
    
    def create_custom_rule(self, rule_definition: Dict[str, Any]) -> RiskRule:
        """Create a completely custom rule"""
        try:
            # Convert conditions
            conditions = []
            for cond_dict in rule_definition.get('conditions', []):
                condition = RuleCondition(
                    field=cond_dict['field'],
                    operator=RuleOperator(cond_dict['operator']),
                    value=cond_dict['value'],
                    case_sensitive=cond_dict.get('case_sensitive', True)
                )
                conditions.append(condition)
            
            # Convert actions
            actions = []
            for action_dict in rule_definition.get('actions', []):
                action = RuleAction(
                    action_type=action_dict['action_type'],
                    parameters=action_dict.get('parameters', {}),
                    severity=AlertSeverity(action_dict.get('severity', 'normal'))
                )
                actions.append(action)
            
            rule = RiskRule(
                rule_id=rule_definition['rule_id'],
                name=rule_definition['name'],
                description=rule_definition['description'],
                conditions=conditions,
                logical_operator=LogicalOperator(rule_definition.get('logical_operator', 'and')),
                risk_level=RiskLevel(rule_definition['risk_level']),
                risk_score_adjustment=rule_definition['risk_score_adjustment'],
                actions=actions,
                enabled=rule_definition.get('enabled', True),
                priority=rule_definition.get('priority', 50),
                category=rule_definition.get('category', 'general'),
                created_by=rule_definition.get('created_by', 'user'),
                created_at=datetime.now(),
                last_modified=datetime.now(),
                tags=rule_definition.get('tags', [])
            )
            
            self.rules[rule.rule_id] = rule
            logger.info(f"Created custom rule '{rule.rule_id}'")
            return rule
            
        except Exception as e:
            logger.error(f"Error creating custom rule: {e}")
            raise
    
    def evaluate_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all rules against entity data"""
        logger.info(f"Evaluating rules for entity: {entity_data.get('name', 'Unknown')}")
        
        evaluation_results = {
            'entity_name': entity_data.get('name', 'Unknown'),
            'evaluation_timestamp': datetime.now().isoformat(),
            'triggered_rules': [],
            'total_risk_adjustment': 0.0,
            'highest_risk_level': RiskLevel.LOW,
            'actions_to_execute': [],
            'rule_count': len(self.rules),
            'enabled_rule_count': len([r for r in self.rules.values() if r.enabled])
        }
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(
            [rule for rule in self.rules.values() if rule.enabled],
            key=lambda x: x.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            try:
                rule_result = self._evaluate_rule(rule, entity_data)
                
                if rule_result['triggered']:
                    evaluation_results['triggered_rules'].append(rule_result)
                    evaluation_results['total_risk_adjustment'] += rule.risk_score_adjustment
                    evaluation_results['actions_to_execute'].extend(rule.actions)
                    
                    # Update highest risk level
                    if self._compare_risk_levels(rule.risk_level, evaluation_results['highest_risk_level']):
                        evaluation_results['highest_risk_level'] = rule.risk_level
                    
                    # Update execution stats
                    self._update_execution_stats(rule.rule_id, True)
                else:
                    self._update_execution_stats(rule.rule_id, False)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        logger.info(f"Rule evaluation complete: {len(evaluation_results['triggered_rules'])} rules triggered")
        return evaluation_results
    
    def _evaluate_rule(self, rule: RiskRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single rule against entity data"""
        condition_results = []
        
        # Evaluate each condition
        for condition in rule.conditions:
            result = self._evaluate_condition(condition, entity_data)
            condition_results.append(result)
        
        # Apply logical operator
        if rule.logical_operator == LogicalOperator.AND:
            triggered = all(condition_results)
        elif rule.logical_operator == LogicalOperator.OR:
            triggered = any(condition_results)
        else:  # NOT - apply to first condition only
            triggered = not condition_results[0] if condition_results else False
        
        return {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'triggered': triggered,
            'condition_results': condition_results,
            'risk_level': rule.risk_level.value,
            'risk_adjustment': rule.risk_score_adjustment if triggered else 0.0,
            'category': rule.category,
            'evaluation_timestamp': datetime.now().isoformat()
        }
    
    def _evaluate_condition(self, condition: RuleCondition, entity_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            # Get field value from entity data
            field_value = self._get_field_value(condition.field, entity_data)
            condition_value = condition.value
            
            # Handle case sensitivity for string comparisons
            if isinstance(field_value, str) and isinstance(condition_value, str):
                if not condition.case_sensitive:
                    field_value = field_value.lower()
                    condition_value = condition_value.lower()
            
            # Evaluate based on operator
            if condition.operator in self.operators:
                return self.operators[condition.operator](field_value, condition_value)
            elif condition.operator == RuleOperator.CONTAINS:
                return condition_value in str(field_value)
            elif condition.operator == RuleOperator.NOT_CONTAINS:
                return condition_value not in str(field_value)
            elif condition.operator == RuleOperator.STARTS_WITH:
                return str(field_value).startswith(str(condition_value))
            elif condition.operator == RuleOperator.ENDS_WITH:
                return str(field_value).endswith(str(condition_value))
            elif condition.operator == RuleOperator.MATCHES_REGEX:
                return bool(re.match(str(condition_value), str(field_value)))
            elif condition.operator == RuleOperator.IN_LIST:
                return field_value in condition_value
            elif condition.operator == RuleOperator.NOT_IN_LIST:
                return field_value not in condition_value
            elif condition.operator == RuleOperator.IS_NULL:
                return field_value is None
            elif condition.operator == RuleOperator.IS_NOT_NULL:
                return field_value is not None
            else:
                logger.warning(f"Unknown operator: {condition.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition for field '{condition.field}': {e}")
            return False
    
    def _get_field_value(self, field_path: str, data: Dict[str, Any]) -> Any:
        """Get field value from nested data using dot notation"""
        try:
            value = data
            for key in field_path.split('.'):
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
                    
                if value is None:
                    break
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting field value for '{field_path}': {e}")
            return None
    
    def _compare_risk_levels(self, level1: RiskLevel, level2: RiskLevel) -> bool:
        """Compare risk levels to determine if level1 is higher than level2"""
        risk_order = {
            RiskLevel.INFO: 1,
            RiskLevel.LOW: 2,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 4,
            RiskLevel.CRITICAL: 5
        }
        
        return risk_order.get(level1, 0) > risk_order.get(level2, 0)
    
    def _update_execution_stats(self, rule_id: str, triggered: bool):
        """Update rule execution statistics"""
        if rule_id not in self.execution_stats:
            self.execution_stats[rule_id] = {
                'total_executions': 0,
                'triggered_count': 0,
                'last_execution': None,
                'last_triggered': None
            }
        
        stats = self.execution_stats[rule_id]
        stats['total_executions'] += 1
        stats['last_execution'] = datetime.now()
        
        if triggered:
            stats['triggered_count'] += 1
            stats['last_triggered'] = datetime.now()
    
    def get_rule_by_id(self, rule_id: str) -> Optional[RiskRule]:
        """Get rule by ID"""
        return self.rules.get(rule_id)
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing rule"""
        try:
            if rule_id not in self.rules:
                return False
            
            rule = self.rules[rule_id]
            
            # Update allowed fields
            allowed_updates = ['name', 'description', 'enabled', 'priority', 
                             'risk_score_adjustment', 'category', 'tags']
            
            for field, value in updates.items():
                if field in allowed_updates:
                    setattr(rule, field, value)
            
            rule.last_modified = datetime.now()
            logger.info(f"Updated rule '{rule_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rule '{rule_id}': {e}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                if rule_id in self.execution_stats:
                    del self.execution_stats[rule_id]
                logger.info(f"Deleted rule '{rule_id}'")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting rule '{rule_id}': {e}")
            return False
    
    def export_rules(self, rule_ids: List[str] = None) -> Dict[str, Any]:
        """Export rules to JSON format"""
        rules_to_export = {}
        
        if rule_ids:
            for rule_id in rule_ids:
                if rule_id in self.rules:
                    rules_to_export[rule_id] = self._serialize_rule(self.rules[rule_id])
        else:
            for rule_id, rule in self.rules.items():
                rules_to_export[rule_id] = self._serialize_rule(rule)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'rule_count': len(rules_to_export),
            'rules': rules_to_export
        }
        
        return export_data
    
    def import_rules(self, import_data: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """Import rules from JSON format"""
        results = {
            'imported_count': 0,
            'skipped_count': 0,
            'errors': []
        }
        
        try:
            rules_data = import_data.get('rules', {})
            
            for rule_id, rule_data in rules_data.items():
                try:
                    if rule_id in self.rules and not overwrite:
                        results['skipped_count'] += 1
                        continue
                    
                    rule = self._deserialize_rule(rule_data)
                    self.rules[rule_id] = rule
                    results['imported_count'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Error importing rule '{rule_id}': {e}")
            
            logger.info(f"Import complete: {results['imported_count']} rules imported")
            
        except Exception as e:
            logger.error(f"Error during import: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _serialize_rule(self, rule: RiskRule) -> Dict[str, Any]:
        """Serialize rule to dictionary"""
        rule_dict = asdict(rule)
        
        # Convert enum values to strings
        rule_dict['logical_operator'] = rule.logical_operator.value
        rule_dict['risk_level'] = rule.risk_level.value
        
        # Convert conditions
        conditions = []
        for condition in rule.conditions:
            cond_dict = asdict(condition)
            cond_dict['operator'] = condition.operator.value
            conditions.append(cond_dict)
        rule_dict['conditions'] = conditions
        
        # Convert actions
        actions = []
        for action in rule.actions:
            action_dict = asdict(action)
            action_dict['severity'] = action.severity.value
            actions.append(action_dict)
        rule_dict['actions'] = actions
        
        # Convert datetime objects
        if rule_dict['created_at']:
            rule_dict['created_at'] = rule.created_at.isoformat()
        if rule_dict['last_modified']:
            rule_dict['last_modified'] = rule.last_modified.isoformat()
        
        return rule_dict
    
    def _deserialize_rule(self, rule_dict: Dict[str, Any]) -> RiskRule:
        """Deserialize rule from dictionary"""
        # Convert conditions
        conditions = []
        for cond_dict in rule_dict.get('conditions', []):
            condition = RuleCondition(
                field=cond_dict['field'],
                operator=RuleOperator(cond_dict['operator']),
                value=cond_dict['value'],
                case_sensitive=cond_dict.get('case_sensitive', True)
            )
            conditions.append(condition)
        
        # Convert actions
        actions = []
        for action_dict in rule_dict.get('actions', []):
            action = RuleAction(
                action_type=action_dict['action_type'],
                parameters=action_dict.get('parameters', {}),
                severity=AlertSeverity(action_dict.get('severity', 'normal'))
            )
            actions.append(action)
        
        # Convert datetime strings
        created_at = None
        if rule_dict.get('created_at'):
            try:
                created_at = datetime.fromisoformat(rule_dict['created_at'])
            except:
                created_at = datetime.now()
        
        last_modified = None
        if rule_dict.get('last_modified'):
            try:
                last_modified = datetime.fromisoformat(rule_dict['last_modified'])
            except:
                last_modified = datetime.now()
        
        rule = RiskRule(
            rule_id=rule_dict['rule_id'],
            name=rule_dict['name'],
            description=rule_dict['description'],
            conditions=conditions,
            logical_operator=LogicalOperator(rule_dict.get('logical_operator', 'and')),
            risk_level=RiskLevel(rule_dict['risk_level']),
            risk_score_adjustment=rule_dict['risk_score_adjustment'],
            actions=actions,
            enabled=rule_dict.get('enabled', True),
            priority=rule_dict.get('priority', 50),
            category=rule_dict.get('category', 'general'),
            created_by=rule_dict.get('created_by', 'system'),
            created_at=created_at,
            last_modified=last_modified,
            tags=rule_dict.get('tags', [])
        )
        
        return rule
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get comprehensive rule statistics"""
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        
        # Category breakdown
        categories = {}
        for rule in self.rules.values():
            categories[rule.category] = categories.get(rule.category, 0) + 1
        
        # Risk level breakdown
        risk_levels = {}
        for rule in self.rules.values():
            level = rule.risk_level.value
            risk_levels[level] = risk_levels.get(level, 0) + 1
        
        # Execution statistics
        total_executions = sum(stats['total_executions'] for stats in self.execution_stats.values())
        total_triggers = sum(stats['triggered_count'] for stats in self.execution_stats.values())
        
        return {
            'total_rules': total_rules,
            'enabled_rules': enabled_rules,
            'disabled_rules': total_rules - enabled_rules,
            'categories': categories,
            'risk_levels': risk_levels,
            'execution_stats': {
                'total_executions': total_executions,
                'total_triggers': total_triggers,
                'trigger_rate': total_triggers / total_executions if total_executions > 0 else 0
            },
            'statistics_timestamp': datetime.now().isoformat()
        }
