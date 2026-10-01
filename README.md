# FraudShield AI — Autonomous Real-Time Fraud Intelligence & Investigation Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Deployment](https://img.shields.io/badge/Deployment-Live-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)]()
[![React](https://img.shields.io/badge/React-19.0-blue.svg)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**FraudShield AI** is an explainable, enterprise-grade real-time fraud detection and analyst investigation platform built for banking and fintech operations.

---

## 🚀 Live Demo & Hack2Ignite Deployment

The platform is **LIVE and publicly accessible**:

| Service | Access Link | Description |
| :--- | :--- | :--- |
| **Live Web Application** | **[Open Live App](https://site-griffin-flower-fluid.trycloudflare.com)** | Full React 19 + Tailwind Operations Dashboard |
| **Interactive API Docs** | **[Open Swagger UI](https://site-griffin-flower-fluid.trycloudflare.com/docs)** | OpenAPI Specification & Live Request Testing |
| **System Health Check** | **[View Health Endpoint](https://site-griffin-flower-fluid.trycloudflare.com/health)** | PostgreSQL, Engine, & Redis Health Status |
| **Live WebSocket Stream** | `wss://site-griffin-flower-fluid.trycloudflare.com/ws/alerts` | Real-time Alert & Event Broadcasting |

### 🔐 Demonstration Accounts (Role-Based Access Control)

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@shieldbank.com` | `AdminPass123!` | Full read/write, user management, system settings |
| **Fraud Analyst** | `analyst@shieldbank.com` | `AnalystPass123!` | Investigations, note mutations, verdict submissions |
| **Risk Manager** | `manager@shieldbank.com` | `ManagerPass123!` | Risk thresholds, model oversight, audit inspections |
| **Read-Only Viewer** | `viewer@shieldbank.com` | `ViewerPass123!` | Audit view only (mutations strictly blocked by RLS) |

### 🎯 Key Demo Highlights

1. **Hero Takeover Scenario (`tx_hero_takeover_007`):**
   - High-amount wire transfer ($18,500) initiated from Singapore via a previously unobserved device.
   - Evaluated to **Risk Score 91/100 (CRITICAL)** with **97.3% supervised fraud probability** and **0.59 anomaly score**.
2. **Local SHAP Feature Attribution:**
   - Real-time signed contributions quantifying why a transaction was flagged (`amount` +2.72, `is_new_device` +1.28).
3. **Forensic Copilot:**
   - Interactive investigation assistant providing evidence summaries and guided next steps.
4. **Real-time Event Streaming:**
   - Low-latency Redis Pub/Sub WebSocket event propagation for instant alert triage.

---

## 🏛️ End-to-End Architecture

```
                                  ┌───────────────────────────────┐
                                  │   React 19 + TypeScript UI   │
                                  │   (Dark / Light Operations)   │
                                  └───────────────┬───────────────┘
                                                  │ HTTPS / WSS
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    FastAPI API Gateway &      │
                                  │    Security / RBAC / RLS      │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │   Causal Feature Engineering  │
                                  │ (Velocity, Novelty, Deviation)│
                                  └───────────────┬───────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
             ┌────────────────────────┐                        ┌───────────────────────┐
             │ Calibrated XGBoost     │                        │   Isolation Forest    │
             │ Classifier (Sigmoid)   │                        │   Anomaly Detector    │
             └───────────┬────────────┘                        └───────────┬───────────┘
                         │ P(Fraud | x)                                    │ Anomaly Score
                         └────────────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │ Composite Risk Engine (0-100) │
                                  │ 45% ML + 35% Rules + 20% Iso  │
                                  └───────────────┬───────────────┘
                                                  │
                         ┌────────────────────────┼────────────────────────┐
                         ▼                        ▼                        ▼
             ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
             │ TreeSHAP Explainer   │ │ Real-Time Alerts &   │ │ Human Investigation  │
             │ Local Attribution    │ │ Redis PubSub / WS    │ │ & Gemini Copilot     │
             └──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

---

## 🌟 Core Capabilities

1. **Dual-Model ML Pipeline**:
   - **Supervised Fraud Classifier**: Extreme Gradient Boosting (`XGBClassifier`) with Platt Sigmoid calibration (`CalibratedClassifierCV`) producing reliable, monotonic fraud probabilities.
   - **Unsupervised Anomaly Detection**: `IsolationForest` detecting novel zero-day attack patterns without ground-truth labels.
2. **Deterministic Composite Risk Engine**:
   - Transparent, audited multi-signal scoring ($0–100$) blending Supervised ML probability (45%), Domain Rules / Velocity boosts (35%), and Anomaly scores (20%).
   - Explicit operational thresholds: `LOW: <30`, `MEDIUM: 30–69`, `HIGH/CRITICAL: ≥70`.
3. **Exact Mathematical Explainability (SHAP)**:
   - TreeSHAP local feature attributions ($f(x) = \phi_0 + \sum_{i=1}^M \phi_i$) for every transaction, explaining exact risk contributors in real time.
4. **Real-Time Alert Stream & WebSockets**:
   - Automated sub-second alert creation on risk threshold breach ($\ge 30$) with Redis PubSub broadcasting and resilient WebSocket client reconnects.
5. **Human-in-the-Loop Investigation Workspace**:
   - Analyst triage lifecycle (`OPEN` $\to$ `IN_REVIEW` $\to$ `RESOLVED`), optimistic concurrency locking (`version` counter), and mandatory decision rationale.
6. **Gemini Investigation Copilot**:
   - Backend-sanitized AI assistant providing evidence summarization and investigation checklists without ever overriding human authority.
7. **Enterprise Security & Multi-Tenancy**:
   - Argon2id password hashing, short-lived JWT access tokens (15m), server-side RBAC, and organization-scoped database queries (Row-Level Security).
8. **Audit Logging & Observability**:
   - Immutable audit trail capturing every decision, state change, and security event; distributed request ID correlation across API and logging layers.

---

## 📊 Authoritative ML Evaluation Metrics

> **Empirical Standard**: Evaluated on the locked, untouched temporal test set ($N = 2,569$, $6.93\%$ fraud rate) from the causal synthetic transaction dataset ($N = 17,123$, $4.95\%$ overall fraud prevalence). All numbers reflect actual model execution—zero metric fabrication.

| Evaluation Metric | Measured Value | Standard / Target | Status |
|---|---|---|---|
| **Precision** | **`92.55%`** | $> 85.0\%$ | ✅ PASS |
| **Recall (Sensitivity)** | **`83.71%`** | $> 80.0\%$ | ✅ PASS |
| **F1-Score** | **`87.91%`** | $> 80.0\%$ | ✅ PASS |
| **PR-AUC (Average Precision)** | **`0.9220`** | $> 0.850$ | ✅ PASS |
| **ROC-AUC** | **`0.9927`** | $> 0.950$ | ✅ PASS |
| **False Positive Rate (FPR)** | **`0.50%`** | $< 1.0\%$ | ✅ PASS |
| **Brier Score (Calibrated)** | **`0.0143`** | $< 0.050$ | ✅ PASS |
| **Single-Tx Inference Latency** | **`< 15 ms`** | $< 100\text{ ms}$ SLA | ✅ PASS |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ (tested on Python 3.11, 3.12, 3.13)
- Node.js 18+ / npm 10+
- (Optional) Docker & Docker Compose

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
# Create virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate | On Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed Deterministic Demo Environment
```bash
python scripts/seed_demo.py
```

### 3. Start Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start Frontend Application
```bash
cd frontend
npm install
npm run dev
```
FraudShield Operations Dashboard: [http://localhost:5173](http://localhost:5173)

### 5. Stream Live Simulated Transactions (Optional)
```bash
python scripts/simulate_transactions.py
```

---

## 🔑 Demo Access Credentials (Role-Based)

| Role | Email | Password | Primary Mission |
|---|---|---|---|
| **Fraud Analyst** | `analyst@shieldbank.com` | `AnalystPass123!` | Triage Alerts · Inspect SHAP · Conduct Investigations |
| **Risk Manager** | `manager@shieldbank.com` | `ManagerPass123!` | Monitor Risk Velocity · Audit Rules · View Models |
| **Platform Admin** | `admin@shieldbank.com` | `AdminPass123!` | Manage Users & Orgs · Review Audit Logs · System Settings |
| **Viewer** | `viewer@shieldbank.com` | `ViewerPass123!` | Read-Only Regulatory Oversight & Compliance |

---

## 🧪 Verification & Test Commands

```bash
# 1. Run complete automated backend test suite (45/45 passing)
python -m pytest backend/tests -v

# 2. Run master forensic ML validation orchestrator
python scripts/run_forensic_validation.py

# 3. Run frontend production build
cd frontend && npm run build

# 4. Run 10x end-to-end demo scenario benchmark
python scripts/test_demo_reliability_10x.py
```

---

## 📚 Technical Documentation

- [Hack2Ignite Final Release Audit](docs/HACKIGNITE_RELEASE_AUDIT.md)
- [System Architecture Specification](docs/architecture.md)
- [Model Card (v2.0.0-forensic)](docs/MODEL_CARD.md)
- [ML Empirical Evaluation Report](docs/ML_EVALUATION_REPORT.md)
- [Probability Calibration Evidence](docs/CALIBRATION_EVIDENCE.md)
- [Domain Generalization & Shift Report](docs/DOMAIN_GENERALIZATION_REPORT.md)
- [Security Architecture & Controls](docs/security.md)
- [Role & Permission Matrix](docs/ROLE_PERMISSION_MATRIX.md)
- [Evidence Traceability Matrix](docs/EVIDENCE_TRACEABILITY_MATRIX.md)
- [Deterministic Demo Scenarios Guide](docs/DEMO_SCENARIOS.md)
- [End-to-End Lifecycle Guide](docs/END_TO_END_LIFECYCLE.md)
- [Observability & Distributed Tracing](docs/OBSERVABILITY.md)
- [AI Safety Disclosure](docs/ai-disclosure.md)
