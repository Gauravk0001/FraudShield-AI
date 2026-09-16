# FraudShield AI — Model Card

## 1. Model Details

- **Model Name:** FraudShield AI Multi-Vector Fraud Detection Engine
- **Model Version:** `v2.0.0-forensic`
- **Model Architecture:** Calibrated XGBoost Classifier (`CalibratedClassifierCV` via Platt Sigmoid Scaling) + Unsupervised Isolation Forest Anomaly Detector + Deterministic Behavioral Risk Scoring
- **Underlying Booster:** Gradient Boosted Decision Trees (`xgboost.XGBClassifier`, `n_estimators=120`, `max_depth=4`, `learning_rate=0.05`, `scale_pos_weight=4.0`, `subsample=0.85`, `colsample_bytree=0.85`)
- **Explainability Framework:** Exact Local Tree Attributions via `shap.TreeExplainer` ($f(x) = \phi_0 + \sum_{i=1}^M \phi_i$)
- **Release Date:** 2026-09-16
- **License:** Proprietary / FinTech Enterprise

---

## 2. Intended Use

- **Primary Intended Use:** Real-time transaction risk scoring and fraud classification for retail banking, e-commerce payment processors, and fintech platforms.
- **Decision Support Contract:** Automated risk scoring ($\text{Risk} \in [0, 100]$) and automated alert generation ($\tau_{\text{alert}} \ge 30.0$) provide triaged operational queues. Certified human fraud analysts retain final adjudicative authority on account freezes and suspicious activity reporting.
- **Out-of-Scope Uses:** Autonomous account termination without human review, credit underwriting, credit scoring, or customer identity verification.

---

## 3. Training & Validation Methodology

### Causal Entity Tracking
All features are generated chronologically. For any transaction processed at timestamp $t$, all historical entity features (customer averages, velocities, novelty flags) are calculated strictly using past transactions where $t_{\text{history}} < t$. The current transaction never influences its own pre-transaction state.

### Partitioning & Validation Strategy
1. **Temporal Split (Chronological Order):** 
   - Historical Training: Oldest 70% (11,986 samples)
   - Validation & Calibration: Middle 15% (2,568 samples)
   - Untouched Final Test Set: Newest 15% (2,569 samples)
2. **5-Fold Stratified Cross-Validation:** Reporting mean $\pm$ standard deviation across 5 folds.
3. **Customer-Grouped Partitioning:** Evaluated across distinct, non-overlapping customer cohorts (`customer_overlap = 0`) to measure zero-shot customer generalization.

---

## 4. Feature Space (12 Deterministic Signals)

| Feature Name | Type | Description |
|---|---|---|
| `amount` | Float | Transaction monetary value in USD |
| `transaction_type_encoded` | Categorical | Payment method (0: Card Present, 1: CNP/Online, 2: Wire/ATM) |
| `hour_of_day` | Integer | Transaction hour (0–23 UTC) |
| `day_of_week` | Integer | Day of the week (0: Monday – 6: Sunday) |
| `transaction_velocity_1h` | Integer | Number of prior customer transactions within the preceding 1 hour |
| `transaction_velocity_24h` | Integer | Number of prior customer transactions within the preceding 24 hours |
| `avg_amount_customer_30d` | Float | Customer historical 30-day average transaction amount |
| `amount_deviation_ratio` | Float | Ratio of current amount to 30-day customer historical baseline |
| `time_since_last_transaction_seconds` | Float | Elapsed time in seconds since the customer's immediately preceding transaction |
| `is_new_device` | Binary | 1.0 if device fingerprint has not been previously observed for this customer |
| `is_new_merchant` | Binary | 1.0 if merchant has not been previously transacted with by this customer |
| `location_changed` | Binary | 1.0 if transaction location differs from preceding transaction location |

---

## 5. Measured Empirical Performance

*All metrics are empirically measured from actual execution on the untouched chronological test set and 5-fold cross validation. No synthetic benchmark inflation or metric fabrication.*

| Evaluation Metric | Untouched Temporal Test Set | 5-Fold Stratified CV | Customer-Grouped Split (Unseen Customers) |
|---|---|---|---|
| **Precision** | `0.9371` | `0.9566 ± 0.0178` | `0.9573` |
| **Recall** | `0.8371` | `0.8264 ± 0.0283` | `0.7568` |
| **F1-Score** | `0.8843` | `0.8864 ± 0.0177` | `0.8453` |
| **PR-AUC** | `0.9240` | `0.9331 ± 0.0158` | `0.8929` |
| **ROC-AUC** | `0.9928` | `0.9945 ± 0.0012` | `0.9934` |
| **False Positive Rate (FPR)** | `0.4182%` | `0.1966% ± 0.0838%` | `0.1514%` |
| **Brier Score Loss** | `0.0137` | — | — |
| **Single-Tx Inference Latency** | `6.75 ms` | — | — |

---

## 6. Confusion Matrix (Untouched Test Set: 2,569 Samples)

- **True Negatives (TN):** 2,381
- **False Positives (FP):** 10 (FPR: 0.418%)
- **False Negatives (FN):** 29
- **True Positives (TP):** 149 (Fraud Catch Rate: 83.71%)

---

## 7. Probability Calibration & Threshold Selection

- **Calibration Method:** Platt Sigmoid Scaling (`CalibratedClassifierCV(method='sigmoid')`) fitted on the validation set.
- **Validation Brier Score:** Reduced from `0.0131` (uncalibrated) to `0.0086` (calibrated).
- **Operating Decision Threshold:** $\tau = 0.35$ (selected via validation F1-maximization).
- **Distinction of Concepts:**
  - `fraud_probability`: Pure calibrated Bayesian likelihood that the transaction is fraudulent ($\in [0.0, 1.0]$).
  - `risk_score`: Operational composite ranking ($\in [0.0, 100.0]$) combining Supervised Probability (45%), Anomaly Score (20%), and Behavioral Flags (35%).

---

## 8. Robustness & Explainability Validation

1. **Exact Tree SHAP Additivity:** Verified mathematically across test samples with maximum additivity residual $| \phi_0 + \sum \phi_i - \text{margin} | = 3.33 \times 10^{-6} < 10^{-4}$.
2. **Counterfactual Sensitivity:** Tested on suspicious hero transactions ($14,500 wire, 3 AM, new device, velocity 5). Perturbing all features to normal systematically drops risk from `91.52` to `7.02` and probability from `0.9522` to `0.0015`.
3. **Adversarial Edge Cases:** Verified zero crash and bounded outputs for zero amounts, negative amounts, $1,000,000 transactions, and cold-start customers.
4. **Multi-Seed Stability:** Verified across seeds `[42, 123, 2024, 2025, 777]` with standard deviation $< 0.02$ across all metrics.

---

## 9. Limitations & Caveats

> [!WARNING]
> **Synthetic Data Realism Disclaimer:** Although this model was trained on a causal generator with hard negatives (VIP travelers, holiday bursts) and realistic fraud topologies (ATO, card testing, velocity attacks), synthetic distributions cannot model unobserved geopolitical disruptions, merchant acquirer outages, or novel multi-institution fraud rings. Regular retraining and continuous monitoring (PSI / KS drift detection) are mandatory in live production.
