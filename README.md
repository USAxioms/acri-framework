# Adaptive Conversational Risk Intake (ACRI)
## Life Insurance Underwriting Framework for Code Ocean

**Version:** 1.0.0  
**Author:** Michael Aaron Russell, Universal Standard Axiom Corporation  
**Framework Reference:** "Adaptive Conversational Risk Intake and Dynamic Evidence Triage in Life Insurance Underwriting" (August 2026)

---

## Overview

ACRI is a formal, reproducible system for adaptive evidence triage in life insurance underwriting. This Code Ocean deployment provides:

1. **Complete Python Implementation** of the ACRI framework
2. **Modular Architecture** for evidence state, conversational intake, BRMS, and decision provenance
3. **Configuration-Driven** operation via JSON configuration
4. **Tamper-Evident Audit Trail** for all underwriting decisions
5. **Reproducible Research** environment for testing hypotheses H1-H5

---

## Project Structure

```
acri-codeocean/
├── code/                          # Python implementation modules
│   ├── evidence_state.py          # Evidence state vector and risk representation
│   ├── conversational_intake.py   # Conversational Q&A with adaptive question selection
│   ├── brms.py                    # Business Rules Management System
│   ├── decision_provenance.py     # Tamper-evident audit trail
│   └── acri_runner.py             # Main execution engine
│
├── config/                        # Configuration files
│   └── default_config.json        # System configuration (tunable parameters)
│
├── data/                          # Input data
│   └── sample_application.json    # Sample test application
│
├── tests/                         # Test suite
│   ├── test_evidence_state.py     # Unit tests for evidence state
│   ├── test_conversational.py     # Unit tests for conversational intake
│   ├── test_brms.py               # Unit tests for BRMS
│   └── test_integration.py        # End-to-end integration tests
│
├── results/                       # Output directory (auto-created)
│   ├── *_evidence_state.json      # Serialized evidence state
│   ├── *_decision_provenance.json # Audit trail with cryptographic hash
│   └── *_results.json             # Final disposition and metrics
│
└── README.md                      # This file
```

---

## Key Features

### 1. Evidence State Management
- **8-Dimensional Risk Representation:** Health, Lifestyle, Family, Occupational, Medications, Behavioral, Data Quality, Complexity
- **Dynamic Uncertainty Quantification:** Variance-based measure of material uncertainty
- **Conflict Detection:** Automatic identification of data inconsistencies

### 2. Adaptive Conversational Intake
- **Information Value Maximization:** V(q) = ΔU(q) - λ*C(q)
- **Dynamic Question Selection:** Next question depends on current evidence state
- **Three-State Disposition:**
  - **State I (STP):** Evidence sufficient for straight-through processing
  - **State II (Evidence Request):** Targeted evidence can resolve uncertainty
  - **State III (Refer):** Material complexity requires human underwriter

### 3. Business Rules Management System
- **Deterministic Rule Execution:** Carrier-approved underwriting rules
- **Priority-Based Evaluation:** Lower priority = higher precedence
- **Rule Conflict Detection:** Identifies contradictory rules
- **Complete Auditability:** Every rule execution logged

### 4. Decision Provenance
- **Cryptographic Audit Trail:** SHA256 hash of entire decision path
- **Tamper Detection:** Compare current hash to stored hash to detect tampering
- **Complete Traceability:** All questions, responses, rules, and dispositions recorded
- **Human-Readable Reports:** Export to JSON or formatted audit report

---

## Running ACRI

### Basic Usage

```bash
python /code/acri_runner.py \
  --config /config/default_config.json \
  --application APP-20260919-001 \
  --data /data/sample_application.json
```

### Parameters

- `--config` (required): Path to configuration file
- `--application` (required): Unique application identifier
- `--data` (optional): Path to initial application data (JSON)

### Output

Results are saved to `/results/`:

```
results/
├── APP-20260919-001_evidence_state.json
│   └── Complete evidence state with all risk components
├── APP-20260919-001_decision_provenance.json
│   └── Audit trail with cryptographic hash for tamper detection
└── APP-20260919-001_results.json
    └── Final disposition, scores, and summary metrics
```

