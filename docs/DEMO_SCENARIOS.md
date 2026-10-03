# FraudShield AI — Deterministic Demo Scenarios Guide

This guide details the 8 deterministic operational demo scenarios packaged in `backend/scripts/demo_scenarios.py`.

---

## Running the Demo Suite

Execute the scenario runner directly:
```bash
python backend/scripts/demo_scenarios.py
```

---

## 8 Deterministic Operational Scenarios

### Scenario 1: Benign Domestic In-Store Transaction
- **Context**: Normal grocery transaction in user's home city with trusted device.
- **Expected Outcome**: Risk score < 25 / 100, $P(\text{Fraud}) < 0.01$, no alert triggered.

### Scenario 2: High-Value Offshore Wire Transfer Anomaly
- **Context**: International wire transfer for $34,850 USD from an unrecognized device.
- **Expected Outcome**: Risk score > 70 / 100, $P(\text{Fraud}) > 0.90$, Anomaly score > 0.55.

### Scenario 3: Real-Time Fraud Alert Generation & Severity Routing
- **Context**: High-risk transaction triggers alert engine.
- **Expected Outcome**: High-severity Alert emitted, broadcast over WebSocket to active analysts.

### Scenario 4: Risk Manager Telemetry & Sensitivity Governance
- **Context**: Risk Manager inspects portfolio metrics and fraud rates.
- **Expected Outcome**: Live metric aggregates computed from real database records (0 fabricated mock numbers).

### Scenario 5: Fraud Analyst Case Lifecycle Initiation
- **Context**: Fraud Analyst claims alert into an active investigation case.
- **Expected Outcome**: Case created in `IN_REVIEW` status with optimistic concurrency lock (Version = 2).

### Scenario 6: Evidence Documentation & SHAP Attribution
- **Context**: Analyst logs feature attributions and investigation findings.
- **Expected Outcome**: Note persisted and linked to case; audit event `INVESTIGATION_NOTE_ADDED` emitted.

### Scenario 7: Case Resolution & Concurrency-Safe Finalization
- **Context**: Analyst confirms unauthorized account takeover and resolves case.
- **Expected Outcome**: Case status shifts to `RESOLVED` with disposition `CONFIRMED_FRAUD`.

### Scenario 8: Immutable Compliance Audit Trail & Tracing
- **Context**: Administrator inspects tenant audit trail.
- **Expected Outcome**: Complete chronological record with `X-Request-ID` correlation and zero leaked credentials.
