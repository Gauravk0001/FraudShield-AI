# Forensic External Dataset Audit & Compatibility Analysis

**Author:** FraudShield AI ML Research & Governance Team  
**Status:** Complete & Approved for Forensic Cross-Domain Evaluation  
**Objective:** Audit public and industry-standard benchmark fraud datasets for structural, semantic, and feature-level compatibility with the FraudShield AI feature store and inference engine.

---

## 1. Executive Summary & Audit Scope

To evaluate whether FraudShield AI's trained models or architectural principles transfer beyond its synthetic training distribution, we performed a comprehensive audit of four premier public fraud datasets:
1. **PaySim Synthetic Financial Datasets** (Mobile Money Transactions)
2. **Kaggle / ULB Credit Card Fraud Detection** (European Cardholders, PCA-transformed)
3. **IEEE-CIS Fraud Detection Benchmark** (Vesta Corporation E-commerce transactions)
4. **Bank Account Fraud (BAF) Suite** (NeurIPS 2022 Benchmark for fairness and tabular fraud)

This audit establishes:
- Schema and entity mappings
- Feature availability and intersection
- Class imbalance and label definitions
- Known data leakage risks and temporal constraints
- Licensing and ethical usage boundaries

---

## 2. Comprehensive Dataset Evaluation Matrix

| Dataset | Publisher / Source | Total Rows | Fraud Rate | Temporal Span | Entity IDs Available | Feature Representation | License | Primary Incompatibilities |
|---|---|---|---|---|---|---|---|---|
| **PaySim** | Lopez-Rojas et al. (NTNU / BDI) | 6,362,620 | 0.129% (8,213) | 744 steps (31 days) | `nameOrig`, `nameDest` | Semantic (Type, Amount, Old/New Balances) | CC BY 4.0 | No device/IP metadata; step-based time; balance tracking rather than velocity counters. |
| **Kaggle / ULB CC** | Andrea Dal Pozzolo et al. (ULB MLG) | 284,807 | 0.173% (492) | 48 hours (172,792s) | None (Anonymized) | 28 PCA components ($V_1 \dots V_{28}$), `Time`, `Amount` | ODbL 1.0 | Heavily transformed PCA features prevent direct semantic alignment without retraining. |
| **IEEE-CIS** | Vesta Corp / Kaggle | 590,540 (Train) | 3.50% (20,663) | 182 days (Timedelta) | `card1-card6`, `addr1-2`, `emaildomain` | 393 features (Cards, Counts, Timedeltas, Matches) | Kaggle Competition / Research | Highly proprietary Vesta engineered features; missing raw geolocation coordinates. |
| **BAF (NeurIPS 2022)** | Feedzai / NeurIPS | 1,000,000 | 1.10% (11,000) | 8 months | `session_id`, `customer_age` | 30 Tabular features (Velocity, Device OS, Credit Risk) | CC BY-NC 4.0 | Bank account application fraud rather than real-time transactional payment authorization. |

---

## 3. Deep-Dive Dataset Audits

### 3.1 PaySim (Mobile Financial Simulation)
* **Schema Definition:**
  - `step`: 1 step = 1 hour (1 to 744).
  - `type`: `CASH_IN`, `CASH_OUT`, `DEBIT`, `PAYMENT`, `TRANSFER`.
  - `amount`: Transaction value in local fiat units.
  - `nameOrig` / `nameDest`: Account identifiers (`C...` for customer, `M...` for merchant).
  - `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`.
  - `isFraud`: Ground truth label (Fraud occurs strictly in `TRANSFER` and `CASH_OUT`).
* **Semantic Intersection with FraudShield AI:**
  - **Common / Direct Mappings:** `amount` $\to$ `amount`, `type` $\to$ `transaction_type` (mapped to `WIRE_DOMESTIC`, `CARD_NOT_PRESENT`, `POS_CHIP`), `nameOrig` $\to$ `customer_id`, `nameDest` $\to$ `merchant_id`.
  - **Engineered Velocity Alignment:** Grouping PaySim chronologically by `step` enables computing rolling transaction counts (`velocity_1h`, `velocity_24h`) and historical account averages (`amount_to_mean_ratio`).
  - **Unavailable Features:** `device_trust_score`, `ip_risk_score`, `distance_from_home_km`, `foreign_transaction_flag`.
