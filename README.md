# FraudShield AI — Autonomous Real-Time Fraud Intelligence Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal.svg)]()
[![React](https://img.shields.io/badge/React-19.0-blue.svg)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

FraudShield AI is an end-to-end, real-time AI fraud intelligence and decision-support platform built for financial institutions and fraud operations teams.

```
Transaction Ingestion ──► Feature Engineering ──► XGBoost Classifier + Isolation Forest
                                                             │
Resolution ◄── Analyst Decision ◄── Gemini Copilot ◄── Risk Score 0–100 & SHAP ◄── Alert Engine & WebSockets
```

---

## 🌟 Key Capabilities
- **Real-Time Processing Pipeline:** Ingestion API with idempotency checks, feature extraction (velocity, novelty, statistical deviation), XGBoost fraud classification, and Isolation Forest anomaly detection.
- **Deterministic 0–100 Risk Engine:** Transparent risk scoring with configurable thresholds (`LOW: 0–30`, `MEDIUM: 31–70`, `HIGH: 71–100`).
- **SHAP Explainability:** TreeExplainer feature attributions for every flagged transaction explaining *why* it was flagged.
- **Automated Alerts & WebSockets:** Real-time Redis pub/sub event stream and authenticated WebSocket push notifications to the dashboard.
- **Analyst Investigation Workspace:** Multi-tab investigation workflow with claim concurrency protection and mandatory resolution rationale.
- **Gemini Investigation Copilot:** Backend-sanitized AI assistant that summarizes evidence and suggests investigation followups without overriding human decision authority.
- **Security & Access Control:** Argon2id password hashing, short-lived JWT access tokens, revocable refresh sessions, server-side RBAC, multi-tenant row-level isolation (RLS), and immutable audit logs.

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

### 2. Seed Demo Data
```bash
python scripts/seed_demo.py
```

### 3. Run Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Open API documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Frontend Dashboard
```bash
cd frontend
npm install
npm dev
```
Open Dashboard UI at: [http://localhost:5173](http://localhost:5173)

### 5. Run Live Transaction Simulator
```bash
python scripts/simulate_transactions.py
```

---

## 🔑 Default Credentials (Demo)

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@shieldbank.com` | `AdminPass123!` |
| **Fraud Analyst** | `analyst@shieldbank.com` | `AnalystPass123!` |
| **Risk Manager** | `manager@shieldbank.com` | `ManagerPass123!` |
| **Viewer** | `viewer@shieldbank.com` | `ViewerPass123!` |

---

## 📚 Documentation
- [Technical Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Model Card](docs/model-card.md)
- [AI Safety Disclosure](docs/ai-disclosure.md)
- [Security & Access Controls](docs/security.md)
- [Hackathon Demo Notes](docs/hackathon-notes.md)
- [Implementation Status Tracker](docs/implementation-status.md)
