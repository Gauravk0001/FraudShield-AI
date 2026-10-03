# FraudShield AI — Data Governance & Privacy Architecture

## 1. Governance Principles

FraudShield AI operates in strict compliance with enterprise financial data governance principles:
1. **Purpose Limitation:** Transaction data is processed exclusively for real-time fraud detection, AML risk assessment, and forensic investigation.
2. **Data Minimization:** Only attributes strictly necessary for risk scoring (amounts, velocity counters, hashed device identifiers, anonymized location codes) are retained in active serving caches.
3. **Target Isolation:** Ground-truth fraud labels are stored in restricted audit tables and never exposed in online scoring feature pipelines.

---

## 2. Data Retention Schedules

| Data Classification | Storage Medium | Retention Policy | Disposal / Purge Mechanism |
|---|---|---|---|
| **Raw Ingested Transactions** | PostgreSQL / Parquet | 90 days active; 7 years archived | Automated partition dropping & cold tier migration |
| **Scored Features & Risk Scores** | `transaction_features` Table | 180 days | Rolling automated retention purge job |
| **High-Risk Alerts & Investigations** | `alerts`, `investigations` Tables | 7 years (Statutory compliance) | Secure soft-deletion with immutable audit log |
| **Analyst Audit Logs** | `audit_logs` Table | Permanent (WORM compliance) | Write-once, read-many append-only storage |
| **Simulation Runs & Benchmark Outputs**| `reports/simulation_runs/` | 30 days local | Rotating run summaries (Git-ignored) |

---

## 3. Cryptographic Protection & Encryption Standards

### In Transit
- All communication across the HTTP REST API, WebSocket streams, and internal Redis/database connections enforces TLS 1.3 encryption with modern cipher suites.
- Internal microservice traffic uses mutual TLS (mTLS) where deployed across cluster boundaries.

### At Rest
- Database volumes (PostgreSQL, SQLite, Redis append-only files) must utilize AES-256 block-level disk encryption (LUKS / AWS KMS / GCP Cloud KMS).
- Exported Parquet splits and training datasets use AES-GCM column-level encryption or storage bucket encryption.

---

## 4. Personally Identifiable Information (PII) Handling

1. **Account Identifiers:** Customer account IDs (`nameOrig`) and destination IDs (`nameDest`) are treated as pseudonymous identifiers. In external logs, IDs are truncated or salted-hashed (e.g. `C***5678`).
2. **IP Addresses:** IP addresses are truncated to `/24` (IPv4) or `/48` (IPv6) in general analytical views.
3. **Cardholder Data (CHD):** Primary Account Numbers (PANs) are strictly out-of-scope for FraudShield AI and must never enter the API payload.

---

## 5. Analyst Ground-Truth Feedback Loop

Ground truth in real financial operations arrives asynchronously:
1. **Immediate Analyst Determination:** Analyst reviews alert in the triage workspace and marks `CONFIRMED_FRAUD` or `FALSE_POSITIVE` via `POST /api/v1/alerts/{id}/label`.
2. **Delayed Customer Chargeback Notification:** External chargeback claims (30–90 days post-transaction) are ingested into the ground-truth reconciliation ledger.
3. **Governed Dataset Refresh:** Weekly batch jobs combine validated chargebacks and analyst labels to produce updated training snapshots, strictly preserving temporal ordering.
