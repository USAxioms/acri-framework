"""
Adaptive Conversational Risk Intake (ACRI)
Conversational Intake Module
Michael Aaron Russell, Universal Standard Axiom Corporation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
from datetime import datetime

from evidence_state import EvidenceState, StructuredRiskState, RiskComponent, DataConsistency


class Disposition(Enum):
    """Possible case dispositions"""
    STP = "straight_through_processing"
    EVIDENCE_REQUEST = "targeted_evidence_request"
    REFER = "refer_to_underwriter"
    POSTPONE = "postpone"
    DECLINE = "decline"


@dataclass
class Question:
    """Conversational question"""
    question_id: str
    text: str
    category: str  # "health", "lifestyle", "family", etc.
    expected_uncertainty_reduction: float  # ΔU(q)
    cost: float  # C(q): operational/applicant burden cost
    required: bool = False
    followup_questions: List[str] = field(default_factory=list)

    def compute_value(self, lambda_cost: float = 0.5) -> float:
        """
        Compute expected information value
        V(q) = ΔU(q) - λ * C(q)
        """
        return self.expected_uncertainty_reduction - (lambda_cost * self.cost)


@dataclass
class ConversationalIntake:
    """
    Adaptive conversational intake system
    Implements ACRI core loop
    """
    applicant_id: str
    evidence_state: EvidenceState
    lambda_cost: float = 0.5  # Cost weighting parameter
    max_conversation_time: float = 15.0  # minutes
    uncertainty_threshold: float = 0.15
    value_threshold: float = 0.20
    
    # Question library
    question_library: Dict[str, Question] = field(default_factory=dict)
    
    # Configuration
    config: Dict = field(default_factory=dict)
    
    # Tracking
    start_time: datetime = field(default_factory=datetime.now)
    conversation_turns: int = 0
    

    def initialize_question_library(self) -> None:
        """Load question library"""
        self.question_library = {
            "q_health_conditions": Question(
                question_id="q_health_conditions",
                text="What medical conditions have you been diagnosed with in the past 5 years?",
                category="health",
                expected_uncertainty_reduction=0.15,
                cost=0.1,
                required=True
            ),
            "q_medications": Question(
                question_id="q_medications",
                text="What medications are you currently taking? Please list the name, dosage, and how long you've been taking it.",
                category="health",
                expected_uncertainty_reduction=0.12,
                cost=0.15,
                required=True
            ),
            "q_family_history": Question(
                question_id="q_family_history",
                text="Does anyone in your immediate family have a history of early death or serious illness?",
                category="family",
                expected_uncertainty_reduction=0.08,
                cost=0.05,
                required=False
            ),
            "q_tobacco": Question(
                question_id="q_tobacco",
                text="Have you used tobacco products in the past 12 months?",
                category="lifestyle",
                expected_uncertainty_reduction=0.10,
                cost=0.02,
                required=True
            ),
            "q_occupation": Question(
                question_id="q_occupation",
                text="What is your primary occupation and any avocational activities involving hazards?",
                category="occupational",
                expected_uncertainty_reduction=0.05,
                cost=0.08,
                required=False
            ),
            "q_driving": Question(
                question_id="q_driving",
                text="Have you had any driving violations or accidents in the past 5 years?",
                category="behavioral",
                expected_uncertainty_reduction=0.03,
                cost=0.05,
                required=False
            )
        }

    def get_next_question(self) -> Optional[Question]:
        """
        Select next question based on information value
        q* = arg max V(q) subject to constraints
        """
        # Generate candidate questions
        candidates = self._generate_candidate_questions()
        
        if not candidates:
            return None
        
        # Score candidates by value
        scored = []
        for question in candidates:
            value = question.compute_value(self.lambda_cost)
            scored.append((question, value))
        
        # Sort by value (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Return highest-value question
        if scored:
            next_question = scored[0][0]
            
            # Check constraints
            if self._check_constraints(next_question):
                return next_question
            else:
                # Try second-ranked if constraint violation
                return scored[1][0] if len(scored) > 1 else None
        
        return None

    def _generate_candidate_questions(self) -> List[Question]:
        """Generate candidates based on current state"""
        candidates = []
        
        # Include required questions not yet asked
        for qid, question in self.question_library.items():
            if question.required:
                if not self._already_asked(qid):
                    candidates.append(question)
            else:
                # Optional: include if uncertainty reduction > threshold
                if question.expected_uncertainty_reduction > self.value_threshold:
                    if not self._already_asked(qid):
                        candidates.append(question)
        
        return candidates

    def _already_asked(self, question_id: str) -> bool:
        """Check if question was already asked"""
        return any(q["question_id"] == question_id 
                  for q in self.evidence_state.questions_asked)

    def _check_constraints(self, question: Question) -> bool:
        """Verify question meets constraints"""
        # Check time constraint
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed > self.max_conversation_time:
            return False
        
        # Check if question is in validated domain
        if question.category in ["health", "lifestyle", "family", "occupational"]:
            return True
        
        return False

    def record_response(self, question_id: str, response: str) -> None:
        """Record applicant response and update state"""
        self.evidence_state.record_question(
            question_id,
            self.question_library[question_id].text,
            self.question_library[question_id].category
        )
        self.evidence_state.record_response(question_id, response)
        
        # Parse response
        parsed = self._parse_response(question_id, response)
        
        # Update evidence state with parsed response
        self._update_evidence_from_response(question_id, parsed)
        
        # Check consistency
        consistency_issues = self._check_consistency(question_id, parsed)
        if consistency_issues:
            for issue in consistency_issues:
                self.evidence_state.add_conflict(
                    field=issue["field"],
                    reported=issue["reported"],
                    corroborating=issue["corroborating"],
                    severity=issue["severity"]
                )
        
        # Recompute uncertainty
        self._update_uncertainty()
        
        self.conversation_turns += 1

    def _parse_response(self, question_id: str, response: str) -> Dict:
        """Parse applicant response"""
        # Simple parsing; in production would use NLP
        parsed = {
            "question_id": question_id,
            "raw_response": response,
            "parsed_value": response.lower(),
            "confidence": 0.7  # Would be determined by NLP confidence
        }
        return parsed

    def _update_evidence_from_response(self, question_id: str, parsed: Dict) -> None:
        """Update evidence state from parsed response"""
        question = self.question_library[question_id]
        
        # Create risk component from response
        component = RiskComponent(
            value=self._compute_risk_value(question, parsed),
            confidence=parsed["confidence"],
            source="conversational_intake",
            timestamp=datetime.now(),
            consistency=DataConsistency.REPORTED
        )
        
        # Store in verified evidence
        self.evidence_state.add_verified_evidence(question.category, component)

    def _compute_risk_value(self, question: Question, parsed: Dict) -> float:
        """Compute risk value from parsed response"""
        # Simplified computation
        response_lower = parsed["raw_response"].lower()
        
        # Category-specific logic
        if question.category == "health":
            if "no" in response_lower or "none" in response_lower:
                return 0.1
            else:
                return 0.5
        elif question.category == "lifestyle":
            if "no" in response_lower:
                return 0.1
            else:
                return 0.6
        elif question.category == "behavioral":
            if "no" in response_lower:
                return 0.1
            else:
                return 0.7
        
        return 0.5  # Default medium risk

    def _check_consistency(self, question_id: str, parsed: Dict) -> List[Dict]:
        """Check consistency with prior disclosures"""
        issues = []
        
        # In production: compare against external data sources, MIB, etc.
        # For now: simple consistency check
        
        return issues

    def _update_uncertainty(self) -> None:
        """Recompute uncertainty measure"""
        # Simplified: uncertainty = 1 - completeness
        completeness = self.evidence_state.evidence_completeness()
        new_uncertainty = 1.0 - completeness
        self.evidence_state.update_uncertainty(new_uncertainty)

    def assess_evidence_sufficiency(self) -> Disposition:
        """
        Determine evidence sufficiency state
        Returns: STP, EVIDENCE_REQUEST, or REFER
        """
        
        # Check State I: Sufficient for STP
        if self._check_stp_requirements():
            return Disposition.STP
        
        # Check State II: Resolvable evidence gap
        if self._has_resolvable_gap():
            return Disposition.EVIDENCE_REQUEST
        
        # Check State III: Material complexity
        if self._has_material_complexity():
            return Disposition.REFER
        
        # Default: needs more information
        return Disposition.EVIDENCE_REQUEST

    def _check_stp_requirements(self) -> bool:
        """Verify all STP requirements"""
        requirements = [
            self._has_sufficient_health_info(),
            self._has_sufficient_lifestyle_info(),
            self._has_sufficient_occupation_info(),
            not self.evidence_state.has_material_conflicts(),
            self.evidence_state.uncertainty < self.uncertainty_threshold
        ]
        return all(requirements)

    def _has_sufficient_health_info(self) -> bool:
        """Check sufficient health information"""
        return "health" in self.evidence_state.verified_evidence

    def _has_sufficient_lifestyle_info(self) -> bool:
        """Check sufficient lifestyle information"""
        return "lifestyle" in self.evidence_state.verified_evidence

    def _has_sufficient_occupation_info(self) -> bool:
        """Check sufficient occupation information"""
        # Optional: return True if not critical
        return True

    def _has_resolvable_gap(self) -> bool:
        """Check if specific evidence would resolve uncertainty"""
        # Look for high-value unanswered questions
        candidates = self._generate_candidate_questions()
        for q in candidates:
            if q.compute_value(self.lambda_cost) > self.value_threshold:
                return True
        return False

    def _has_material_complexity(self) -> bool:
        """Identify material complexity"""
        # Multiple conditions + conflicts
        num_conditions = len([v for v in self.evidence_state.verified_evidence.values()])
        num_conflicts = len([c for c in self.evidence_state.conflicts if c.severity == "high"])
        
        return (num_conditions >= 3 and num_conflicts > 0) or num_conflicts >= 2

    def get_conversation_summary(self) -> Dict:
        """Generate summary of conversation"""
        return {
            "applicant_id": self.applicant_id,
            "turns": self.conversation_turns,
            "elapsed_time": (datetime.now() - self.start_time).total_seconds() / 60,
            "uncertainty": self.evidence_state.uncertainty,
            "completeness": self.evidence_state.evidence_completeness(),
            "conflicts": len(self.evidence_state.conflicts),
            "disposition": self.assess_evidence_sufficiency().value
        }