* **Leakage Risks:** PaySim contains a known synthetic artifact where `oldbalanceOrg - amount != newbalanceOrig` in fraudulent transactions due to simulation shortcuts. Any model evaluated on PaySim must avoid using raw balance arithmetic to prevent trivial overfit.

### 3.2 Kaggle / ULB Credit Card Fraud
* **Schema Definition:**
  - `Time`: Elapsed seconds from first transaction.
  - `V1` to `V28`: Principal Component Analysis (PCA) transformed features from proprietary customer and transaction vectors.
  - `Amount`: Transaction amount in EUR.
  - `Class`: 1 for fraud, 0 for legitimate.
* **Semantic Intersection with FraudShield AI:**
  - Direct feature transfer is mathematically impossible because $V_1 \dots V_{28}$ are orthogonal projections of an undisclosed 28-dimensional proprietary feature space.
  - **Scientific Role:** Serves as a benchmark for **Cross-Architecture Performance & Calibration Comparison** (comparing XGBoost vs Random Forest vs Logistic Regression on raw tabular class-imbalanced fraud).

### 3.3 IEEE-CIS Fraud Detection
* **Schema Definition:**
  - Transaction tables (`TransactionAmt`, `ProductCD`, `card1-card6`, `addr1-2`, `dist1-2`, `P_emaildomain`, `R_emaildomain`, `C1-C14`, `D1-D15`, `M1-M9`, `V1-V339`).
  - Identity tables (`DeviceType`, `DeviceInfo`, `id_01-id_38`).
* **Semantic Intersection with FraudShield AI:**
  - **Direct Mappings:** `TransactionAmt` $\to$ `amount`, `dist1` $\to$ `distance_from_home_km`, `DeviceType`/`DeviceInfo` $\to$ `device_id`/`device_trust_score`, `addr1`/`addr2` $\to$ location risk proxy.
  - High semantic similarity in risk concepts (velocity counters $C_1 \dots C_{14}$, time delta counters $D_1 \dots D_{15}$, device fingerprinting).

---

## 4. Feature Intersection Taxonomy

To enable scientifically rigorous cross-domain evaluation without inventing missing data or violating schema contracts, we classify the FraudShield AI feature set into three distinct tiers:

```
+-------------------------------------------------------------------------------+
|                           FEATURE TAXONOMY MAPPING                            |
+-----------------------------------+-------------------------------------------+
| TIER 1: COMMON FEATURES           | Shared directly across real & synthetic   |
| (amount, hour_of_day,             | domains with standard physical semantics. |
|  day_of_week, velocity_1h, etc.)  |                                           |
+-----------------------------------+-------------------------------------------+
| TIER 2: DERIVABLE FEATURES        | Can be computed from transactional logs   |
| (amount_to_mean_ratio,            | using identical causal windowing logic.   |
|  customer_age_days, etc.)         |                                           |
+-----------------------------------+-------------------------------------------+
| TIER 3: DOMAIN-SPECIFIC / NOVEL   | Available only when device/telemetry      |
| (ip_risk_score, device_novelty,   | collector is active in production client. |
|  distance_from_home_km)           |                                           |
+-----------------------------------+-------------------------------------------+
```

### Strict Zero-Fabrication Rule:
When evaluating models across domains:
1. Missing Tier 3 features in external datasets must be filled using baseline uninformative priors (e.g. `neutral` median values: `device_trust_score=0.85`, `ip_risk_score=0.10`, `is_new_device=0`).
2. Models must be evaluated under both **Zero-Imputation Mode** (zero-shot synthetic $\to$ external) and **Domain-Randomized Synthetic Transfer** to observe exact performance degradation.
3. No external dataset labels or distributions shall be altered to enhance reported benchmark scores.