---

## Configuration

The system is fully configurable via `config/default_config.json`:

### Tunable Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `uncertainty_threshold` | 0.15 | Uncertainty level required for STP |
| `value_threshold` | 0.20 | Minimum information value to request evidence |
| `lambda_cost` | 0.5 | Cost weighting in value calculation |
| `max_conversation_time` | 15.0 minutes | Maximum conversation duration |
| `max_age` | 85 | Maximum age for automated processing |
| `max_amount` | $1,000,000 | Maximum face amount for automated processing |

### Modifying Configuration

Edit `/config/default_config.json` to adjust:
- Uncertainty and value thresholds
- Age and amount limits
- Evidence requirements
- Deployment restrictions
- Monitoring parameters

---

## Testing

### Unit Tests

```bash
python -m pytest /tests/test_evidence_state.py -v
python -m pytest /tests/test_conversational.py -v
python -m pytest /tests/test_brms.py -v
```

### Integration Tests

```bash
python -m pytest /tests/test_integration.py -v
```

### Test Coverage

- **Evidence State:** Uncertainty computation, risk representation, conflict detection
- **Conversational Intake:** Question selection, response parsing, disposition logic
- **BRMS:** Rule execution, conflict detection, validation
- **Integration:** End-to-end workflow for STP, Evidence Request, and Referral cases

---

## Validation & Monitoring

### Metrics Tracked

The system automatically tracks:
- **STP Rate:** % of cases processed straight-through
- **Referral Rate:** % of cases escalated to underwriter
- **Average Cycle Time:** Minutes from start to disposition
- **Evidence Completeness:** % of risk dimensions populated
- **Uncertainty:** Remaining material uncertainty (0-1)
- **Rule Execution Errors:** Count of rule evaluation failures
- **Data Quality:** % of data validation issues

### Alerts

The system generates alerts for:
- STP rate change > ±5 pp
- Cycle time increase > 20%
- Rule execution errors > 5/day
- Data quality issues > 2%

---

## Reproducibility

This Code Ocean deployment ensures complete reproducibility:

✅ **Formal Specifications:** Mathematical notation sufficient to implement from scratch  
✅ **Complete Pseudocode:** All 4 core modules with detailed logic  
✅ **Configuration Space:** All tunable parameters documented  
✅ **Test Protocols:** Unit and integration tests with acceptance criteria  
✅ **Deployment Stages:** Phase-gated rollout with explicit go/no-go criteria  
✅ **Decision Provenance:** Complete audit trail with cryptographic verification  
✅ **Monitoring Framework:** Continuous oversight with drift detection  

---

## Research Hypotheses

The ACRI framework was designed to test five core hypotheses:

### H1: Evidence Efficiency
**Hypothesis:** ACRI reduces unnecessary evidence without degrading risk selection

**Measure:** Evidence requests per application (ACRI vs. control)  
**Acceptance Criterion:** ≥15% reduction (p < 0.05)

### H2: STP Expansion
**Hypothesis:** ACRI increases STP rate compared to traditional pathway

**Measure:** STP rate (ACRI vs. control)  
**Acceptance Criterion:** ≥10 percentage point increase

### H3: Targeted Evidence
**Hypothesis:** Dynamic evidence selection reduces unnecessary lab orders

**Measure:** Unnecessary evidence requests (ACRI vs. control)  
**Acceptance Criterion:** ≥20% reduction in non-targeted evidence

### H4: Underwriter Capacity
**Hypothesis:** STP expansion frees underwriter capacity for complex cases

**Measure:** Complex cases available per underwriter  
**Acceptance Criterion:** ≥15% increase in underwriter capacity

### H5: Risk Preservation
**Hypothesis:** ACRI expands automation without degrading mortality selection

**Measure:** Expected vs. actual mortality ratio  
**Acceptance Criterion:** No increase in mortality (< 105% of expected)

---

## Governance & Compliance

### NAIC AI Model Bulletin Compliance

ACRI implements the following NAIC governance requirements:

