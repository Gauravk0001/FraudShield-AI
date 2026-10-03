# Security & Access Controls — FraudShield AI

## 1. Password Hashing & JWT Security
- **Password Hashing:** Argon2id with bcrypt fallback. Plaintext passwords or SHA-256 password storage are strictly prohibited.
- **Short-Lived Access Tokens:** Signed JWT access tokens expiring in 15 minutes.
- **Revocable Refresh Sessions:** Secure HttpOnly SameSite cookies with UUID JTI tracking.

## 2. Server-Side RBAC
Four primary roles enforced strictly on backend FastAPI routes:
- `ADMIN`: Full system management, user administration, model versions, audit logs.
- `FRAUD_ANALYST`: Dashboard, search transactions, risk scores, SHAP explanations, alerts, investigation notes, decision recording, Copilot assistant.
- `RISK_MANAGER`: Dashboard, transactions, alerts, investigation reviews, analyst reassignments, model performance tracking.
- `VIEWER`: Read-only access to approved transactions & alerts.

## 3. Multi-Tenant Organization Isolation (RLS)
- Every transaction, alert, investigation, and entity is bound to an `organization_id`.
- Backend query filters enforce organization boundaries server-side.

## 4. Race Condition & Concurrency Protection
- Investigation claiming (`POST /api/v1/investigations/{id}/claim`) uses row-level locking / optimistic update checks to prevent two analysts from simultaneously claiming the same case.
