# FraudShield AI — Evidence Traceability Matrix

**Status:** Complete — All numerical claims traced to executable code  
**Policy:** No unsupported numerical claims. Every number references a source artifact.  
**Generated:** 2026-09-16 from actual code execution

---

## How to Read This Matrix

- **SUPPORTED** = Claim verified by running the referenced script and matching output
- **SUPPORTED (CORRECTED)** = Claim was inaccurate; corrected value from actual execution is shown
- **PASS WITH LIMITATION** = Claim is true but requires additional context
- **NOT EMPIRICALLY VERIFIABLE** = Claim is analytical/architectural, not a numerical measurement

---

## A. Dataset Claims

| Claim | Value | Source Code | Artifact | Status |
|---|---|---|---|---|
| Total transactions | 17,123 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `transactions` | **SUPPORTED** |
| Legitimate transactions | 16,276 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `legitimate_transactions` | **SUPPORTED** |
| Fraudulent transactions | 847 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `fraudulent_transactions` | **SUPPORTED** |
| Fraud rate | 4.95% | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `fraud_rate_pct` | **SUPPORTED** |
| Unique customers | 600 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `customers` | **SUPPORTED** |
| Unique merchants | 183 (not 150) | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `merchants` | **SUPPORTED (NOTE: generated 183 unique, not 150 configured)** |
| Unique devices | 1,900 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `devices` | **SUPPORTED** |
| Date range | 2026-01-01 to 2026-02-14 | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `date_range` | **SUPPORTED** |
| 6 fraud topologies | ATO 25%, CNP 22%, Card Testing 18%, Velocity 15%, Wire 12%, Triangulation 8% | `scripts/generate_forensic_dataset.py` | `data/forensic_dataset_metadata.json` → `fraud_topologies_percentages` | **SUPPORTED** |
| Chronological ordering | 100% monotonic | `scripts/validate_dataset_integrity.py` | console output | **SUPPORTED** |
| Dataset SHA-256 | 3674b803fe9d4a12... | `scripts/validate_dataset_integrity.py` | `data/forensic_dataset_metadata.json` → `sha256_hash` | **SUPPORTED** |
| Test set SHA-256 | 985e08d215249e42... | `scripts/final_test_manifest.py --verify` | `data/final_test_manifest.json` → `test_data_sha256` | **SUPPORTED** |

---

## B. Calibration Claims

| Claim | Value | Source Code | Artifact | Status |
|---|---|---|---|---|
| Calibration partition | Middle 15% (2,568 samples) | `scripts/evaluate_calibration.py` lines 53-64 | console output | **SUPPORTED** |
| Test set not used for calibration | — | `scripts/evaluate_calibration.py` line 69 explicit print | console output | **SUPPORTED** |
| Uncalibrated Brier | 0.0098–0.0102 | `scripts/evaluate_calibration.py` + `scripts/run_forensic_audit.py` | `docs/CALIBRATION_EVALUATION.md` | **SUPPORTED (CORRECTED: ~0.0102 in audit run, ~0.0098 in prior runs due to XGBoost ordering)** |
| Platt Brier | 0.0086–0.0088 | `scripts/evaluate_calibration.py` + `scripts/run_forensic_audit.py` | `docs/CALIBRATION_EVALUATION.md` | **SUPPORTED (CORRECTED: 0.0088 in audit run)** |
| Platt ECE | 0.0029–0.0038 | `scripts/evaluate_calibration.py` + `scripts/run_forensic_audit.py` | `docs/CALIBRATION_EVALUATION.md` | **SUPPORTED (CORRECTED: 0.0029 in audit run)** |
| Isotonic Brier | 0.0076–0.0077 | `scripts/run_forensic_audit.py` | `docs/CALIBRATION_EVIDENCE.md` | **SUPPORTED** |
| Isotonic ECE | 0.0000 | `scripts/run_forensic_audit.py` | `docs/CALIBRATION_EVIDENCE.md` | **SUPPORTED** |
| Platt selected for smoothness | Architectural | `scripts/evaluate_calibration.py` line 128-133 | `docs/CALIBRATION_EVIDENCE.md` | **SUPPORTED — Isotonic has better metrics; Platt selected for composite risk smoothness** |

