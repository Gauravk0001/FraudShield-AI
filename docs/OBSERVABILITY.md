# FraudShield AI — Observability, Structured Logging & Tracing

## 1. Observability Architecture

FraudShield AI incorporates enterprise-grade observability across all execution paths:
- **Request Tracing**: `X-Request-ID` correlation middleware ensures full distributed traceability from API gateways to database operations.
- **Context-Bound Logging**: Python `logging` with Python 3.11+ `contextvars` automatically injects `req`, `org`, `user`, and `tx` tags into all structured log lines.
- **Data Protection & Sanitization**: Strict regex sanitization scrubs passwords, bearer tokens, API keys, and raw card credentials prior to disk emission.

---

## 2. Structured Log Format

Log outputs adhere to the standardized structured pattern:
```text
YYYY-MM-DD HH:MM:SS,mmm - fraudshield - LEVEL - [req=<request_id> org=<org_id> user=<user_id>] <message>
```

### Example Log Lines:
```text
2026-09-16 19:15:37,465 - fraudshield - INFO - [req=fc905426] Loaded calibrated fraud classifier model from /models_artifacts/fraud_classifier.joblib
2026-09-16 19:15:37,620 - fraudshield - INFO - [req=fc905426] Initialized SHAP TreeExplainer on XGBoost booster
2026-09-16 19:15:38,112 - fraudshield - INFO - [req=7c8b21ef org=org_44a9 user=usr_analyst] [AUDIT] Action: INVESTIGATION_RESOLVED | Entity: CASE-8812 | Request: 7c8b21ef
```

---

## 3. Request Correlation (`X-Request-ID`)

All incoming HTTP requests pass through `RequestIDCorrelationMiddleware`:
1. If client supplies `X-Request-ID`, it is validated and preserved.
2. If client omits the header, a high-entropy short UUID is dynamically generated.
3. The request ID is set in the asynchronous context (`ctx_request_id.set(req_id)`).
4. The response includes `X-Request-ID: <req_id>`.
5. All database audit logs record the exact `request_id` for compliance investigations.

---

## 4. Credential Sanitization Invariant

The logging pipeline employs `SanitizingFormatter` with pre-compiled regex filters covering:
- `Bearer [A-Za-z0-9\-\._~\+\/]+=*`
- `"(?:password|token|secret|key|authorization)"\s*:\s*"[^"]+"`
- Basic Auth patterns

All sensitive tokens are replaced with `[REDACTED]` before writing to standard out or file handlers.
