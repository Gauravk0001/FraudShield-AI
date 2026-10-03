# FraudShield AI — PaySim Model Card

## 1. Model Details
- **Model Name:** FraudShield PaySim Calibrated Classifier
- **Model Type:** Extreme Gradient Boosting (`XGBClassifier`) with Platt Sigmoid Probability Calibration (`CalibratedClassifierCV`)
- **Version:** `paysim-v1-no_balance` (Defensible Baseline) / `paysim-v1-with_balance` (Exploratory Prototype)
- **Artifact Location:** `backend/models_artifacts/paysim/`
- **Developer:** FraudShield AI Engineering & Research Team
- **Intended Use:** Pre-production decision-support assistance for fraud analysts. **NOT for autonomous account freezes or irreversible customer actions.**

---

## 2. Intended Use & Safety Boundary

### In-Scope
- Scoring incoming financial transactions in real-time.
- Triaging suspicious events into three advisory recommendation tiers:
  - `APPROVE`
  - `STEP_UP` (Prompt multi-factor authentication or verification)
  - `HOLD_FOR_REVIEW` (Temporarily hold funds pending human analyst triage)
- Providing explainable top factors (SHAP values & reason codes) to assist analyst investigations.

### Out-of-Scope & Prohibited Uses
- **Autonomous Permanent Declines:** The model must not autonomously issue final declines or freezes without explicit, authorized business rule logic.
- **Credit Underwriting or Scoring:** This model is strictly an event-level anomaly and fraud detector; it must not be used for customer creditworthiness decisions.
- **Unverified Production Deployment:** Models trained with balance-derived shortcuts must not be marketed or deployed as production-ready.

---

## 3. Data & Training Regime

### Source Dataset
- **Dataset:** PaySim Synthetic Financial Mobile Money Dataset (`PS_20174392719_1491204439457_Log.csv`)
- **Synthetic Origin Notice:** PaySim is an agent-based simulation created in 2017. Real-world fraud patterns, mule networks, and money laundering schemes exhibit distinct structural behaviors not captured in synthetic data.

### Chronological Splitting Policy
PaySim steps represent simulated hourly time progression from step 1 to 744 (31 days). Random splitting was strictly avoided to prevent temporal leakage:
- **Training Split (Steps 1 to 521, First 70%):** 17,388 samples (1.05% fraud prevalence)
- **Validation Split (Steps 522 to 632, Next 15%):** 3,851 samples (1.35% fraud prevalence)
- **Locked Test Split (Steps 633 to 743, Final 15%):** 3,761 samples (0.98% fraud prevalence)

### Feature Architecture (16 Features - Defensible Baseline)
1. `amount`: Transaction monetary amount
2. `log_amount`: Scale-normalized `log1p(amount)`
3. `type_encoded`: Ordinal encoding of transaction method
4. `step_hour_of_day`: Simulated 24-hour cycle
5. `step_day_of_week`: Simulated 7-day weekly cycle
6. `velocity_origin_1h`: Origin transaction count in strictly prior 1 step
7. `velocity_origin_6h`: Origin transaction count in strictly prior 6 steps
8. `velocity_origin_24h`: Origin transaction count in strictly prior 24 steps
9. `total_amount_origin_1h`: Origin transaction amount sum in strictly prior 1 step
10. `total_amount_origin_6h`: Origin transaction amount sum in strictly prior 6 steps
11. `total_amount_origin_24h`: Origin transaction amount sum in strictly prior 24 steps
12. `historical_avg_amount_origin`: Running historical average transaction amount
13. `amount_deviation_ratio`: Ratio of current amount to historical average
14. `is_first_time_destination`: Novelty indicator for origin-destination pair
15. `dest_prior_inbound_count`: Prior inbound transfers received by destination
16. `is_dest_customer_p2p`: Destination account type (Customer P2P vs. Merchant)

---

## 4. Evaluation Metrics (Actual Execution on Locked Test Split)

| Metric | Result | Benchmark Context |
|---|---|---|
| **ROC-AUC** | **0.8063** | Strong discriminative ability over class-imbalanced test split |
| **PR-AUC** | **0.0319** | Evaluated at 0.98% fraud prevalence |
| **Recall @ 1.0% FPR** | **5.41%** | Fixed enterprise false alarm constraint |
| **Brier Calibration Score** | **0.0097** | Well-calibrated probabilities via Platt Sigmoid scaling |
| **Inference Latency (p50)** | **11.71 ms** | Fast real-time evaluation |
| **Inference Latency (p95)** | **13.87 ms** | Suitable for sub-50ms SLA |
| **Inference Latency (p99)** | **17.54 ms** | Predictable tail latency |

---

## 5. Balance Shortcut Disclosure & Ethical Considerations

> [!CAUTION]
> In PaySim, simulated fraud agents frequently drain the origin account balance entirely (`newbalanceOrig == 0`). Including balance discrepancy variables enables tree-based models to achieve near-perfect synthetic accuracy on PaySim by memorizing this arithmetic artifact.
> In real production banking, ledger postings are asynchronous, pending transactions create hold amounts, and credit lines mean balance subtraction arithmetic does not reliably detect fraud.
> Models utilizing balance features are exploratory prototypes only. The model card reflects the **Defensible Baseline** (`--no-balance`), ensuring honest reporting.

---

## 6. Model Governance & Artifact Verification

All production-bound artifacts are signed with SHA-256 hashes stored in `artifact_hashes.json`. Any divergence in hashes or feature schemas triggers automatic rollback and halts service loading.
