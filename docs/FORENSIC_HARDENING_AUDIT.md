# FraudShield AI — Forensic ML Hardening Audit

**Audit Timestamp:** 2026-09-16T08:55:00Z  
**Repository:** https://github.com/Gauravk0001/FraudShield-AI.git  
**Auditor:** Principal ML Engineer & MLOps Auditor  
**Audit Purpose:** Comprehensive forensic assessment of data generation, leakage controls, split methodology, probability calibration, risk engine weighting, SHAP explainability, and multi-seed stability.

---

## 1. System Architecture Overview

```
Incoming Transaction JSON
          │
          ▼
┌────────────────────────────────────────┐
│   Causal Feature Engineering Pipeline  │
│   (Strictly t_history < t_transaction) │
└──────────────────┬─────────────────────┘
                   │ 12 Causal Features
                   ▼
       ┌───────────┴───────────┐
       ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  XGBoost      │       │  Isolation    │
│  Classifier   │       │  Forest       │
│  (Calibrated) │       │  (Anomaly)    │
└──────┬────────┘       └───────┬───────┘
       │                        │
       │ Prob ∈ [0, 1]          │ Score ∈ [0, 1]
       └───────────┬────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│     Composite Risk Scoring Engine      │
│  (ML 45% + Anomaly 20% + Behav 35%)    │
└──────────────────┬─────────────────────┘
                   │ Risk ∈ [0, 100]
                   ▼
┌────────────────────────────────────────┐
│     SHAP TreeExplainer & Triage        │
│    Alert Threshold >= 30.0             │
└────────────────────────────────────────┘
```

---

## 2. Forensic Findings & Inconsistencies Identified

### A. Composite Risk Engine Weighting
- **Current State:** Hardcoded as `45% ML + 20% Anomaly + 35% Behavioral Signals`.
- **Finding:** While the calibrated XGBoost model has high standalone precision (`0.9371`) and PR-AUC (`0.9240`), the composite formula shifts the precision/recall profile towards high recall (`0.9563`) at the expense of higher false positives (`7.67%` FPR).
- **Required Action:** Run an empirical weight grid sensitivity experiment across ML weights (`0.50–0.70`), Anomaly weights (`0.10–0.25`), and Behavioral weights on validation data only, evaluating operational triage tradeoffs.

### B. Probability Calibration Selection
- **Current State:** Platt Sigmoid calibration was selected, but earlier logs showed Isotonic regression achieved a lower raw Brier score on validation data (`0.0076` vs `0.0086`).
- **Finding:** Isotonic regression can overfit on smaller calibration sets or create stepped, non-smooth probabilities that degrade under out-of-distribution domain shift, whereas Platt scaling maintains strictly monotonic sigmoid mapping.
- **Required Action:** Formalize a pre-defined calibration selection rubric (Brier score, ECE, log loss, monotonicity, and out-of-distribution stability) on a dedicated calibration partition without touching the final test set.

### C. Multi-Seed Stability Implementation
- **Current State:** Multi-seed evaluation reported `0.0000` standard deviation across seeds `[42, 123, 2024, 2025, 777]`.
- **Finding:** The earlier multi-seed loop re-evaluated the exact same static dataset instance without varying the generative seed or bootstrap partition, masking true data-generation variance.
- **Required Action:** Implement a true multi-seed experiment where generative seed and model random states vary together, evaluating genuine empirical standard deviation across all 5 seeds on the fixed untouched test schema.

### D. Dataset Metadata Consistency
- **Current State:** Discrepancies existed across past markdown docs regarding sample counts (e.g. 5,000 vs 10,000 vs 17,123).
- **Finding:** Hand-edited markdown summaries led to drift between code constants and documentation.
- **Required Action:** Establish `data/forensic_dataset_metadata.json` as the single authoritative source of truth, enforced by `scripts/validate_dataset_integrity.py`.

### E. Counterfactual Non-Linearity
- **Current State:** Counterfactual perturbations on high-risk transactions (e.g., dropping velocity from 5 to 0) retained elevated risk scores due to lingering amount and device flags.
- **Finding:** Tree-based ensemble splits create non-linear interaction surfaces; single-feature perturbation does not immediately drop the score if other orthogonal risk signals remain high.
- **Required Action:** Trace feature attribution deltas through SHAP and document explainable non-linear interactions vs potential edge-case bugs.

### F. Domain Generalization & External Data
- **Current State:** Synthetic dataset validation cannot prove performance in live banking environments with unobserved macroeconomic dynamics.
- **Required Action:** Perform compatibility audit against standard public fraud datasets (e.g., Credit Card Fraud Detection / PaySim), measure feature intersection, conduct synthetic domain-shift experiments, and build PSI/KS drift monitoring.

---

## 3. Provenance of Current Model Artifacts

| Artifact | Location | Architecture | Provenance |
|---|---|---|---|
| `fraud_classifier.joblib` | `models_artifacts/` | `CalibratedClassifierCV(XGBoost)` | Trained on causal synthetic partition (seed 42) |
| `base_xgboost.joblib` | `models_artifacts/` | `xgboost.XGBClassifier` (120 trees, depth 4) | Base booster for SHAP TreeExplainer |
| `isolation_forest.joblib`| `models_artifacts/` | `sklearn.ensemble.IsolationForest` | Unsupervised baseline on normal samples |
| `model_metadata.json` | `models_artifacts/` | JSON Metadata | Schema, feature list, operating thresholds |

---

## 4. Hardening Roadmap

1. [x] Audit complete and inconsistencies documented.
2. [ ] Establish authoritative dataset metadata (`data/forensic_dataset_metadata.json`) & integrity validator.
3. [ ] Implement Risk Engine weight sensitivity analysis & threshold evaluation (`scripts/evaluate_risk_engine.py`).
4. [ ] Implement rigorous Calibration selection suite (`scripts/evaluate_calibration.py`).
5. [ ] Implement true Multi-Seed stability suite (`scripts/evaluate_multiseed.py`).
6. [ ] Implement forensic counterfactual validation (`scripts/evaluate_counterfactuals.py`).
7. [ ] External dataset audit & cross-domain evaluation (`docs/EXTERNAL_DATASET_AUDIT.md`, `scripts/evaluate_domain_shift.py`).
8. [ ] Implement production PSI/KS drift monitor (`backend/app/services/drift_service.py`).
9. [ ] Create final test manifest with SHA-256 hash protection (`data/final_test_manifest.json`).
10. [ ] Master orchestration script (`scripts/run_forensic_validation.py`).
11. [ ] Update `docs/MODEL_CARD.md`, `docs/ML_EVALUATION_REPORT.md`, and create `docs/HACKIGNITE_ML_DEFENSE.md`.
