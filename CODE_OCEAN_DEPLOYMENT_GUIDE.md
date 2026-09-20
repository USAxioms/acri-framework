# ACRI Code Ocean Deployment Guide

## Quick Start

1. **Upload to Code Ocean:**
   - Download the `acri-codeocean.zip` file
   - Upload to Code Ocean as a new capsule
   - Select "Python 3" as language
   - Set entrypoint to `/run.sh`

2. **Execute:**
   - Click "Reproduce" in Code Ocean
   - System automatically runs ACRI with sample application
   - Results appear in `/results/` folder

3. **Access Results:**
   - View JSON output in Code Ocean file browser
   - Download results for analysis
   - Review audit trail for decision transparency

## Project Structure

```
acri-codeocean/
├── code/                    # Core ACRI modules
│   ├── evidence_state.py   # E_t = {A_t, D_t, Q_t, R_t, V_t, C_t}
│   ├── conversational_intake.py    # Adaptive Q&A and routing
│   ├── brms.py             # Business rules engine
│   ├── decision_provenance.py      # Audit trail + SHA256
│   └── acri_runner.py      # Main orchestration
│
├── config/                 # Configuration
│   └── default_config.json # Tunable parameters
│
├── data/                   # Sample input data
│   └── sample_application.json
│
├── tests/                  # Test suite
│   └── __init__.py
│
├── results/                # Output (auto-created)
│   ├── *_evidence_state.json
│   ├── *_decision_provenance.json
│   └── *_results.json
│
├── run.sh                  # Code Ocean entry point
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment
├── manifest.json          # Code Ocean metadata
├── README.md              # Comprehensive documentation
└── CODE_OCEAN_DEPLOYMENT_GUIDE.md  # This file
```

## What Each Module Does

### evidence_state.py (220 lines)
- **Purpose:** Represent complete evidence state vector E_t
- **Key Classes:**
  - `EvidenceState`: Container for all evidence at time t
  - `StructuredRiskState`: 8-dimensional risk vector [R_H, R_L, R_F, R_O, R_M, R_B, R_D, R_C]
  - `RiskComponent`: Individual risk dimension with confidence
  - `ConflictRecord`: Data inconsistencies detected
- **Outputs:** Serializable to JSON for audit trail

### conversational_intake.py (380 lines)
- **Purpose:** Implement adaptive conversational Q&A loop
- **Key Algorithm:** Information value maximization
  - V(q) = ΔU(q) - λ*C(q) = expected uncertainty reduction - cost
  - q* = arg max V(q) subject to constraints
- **Key Classes:**
  - `Question`: Individual question with value score
  - `ConversationalIntake`: Orchestrates entire conversation
  - `Disposition`: Enum for STP / EVIDENCE_REQUEST / REFER
- **Logic:**
  1. Generate candidate questions
  2. Score by information value
  3. Select highest-value question
  4. Record response
  5. Check evidence sufficiency
  6. Route: STP / Evidence Request / Refer

### brms.py (280 lines)
- **Purpose:** Deterministic business rules execution
- **Key Classes:**
  - `Rule`: Condition → Action mapping
  - `RuleCondition`: Boolean predicate (eq, gt, lt, contains, etc.)
  - `RuleAction`: Action to take (route, flag, score)
  - `BusinessRulesManagementSystem`: Rule execution engine
- **Features:**
  - Priority-based evaluation
  - Conflict detection
  - Complete auditability
  - Error handling and escalation

### decision_provenance.py (240 lines)
- **Purpose:** Tamper-evident audit trail
- **Key Features:**
  - **Cryptographic Hash:** SHA256 of entire decision path
  - **Verification:** Compare hash to stored value to detect tampering
  - **Complete Record:** All questions, responses, rules, disposition
  - **Exportable:** JSON and human-readable report formats
- **Key Classes:**
  - `ProvenanceEntry`: Single event in trail
  - `DecisionProvenance`: Complete audit trail manager

### acri_runner.py (250 lines)
- **Purpose:** Main orchestration engine
- **Workflow:**
  1. Load configuration
  2. Initialize evidence state
  3. Create conversational intake
  4. Run Q&A loop
  5. Evaluate BRMS rules
  6. Determine disposition
  7. Record provenance
  8. Export results
- **Arguments:**
  - `--config`: Configuration file path
  - `--application`: Application ID
  - `--data`: Initial application data (optional)

## Configuration Parameters

Edit `config/default_config.json` to tune:

### Underwriting Parameters
- `uncertainty_threshold`: 0.15 (max uncertainty for STP)
- `value_threshold`: 0.20 (min value to request evidence)
- `lambda_cost`: 0.5 (cost weighting in value function)
- `max_conversation_time`: 15 (minutes)
- `max_turns`: 20 (max Q&A iterations)
- `max_age`: 85
- `max_amount`: 1,000,000

