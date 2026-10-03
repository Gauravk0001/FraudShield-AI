# FraudShield AI — Multi-Seed Stability & Variance Report

**Audit Date:** 2026-09-16 17:32:39 UTC  
**Seeds Evaluated:** `[42, 123, 2024, 2025, 777]`  
**Evaluation Protocol:** Seed-dependent data generation and model retraining evaluated on a **single fixed, untouched final test set** (2,569 samples).

---

## 1. Multi-Seed Stability Summary Table

| Evaluation Metric | Mean ($\mu$) | Standard Deviation ($\sigma$) | Coefficient of Variation ($CV$) | Minimum | Maximum |
|---|---|---|---|---|---|
| **Precision** | `0.9353` | `0.0120` | `1.28%` | `0.9222` | `0.9548` |
| **Recall** | `0.8404` | `0.0126` | `1.50%` | `0.8315` | `0.8652` |
| **F1-Score** | `0.8852` | `0.0050` | `0.56%` | `0.8791` | `0.8928` |
| **PR-AUC** | `0.9324` | `0.0044` | `0.48%` | `0.9255` | `0.9382` |
| **ROC-AUC** | `0.9935` | `0.0004` | `0.04%` | `0.9929` | `0.9940` |
| **False Positive Rate (FPR)** | `0.4350%` | `0.0901%` | `20.71%` | `0.2928%` | `0.5437%` |
| **Brier Score Loss** | `0.0131` | `0.0006` | `4.48%` | `0.0124` | `0.0138` |

---

## 2. Per-Seed Performance Breakdown

| Random Seed | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | FPR | Brier Loss |
|---|---|---|---|---|---|---|---|
| **Seed 42** | `0.9255` | `0.8371` | `0.8791` | `0.9255` | `0.9929` | `0.5019%` | `0.0138` |
| **Seed 123** | `0.9222` | `0.8652` | `0.8928` | `0.9382` | `0.9937` | `0.5437%` | `0.0124` |
| **Seed 2024** | `0.9548` | `0.8315` | `0.8889` | `0.9343` | `0.9940` | `0.2928%` | `0.0127` |
| **Seed 2025** | `0.9313` | `0.8371` | `0.8817` | `0.9294` | `0.9938` | `0.4601%` | `0.0138` |
| **Seed 777** | `0.9427` | `0.8315` | `0.8836` | `0.9344` | `0.9932` | `0.3764%` | `0.0129` |

---

## 3. Findings & Stability Interpretation

1. **Empirical Variance:** Standard deviations across all primary metrics remain bounded ($\sigma_{\text{F1}} < 0.03$), demonstrating that model convergence is not fragile to initial random weight assignments or entity cohort sequencing.
2. **Generalization Robustness:** Across all 5 seeds, PR-AUC consistently remains above `0.90` and ROC-AUC remains above `0.99`, confirming that feature engineering signals (velocity bursts, amount deviation ratios, and novelty transitions) provide stable discriminative signals.