---

## C. Multi-Seed Stability Claims

| Claim | Documented | Audited | Source Code | Status |
|---|---|---|---|---|
| Seeds evaluated | [42, 123, 2024, 2025, 777] | [42, 123, 2024, 2025, 777] | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| Training independence | — | All 5 training hashes unique | `scripts/run_forensic_audit.py` + `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| Test set identical across seeds | 2,569 rows | 2,569 rows, same SHA-256 | `scripts/run_forensic_audit.py` | **SUPPORTED** |
| F1 mean | 0.8852 | 0.8852 | `scripts/evaluate_multiseed.py` | **SUPPORTED — reproduced exactly** |
| F1 std | ±0.0050 | ±0.0050 | `scripts/evaluate_multiseed.py` | **SUPPORTED — reproduced exactly** |
| Precision mean | 0.9353 | 0.9353 | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| Recall mean | 0.8404 | 0.8404 | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| PR-AUC mean | 0.9324 | 0.9324 | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| ROC-AUC mean | 0.9935 | 0.9935 | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| FPR mean | 0.435% | 0.435% | `scripts/evaluate_multiseed.py` | **SUPPORTED** |
| Brier mean | 0.0131 | 0.0131 | `scripts/evaluate_multiseed.py` | **SUPPORTED** |

### Per-Seed Table (Audited Values)

| Seed | Training Data Hash | Precision | Recall | F1 | PR-AUC | ROC-AUC | FPR | Brier |
|---|---|---|---|---|---|---|---|---|
| 42 | `2550db8f0c37...` | 0.9255 | 0.8371 | 0.8791 | 0.9255 | 0.9929 | 0.5019% | 0.0138 |
| 123 | `2edbce5c42a9...` | 0.9222 | 0.8652 | 0.8928 | 0.9382 | 0.9937 | 0.5437% | 0.0124 |
| 2024 | `ffe516e00de0...` | 0.9548 | 0.8315 | 0.8889 | 0.9343 | 0.9940 | 0.2928% | 0.0127 |
| 2025 | `927cd169e964...` | 0.9313 | 0.8371 | 0.8817 | 0.9294 | 0.9938 | 0.4601% | 0.0138 |
| 777 | `4242e5a78423...` | 0.9427 | 0.8315 | 0.8836 | 0.9344 | 0.9932 | 0.3764% | 0.0129 |
| **Mean** | — | **0.9353** | **0.8404** | **0.8852** | **0.9324** | **0.9935** | **0.4350%** | **0.0131** |
| **Std** | — | ±0.0120 | ±0.0126 | ±0.0050 | ±0.0044 | ±0.0004 | ±0.0901% | ±0.0006 |

---

## D. Risk Engine Claims

| Claim | Value | Source Code | Audit Finding | Status |
|---|---|---|---|---|
| fraud_probability ≠ risk_score | — | `backend/app/services/risk_service.py` | Sample: prob=0.0015, risk=12.15 — confirmed different | **SUPPORTED** |
| Production weights 45/20/35 | ML=0.45, Anom=0.20, Beh=0.35 | `backend/app/services/risk_service.py` line 42 | Confirmed in code | **SUPPORTED** |
| Grid search conducted | 15+ configs | `scripts/evaluate_risk_engine.py` lines 107-134 | Confirmed, grid covers ML:0.50-0.70, Anom:0.10-0.25 | **PASS WITH LIMITATION** |
| 45% ML not in grid range | — | `scripts/evaluate_risk_engine.py` lines 107 | Grid starts at ML=0.50; 0.45 not tested in original script | **CORRECTED: Audit expanded grid to include ML=0.40-0.70** |
| Production config is grid optimum | — | `scripts/run_forensic_audit.py` | Production PR-AUC=0.9176; Top config (70/25/5)=0.9525 on validation | **CORRECTED: Production is NOT the grid optimum** |
| ML-only FPR 0.29% | 0.29% | `scripts/evaluate_risk_engine.py` | Confirmed on validation | **SUPPORTED** |
| Risk tier LOW: 84.7% | 84.7% | `scripts/evaluate_risk_engine.py` | On validation set | **SUPPORTED** |
| Risk tier MEDIUM: 12.1% | 12.1% | `scripts/evaluate_risk_engine.py` | On validation set | **SUPPORTED** |
| Risk tier HIGH: 2.8% | 2.8% | `scripts/evaluate_risk_engine.py` | On validation set | **SUPPORTED** |
| Risk tier CRITICAL: 0.35% | 0.35% | `scripts/evaluate_risk_engine.py` | On validation set | **SUPPORTED** |

> [!WARNING]
> **Risk Engine Weight Discrepancy:** The original grid search in `evaluate_risk_engine.py` tested ML weights of 0.50–0.70, but the production config uses ML=0.45. The expanded audit grid (0.40–0.70) shows the configuration `ML=0.70 / Anom=0.25 / Beh=0.05` achieves PR-AUC=0.9525 vs production 0.9176 on the validation set. This is a **0.0349 gap**. The production config was chosen for operational interpretability (balanced behavioral signal contribution) rather than raw metric optimization. This must be explicitly documented and is **not** a case of test-set optimization.

---

## E. Counterfactual Claims

| Perturbation | Base Prob | Perturbed Prob | Delta | Base Risk | Perturbed Risk | Classification | Status |
|---|---|---|---|---|---|---|---|
| A. Amount $14.5k → $45 | 0.9513 | 0.9691 | +0.0178 | 91.48 | 90.59 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| B. Velocity 5 → 0 | 0.9513 | 0.9743 | +0.0230 | 91.48 | 90.76 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| C. New → Known Device | 0.9513 | 0.9532 | +0.0019 | 91.48 | 91.43 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| D. New → Known Merchant | 0.9513 | 0.9513 | 0.0000 | 91.48 | 91.81 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| E. Foreign → Home Location | 0.9513 | 0.9740 | +0.0228 | 91.48 | 92.33 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| F. Wire → Card Present | 0.9513 | 0.0019 | **-0.9494** | 91.48 | **48.63** | EXPECTED | **SUPPORTED** |
| G. 3am → 2pm | 0.9513 | 0.9691 | +0.0178 | 91.48 | 92.16 | NONLINEAR_EXPLAINABLE | **DOCUMENTED** |
| H. Fully Benign | 0.9513 | **0.0014** | **-0.9498** | 91.48 | **10.53** | EXPECTED | **SUPPORTED** |

> [!NOTE]
> **Counterfactual Nonlinearity Explanation:** Perturbations A–E and G produce `NONLINEAR_EXPLAINABLE` results — reducing a single signal does not reduce risk when the transaction is simultaneously flagged by multiple other high-risk signals. XGBoost's orthogonal decision tree branches can activate fraud leaf nodes via independent feature combinations. For example: reducing amount from $14,500 to $45 does NOT eliminate the wire transfer type + new device + new merchant combination — those signals continue to activate high-fraud tree paths. Only when ALL signals are normalized simultaneously (H) does fraud probability collapse to 0.0014.

---

## F. Domain Generalization Claims

> [!IMPORTANT]
> **Domain Type Classification:** All five domains are **synthetic domain-shift stress tests** — not real external dataset evaluations. The claim "evaluated against external datasets" must NOT be made. The correct claim is "evaluated under synthetic distribution shifts that simulate external dataset conditions."

| Domain | Type | F1 | PR-AUC | FPR | Drift Status | Status |
|---|---|---|---|---|---|---|
| A: Standard Baseline | Synthetic holdout (same distribution) | 0.9154 | 0.9542 | 0.39% | LOW_DRIFT | **SUPPORTED** |
| B: High-Velocity | Synthetic covariate shift (velocity 3.5×) | 0.6196 | 0.7796 | 4.19% | HIGH_DRIFT | **SUPPORTED** |
| C: Cross-Border Wire | Synthetic covariate shift (amount log-normal) | 0.3964 | 0.2819 | 9.33% | HIGH_DRIFT | **SUPPORTED** |
| D: Account Takeover | Synthetic covariate shift (device/merchant 90% new) | 0.2112 | 0.6475 | 31.76% | HIGH_DRIFT | **SUPPORTED** |
| E: External Proxy | Synthetic telemetry masking (device features set to neutral) | 0.7543 | 0.7530 | 0.18% | LOW_DRIFT | **SUPPORTED** |

---

## G. Drift Monitoring Claims

| Claim | Status | Notes |
|---|---|---|
| PSI implemented correctly | **SUPPORTED** | Quantile bins, epsilon smoothing, verified |
| KS implemented correctly | **SUPPORTED** | scipy.stats.ks_2samp, exact two-sample test |
| LOW_DRIFT: PSI < 0.10 | **SUPPORTED** | Hardcoded threshold in drift_service.py |
| MODERATE_DRIFT: PSI 0.10-0.25 | **SUPPORTED** | Hardcoded threshold in drift_service.py |
| HIGH_DRIFT: PSI >= 0.25 | **SUPPORTED** | Hardcoded threshold in drift_service.py |
| Empty dataset handled | **SUPPORTED** | Returns 0.0 without crash (verified) |
| Constant feature PSI | **SUPPORTED (CLARIFIED)** | Constant current vs varying baseline = HIGH PSI (correct behavior — it IS extreme drift) |
| NaN handling | **SUPPORTED** | Caller must fill NaN before calling; verified with dropna() |
| Drift ≠ model failure | **DOCUMENTED** | Explicitly noted in drift_service.py and docs |

---

## H. Final Test Integrity

| Claim | Value | Status |
|---|---|---|
| Test set SHA-256 | 985e08d215249e42edbbc71d57410f04e200ad876a2d55603d9ac21c01775a47 | **SUPPORTED — verified in audit** |
| Test rows | 2,569 | **SUPPORTED** |
| Test fraud count | 178 (6.93%) | **SUPPORTED** |
| Test never used for training | — | **SUPPORTED — temporal split enforces this** |
| Test never used for calibration | — | **SUPPORTED — calibration only on validation** |
| Test never used for threshold selection | — | **SUPPORTED — threshold selected on validation** |
| Test never used for weight grid | — | **SUPPORTED — weight grid only on validation** |

---

## I. Reproducibility Claims

| Claim | Status | Command |
|---|---|---|
| `python scripts/run_forensic_validation.py` passes all 8 steps | **SUPPORTED** | Verified: `forensic_v2`, Status=PASS |
| `python -m pytest backend/tests -v` → 34 passed | **SUPPORTED** | Verified multiple times |
| `npm run build` passes | **SUPPORTED** | Frontend build 6.36s, 0 errors |
| Domain shift script runs | **SUPPORTED** | All 5 domains evaluated |
| Drift service imports correctly | **SUPPORTED** | No import errors |

---

## J. Claims Requiring Correction in Documentation

| Document | Stale Claim | Corrected Claim |
|---|---|---|
| `docs/ML_EVALUATION_REPORT.md` Section 8 | "grid covers ML 0.50-0.70" | Grid covers ML 0.40-0.70 in the audit; original `evaluate_risk_engine.py` only covers 0.50-0.70. The 45% production weight was NOT in the original grid search range — it was selected separately. |
| `docs/MODEL_CARD.md` §6 | Does not distinguish synthetic domains from real external evaluation | Updated to state: "5 synthetic domain-shift stress tests; no real external dataset evaluation performed" |
| `docs/HACKIGNITE_ML_DEFENSE.md` Q14 | "External Benchmark Proxy" implies external validation | Corrected to: synthetic telemetry masking simulation |
| `docs/CALIBRATION_EVALUATION.md` | Selection rationale hardcoded before running | `docs/CALIBRATION_EVIDENCE.md` provides transparent comparison showing Isotonic beats Platt on Brier+ECE |
| `docs/RISK_ENGINE_EVALUATION.md` | Does not state production config is NOT the grid optimum | Must add note that top grid config (ML=0.70) outperforms production (ML=0.45) by 0.0349 PR-AUC on validation |
