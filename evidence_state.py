"""
Adaptive Conversational Risk Intake (ACRI)
Evidence State Module
Michael Aaron Russell, Universal Standard Axiom Corporation
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class DataConsistency(Enum):
    """Data consistency levels"""
    REPORTED = "reported"
    CORROBORATED = "corroborated"
    VERIFIED = "verified"
    CONFLICTED = "conflicted"


@dataclass
class RiskComponent:
    """Individual risk component"""
    value: float  # [0, 1] normalized
    confidence: float  # confidence level
    source: str  # data source
    timestamp: datetime
    consistency: DataConsistency = DataConsistency.REPORTED

    def to_dict(self):
        return {
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "consistency": self.consistency.value
        }


@dataclass
class StructuredRiskState:
    """8-dimensional risk state vector"""
    health: RiskComponent  # RH: health indicators
    lifestyle: RiskComponent  # RL: lifestyle
    family_history: RiskComponent  # RF: family history
    occupational: RiskComponent  # RO: occupational/avocational
    medications: RiskComponent  # RM: medication indicators
    behavioral: RiskComponent  # RB: behavioral/driving
    data_quality: RiskComponent  # RD: data consistency
    complexity: RiskComponent  # RC: multi-impairment complexity

    def to_array(self) -> List[float]:
        """Return as 8-element vector"""
        return [
            self.health.value,
            self.lifestyle.value,
            self.family_history.value,
            self.occupational.value,
            self.medications.value,
            self.behavioral.value,
            self.data_quality.value,
            self.complexity.value
        ]

    def to_dict(self):
        return {
            "health": self.health.to_dict(),
            "lifestyle": self.lifestyle.to_dict(),
            "family_history": self.family_history.to_dict(),
            "occupational": self.occupational.to_dict(),
            "medications": self.medications.to_dict(),
            "behavioral": self.behavioral.to_dict(),
            "data_quality": self.data_quality.to_dict(),
            "complexity": self.complexity.to_dict()
        }


@dataclass
class ConflictRecord:
    """Record of data conflicts/inconsistencies"""
    timestamp: datetime
    field: str
    reported_value: str
    corroborating_value: str
    severity: str  # "low", "medium", "high"
    resolved: bool = False
    resolution: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class EvidenceState:
    """
    Complete evidence state at time t
    E_t = {A_t, D_t, Q_t, R_t, V_t, C_t}
    """
    application_id: str
    timestamp: datetime
    
    # A_t: Applicant disclosures
    applicant_disclosures: Dict[str, str] = field(default_factory=dict)
    
    # D_t: Authorized external data
    external_data: Dict[str, str] = field(default_factory=dict)
    
    # Q_t: Questions asked
    questions_asked: List[Dict] = field(default_factory=list)
    
    # R_t: Responses received
    responses: List[Dict] = field(default_factory=list)
    
    # V_t: Verified evidence
    verified_evidence: Dict[str, RiskComponent] = field(default_factory=dict)
    
    # C_t: Conflicts/inconsistencies
    conflicts: List[ConflictRecord] = field(default_factory=list)
    
    # Risk state representation
    risk_state: Optional[StructuredRiskState] = None
    
    # Uncertainty measure
    uncertainty: float = 1.0  # [0, 1] where 1 = maximum uncertainty
    
    # Material uncertainty threshold
    uncertainty_threshold: float = 0.15

    def add_disclosure(self, field: str, value: str) -> None:
        """Add applicant disclosure"""
        self.applicant_disclosures[field] = value
        self.timestamp = datetime.now()

    def add_external_data(self, source: str, data: str) -> None:
        """Add external data source result"""
        self.external_data[source] = data
        self.timestamp = datetime.now()

    def record_question(self, question_id: str, text: str, category: str) -> None:
        """Record question asked"""
        self.questions_asked.append({
            "question_id": question_id,
            "text": text,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })

    def record_response(self, question_id: str, response: str) -> None:
        """Record applicant response"""
        self.responses.append({
            "question_id": question_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    def add_verified_evidence(self, field: str, component: RiskComponent) -> None:
        """Add verified evidence item"""
        self.verified_evidence[field] = component
        self.timestamp = datetime.now()

    def add_conflict(self, field: str, reported: str, corroborating: str, 
                     severity: str) -> None:
        """Record data conflict"""
        conflict = ConflictRecord(
            timestamp=datetime.now(),
            field=field,
            reported_value=reported,
            corroborating_value=corroborating,
            severity=severity
        )
        self.conflicts.append(conflict)

    def update_uncertainty(self, new_uncertainty: float) -> None:
        """Update uncertainty measure"""
        self.uncertainty = max(0.0, min(1.0, new_uncertainty))

    def is_uncertainty_resolvable(self) -> bool:
        """Check if remaining uncertainty is resolvable"""
        return self.uncertainty > 0.0  # Would be formalized in practice

    def has_material_conflicts(self) -> bool:
        """Check for material conflicts"""
        return any(c.severity == "high" and not c.resolved for c in self.conflicts)

    def evidence_completeness(self) -> float:
        """Measure evidence completeness [0, 1]"""
        total_expected = 8  # 8 risk dimensions
        
        if self.risk_state is None:
            return 0.0
        
        dimensions = self.risk_state.to_array()
        # Completeness = average non-zero dimension
        non_zero = sum(1 for d in dimensions if d > 0.0)
        return non_zero / total_expected

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "application_id": self.application_id,
            "timestamp": self.timestamp.isoformat(),
            "applicant_disclosures": self.applicant_disclosures,
            "external_data": self.external_data,
            "questions_asked": self.questions_asked,
            "responses": self.responses,
            "verified_evidence": {k: v.to_dict() for k, v in self.verified_evidence.items()},
            "conflicts": [c.to_dict() for c in self.conflicts],
            "risk_state": self.risk_state.to_dict() if self.risk_state else None,
            "uncertainty": self.uncertainty,
            "uncertainty_threshold": self.uncertainty_threshold,
            "completeness": self.evidence_completeness()
        }

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)
