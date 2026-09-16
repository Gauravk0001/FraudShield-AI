# FraudShield AI — HackIgnite ML Defense Guide (Evidence-Backed)
**Version:** v2.0-forensic-audit  
**Updated:** 2026-09-16 — All answers reference measured evidence

---

## Q1. Why should we trust your synthetic dataset?

**Honest answer:** You should treat it as a synthetic dataset — not a real-world dataset. Trust in the dataset comes from its construction methodology, not its scale.

**Evidence:**
- The dataset uses **causal temporal simulation**: every feature is derived only from transactions at `timestamp < current_timestamp`. No future information leaks backward. See `scripts/generate_forensic_dataset.py` and `test_causal_temporal_feature_boundaries` (PASSING).
- The fraud topology distribution (6 types, percentages validated) reflects real-world fraud literature. See `data/forensic_dataset_metadata.json` → `fraud_topologies_percentages`.
- Dataset SHA-256: `3674b803fe9d4a12...` — locked. See `data/forensic_dataset_metadata.json` → `sha256_hash`.
- 6/6 forensic integrity checks pass: row count, label counts, topologies, entity counts, date ordering. See `scripts/validate_dataset_integrity.py`.

**Honest limitation:** 17,123 transactions across 45 days and 600 customers is a controlled synthetic universe. It does not represent production-scale behavioral diversity, institutional geography, or real fraud ring coordination.

---

## Q2. What happens when customer behavior changes?

**Answer:** The system detects distributional shift via PSI/KS drift monitoring, then requires human decision before any model update.

**Evidence:**
- `backend/app/services/drift_service.py` — `DriftMonitor` class computes PSI and KS per feature on each evaluation window.
- Three governance tiers: `LOW_DRIFT` (PSI<0.10, KS<0.05), `MODERATE_DRIFT` (PSI 0.10-0.25), `HIGH_DRIFT` (PSI≥0.25 OR KS≥0.10).
- Domain B stress test simulated customer velocity shift 3.5×: PSI triggered HIGH_DRIFT. Model F1 dropped from 0.9154 to 0.6196.
- **No automatic retraining** — governance alert triggers human review.

**Honest limitation:** Drift detection does NOT automatically prove model degradation. PSI/KS measure feature distribution shift, not model performance shift. A shift in legitimate customer behavior (e.g. holiday spending surge) could trigger HIGH_DRIFT without model accuracy degrading.

---

## Q3. What happens when fraud patterns change?

**Answer:** The system will degrade. This is a documented limitation.

**Evidence:**
- Domain C stress test: Cross-border wire fraud surge → PR-AUC drops to **0.2819** (from 0.9542 in standard distribution).
- Domain D stress test: Account takeover where 90% of transactions have new devices → F1 drops to **0.2112** because the `is_new_device` feature loses discriminative power.
- These degradations are measured, not assumed. See `docs/DOMAIN_GENERALIZATION_REPORT.md` and `docs/domain_generalization_results.json`.

**What would help:** The behavioral rule engine provides some resilience (still catches velocity bursts), but when the fraud itself is slow and patient, supervised feature signals may not activate until calibration is updated on new labeled data.

---

## Q4. How do you detect distribution drift?

**Answer:** Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) test on each feature and on the prediction distribution.

**Evidence:**
```python
# backend/app/services/drift_service.py
dm = DriftMonitor(baseline_df=X_baseline, baseline_preds=preds_baseline)
result = dm.evaluate_feature_drift(current_df, current_preds)
# result["overall_status"] = "LOW_DRIFT" | "MODERATE_DRIFT" | "HIGH_DRIFT"
# result["feature_metrics"][feature]["psi"] — per-feature PSI
# result["feature_metrics"][feature]["ks_statistic"] — KS test statistic
# result["feature_metrics"][feature]["ks_pvalue"] — KS p-value
```
- **PSI formula:** PSI = Σ (actual_pct_i - expected_pct_i) × ln(actual_pct_i / expected_pct_i)
- Verified working against domain shift scenarios and edge cases (empty datasets, NaN inputs, constant features).

---

## Q5. Have you tested on external data?

**Honest answer:** **No.** All five domain evaluations are **synthetic distribution-shift stress tests**, not real external dataset evaluations.