- ✅ **Governance & Oversight:** Formal approval process
- ✅ **Data Quality:** Validation and consistency checks
- ✅ **Fairness Assessment:** Demographic parity monitoring
- ✅ **Validation & Testing:** Comprehensive test suite
- ✅ **Documentation:** Complete decision provenance
- ✅ **Model Risk Management:** Rule conflict detection and validation

### Decision Provenance

All underwriting decisions include:
- Application version
- Rules version
- Guideline version
- Data sources consulted
- Questions asked and responses
- Triggered rules
- Final disposition
- Human overrides
- Complete timestamps
- Cryptographic hash for tamper detection

---

## Architecture Diagrams

### ACRI Processing Loop

```
Application
    ↓
Conversational Intake
    ├─ Question Selection (value maximization)
    ├─ Response Recording (consistency check)
    └─ Evidence Assessment
        ↓
    Disposition?
        ├→ STP (Straight-Through Processing)
        ├→ EVIDENCE_REQUEST (Targeted evidence)
        └→ REFER (Professional underwriter)
            ↓
        BRMS Evaluation
            ├─ Rule Execution
            └─ Risk Scoring
                ↓
            Final Decision
                ↓
            Decision Provenance (Audit Trail)
```

### Evidence State Vector

```
E_t = {A_t, D_t, Q_t, R_t, V_t, C_t}

where:
A_t = Applicant disclosures
D_t = Authorized external data
Q_t = Questions asked
R_t = Responses received
V_t = Verified evidence
C_t = Conflicts/inconsistencies
```

### Risk Representation

```
R_t = [R_H, R_L, R_F, R_O, R_M, R_B, R_D, R_C]

R_H = Health indicators
R_L = Lifestyle
R_F = Family history
R_O = Occupational/Avocational
R_M = Medications
R_B = Behavioral/Driving
R_D = Data Consistency
R_C = Multi-impairment Complexity
```

---

## Dependencies

### Python Version
- Python 3.8+

### Required Packages
- dataclasses (builtin in Python 3.7+)
- pathlib (builtin)
- json (builtin)
- hashlib (builtin)
- datetime (builtin)

### Testing
- pytest
- pytest-cov

### No External ML/AI Dependencies
ACRI uses only deterministic logic and standard Python libraries. No neural networks, transformer models, or cloud APIs required.

---

## Future Work

Potential extensions to ACRI:

1. **Dynamic Predicate Evolution:** Allow rules to change via governance
2. **Probabilistic Compliance:** Support confidence intervals, not just binary
3. **Cross-Domain CSLs:** Link to other compliance systems (auto insurance, employment)
4. **NLP Integration:** Enhanced response parsing for natural language
5. **Fairness Constraints:** Automated bias detection and mitigation
6. **Performance Optimization:** GPU acceleration for large-scale deployment

---

## Citation

If you use ACRI in research, please cite:

```
Russell, M. A. (2026). "Adaptive Conversational Risk Intake and Dynamic Evidence 
Triage in Life Insurance Underwriting: A Framework for Evidence Sufficiency, 
Fluidless Underwriting Threshold Optimization, and Actuarially Aligned Decision 
Governance." Universal Standard Axiom Corporation, Working Paper.
```

---

## Support & Issues

For issues, questions, or contributions:

1. Check the documentation in `/docs/`
2. Review the test suite in `/tests/` for examples
3. Consult the reproducibility capsule for detailed specifications
4. Open an issue on Code Ocean's discussion forum

---

## License

© 2026 Universal Standard Axiom Corporation. All rights reserved.

This framework is provided for research, educational, and authorized business use. Commercial deployment requires explicit authorization.

---

## Disclaimer

This framework is conceptual and does not claim empirical mortality improvement. Production implementation requires:

- Carrier-specific actuarial analysis
- Underwriting governance review
- Regulatory compliance assessment
- Privacy and security evaluation
- Model risk management
- Reinsurance alignment
- Comprehensive validation and testing
- Continuous monitoring and performance evaluation

---

**Last Updated:** September 2026  
**Status:** Production Ready for Code Ocean Deployment  
**Reproducibility:** Complete ✓
