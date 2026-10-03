# FraudShield AI — PaySim Dataset Integration & Data Governance Guide

## 1. Executive Notice: Synthetic Data Nature

> [!WARNING]
> **PaySim is an agent-based synthetic simulation**, generated in 2017 using the PaySim simulator. It simulates mobile money transfers based on aggregated financial data.
> **PaySim is NOT real customer or banking transaction data.** 
> All reported offline metrics (PR-AUC, ROC-AUC, Precision, Recall) must be understood as synthetic benchmark performance. Real-world fraud operations face evolving adversarial attacks, data drift, and delayed ground truth not present in synthetic data.

---

## 2. Expected Source Schema & Column Mapping

The authoritative source file is:
`PS_20174392719_1491204439457_Log.csv`

| Raw Column | Meaning in PaySim | FraudShield Internal Mapping | Usage in FraudShield AI |
|---|---|---|---|
| `step` | Simulated time unit (1 step = 1 hour) | `simulated_step` / `event_time` | Chronological ordering & velocity windowing. **Simulated step, NOT real clock time.** |
| `type` | Transaction method | `transaction_type` | Categorical feature (`PAYMENT`, `CASH_IN`, `DEBIT`, `CASH_OUT`, `TRANSFER`). |
| `amount` | Transaction value in local currency | `amount` | Core feature (`amount`, `log1p(amount)`) and loss input. |
| `nameOrig` | Origin customer account ID | `customer_id` / `origin_account_id` | Historical velocity and running average aggregations. |
| `oldbalanceOrg` | Origin initial balance before transaction | `oldbalance_org` | Balance feature variant. **Synthetic shortcut variable.** |
| `newbalanceOrig` | Origin post-transaction balance | `newbalance_orig` | Balance feature variant. **Synthetic shortcut variable.** |
| `nameDest` | Destination account ID | `destination_account_id` | Destination novelty tracking. **Do NOT assume merchant.** Prefix `C` indicates P2P Customer; prefix `M` indicates Merchant. |
| `oldbalanceDest` | Destination initial balance | `oldbalance_dest` | Balance feature variant. **Synthetic shortcut variable.** |
| `newbalanceDest` | Destination post-transaction balance | `newbalance_dest` | Balance feature variant. **Synthetic shortcut variable.** |
| `isFraud` | Ground-truth simulated fraud label | `is_fraud` (Local target ONLY) | **STRICTLY EXCLUDED** from model input. Used only for offline training and evaluation. |
| `isFlaggedFraud` | Heuristic simulation flag (>200,000) | `is_flagged_fraud` (Local target ONLY) | **STRICTLY EXCLUDED** from model input. |

---

## 3. Ground-Truth Isolation & Leakage Prevention Rules

1. **Strict Target Isolation:**
   `isFraud` and `isFlaggedFraud` are **never** passed into feature engineering, feature vectors, or online API scoring. They are retained strictly in offline training and evaluation scripts.
2. **Causal Temporal Boundaries:**
   Historical metrics (e.g., origin velocity, past amounts, first-time destination flags) use **only** records where `step < current_step`. State is updated strictly **after** the transaction is scored.
3. **No Destination Generalization:**
   Destination accounts are partitioned: accounts beginning with `C` are treated as P2P transfers; accounts beginning with `M` are treated as commercial merchants.

---

## 4. Balance-Derived Variables & The "Shortcut" Hazard

In PaySim, simulated fraud agents frequently empty the origin account completely (`newbalanceOrig == 0.0`), and exact balance subtraction arithmetic reveals simulated fraud directly.

In real-world production banking:
- Balances are updated asynchronously across ledger systems.
- Overdraft protection, pending holds, multi-currency conversions, and credit lines mean balance arithmetic is never a reliable fraud heuristic.

### Dual-Variant Requirement
FraudShield AI trains and benchmarks two distinct model configurations:
1. **Defensible Baseline (`--no-balance`):** Uses only transaction amount, type, temporal step cycles, velocities, running averages, and destination novelty. This is the honest, defensible baseline.
2. **Exploratory Prototype (`--with-balance`):** Incorporates balance discrepancies and account-emptied indicators. This model is explicitly documented as exploiting synthetic shortcuts and **must not be characterized as production-ready**.

---

## 5. Download Instructions

### Method A: Manual Download (Recommended)
1. Navigate to the official Kaggle dataset page:
   [https://www.kaggle.com/datasets/ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1)
2. Log in and download the archive (`archive.zip`, ~470 MB).
3. Extract `PS_20174392719_1491204439457_Log.csv` into the repository `data/` folder:
   ```
   data/PS_20174392719_1491204439457_Log.csv
   ```
4. Run dataset preparation:
   ```bash
   python scripts/prepare_paysim.py
   ```

### Method B: Kaggle CLI / `kagglehub`
If your Kaggle API credentials are already configured in `~/.kaggle/kaggle.json` or via `KAGGLE_USERNAME` and `KAGGLE_KEY`:
```bash
python scripts/download_paysim.py
python scripts/prepare_paysim.py
```

### Method C: Fast Offline Synthetic Demo Mode
If you are running in a restricted or offline evaluation environment without access to Kaggle:
```bash
python scripts/prepare_paysim.py
```
This automatically synthesizes a reproducible 25,000-row sample spanning steps 1 to 744 matching the exact PaySim distribution, enabling immediate verification of the full training, evaluation, and simulation stack.

---

## 6. Chronological Dataset Splitting Policy

PaySim steps run from step 1 to 744 (representing 31 days of continuous simulated time). Random splitting is strictly prohibited. We enforce a chronological step split:

- **Training Split (First 70% of steps, ~Steps 1 to 520):** Used strictly for model fitting and hyperparameter tuning.
- **Validation Split (Next 15% of steps, ~Steps 521 to 632):** Used strictly for probability calibration, cost curve analysis, and decision threshold selection.
- **Locked Test Split (Final 15% of steps, ~Steps 633 to 744):** Held out as an untouched benchmark for final reporting and simulator replay.
