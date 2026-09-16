# FraudShield AI — Role Permission & RBAC Matrix

## 1. Executive Summary
FraudShield AI implements strict **Server-Side Role-Based Access Control (RBAC)** across all endpoints and business capabilities. Frontend navigation and UI visibility adapt dynamically to user roles, while backend dependencies (`require_role`, `get_current_user`) strictly enforce authorization invariants.

---

## 2. Platform Roles & Personas

| Role | Target Persona | Primary Responsibilities |
| :--- | :--- | :--- |
| **`ADMIN`** | Platform / System Administrator | Organization configuration, sensitive risk engine tuning, audit log inspection, user management |
| **`RISK_MANAGER`** | Senior Risk & Compliance Officer | Operational exposure monitoring, model performance oversight, threshold review & tuning, queue monitoring |
| **`FRAUD_ANALYST`** | Fraud Investigation Specialist | Daily alert triage, transaction intelligence, evidence gathering, SHAP feature inspection, case resolution |
| **`VIEWER`** | Read-Only Auditor / Executive | High-level portfolio viewing, compliance observation (strictly zero write/mutation permissions) |

---

## 3. Comprehensive Endpoint Permission Matrix

| Endpoint | Method | `ADMIN` | `RISK_MANAGER` | `FRAUD_ANALYST` | `VIEWER` | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `/api/v1/auth/register` | POST | 🟢 Public | 🟢 Public | 🟢 Public | 🟢 Public | Provision tenant user |
| `/api/v1/auth/login` | POST | 🟢 Public | 🟢 Public | 🟢 Public | 🟢 Public | Issue JWT bearer token |
| `/api/v1/auth/me` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Self-identity & tenant info |
| `/api/v1/dashboard/stats` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Live tenant KPIs |
| `/api/v1/dashboard/trends` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Historical volume & risk trends |
| `/api/v1/transactions` | POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | Transaction scoring & ingestion |
| `/api/v1/transactions` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | List scoped transactions |
| `/api/v1/transactions/{id}` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Transaction detail & SHAP factors |
| `/api/v1/alerts` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | List scoped fraud alerts |
| `/api/v1/alerts/{id}` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Alert details & risk breakdown |
| `/api/v1/investigations` | POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | Open investigation case from alert |
| `/api/v1/investigations` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | List scoped investigation cases |
| `/api/v1/investigations/{id}` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Case details, history, & notes |
| `/api/v1/investigations/{id}/claim` | POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | Assign case with concurrency lock |
| `/api/v1/investigations/{id}/notes` | POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | Append evidence & findings note |
| `/api/v1/investigations/{id}/resolve`| POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | Resolve case (CONFIRMED/FALSE_POS) |
| `/api/v1/settings` | GET | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | 🔴 403 Forbidden | Engine config & system diagnostics |
| `/api/v1/settings` | PATCH | 🟢 Allowed | 🟢 Allowed | 🔴 403 Forbidden | 🔴 403 Forbidden | Adjust sensitivity thresholds |
| `/api/v1/audit-logs` | GET | 🟢 Allowed | 🔴 403 Forbidden | 🔴 403 Forbidden | 🔴 403 Forbidden | Immutable audit trail review |
| `/api/v1/copilot/chat` | POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Role-adapted AI Copilot persona |
| `/api/v1/models/summary` | GET | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Model metadata & calibration |
| `/api/v1/models/explain/shap`| POST | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | 🟢 Allowed | Model explainability attribution |

---

## 4. Multi-Tenant Row-Level Security (RLS)
All database queries automatically filter on `organization_id == current_user.organization_id`. Even users with `ADMIN` privileges are strictly restricted to their own organization's records and cannot view cross-tenant transactions, alerts, cases, or audit logs.