**Evidence:**
- `docs/EXTERNAL_DATASET_AUDIT.md` — audited PaySim, Kaggle CC Fraud, IEEE-CIS, BAF for schema compatibility.
- **Finding:** Direct transfer evaluation is **scientifically invalid** for these datasets because:
  - PaySim: different feature schema (nameOrig, nameDest, oldbalanceOrg — not compatible with FraudShield features)
  - Kaggle CC Fraud: anonymized V1–V28 PCA features — no mapping to interpretable features
  - IEEE-CIS: has `card1-6`, `addr1-2`, `C1-14`, `D1-15` — mismatched semantics
  - BAF: realistic but features don't map to FraudShield's velocity/device schema
- **Domain E ("External Proxy")** simulates what happens if device/location telemetry features are unavailable — not a real external dataset evaluation.

**What was measured instead:** Synthetic covariate shift experiments showing performance under plausible distribution changes. These have scientific validity as robustness tests but cannot substitute for real-world evaluation.

---

## Q6. What happens if external performance drops?

**Answer:** It is expected to drop. The question is how much, and the system is designed to detect this.

**Evidence:**
- Domain shift stress test results:
  - Standard: F1=0.9154 (baseline behavior)
  - High Velocity: F1=0.6196 (-33% degradation)
  - Cross-Border Wire: F1=0.3964 (-57% degradation)
  - Account Takeover Mass: F1=0.2112 (-77% degradation)
  - Telemetry Masking: F1=0.7543 (-18% degradation)
- **Early Warning:** HIGH_DRIFT PSI fires when these covariate shifts occur, before manually inspecting prediction quality.
- **Recovery path:** Collect labeled examples from the new domain, retrain with balanced representation. The feature engineering pipeline is domain-agnostic.

---

## Q7. Why does the composite risk score differ from model probability?

**Answer:** They serve different purposes in different parts of the system.

**Evidence from `backend/app/services/risk_service.py` line 42:**
```python
raw_risk = (fraud_probability * 45.0) + (anomaly_score * 20.0) + (min(behavioral_boost, 1.0) * 35.0)
risk_score = round(float(min(100.0, max(0.0, raw_risk))), 2)
```

- `fraud_probability` ∈ [0.0, 1.0]: Calibrated XGBoost posterior probability of fraud. Used for automated binary routing decisions (threshold 0.35).
- `risk_score` ∈ [0.0, 100.0]: Operational triage score blending supervised ML (45%), unsupervised anomaly (20%), and deterministic behavioral rules (35%). Used for analyst queue routing, investigation priority, and alert tiering.

**Verified in forensic audit:** Sample transaction with fraud_prob=0.0015 produced risk_score=12.15 — different scale AND different composition confirmed.

**Why not just use probability?** A transaction with moderate ML probability (0.45) but extreme velocity burst (behavioral_score=0.90) should still trigger analyst review — this would score ~50/100 composite but only 0.45 probability. The composite captures operational context that the supervised model alone cannot.

---

## Q8. Why did you choose your calibration method?

**Honest answer:** Platt Sigmoid was chosen for architectural reasons, **not because it has the best calibration metrics**. Isotonic Regression is strictly better on both Brier Score and ECE on the validation set.

**Evidence (from `scripts/run_forensic_audit.py` — actual measured values):**

| Method | Brier | ECE | Log Loss |
|---|---|---|---|
| Uncalibrated | 0.0102 | 0.0168 | 0.0427 |
| **Platt Sigmoid (selected)** | **0.0088** | **0.0029** | **0.0371** |
| Isotonic Regression | 0.0077 | 0.0000 | 0.0277 |

**Selection rationale:** The composite risk engine requires continuous probability gradients across [0.0, 1.0] for smooth risk scoring. Isotonic Regression fits a piecewise monotonic step function that maps multiple raw probabilities to identical flat bins on sparse fraud tails (73 fraud events in 2,568-sample validation). Platt Sigmoid's smooth logistic transformation preserves fine-grained probability ordering.

**This is a documented engineering tradeoff.** See `docs/CALIBRATION_EVIDENCE.md` for full analysis.

---

## Q9. How stable is your model across seeds?

**Answer:** Very stable. F1 std=±0.0050 across 5 independently-trained models.

**Evidence (from actual code execution — results reproduced in forensic audit):**