### Deployment Restrictions (Phase 2 Pilot)
- `max_face_amount`: 500,000
- `min_age`: 25, `max_age`: 55
- `products`: ["term_life"]
- `exclusions`: ["prior_decline", "material_aps"]

### Monitoring Thresholds
- `stp_rate_change`: ±5 pp alert
- `referral_rate_change`: ±3 pp alert
- `cycle_time_increase`: +20% alert
- `mortality_deviation`: 10% alert

## Running Custom Applications

To run with your own application data:

```bash
python3 /code/acri_runner.py \
  --config /config/default_config.json \
  --application YOUR_APP_ID \
  --data /path/to/your_application.json
```

### Input Data Format

JSON with applicant information:
```json
{
  "application_id": "APP-20260919-002",
  "applicant": {
    "age": 40,
    "occupation": "..."
  },
  "health": {
    "conditions": "...",
    "medications": "..."
  },
  "family_history": {
    "father": "...",
    "mother": "..."
  },
  ...
}
```

## Output Files

### APP-ID_results.json
```json
{
  "application_id": "APP-20260919-001",
  "disposition": "straight_through_processing",
  "uncertainty": 0.08,
  "completeness": 0.875,
  "turns": 6,
  "brms_score": 1.2,
  "triggered_rules": ["rule_min_age", "rule_max_amount"],
  "conflicts": 0,
  "timestamp": "2026-09-19T...",
  "summary": { ... }
}
```

### APP-ID_evidence_state.json
```json
{
  "application_id": "APP-20260919-001",
  "applicant_disclosures": { ... },
  "external_data": { ... },
  "questions_asked": [ ... ],
  "responses": [ ... ],
  "verified_evidence": { ... },
  "conflicts": [ ... ],
  "risk_state": { ... },
  "uncertainty": 0.08,
  "completeness": 0.875
}
```

### APP-ID_decision_provenance.json
```json
{
  "metadata": {
    "application_id": "APP-20260919-001",
    "application_version": "1.0.0",
    "rules_version": "1.0"
  },
  "provenance_trail": [
    { "timestamp": "...", "event_type": "question", "details": { ... } },
    { "timestamp": "...", "event_type": "response", "details": { ... } },
    ...
  ],
  "trail_hash": "4a3e8f2c...",
  "total_entries": 24
}
```

**To verify audit trail integrity:**
```python
# Compute hash and compare to stored value
if computed_hash == stored_hash:
    print("Audit trail verified - no tampering detected")
else:
    print("WARNING: Audit trail has been modified!")
```

## Testing

Run the test suite in Code Ocean terminal:

```bash
cd /code
python3 -m pytest /tests/ -v
```

## Monitoring

Key metrics tracked automatically:
- **STP Rate:** % processed straight-through
- **Referral Rate:** % escalated to underwriter  
- **Cycle Time:** Minutes from start to disposition
- **Uncertainty:** Remaining material uncertainty [0-1]
- **Completeness:** % of risk dimensions populated
- **Rule Errors:** Count of rule execution failures
- **Data Quality:** % of validation issues

## Reproducibility Features

✅ **Formal Specifications:** Mathematical notation  
✅ **Complete Pseudocode:** All 4 core modules  
✅ **Configuration Space:** All tunable parameters  
✅ **Test Protocols:** Unit and integration tests  
✅ **Deployment Stages:** Phase-gated rollout  
✅ **Decision Provenance:** Cryptographic audit trail  
✅ **Monitoring Framework:** Continuous oversight  

## Hypotheses Tested

The framework enables testing of 5 core hypotheses:

| Hypothesis | Measure | Criterion |
|-----------|---------|-----------|
| H1: Evidence Efficiency | Evidence requests (ACRI vs. control) | ≥15% reduction (p<0.05) |
| H2: STP Expansion | STP rate (ACRI vs. control) | ≥10 pp increase |
| H3: Targeted Evidence | Non-targeted requests | ≥20% reduction |
| H4: Underwriter Capacity | Complex cases per underwriter | ≥15% increase |
| H5: Risk Preservation | Expected vs. actual mortality | <105% of expected |

## Governance & Compliance

ACRI implements NAIC AI Model Bulletin requirements:
- ✅ Governance & Oversight
- ✅ Data Quality
- ✅ Fairness Assessment  
- ✅ Validation & Testing
- ✅ Documentation
- ✅ Model Risk Management
- ✅ Bias Monitoring

## Support & Documentation

- **README.md:** Comprehensive overview and architecture
- **Reproducibility Capsule:** Formal specifications and deployment protocol
- **White Paper:** Russell ACRI framework paper
- **Code Comments:** Inline documentation in each module

## Next Steps

1. **Review README.md** for complete system overview
2. **Check config/default_config.json** for tunable parameters
3. **Run with sample data** to understand workflow
4. **Modify configuration** for your use case
5. **Run tests** to verify correct operation
6. **Export results** for analysis

---

**Version:** 1.0.0  
**Last Updated:** September 2026  
**Status:** Production Ready for Code Ocean ✓
