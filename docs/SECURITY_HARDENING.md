# FraudShield AI — Security Hardening & Production Safety Guide

## 1. Zero-Trust Production Hardening Policies

FraudShield AI enforces automated production startup safeguards to prevent insecure deployments, credential exposure, or inadvertent test data activation.

### 1.1 Strict Secret Key Enforcement
- **Startup Guardrail:** If `ENVIRONMENT == "production"`, the application inspects `SECRET_KEY`.
- If `SECRET_KEY` is missing, empty, shorter than 32 characters, or matches default/development placeholder strings (e.g. `change_this...`, `dev-insecure...`), the application **terminates startup immediately** (`RuntimeError`) and writes a critical audit log.
- **Development Default:** The fallback development key is explicitly prefixed with `dev-insecure-...-unsafe-for-prod` to guarantee that accidental production inheritance fails validation.

### 1.2 Demo Seeding & User Lockout
- In production, `ENABLE_DEMO_SEED` is strictly `False`.
- Any attempt to invoke `seed_demo_environment()` in production immediately returns `status: blocked_in_production`.
- Demo users (`admin@shieldbank.com`, password `AdminPass123!`) are **never** seeded or created in production databases.

### 1.3 Database Credential Protection
- Hardcoded database passwords (`fraudshield_secret_pass`) are rejected at startup in production.
- Production deployments must supply credentials via environment variables (`DATABASE_URL` or secret manager injection).
- SQLite storage is strictly designated for local single-worker development only.

---

## 2. Multi-Tenant Data Isolation & Access Controls

1. **Row-Level Organization Isolation:**
   Every database query across transactions, alerts, risk scores, investigations, and audit logs filters strictly by `current_user.organization_id`.
2. **Role-Based Access Control (RBAC):**
   - `ADMIN`: Full administrative control, model rollback, system configuration.
   - `RISK_MANAGER`: Model oversight, threshold configuration, case backlog management.
   - `FRAUD_ANALYST`: Alert triage, investigation execution, ground-truth labeling.
   - `VIEWER`: Read-only audit and regulatory reporting access.
3. **Rate Limiting:**
   - `/api/v1/score`: 600 requests/minute per tenant.
   - `/api/v1/auth/login`: 30 attempts/minute per IP to prevent brute-force attacks.

---

## 3. Information Disclosure & Error Sanitization

- Global exception handlers intercept unhandled exceptions, log the full stack trace internally with correlation ID `X-Request-ID`, and return sanitized JSON responses to clients.
- Internal database paths, connection URLs, model binary locations, and customer PII are never returned in error payloads.

---

## 4. Software Bill of Materials (SBOM) Generation

To generate a CycloneDX or SPDX compliant SBOM for container and dependency audits:

### Python Backend SBOM (via cyclonedx-bom)
```bash
pip install cyclonedx-bom
cyclonedx-py requirements backend/requirements.txt -o backend/sbom.json
```

### Frontend SBOM (via npm)
```bash
cd frontend
npm sbom --sbom-format cyclonedx > frontend-sbom.json
```

---

## 5. Vulnerability Scanning Instructions

### Python Dependency Scanning (via pip-audit)
```bash
pip install pip-audit
pip-audit -r backend/requirements.txt
```

### Frontend Dependency Scanning (via npm audit)
```bash
cd frontend
npm audit --audit-level=high
```

### Container Image Scanning (via Trivy)
```bash
trivy image fraudshield-backend:latest
trivy image fraudshield-frontend:latest
```

---

## 6. Secret Scanning Protocols

Automated pre-commit hooks and CI/CD pipelines must execute GitLeaks or TruffleHog to ensure credentials, API keys, or private certificates are never committed:

```bash
# Scan repository with Gitleaks
gitleaks detect --source . --verbose
```