| Seed | Training Data Hash | F1 | PR-AUC | ROC-AUC |
|---|---|---|---|---|
| 42 | `2550db8f0c37...` | 0.8791 | 0.9255 | 0.9929 |
| 123 | `2edbce5c42a9...` | 0.8928 | 0.9382 | 0.9937 |
| 2024 | `ffe516e00de0...` | 0.8889 | 0.9343 | 0.9940 |
| 2025 | `927cd169e964...` | 0.8817 | 0.9294 | 0.9938 |
| 777 | `4242e5a78423...` | 0.8836 | 0.9344 | 0.9932 |
| **Mean** | — | **0.8852** | **0.9324** | **0.9935** |
| **Std** | — | **±0.0050** | **±0.0044** | **±0.0004** |

- Each seed generates an independent dataset (unique training data hash per seed — all different).
- All seeds evaluate on the **same fixed test set** (SHA-256: `985e08d2...`).
- Coefficient of Variation for F1 = 0.56%. ROC-AUC CV = 0.04%.

---

## Q10. How do you know features don't leak future information?

**Answer:** By construction and by automated test.

**Evidence:**

**By construction** (`scripts/generate_forensic_dataset.py`):
```python
# For each transaction at timestamp T:
past_txns = [t for t in customer_history if t["timestamp"] < current_timestamp]
velocity_1h = count(past_txns where timestamp >= T - 1h and timestamp < T)
avg_amount_30d = mean([t.amount for t in past_txns where timestamp >= T - 30d])
is_new_device = 1 if device not in {t.device for t in past_txns} else 0
```
All features use `< current_timestamp` strict inequality.

**By automated test** (PASSING in 34/34 suite):
- `test_causal_temporal_feature_boundaries` — verifies velocity features are 0 for first transaction
- `test_future_leakage_invariance` — verifies shuffling timestamp order changes features
- `test_no_target_correlation_leakage` — verifies no feature is a near-perfect proxy for the label
- `test_customer_grouped_split_zero_leakage` — verifies no customer appears in both train and test when grouped

---

## Q11. How do you validate counterfactual behavior?

**Answer:** Through 8 controlled perturbation experiments with full SHAP decomposition.

**Evidence (from forensic audit — actual execution):**

The model shows expected monotonic behavior only for the most significant signals:

| Perturbation | Prob Change | Risk Change | Classification |
|---|---|---|---|
| Wire → Card Present | -0.9494 | -42.85 | EXPECTED (strong monotonic) |
| Fully Benign | -0.9498 | -80.95 | EXPECTED (strong monotonic) |
| Amount $14k→$45 | +0.0178 | -0.89 | NONLINEAR_EXPLAINABLE |
| Velocity 5→0 | +0.0230 | +0.28 | NONLINEAR_EXPLAINABLE |

**Why do some single-feature reductions increase probability?**

XGBoost uses orthogonal decision tree paths. A transaction with 6 simultaneous high-risk indicators (wire transfer + 3am + new device + new merchant + foreign location + high velocity) will remain at high fraud probability even when one signal is normalized, because the other 5 signals activate independent tree paths.

This is not a bug. Only when ALL signals are simultaneously benign does the fraud probability collapse to 0.0014 (Perturbation H).

---

## Q12. What is your biggest known limitation?

**Answer:** The system was trained and evaluated on synthetic data. Real-world performance is unknown and cannot be claimed from these results.

**Specifically demonstrated limitations:**

1. **Domain C failure (PR-AUC=0.2819):** Under cross-border wire surge, the model nearly fails. If this fraud pattern emerges, detection collapses until retraining.

2. **Domain D failure (F1=0.2112):** When 90% of transactions have new devices (mass account takeover), the `is_new_device` feature loses all discriminative power. Risk scores degrade severely.

3. **No adversarial robustness:** The model has not been tested against adversarial examples — feature values crafted to stay below fraud thresholds while committing fraud. A sophisticated fraudster could potentially reverse-engineer the behavioral rules (they are documented in `risk_service.py`).

4. **Synthetic scale:** 600 customers, 183 merchants, 45 days. Real systems have millions of entities. Velocity patterns, behavioral baselines, and fraud coordination at scale may be qualitatively different.

5. **Calibration on sparse tail:** Calibration was fit on 73 fraud events in validation. This is statistically marginal for reliable probability estimation.

6. **No concept drift correction:** The model will degrade over time as fraud patterns evolve. The drift detector signals this but does not correct it.

**None of these limitations invalidate the system as a demonstration.** They represent the honest boundary of what has been empirically demonstrated vs. what would require real-world deployment evidence.
