"""
Adaptive Conversational Risk Intake (ACRI)
Main Runner Script
Michael Aaron Russell, Universal Standard Axiom Corporation

Usage:
    python acri_runner.py --config config.json --application test_app_001
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from evidence_state import EvidenceState, StructuredRiskState, RiskComponent, DataConsistency
from conversational_intake import ConversationalIntake, Disposition, Question
from brms import BusinessRulesManagementSystem, Rule, RuleCondition, RuleAction
from decision_provenance import DecisionProvenance


class ACRIRunner:
    """Main ACRI execution engine"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.brms = BusinessRulesManagementSystem()
        self.decision_provenance = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file: {config_path}")
            sys.exit(1)

    def initialize_brms(self) -> None:
        """Initialize BRMS with rules from config"""
        # Add standard rules
        self.brms.add_rule(
            Rule(
                rule_id="rule_min_age",
                priority=1,
                conditions=[],
                action=RuleAction(action_type="check", target="age", value=18),
                description="Minimum age 18"
            )
        )

        self.brms.add_rule(
            Rule(
                rule_id="rule_max_amount",
                priority=2,
                conditions=[],
                action=RuleAction(action_type="check", target="amount", 
                                 value=self.config.get("max_amount", 1000000)),
                description="Maximum face amount check"
            )
        )

    def run_underwriting(self, application_id: str, initial_data: dict = None) -> dict:
        """
        Run complete underwriting workflow
        
        Args:
            application_id: Unique application identifier
            initial_data: Initial applicant information
            
        Returns:
            Underwriting result with disposition
        """
        print(f"\n{'='*60}")
        print(f"ACRI Underwriting Run: {application_id}")
        print(f"Started: {datetime.now()}")
        print(f"{'='*60}\n")

        # Create evidence state
        evidence_state = EvidenceState(
            application_id=application_id,
            timestamp=datetime.now(),
            uncertainty_threshold=self.config.get("uncertainty_threshold", 0.15)
        )

        # Add initial data if provided
        if initial_data:
            for field, value in initial_data.items():
                evidence_state.add_disclosure(field, str(value))

        # Create conversational intake system
        intake = ConversationalIntake(
            applicant_id=application_id,
            evidence_state=evidence_state,
            lambda_cost=self.config.get("lambda_cost", 0.5),
            max_conversation_time=self.config.get("max_conversation_time", 15.0),
            uncertainty_threshold=self.config.get("uncertainty_threshold", 0.15),
            value_threshold=self.config.get("value_threshold", 0.20)
        )

        # Initialize question library
        intake.initialize_question_library()

        # Create decision provenance tracker
        self.decision_provenance = DecisionProvenance(application_id)
        self.decision_provenance.record_application_start(
            application_version="1.0",
            rules_version=self.brms.rules_version
        )

        # Conversational loop
        print("Starting conversational intake...\n")

        while intake.conversation_turns < self.config.get("max_turns", 20):
            # Get next question
            question = intake.get_next_question()

            if question is None:
                print("No more questions to ask.")
                break

            # Display question
            print(f"Q{intake.conversation_turns + 1}: {question.text}")
            print(f"   [Category: {question.category}, Value Score: {question.compute_value(intake.lambda_cost):.3f}]")

            # Record question
            self.decision_provenance.record_question(
                question.question_id,
                question.text,
                question.category
            )

            # Simulate response (in production: get from UI)
            response = self._simulate_response(question)
            print(f"Response: {response}\n")

            # Record response
            intake.record_response(question.question_id, response)
            self.decision_provenance.record_response(question.question_id, response)

            # Check evidence sufficiency
            disposition = intake.assess_evidence_sufficiency()

            if disposition == Disposition.STP:
                print(f"✓ Evidence sufficient for STP (Uncertainty: {evidence_state.uncertainty:.3f})")
                break
            elif disposition == Disposition.REFER:
                print(f"→ Material complexity detected, refer to underwriter")
                break

        # Run BRMS evaluation
        print(f"\n{'='*60}")
        print("BRMS Evaluation")
        print(f"{'='*60}\n")

        brms_results = self.brms.evaluate(evidence_state)
        print(f"Rules evaluated: {len(self.brms.rules)}")
        print(f"Triggered rules: {len(brms_results['triggered_rules'])}")
        print(f"Risk score: {brms_results['score']:.2f}")

        # Assess final disposition
        print(f"\n{'='*60}")
        print("Final Assessment")
        print(f"{'='*60}\n")

        final_disposition = intake.assess_evidence_sufficiency()
        print(f"Final Disposition: {final_disposition.value}")
        print(f"Evidence Completeness: {evidence_state.evidence_completeness():.1%}")
        print(f"Remaining Uncertainty: {evidence_state.uncertainty:.3f}")
        print(f"Conversation Turns: {intake.conversation_turns}")

        # Record disposition
        self.decision_provenance.record_disposition(
            disposition=final_disposition.value,
            reasoning="Evidence sufficiency assessment complete",
            confidence=1.0 - evidence_state.uncertainty
        )

        # Generate results
        results = {
            "application_id": application_id,
            "disposition": final_disposition.value,
            "uncertainty": evidence_state.uncertainty,
            "completeness": evidence_state.evidence_completeness(),
            "turns": intake.conversation_turns,
            "brms_score": brms_results["score"],
            "triggered_rules": brms_results["triggered_rules"],
            "conflicts": len(evidence_state.conflicts),
            "timestamp": datetime.now().isoformat(),
            "summary": intake.get_conversation_summary()
        }

        # Save evidence state
        self._save_evidence_state(evidence_state)

        # Save decision provenance
        self._save_provenance(self.decision_provenance)

        # Save results
        self._save_results(results)

        print(f"\n{'='*60}")
        print("Underwriting Complete")
        print(f"Results saved to /results/")
        print(f"{'='*60}\n")

        return results

    def _simulate_response(self, question: Question) -> str:
        """Simulate applicant response"""
        # In production: get from conversational UI
        responses = {
            "q_health_conditions": "I have controlled hypertension, no other conditions",
            "q_medications": "Lisinopril 10mg daily for 3 years",
            "q_family_history": "No early deaths in family",
            "q_tobacco": "No, never used tobacco",
            "q_occupation": "Software engineer, sedentary work",
            "q_driving": "No violations or accidents"
        }
        return responses.get(question.question_id, "No response")

    def _save_evidence_state(self, evidence_state: EvidenceState) -> None:
        """Save evidence state to JSON"""
        output_dir = Path("/results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{evidence_state.application_id}_evidence_state.json"
        with open(output_file, 'w') as f:
            f.write(evidence_state.to_json())
        print(f"Evidence state saved: {output_file}")

    def _save_provenance(self, provenance: 'DecisionProvenance') -> None:
        """Save decision provenance to JSON"""
        output_dir = Path("/results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{provenance.application_id}_decision_provenance.json"
        with open(output_file, 'w') as f:
            json.dump(provenance.get_provenance_record(), f, indent=2, default=str)
        print(f"Decision provenance saved: {output_file}")

    def _save_results(self, results: dict) -> None:
        """Save final results to JSON"""
        output_dir = Path("/results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{results['application_id']}_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="ACRI Underwriting System"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--application",
        required=True,
        help="Application ID"
    )
    parser.add_argument(
        "--data",
        help="Path to initial application data (JSON)"
    )

    args = parser.parse_args()

    # Load initial data if provided
    initial_data = None
    if args.data:
        try:
            with open(args.data, 'r') as f:
                initial_data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Initial data file not found: {args.data}")

    # Run ACRI
    runner = ACRIRunner(args.config)
    runner.initialize_brms()
    results = runner.run_underwriting(args.application, initial_data)

    # Exit with appropriate code
    if results["disposition"] == "straight_through_processing":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
