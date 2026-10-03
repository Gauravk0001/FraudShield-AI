# FraudShield AI — Judge Demo Checklist & Walkthrough Guide

**Flow Architecture:** `DETECT` -> `EXPLAIN` -> `INVESTIGATE` -> `DECIDE` -> `AUDIT`

---

## Pre-Demo Quickstart

1. **Start Backend Server:**
   ```bash
   python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
   ```
2. **Start Frontend Server:**
   ```bash
   cd frontend
   npm run dev
   ```
3. **Open Browser:** Navigate to `http://localhost:5173`.

---

## Demonstration Script & Step-by-Step Flow

### Step 1: One-Click Authentication & Role Overview (`Login.tsx`)
- On the login screen, click **"Analyst (Full Access)"** (`analyst@shieldbank.com`).
- Highlight that the platform uses Argon2id password hashing and JWT access sessions with granular RBAC (`Admin`, `Analyst`, `Risk Manager`, `Viewer`).

### Step 2: Live Operations Dashboard (`Dashboard.tsx`)
- Inspect top-level KPI metrics: Total Transactions, High Risk Alerts, Flagged Ratio, Open Investigations.
- View the **Risk Trends Chart** illustrating transaction volume grouped by risk level.
- Point out the **Live WebSocket Connection Indicator** in the top navigation bar.

### Step 3: Real-Time Detection & Ingestion (`Transactions.tsx`)
- In a separate terminal or background, run the simulator:
  ```bash
  python scripts/simulate_transactions.py
  ```
- Watch high-risk transactions arrive instantly in the transaction list with animated risk badges (`HIGH`, `MEDIUM`, `LOW`).

### Step 4: Explainability & SHAP Decomposition (`TransactionDrawer.tsx`)
- Click on a transaction with `HIGH` risk (e.g., `$12,500.00` wire transfer).
- The **Transaction Detail Drawer** opens:
  - Supervised Fraud Probability (XGBoost)
  - Unsupervised Anomaly Score (Isolation Forest)
  - Composite Deterministic Risk Score (`0–100`)
  - **Local SHAP Feature Importance Bars** showing exact mathematical contributions (e.g., `amount_zscore`, `velocity_1h`, `device_novelty`).

### Step 5: Investigation Workspace & Concurrency Locking (`Investigations.tsx`)
- Click **"Investigate Alert"** from the alert or transaction drawer.
- Navigate to the **Investigation Workspace**:
  - Review transaction metadata and customer history tabs.
  - Click **"Claim Investigation"** to lock the case to your analyst ID (optimistic concurrency versioning prevents race conditions).
  - Add evidence notes in the analyst notes feed.

### Step 6: Gemini Copilot Decision Support (`CopilotDrawer.tsx`)
- Click the **"Ask Copilot"** button to open the embedded assistant.
- Click a quick suggestion chip: `"Explain top risk factors"` or `"Summarize evidence for resolution"`.
- Note the safety guardrails: The Copilot provides probabilistic decision support and evidence synthesis, but **cannot** alter risk scores or make final decisions.

### Step 7: Mandatory Decision & Resolution
- In the **Resolution Panel**, choose a verdict:
  - `CONFIRMED_FRAUD` (Block account & initiate chargeback)
  - `FALSE_POSITIVE` (Whitelist & release funds)
- Enter mandatory decision rationale (minimum 5 characters required).
- Click **"Submit Final Resolution"**. The status transitions to `RESOLVED` and becomes immutable.

### Step 8: Immutable Audit Trail (`AuditLogs.tsx`)
- Navigate to **Audit Logs** to show judges the immutable event stream capturing:
  - User login event
  - Transaction evaluation
  - Alert trigger
  - Investigation claim
  - Final resolution rationale and timestamp.

---

## Demo Verification Summary

| Checkpoint | Status | Latency / SLA |
|---|---|---|
| Single Transaction Inference | Verified | `< 10ms` |
| WebSocket Event Broadcast | Verified | Real-time |
| SHAP Feature Decomposition | Verified | Deterministic |
| Concurrency Lock Safety | Verified | Optimistic versioning |
| Copilot Guardrails | Verified | Boundary protected |
| Audit Trail Persistence | Verified | Immutable DB records |
