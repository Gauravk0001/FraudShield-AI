# API Reference Document — FraudShield AI

Base URL: `http://localhost:8000/api/v1`

## 1. Authentication Endpoints (`/auth`)
- `POST /api/v1/auth/login`: Authenticates user (email/password), returns JWT access token (15-min expiry) & HttpOnly refresh cookie.
- `POST /api/v1/auth/refresh`: Issues new access token using valid refresh session.
- `GET /api/v1/auth/me`: Returns current authenticated user profile and assigned role.
- `POST /api/v1/auth/logout`: Revokes refresh session.

## 2. Transaction Ingestion & Detail (`/transactions`)
- `POST /api/v1/transactions`: Validates, generates features, runs ML inference, scores risk, computes SHAP attributions, and persists transaction.
- `GET /api/v1/transactions`: List transactions with search, filter (risk_level, status), and pagination.
- `GET /api/v1/transactions/{id}`: Full transaction detail including customer, merchant, device, risk score breakdown, and SHAP factors.

## 3. Alerts (`/alerts`)
- `GET /api/v1/alerts`: List alerts filtered by status (`NEW`, `UNDER_REVIEW`, `RESOLVED`) and severity.
- `PATCH /api/v1/alerts/{id}`: Update alert status or assignment.

## 4. Investigation Workspace (`/investigations`)
- `POST /api/v1/investigations`: Start investigation for a flagged alert.
- `POST /api/v1/investigations/{id}/claim`: Claim investigation (protected with optimistic row-level concurrency locking).
- `POST /api/v1/investigations/{id}/notes`: Add analyst evidence note.
- `POST /api/v1/investigations/{id}/decision`: Record final resolution decision (`CONFIRMED_FRAUD`, `FALSE_POSITIVE`, `SUSPICIOUS_ESCALATED`, `INCONCLUSIVE`).

## 5. Gemini Copilot (`/copilot`)
- `POST /api/v1/copilot/chat`: Communicates with Gemini backend service, passing sanitized evidence context.

## 6. Audit & Models (`/audit-logs`, `/models`)
- `GET /api/v1/audit-logs`: Admin audit trail of sensitive actions.
- `GET /api/v1/models`: Active ML model versions, evaluation metrics, and feature schemas.
