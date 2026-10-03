# FraudShield AI — Production Operations & Incident Response Runbook

## 1. System Architecture & Startup Procedure

FraudShield AI operates as a unified decision-support stack comprising:
- **Backend:** FastAPI serving `/api/v1/score`, `/api/v1/metrics`, WebSocket pub/sub.
- **Inference Engine:** Platt-calibrated XGBoost classifier + Isolation Forest anomaly detector.
- **Frontend:** React 19 + TypeScript + Vite live analyst dashboard.
- **Data Stores:** PostgreSQL (primary ledger) + Redis (event bus) + Parquet (cold analytics).

### 1.1 Local / Development Startup
```bash
# Backend (from repository root)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev
```

### 1.2 Production Startup Requirements
- `ENVIRONMENT=production`
- `SECRET_KEY`: Minimum 32-character high-entropy secret.
- `DATABASE_URL`: Authenticated PostgreSQL connection URI.
- `ENABLE_DEMO_SEED=False`: Demo data and demo users are blocked by default.

---

## 2. Health & Observability Endpoints

| Endpoint | Method | Expected Output | Purpose |
|---|---|---|---|
| `/health` | `GET` | `{"status": "ok", "database": "healthy", "model_load_status": "LOADED"}` | Cluster readiness probe |
| `/api/v1/metrics` | `GET` | Latency percentiles (p50/p95/p99), alert rate, decision breakdown | Prometheus / Datadog scraping |
| `/api/v1/score` | `POST` | `fraud_probability`, `anomaly_score`, `risk_score`, `decision`, `reasons` | Real-time scoring API |
| `/api/v1/alerts/{id}/label` | `POST` | Updated alert with audit trail | Analyst ground-truth labeling |

---

## 3. Incident Playbooks

### Playbook A: Degraded Mode Activated (`degraded: true`)
- **Symptoms:** `/api/v1/metrics` reports `degraded_responses > 0`; scoring reasons include `MODEL_UNAVAILABLE_RULE_FALLBACK`.
- **Impact:** System automatically uses deterministic safety rules. No unhandled 500 errors.
- **Action Steps:**
  1. Inspect backend logs for `Inference exception` or `PaySim model artifacts not found`.
  2. Verify artifact integrity:
     ```bash
     python scripts/validate_model_artifacts.py
     ```
  3. If corrupt or missing, restore signed artifacts from backup or execute rollback.

### Playbook B: Model Rollback Procedure
If model drift, latency anomalies, or calibration errors occur:
1. Verify rollback candidate:
   ```bash
   python scripts/validate_model_artifacts.py --rollback-from backend/models_artifacts/paysim_v0_stable
   ```
2. Restart backend workers or call reload trigger.
3. Verify `/health` returns `model_load_status: LOADED`.

### Playbook C: Threshold Adjustment Protocol
1. Modify `backend/models_artifacts/paysim/thresholds.json` or update via settings API.
2. Ensure `step_up_threshold < hold_for_review_threshold`.
3. Verify change is recorded in immutable `audit_logs` table.

---

## 4. Disaster Recovery & Backup

1. **Database:** Hourly pg_dump backups of `audit_logs`, `alerts`, `investigations`.
2. **Model Artifacts:** Version-controlled artifact storage with signed SHA-256 manifests.
