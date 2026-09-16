# FraudShield AI — Autonomous Real-Time Fraud Intelligence & Investigation Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal.svg)]()
[![React](https://img.shields.io/badge/React-19.0-blue.svg)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

FraudShield AI is an explainable, real-time fraud intelligence and investigation platform combining:

- **Calibrated Supervised Machine Learning:** Monotonically calibrated XGBoost classifier with TreeExplainer SHAP feature attributions.
- **Unsupervised Anomaly Detection:** Isolation Forest outlier scoring for zero-day fraud pattern detection.
- **Deterministic Composite Risk Engine:** Transparent, audited multi-signal scoring (45% ML, 35% Rules/Behavioral, 20% Anomaly).
- **Real-Time Alerting & Push Notifications:** Low-latency Redis PubSub and authenticated WebSocket stream broadcasting to operations centers.
- **Role-Based Operational Experiences:** Tailored workspaces for **Fraud Analysts** (triage & investigation), **Risk Managers** (oversight & sensitivity tuning), **Platform Admins** (audit logs & settings), and **Viewers** (read-only monitoring).
- **Gemini Copilot Decision Support:** Sanitized AI assistant providing evidence interpretation and follow-up guidance without ever overriding human decision authority.
- **Multi-Tenant Security & Immutable Audit Logs:** Argon2id password hashing, JWT authentication, organization tenant isolation (RLS), and request ID correlation.
- **Continuous Drift Monitoring:** Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) feature drift detection.
- **Defensible ML Validation:** Validated against causal synthetic data with strict temporal splits, entity-grouped holdouts, and zero future leakage.

```
Transaction Ingestion ──► Feature Engineering ──► XGBoost Classifier + Isolation Forest
                                                             │
Resolution ◄── Analyst Decision ◄── Gemini Copilot ◄── Risk Score 0–100 & SHAP ◄── Alert Engine & WebSockets
```

> **Important Disclosure:** Empirical model evaluation within this repository is conducted using causal synthetic transaction datasets designed to mimic real-world distributions and adversarial attacks without exposing private banking data. FraudShield AI functions strictly as a decision-support system; all final fraud determinations remain with authorized human investigators.

---

## 🌟 Key Capabilities

1. **Real-Time Processing Pipeline:** Ingestion API with idempotency checks, causal feature extraction (velocity, novelty, statistical deviation), XGBoost fraud probability, and Isolation Forest anomaly score.
2. **Deterministic 0–100 Risk Engine:** Transparent composite scoring with customizable thresholds (`LOW: <30`, `MEDIUM: 30–69`, `HIGH/CRITICAL: ≥70`).
3. **SHAP Explainability:** Mathematical TreeExplainer feature attributions for every flagged transaction explaining *why* it was flagged.
4. **Automated Alerts & WebSockets:** Sub-second alert generation and resilient WebSocket notifications with exponential backoff and bounded queues.
5. **Analyst Investigation Workspace:** Multi-tab investigation workflow with claim concurrency protection, evidence review, and mandatory resolution rationale.
6. **Gemini Investigation Copilot:** Backend-sanitized AI assistant that summarizes evidence and suggests investigation followups without overriding human decision authority.
7. **Security & Access Control:** Argon2id password hashing, short-lived JWT access tokens, revocable refresh sessions, server-side RBAC, multi-tenant row-level isolation (RLS), and immutable audit logs.
8. **Dual-Theme Design System:** Complete Light and Dark theme application across dashboards, navigation, cards, tables, and charts.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ / npm 10+
- (Optional) Docker & Docker Compose

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
python -m venv venv
# On Windows: venv\Scripts\activate | On Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed Deterministic Demo Data
```bash
python scripts/seed_demo.py
```

### 3. Run Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Open API documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open Dashboard UI at: [http://localhost:5173](http://localhost:5173)

### 5. Run Live Transaction Simulator (Optional)
```bash
python scripts/simulate_transactions.py
```

---

## 🔑 Default Credentials (Demo)

| Role | Email | Password | Primary Mission |
|---|---|---|---|
| **Fraud Analyst** | `analyst@shieldbank.com` | `AnalystPass123!` | Detect · Triage · Investigate · Document |
| **Risk Manager** | `manager@shieldbank.com` | `ManagerPass123!` | Oversee · Monitor · Govern · Optimize |
| **Platform Admin** | `admin@shieldbank.com` | `AdminPass123!` | Configure · Audit · Manage · Control |
| **Viewer** | `viewer@shieldbank.com` | `ViewerPass123!` | Observe · Review · Report |

---

## 🧪 Verification & Test Suites

```bash
# Run backend pytest suite (45/45 passing)
python -m pytest backend/tests -v

# Run master forensic ML validation pipeline
python scripts/run_forensic_validation.py

# Run frontend production build
cd frontend && npm run build

# Run 10x demo scenario reliability test
python scripts/test_demo_reliability_10x.py
```

---

## 📚 Technical Documentation
- [HackIgnite Final Release Audit](docs/HACKIGNITE_RELEASE_AUDIT.md)
- [Technical Architecture](docs/architecture.md)
- [Security & Access Controls](docs/security.md)
- [Model Card & Forensic Evidence](docs/MODEL_CARD.md)
- [Role & Permission Matrix](docs/ROLE_PERMISSION_MATRIX.md)
- [End-to-End Lifecycle](docs/END_TO_END_LIFECYCLE.md)
- [Observability & Request Tracing](docs/OBSERVABILITY.md)
- [Deterministic Demo Scenarios Guide](docs/DEMO_SCENARIOS.md)
- [Implementation Status Tracker](docs/implementation-status.md)
- [AI Safety Disclosure](docs/ai-disclosure.md)
