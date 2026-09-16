# FraudShield AI — Frontend/Backend Integration Forensic Audit

**Audit Date:** 2026-09-16  
**Auditor:** Antigravity Forensic Engineering  
**Application Endpoints:** Frontend `http://127.0.0.1:5173`, Backend `http://127.0.0.1:8000`

---

## 1. Executive Summary

An architectural and forensic code audit of FraudShield AI was conducted to identify the root causes of integration, routing, and API failures across the application. 

The audit identified 5 distinct categories of integration breakdowns:
1. **Audit Logs HTTP 500 Failure**: Direct column name and schema mismatch between SQLAlchemy ORM model (`created_at`, `entity_type`, `entity_id`) and Pydantic response schema / SQL order-by query (`timestamp`, `resource_type`, `resource_id`).
2. **Missing Alerts Page & Routing Alias**: `/alerts` route in `App.tsx` mapped to `<Transactions />` instead of a dedicated Alerts page; no `Alerts.tsx` component was present.
3. **Settings Wildcard Redirect**: Clicking `/settings` hit wildcard `*` route in `App.tsx` and redirected to `/` (Overview) due to missing route and page component.
4. **Transactions Page Degradation**: Swallowed API exceptions, missing query-string deep link support (`?id=...`), and placeholder `alert()` stub for investigation creation.
5. **Role-Based Routing Gaps**: Missing explicit 403 Forbidden UI treatment on role-restricted pages.

---

## 2. Detailed Mismatch Traceability Matrix

| Component / Page | Frontend Route | Backend Endpoint | Issue Category | Root Cause |
|---|---|---|---|---|
| **Audit Logs** | `/audit-logs` | `GET /api/v1/audit-logs` | Backend Exception (500) | `query.order_by(AuditLog.timestamp.desc())` raised `AttributeError` because column is `created_at`. Pydantic schema validation failed on missing required fields `resource_type`, `resource_id`, `timestamp`. |
| **Alerts** | `/alerts` | `GET /api/v1/alerts` | Route Mapping & Missing Page | `App.tsx` mapped route `alerts` to `<Transactions />`. No dedicated `Alerts.tsx` page existed in `frontend/src/pages/`. |
| **Settings** | `/settings` | `GET /api/v1/settings` *(missing)* | Route Not Found & Redirect | No route for `settings` existed in `App.tsx`. Request hit `<Route path="*" element={<Navigate to="/" replace />} />`. No `Settings.tsx` or backend settings endpoint existed. |
| **Transactions** | `/transactions` | `GET /api/v1/transactions` | Error Handling & Deep Linking | Silently caught API errors in `catch (err) { console.error(err); }` without user feedback. Ignored `?id=` query parameter from Dashboard links. Drawer investigation button used `alert()` popup. |
| **Models** | `/models` | `GET /api/v1/models` | Schema Vulnerability | `ModelVersion` model column names (`metadata_json`, `model_type`) vs route expectations (`m.model_name`, `m.model_metadata`). |
| **Auth / RBAC** | All routes | `GET /api/v1/auth/me` | Role Handling | Admin-only routes (`/audit-logs`, `/settings`) lacked in-page fallback rendering for unauthorized roles. |

---

## 3. Database Layer Inspection

- **Database File**: `fraudshield.db` (SQLite development instance) and PostgreSQL compatibility schemas.
- **ORM Table Names**:
  - `organizations` (`id`, `name`, `created_at`)
  - `users` (`id`, `organization_id`, `email`, `role`, `hashed_password`, `is_active`)
  - `transactions` (`id`, `organization_id`, `transaction_id`, `customer_id`, `amount`, `timestamp`, etc.)
  - `risk_scores` (`id`, `transaction_id`, `fraud_probability`, `risk_score`, `risk_level`, etc.)
  - `alerts` (`id`, `organization_id`, `transaction_id`, `risk_score`, `severity`, `status`, etc.)
  - `investigations` (`id`, `organization_id`, `alert_id`, `transaction_id`, `status`, `decision`, etc.)
  - `audit_logs` (`id`, `organization_id`, `user_id`, `action`, `entity_type`, `entity_id`, `details`, `ip_address`, `request_id`, `created_at`)
  - `model_versions` (`id`, `version`, `model_type`, `feature_schema_version`, `metrics`, `artifact_path`, `status`, `metadata_json`, `created_at`)

---

## 4. Remediation Plan

1. **Fix Audit Logs Backend**:
   - Update `app/models/audit.py` to expose property aliases (`timestamp`, `resource_type`, `resource_id`).
   - Update `app/api/routes/audit.py` to query `AuditLog.created_at.desc()` and support comprehensive field serialization.
2. **Build Dedicated Alerts Component (`Alerts.tsx`)**:
   - Implement full alerts management UI: severity badges, status filtering, analyst assignment, inspection drawer, and direct navigation to investigations.
3. **Build Dedicated Settings Module (`Settings.tsx` & `backend/app/api/routes/settings_route.py`)**:
   - Implement backend settings router with GET & PATCH endpoints for risk thresholds and system config.
   - Implement frontend `Settings.tsx` with Admin-only access guard, threshold sliders/inputs, system diagnostics, and real save actions.
4. **Harden Transactions Page**:
   - Add proper loading/error/empty UI states, support URL query parameters (`?id=`), and enable seamless investigation creation.
5. **Update Routing & Navigation (`App.tsx`)**:
   - Map `/alerts` to `<AlertsPage />` and `/settings` to `<SettingsPage />`.
6. **Validate End-to-End**:
   - Verify all 8 routes in browser, run pytest suite, build frontend, and perform live transaction-to-audit-log pipeline flow test.
