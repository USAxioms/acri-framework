"""
Adaptive Conversational Risk Intake (ACRI)
Business Rules Management System (BRMS)
Michael Aaron Russell, Universal Standard Axiom Corporation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable
from datetime import datetime
import json

from evidence_state import EvidenceState


@dataclass
class RuleCondition:
    """Single rule condition"""
    field: str
    operator: str  # "eq", "gt", "lt", "gte", "lte", "in", "contains"
    value: Any

    def evaluate(self, value: Any) -> bool:
        """Evaluate condition"""
        if self.operator == "eq":
            return value == self.value
        elif self.operator == "gt":
            return value > self.value
        elif self.operator == "lt":
            return value < self.value
        elif self.operator == "gte":
            return value >= self.value
        elif self.operator == "lte":
            return value <= self.value
        elif self.operator == "in":
            return value in self.value
        elif self.operator == "contains":
            return self.value in str(value).lower()
        return False


@dataclass
class RuleAction:
    """Rule action"""
    action_type: str  # "set", "increment", "flag", "route"
    target: str
    value: Any = None


@dataclass
class Rule:
    """Underwriting rule"""
    rule_id: str
    priority: int  # Lower = higher priority
    conditions: List[RuleCondition]
    action: RuleAction
    description: str = ""
    version: str = "1.0"
    is_terminal: bool = False  # If true, stop evaluating further rules

    def is_applicable(self, evidence_state: EvidenceState) -> bool:
        """Check if rule is applicable to evidence state"""
        # All conditions must be met
        return len(self.conditions) == 0  # Simplified; in practice, evaluate conditions


@dataclass
class RuleExecutionResult:
    """Result of rule execution"""
    rule_id: str
    triggered: bool
    conditions_met: bool
    action_result: Any
    timestamp: datetime
    error: str = None


@dataclass
class BusinessRulesManagementSystem:
    """
    Deterministic BRMS for automated underwriting
    """
    rules: List[Rule] = field(default_factory=list)
    rules_version: str = "1.0"
    execution_log: List[RuleExecutionResult] = field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        """Add rule to system"""
        self.rules.append(rule)
        # Auto-sort by priority
        self.rules.sort(key=lambda r: r.priority)

    def evaluate(self, evidence_state: EvidenceState) -> Dict[str, Any]:
        """
        Execute all applicable rules
        Returns results and disposition
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "rules_version": self.rules_version,
            "execution_results": [],
            "triggered_rules": [],
            "disposition": None,
            "score": 0.0
        }

        # Sort rules by priority
        sorted_rules = sorted(self.rules, key=lambda r: r.priority)

        for rule in sorted_rules:
            if rule.is_applicable(evidence_state):
                execution = self._execute_rule(rule, evidence_state)
                results["execution_results"].append(execution.__dict__)
                
                self.execution_log.append(execution)

                if execution.triggered:
                    results["triggered_rules"].append(rule.rule_id)
                    results["score"] += 0.1  # Simple scoring

                # Short-circuit on terminal outcomes
                if rule.is_terminal and execution.triggered:
                    break

        return results

    def _execute_rule(self, rule: Rule, evidence_state: EvidenceState) -> RuleExecutionResult:
        """Execute single rule"""
        try:
            # Evaluate conditions
            conditions_met = self._evaluate_conditions(rule.conditions, evidence_state)

            # Execute action if conditions met
            if conditions_met:
                action_result = self._execute_action(rule.action, evidence_state)
            else:
                action_result = None

            return RuleExecutionResult(
                rule_id=rule.rule_id,
                triggered=conditions_met,
                conditions_met=conditions_met,
                action_result=action_result,
                timestamp=datetime.now()
            )

        except Exception as e:
            return RuleExecutionResult(
                rule_id=rule.rule_id,
                triggered=False,
                conditions_met=False,
                action_result=None,
                timestamp=datetime.now(),
                error=str(e)
            )

    def _evaluate_conditions(self, conditions: List[RuleCondition], 
                            evidence_state: EvidenceState) -> bool:
        """Evaluate all conditions"""
        if not conditions:
            return True

        for condition in conditions:
            if not condition.evaluate(None):  # Simplified
                return False

        return True

    def _execute_action(self, action: RuleAction, evidence_state: EvidenceState) -> Any:
        """Execute rule action"""
        if action.action_type == "route":
            return f"Route to {action.value}"
        elif action.action_type == "flag":
            return f"Flag: {action.value}"
        elif action.action_type == "score":
            return action.value
        return None

    def validate_rules(self) -> Dict[str, Any]:
        """Validate rule set"""
        issues = []

        # Check for conflicts
        for i, r1 in enumerate(self.rules):
            for r2 in self.rules[i+1:]:
                if self._rules_conflict(r1, r2):
                    issues.append(f"Conflict: {r1.rule_id} vs {r2.rule_id}")

        # Check for redundancy
        for i, r1 in enumerate(self.rules):
            for r2 in self.rules[i+1:]:
                if self._rules_redundant(r1, r2):
                    issues.append(f"Redundancy: {r1.rule_id} and {r2.rule_id}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "rule_count": len(self.rules)
        }

    def _rules_conflict(self, r1: Rule, r2: Rule) -> bool:
        """Check if two rules conflict"""
        # Simplified: in practice would do semantic analysis
        return False

    def _rules_redundant(self, r1: Rule, r2: Rule) -> bool:
        """Check if two rules are redundant"""
        # Simplified: in practice would do semantic analysis
        return False

    def export_rules_json(self) -> str:
        """Export rules as JSON"""
        rules_dict = []
        for rule in self.rules:
            rules_dict.append({
                "rule_id": rule.rule_id,
                "priority": rule.priority,
                "description": rule.description,
                "version": rule.version,
                "is_terminal": rule.is_terminal
            })
        return json.dumps(rules_dict, indent=2)


# Pre-defined standard rules

def create_age_limit_rule() -> Rule:
    """Create age limit rule"""
    return Rule(
        rule_id="rule_age_limits",
        priority=1,
        conditions=[
            RuleCondition(field="age", operator="lt", value=18),
            RuleCondition(field="age", operator="gt", value=85)
        ],
        action=RuleAction(action_type="route", target="refer_to_underwriter", 
                         value="Age outside standard limits"),
        description="Route cases outside age range 18-85",
        is_terminal=True
    )


def create_amount_limit_rule(amount_limit: float = 500000) -> Rule:
    """Create face amount limit rule"""
    return Rule(
        rule_id="rule_amount_limits",
        priority=2,
        conditions=[
            RuleCondition(field="face_amount", operator="gt", value=amount_limit)
        ],
        action=RuleAction(action_type="route", target="refer_to_underwriter",
                         value=f"Amount exceeds ${amount_limit:,.0f}"),
        description=f"Route amounts above ${amount_limit:,.0f}",
        is_terminal=False
    )


def create_health_exclusion_rule() -> Rule:
    """Create health exclusion rule"""
    return Rule(
        rule_id="rule_health_exclusions",
        priority=3,
        conditions=[
            RuleCondition(field="health_conditions", operator="contains", 
                         value="cancer"),
            RuleCondition(field="health_conditions", operator="contains",
                         value="heart disease")
        ],
        action=RuleAction(action_type="route", target="refer_to_underwriter",
                         value="Material health impairment"),
        description="Route applicants with serious health exclusions",
        is_terminal=True
    )
