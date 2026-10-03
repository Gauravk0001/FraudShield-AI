# FraudShield AI — Model Release, Threshold Governance & Rollback Process

## 1. Overview & Principles

Machine learning models deployed to FraudShield AI must adhere to governed release procedures to ensure stability, safety, explainability, and zero customer harm. 

Because FraudShield AI operates as an advisory **decision-support system**, releases must prioritize:
1. **Calibrated Probabilities:** Output probabilities must correspond to empirical fraud rates.
2. **Defensible Features:** Zero tolerance for synthetic shortcuts or unvalidated proxy variables.
3. **Reproducibility & Traceability:** Every release must be traceable to training commit hashes, dataset digests, and signed artifact hashes.
4. **Instant Rollback Capability:** Immediate fallback to verified prior artifact versions or deterministic rules.

---

## 2. Model Release Gate Checklist

Before promoting any model artifact to active serving:

- [ ] **Data Lineage:** Dataset split verified as chronological 70/15/15 step split.
- [ ] **Leakage Check:** Automated verification that `isFraud` and `isFlaggedFraud` are strictly excluded from feature schema.
- [ ] **Dual-Variant Check:** If balance features are included, the model is tagged as `EXPLORATORY_PROTOTYPE` and forbidden from production promotion.
- [ ] **Cryptographic Signing:** SHA-256 hashes generated for all `.joblib` and `.json` artifacts and written to `artifact_hashes.json`.
- [ ] **Validation Verification:** `python scripts/validate_model_artifacts.py` passes with zero errors.
- [ ] **Cost-Optimal Calibration:** Decision thresholds tuned on validation split minimizing expected loss.
- [ ] **Latency Benchmark:** Measured p95 inference latency is under 30ms.
- [ ] **Audit Entry:** Model version, feature count, and release approver recorded in `audit_logs`.

---

## 3. Operating Decision Threshold Governance

Operating thresholds for `APPROVE`, `STEP_UP`, and `HOLD_FOR_REVIEW` are calculated by minimizing expected business cost:

$$\text{Loss} = \sum_{\text{Hold}} \text{FALSE\_DECLINE\_COST} + \sum_{\text{Missed}} (\text{Amount} + \text{MISSED\_FRAUD\_FIXED\_COST})$$

### Default Threshold Guidelines
- **`STEP_UP`:** Probability $\ge 0.05$ (prompts MFA / secondary confirmation).
- **`HOLD_FOR_REVIEW`:** Probability $\ge 0.10$ (pauses funds, routes to analyst triage queue).
- **Authorized `BLOCK`:** Probability $\ge 0.95$ AND satisfied explicit business policy rule (e.g. sanctioned destination account or known compromised credential).

### Threshold Change Protocol
1. Threshold changes can only be enacted by users with the `ADMIN` or `RISK_MANAGER` role.
2. Every threshold adjustment triggers an immutable `AUDIT_LOG` entry documenting:
   - User ID and role of the modifier
   - Previous threshold values
   - New threshold values
   - Justification / incident ticket ID
3. Changes take effect dynamically without requiring server restart.

---

## 4. Rollback Procedure

If anomalous model behavior, concept drift, or inference degradation is detected in production:

### Automated Rollback
```bash
python scripts/validate_model_artifacts.py --rollback-from backend/models_artifacts/paysim_v0_stable
```

### Manual Rollback Steps
1. Navigate to `backend/models_artifacts/paysim/`.
2. Replace corrupt/degraded model artifacts with the designated stable version backup.
3. Validate signatures:
   ```bash
   python scripts/validate_model_artifacts.py
   ```
4. Trigger the reload endpoint or restart the backend service.
5. Inspect `/api/v1/metrics` to verify that `model_load_status` is `LOADED` and `degraded` is `false`.

---

## 5. Drift Monitoring & Incident Response

### Triggers for Retraining or Rollback
1. **Scoring Latency Drift:** p95 latency exceeds 50ms over a 15-minute sliding window.
2. **Alert Rate Spike:** Proportion of transactions flagged as `HOLD_FOR_REVIEW` deviates by more than $3\times$ from historical moving average.
3. **Degraded Response Trigger:** More than 5 requests in 60 seconds fall back to deterministic rules (`degraded: true`).
4. **Data Drift:** Kolomogorov-Smirnov (KS) test on incoming amount or velocity distributions indicates statistically significant divergence ($p < 0.01$).

### Incident Escalation
- **Level 1 (Degraded Fallback Active):** On-call ML engineer notified. System continues safe deterministic rule scoring.
- **Level 2 (High False Alarm Rate):** Risk Operations Manager adjusts `HOLD_FOR_REVIEW` threshold upward to mitigate analyst queue exhaustion while investigating root cause.
- **Level 3 (Model Corruption):** Execute immediate rollback to prior signed artifact version.
