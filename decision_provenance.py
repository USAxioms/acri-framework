"""
Adaptive Conversational Risk Intake (ACRI)
Decision Provenance Module - Tamper-Evident Audit Trail
Michael Aaron Russell, Universal Standard Axiom Corporation
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class ProvenanceEntry:
    """Single entry in decision provenance trail"""
    timestamp: datetime
    event_type: str  # "question", "response", "data_source", "rule", "disposition"
    details: Dict[str, Any]
    sequence_number: int

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "details": self.details,
            "sequence_number": self.sequence_number
        }


class DecisionProvenance:
    """
    Tamper-evident decision provenance system
    Maintains complete audit trail of underwriting decision
    """

    def __init__(self, application_id: str):
        self.application_id = application_id
        self.provenance_trail: List[ProvenanceEntry] = []
        self.sequence_counter = 0
        self.creation_time = datetime.now()

        # Metadata
        self.metadata = {
            "application_id": application_id,
            "created": self.creation_time.isoformat(),
            "application_version": None,
            "rules_version": None,
            "guideline_version": None
        }

    def record_application_start(self, application_version: str = None,
                                 rules_version: str = None) -> None:
        """Record application initialization"""
        self.metadata["application_version"] = application_version
        self.metadata["rules_version"] = rules_version

        self._add_entry(
            event_type="application_start",
            details={
                "application_version": application_version,
                "rules_version": rules_version
            }
        )

    def record_question(self, question_id: str, question_text: str,
                       category: str) -> None:
        """Record question presented"""
        self._add_entry(
            event_type="question",
            details={
                "question_id": question_id,
                "text": question_text,
                "category": category
            }
        )

    def record_response(self, question_id: str, response: str) -> None:
        """Record applicant response"""
        self._add_entry(
            event_type="response",
            details={
                "question_id": question_id,
                "response": response
            }
        )

    def record_data_source(self, source_name: str, result: Any) -> None:
        """Record external data source result"""
        self._add_entry(
            event_type="data_source",
            details={
                "source": source_name,
                "result": str(result)
            }
        )

    def record_rule_execution(self, rule_id: str, conditions_met: bool,
                             action_taken: str) -> None:
        """Record rule execution"""
        self._add_entry(
            event_type="rule",
            details={
                "rule_id": rule_id,
                "conditions_met": conditions_met,
                "action_taken": action_taken
            }
        )

    def record_disposition(self, disposition: str, reasoning: str,
                          confidence: float) -> None:
        """Record final disposition"""
        self._add_entry(
            event_type="disposition",
            details={
                "disposition": disposition,
                "reasoning": reasoning,
                "confidence": confidence
            }
        )

    def record_human_override(self, override_type: str, reason: str,
                            underwriter_id: str) -> None:
        """Record human override of automated decision"""
        self._add_entry(
            event_type="human_override",
            details={
                "override_type": override_type,
                "reason": reason,
                "underwriter_id": underwriter_id
            }
        )

    def _add_entry(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add entry to provenance trail"""
        entry = ProvenanceEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            details=details,
            sequence_number=self.sequence_counter
        )
        self.provenance_trail.append(entry)
        self.sequence_counter += 1

    def get_provenance_record(self) -> Dict[str, Any]:
        """Get complete provenance record"""
        trail_list = [entry.to_dict() for entry in self.provenance_trail]

        record = {
            "metadata": self.metadata,
            "provenance_trail": trail_list,
            "trail_hash": self._compute_trail_hash(),
            "total_entries": len(self.provenance_trail),
            "completion_time": datetime.now().isoformat()
        }
        return record

    def _compute_trail_hash(self) -> str:
        """
        Compute cryptographic hash of entire provenance trail
        Hash = SHA256(concatenation of all entries in sequence)
        """
        hasher = hashlib.sha256()

        for entry in self.provenance_trail:
            entry_json = json.dumps(entry.to_dict(), sort_keys=True)
            hasher.update(entry_json.encode())

        return hasher.hexdigest()

    def verify_trail_integrity(self, stored_hash: str) -> bool:
        """Verify that provenance trail has not been tampered with"""
        current_hash = self._compute_trail_hash()
        return current_hash == stored_hash

    def get_decision_path(self) -> List[str]:
        """Extract simplified decision path"""
        path = []
        for entry in self.provenance_trail:
            if entry.event_type == "question":
                path.append(f"Q: {entry.details['question_id']}")
            elif entry.event_type == "rule":
                if entry.details['conditions_met']:
                    path.append(f"R: {entry.details['rule_id']}")
            elif entry.event_type == "disposition":
                path.append(f"D: {entry.details['disposition']}")
        return path

    def audit_trail_summary(self) -> Dict[str, Any]:
        """Generate audit trail summary"""
        event_counts = {}
        for entry in self.provenance_trail:
            event_type = entry.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "application_id": self.application_id,
            "total_events": len(self.provenance_trail),
            "event_breakdown": event_counts,
            "start_time": self.creation_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "decision_path": self.get_decision_path(),
            "trail_hash": self._compute_trail_hash()
        }

    def export_to_json(self) -> str:
        """Export complete provenance record as JSON"""
        record = self.get_provenance_record()
        return json.dumps(record, indent=2, default=str)

    def export_to_audit_report(self) -> str:
        """Export as human-readable audit report"""
        report = f"""
DECISION PROVENANCE AUDIT REPORT
================================

Application ID: {self.application_id}
Created: {self.creation_time}
Report Generated: {datetime.now()}

METADATA
--------
Application Version: {self.metadata.get('application_version')}
Rules Version: {self.metadata.get('rules_version')}
Trail Hash: {self._compute_trail_hash()}

DECISION TRAIL ({len(self.provenance_trail)} events)
----------------
"""
        for i, entry in enumerate(self.provenance_trail):
            report += f"\n{i+1}. [{entry.event_type.upper()}] {entry.timestamp}\n"
            for key, value in entry.details.items():
                report += f"   {key}: {value}\n"

        report += f"""
SUMMARY
-------
{self._format_summary()}

VERIFICATION
------------
Trail Hash: {self._compute_trail_hash()}
To verify integrity, compute SHA256 hash of all entries in sequence order.
If hash matches above, trail has not been tampered with.
"""
        return report

    def _format_summary(self) -> str:
        """Format summary statistics"""
        summary = self.audit_trail_summary()
        text = f"Total Events: {summary['total_counts']}\n"
        for event_type, count in summary['event_breakdown'].items():
            text += f"  {event_type}: {count}\n"
        return text
