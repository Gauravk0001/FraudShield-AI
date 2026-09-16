# Technical Architecture Document — FraudShield AI

## Architecture Overview
FraudShield AI is implemented as a high-performance **modular monolith** designed for real-time financial fraud detection, explainability, risk scoring, and AI-assisted investigation workflows.

```
React 19 + TypeScript + Vite (Dashboard UI)
        │  ▲
        ▼  │ (REST / WebSocket)
FastAPI Backend (Authentication, RBAC, Multi-Tenant RLS)
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
PostgreSQL (Source of Truth)   Redis (Pub/Sub Event Bus)
   │
   ├─► Feature Generator (Velocity, Novelty, Historical)
   ├─► XGBoost Fraud Classifier (Supervised Probabilities)
   ├─► Isolation Forest (Unsupervised Anomaly Scores)
   ├─► Deterministic Risk Engine (0-100 Score & Level)
   ├─► SHAP TreeExplainer (Feature Attribution)
   └─► Gemini AI Copilot Service (Sanitized Context)
```

## Core Modules & Data Flow
1. **Transaction Ingestion & Idempotency Pipeline:**
   - Ingests incoming transactions via `POST /api/v1/transactions`.
   - Checks idempotency against existing transaction IDs in DB.
2. **Deterministic Feature Engineering:**
   - Extracts 13 real-time velocity (1-minute, 1-hour transaction frequencies), amount deviations from historical baseline, and device/location/merchant novelty indicators.
3. **ML Ensemble & Risk Engine:**
   - **XGBoost Classifier:** Computes supervised fraud probability \(P \in [0,1]\).
   - **Isolation Forest:** Computes statistical anomaly score.
   - **Deterministic Risk Engine:** Merges probabilities into a normalized 0-100 risk score:
     - `0–30`: LOW
     - `31–70`: MEDIUM
     - `71–100`: HIGH
4. **SHAP Explainability:**
   - Explains tree predictions with feature attributions, direction (positive/negative risk contribution), and human-readable operational explanations.
5. **Alert Engine & WebSocket Streaming:**
   - Automatically triggers alerts when risk score \(\ge 70\). Publishes structured JSON events to Redis PubSub and broadcasts to authenticated WebSocket clients.
6. **Gemini AI Copilot:**
   - Backend-sanitized evidence context provider. Receives no PII or credentials. Assists human analysts with evidence summaries and follow-up guidance.
