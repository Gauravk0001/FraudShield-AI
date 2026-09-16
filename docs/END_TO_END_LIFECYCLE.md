# FraudShield AI — End-to-End Fraud Detection & Investigation Lifecycle

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ 1. Transaction  │ ----> │  2. ML & Risk   │ ----> │ 3. Real-Time    │ ----> │ 4. Investigation│
│    Ingestion    │       │     Scoring     │       │    Alert (WS)   │       │  Case Creation  │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
                                                                                       │
                                                                                       ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ 8. Audit Trail  │ <---- │ 7. State Update │ <---- │ 6. Case Final   │ <---- │ 5. Evidence &   │
│   & Governance  │       │   & Notification│       │    Decision     │       │   SHAP Notes    │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## Step-by-Step Lifecycle Stages

### 1. Ingestion (`POST /api/v1/transactions`)
- **Ingestion**: Upstream payments / core banking gateway submits transaction payload.
- **Validation**: Strict Pydantic schema validation enforcing positive amounts, valid ISO currencies, and required identifiers.
- **Correlation**: `X-Request-ID` assigned and propagated across contextvars for distributed tracing.

### 2. Composite Risk Scoring Pipeline
- **Ensemble Evaluation**:
  - Calibrated XGBoost Classifier produces probabilistic fraud likelihood $P(\text{Fraud})$.
  - Unsupervised Isolation Forest measures behavioral and velocity divergence (Anomaly Score).
  - Deterministic Rule Engine checks known heuristics (e.g. velocity bursts, blacklisted TOR nodes).
- **Composite Formula**:
  $$\text{Risk Score} = (0.45 \cdot P(\text{Fraud}) + 0.20 \cdot \text{Anomaly} + 0.35 \cdot \text{Rule Penalty}) \times 100$$
- **Explainability**: SHAP TreeExplainer generates signed local feature contributions for the top 5 factors.

### 3. Real-Time Alert Broadcast (`WebSocket /ws/alerts`)
- If $\text{Risk Score} \ge \text{Risk Threshold High}$ (default 70.0) or $\ge 90.0$ (Critical):
  - An `Alert` entity is persisted in PostgreSQL/SQLite.
  - Broadcasted asynchronously to connected Analyst and Risk Manager sessions over WebSocket.
  - Frontend Notification Center queues real-time card with audio/visual badge (bounded to 25 items).

### 4. Case Creation & Concurrency Claiming (`POST /api/v1/investigations`)
- Fraud Analyst initiates investigation case linked to the alert.
- Analyst claims ownership via `POST /api/v1/investigations/{id}/claim` which increments optimistic lock version.

### 5. Evidence Gathering & AI Copilot Consultation
- Analyst reviews exact transaction timeline, device fingerprint, and SHAP directional attribution.
- Analyst adds detailed case findings via `POST /api/v1/investigations/{id}/notes`.
- Note creation emits an immutable audit event (`INVESTIGATION_NOTE_ADDED`).

### 6. Case Resolution & Disposition (`POST /api/v1/investigations/{id}/resolve`)
- Analyst selects disposition (`CONFIRMED_FRAUD`, `FALSE_POSITIVE`, `SUSPICIOUS_MONITORED`, `NO_ACTION_REQUIRED`).
- Case status shifts to `RESOLVED`, recording resolution timestamp and rationale.

### 7. State Synchronization
- Associated `Alert` transitions to `RESOLVED`.
- Dashboard metrics update live exposure counters and fraud prevention telemetry.

### 8. Audit Logging (`GET /api/v1/audit-logs`)
- Every critical mutation produces an immutable `AuditLog` row containing `organization_id`, `user_id`, `action`, `request_id`, and redacted sanitized metadata.
