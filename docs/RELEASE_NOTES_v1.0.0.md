# FraudShield AI — Release v1.0.0 (Hack2Ignite Final Production Release)

## 🌟 Executive Overview
FraudShield AI is an enterprise-grade, real-time autonomous fraud intelligence and investigation platform engineered for banking and fintech infrastructures. This production release marks the validated deployment for the **Hack2Ignite** competition.

---

## 🚀 Live Public Deployment
- **Live Operations Dashboard:** [https://site-griffin-flower-fluid.trycloudflare.com](https://site-griffin-flower-fluid.trycloudflare.com)
- **Interactive OpenAPI Docs:** [https://site-griffin-flower-fluid.trycloudflare.com/docs](https://site-griffin-flower-fluid.trycloudflare.com/docs)
- **Live System Health Check:** [https://site-griffin-flower-fluid.trycloudflare.com/health](https://site-griffin-flower-fluid.trycloudflare.com/health)
- **Real-Time WebSocket Feed:** `wss://site-griffin-flower-fluid.trycloudflare.com/ws/alerts`

---

## 🔑 Demo Access Credentials (Role-Based Access Control)
- **Super Admin:** `admin@shieldbank.com` / `AdminPass123!`
- **Fraud Analyst:** `analyst@shieldbank.com` / `AnalystPass123!`
- **Risk Manager:** `manager@shieldbank.com` / `ManagerPass123!`
- **Viewer:** `viewer@shieldbank.com` / `ViewerPass123!`

---

## 📦 What's Included in This Release
1. **Dual-Model ML Pipeline**:
   - Supervised Platt-scaled `XGBClassifier` achieving 92.55% precision and 0.9927 ROC-AUC.
   - Unsupervised `IsolationForest` detecting novel zero-day anomalies.
2. **Deterministic Composite Scoring**:
   - Multi-signal scoring engine blending Supervised ML (45%), Domain Rules / Velocity (35%), and Anomaly Detection (20%).
3. **Exact Mathematical Explainability**:
   - Sub-15ms local TreeSHAP attribution generating signed feature contribution scores for every transaction.
4. **Interactive Analyst Copilot**:
   - Gemini-powered contextual RAG assistant providing evidence summaries and guided next steps.
5. **Production Docker Stack**:
   - Self-contained multi-container deployment: FastAPI backend, Alpine Nginx frontend, PostgreSQL, and Redis event bus.
6. **Full Validation Suite**:
   - 45/45 automated backend test suite passing (100%).
