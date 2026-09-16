# Technical Architecture Document — FraudShield AI

**Product:** FraudShield AI

**Problem Statement:** FT-02 — AI-powered fraud detection for suspicious transactions in real time.

**Target:** Hack 2 Ignite 48-hour MVP

**Architecture style:** Modular monolith + event-driven components, designed to evolve into services later

---

# 1. Architecture Decision

For a **48-hour hackathon**, I would **not** build a large microservice architecture.

Use:

```
React
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
ML Engine
  ↓
Redis/WebSocket
```

with the AI copilot connected as a separate integration.

The architecture should be **modular internally**, even though it is deployed as a small number of services.

### Recommended deployment

```
                    ┌─────────────────────┐
                    │      React UI       │
                    │   Fraud Dashboard   │
                    └──────────┬──────────┘
                               │ HTTPS
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │    API Gateway      │
                    └─────┬─────┬─────────┘
                          │     │
             ┌────────────┘     └─────────────┐
             ▼                                ▼
      ┌──────────────┐                 ┌──────────────┐
      │ PostgreSQL   │                 │    Redis     │
      │ Persistent DB│                 │ Events/Cache │
      └──────────────┘                 └──────┬───────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ Fraud Engine │
                                      │ ML + Rules   │
                                      └──────┬───────┘
                                             │
                          ┌──────────────────┴──────────────┐
                          ▼                                 ▼
                   ┌──────────────┐                 ┌──────────────┐
                   │ SHAP/XAI     │                 │ Gemini       │
                   │ Explanation  │                 │ Copilot     │
                   └──────────────┘                 └──────────────┘
```

This is enough to demonstrate **real-time detection, explainability and investigation** without wasting your 48-hour window on infrastructure.

---

# 2. Technology Stack

## Frontend

### React + TypeScript

**Why:**

- Fast development
- Component-based architecture
- Excellent dashboard ecosystem
- Type safety
- Easy API integration
- Strong hackathon productivity

### Tailwind CSS

Use it for rapidly building:

- cards
- tables
- badges
- modals
- dashboards
- responsive layouts

### ECharts

Use for:

- fraud trends
- risk distribution
- transaction volume
- risk-factor visualization

---

# 3. Backend

## FastAPI

This should be your primary backend.

### Why FastAPI?

```
Python
  ↓
ML model
  ↓
FastAPI
```

You don't need to build a separate Java/Node backend around Python ML.

FastAPI gives you:

- REST APIs
- WebSockets
- automatic OpenAPI documentation
- Pydantic validation
- async support
- easy Python ML integration

---

# 4. Database

## PostgreSQL

Use PostgreSQL as the primary persistent database.

### Why?

Your system needs relationships between:

```
Customers
Transactions
Merchants
Devices
Alerts
Risk Scores
Investigations
Users
Models
```

This is relational data.

PostgreSQL is therefore a better fit than MongoDB for the MVP.

---

# 5. Redis

Redis is useful for the **real-time layer**.

Use it for:

- short-lived transaction events
- caching
- WebSocket event propagation
- rate limiting
- temporary state

Don't use Redis as your permanent transaction database.

Architecture:

```
Transaction
     ↓
Redis/Event Layer
     ↓
Fraud Engine
     ↓
PostgreSQL
```

---

# 6. Machine Learning

## Primary model

I'd use:

### XGBoost

for supervised fraud classification **if your selected training data supports it**.

Advantages:

- Excellent for tabular data
- Fast training
- Works well with engineered transaction features
- Easy to deploy
- Compatible with explainability workflows

---

## Secondary model

### Isolation Forest

Use it for anomaly detection.

```
Transaction
     ↓
Isolation Forest
     ↓
Anomaly Score
```

This gives you two perspectives:

```
                    Transaction
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Fraud Classifier      Anomaly Detector
              │                     │
              └──────────┬──────────┘
                         ▼
                     Risk Engine
```

---

# 7. Explainability

## SHAP

SHAP provides feature-level explanations for supported models.

Example:

```
Risk Score: 92

Contributors:

Transaction Amount       HIGH
Transaction Velocity     HIGH
Device Novelty           MEDIUM
Location Deviation       MEDIUM
Merchant Novelty         LOW
```

Important architecture principle:

> **The LLM should explain the evidence, not manufacture the evidence.**
> 

---

# 8. AI Copilot

## Gemini API

Use Gemini as the **investigation assistant**.

Architecture:

```
Transaction
    ↓
Fraud Engine
    ↓
Risk + Evidence
    ↓
Copilot Context
    ↓
Gemini
    ↓
Investigation Summary
```

The prompt should contain structured evidence:

```json
{
  "risk_score": 92,
  "risk_factors": [
    "high_amount",
    "new_device",
    "high_velocity"
  ]
}
```

Gemini then turns this into a human-readable investigation summary.

---

# 9. Real-Time Communication

## WebSockets

Your dashboard should receive alerts without requiring manual refresh.

```
Transaction
     ↓
Fraud Engine
     ↓
Risk > threshold
     ↓
Alert Created
     ↓
WebSocket Event
     ↓
React Dashboard
     ↓
🚨 Alert appears
```

This is important because FT-02 explicitly requires **real-time identification**.

---

# 10. Project Structure

I recommend the following structure:

```
fraudshield-ai/
│
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── LICENSE
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── ai-disclosure.md
│   ├── model-card.md
│   └── hackathon-notes.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   │
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── transactions.py
│   │   │       ├── alerts.py
│   │   │       ├── investigations.py
│   │   │       ├── dashboard.py
│   │   │       ├── copilot.py
│   │   │       └── health.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── merchant.py
│   │   │   ├── device.py
│   │   │   ├── transaction.py
│   │   │   ├── risk_score.py
│   │   │   ├── alert.py
│   │   │   └── investigation.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── transaction.py
│   │   │   ├── alert.py
│   │   │   ├── investigation.py
│   │   │   └── copilot.py
│   │   │
│   │   ├── services/
│   │   │   ├── transaction_service.py
│   │   │   ├── fraud_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── investigation_service.py
│   │   │   └── copilot_service.py
│   │   │
│   │   ├── ml/
│   │   │   ├── inference.py
│   │   │   ├── preprocessing.py
│   │   │   ├── feature_engineering.py
│   │   │   ├── anomaly_detector.py
│   │   │   ├── fraud_classifier.py
│   │   │   └── explainability.py
│   │   │
│   │   ├── realtime/
│   │   │   ├── websocket_manager.py
│   │   │   ├── event_processor.py
│   │   │   └── transaction_stream.py
│   │   │
│   │   └── utils/
│   │       ├── validators.py
│   │       ├── constants.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── test_transactions.py
│   │   ├── test_fraud.py
│   │   ├── test_risk.py
│   │   └── test_alerts.py
│   │
│   └── models_artifacts/
│       ├── fraud_model.pkl
│       ├── anomaly_model.pkl
│       └── feature_config.json
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       │
│       ├── components/
│       │   ├── ui/
│       │   ├── dashboard/
│       │   ├── transactions/
│       │   ├── alerts/
│       │   └── investigation/
│       │
│       ├── pages/
│       │   ├── Login.tsx
│       │   ├── Dashboard.tsx
│       │   ├── Transactions.tsx
│       │   ├── Alerts.tsx
│       │   ├── Investigation.tsx
│       │   └── Settings.tsx
│       │
│       ├── services/
│       │   ├── api.ts
│       │   ├── transactionApi.ts
│       │   ├── alertApi.ts
│       │   └── copilotApi.ts
│       │
│       ├── hooks/
│       │   ├── useWebSocket.ts
│       │   └── useAlerts.ts
│       │
│       ├── types/
│       │   ├── transaction.ts
│       │   ├── alert.ts
│       │   └── investigation.ts
│       │
│       └── utils/
│           ├── formatters.ts
│           └── risk.ts
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── notebooks/
│   ├── exploration.ipynb
│   ├── preprocessing.ipynb
│   ├── training.ipynb
│   └── evaluation.ipynb
│
└── scripts/
    ├── seed_database.py
    ├── train_model.py
    └── simulate_transactions.py
```

---

# 11. Database Architecture

The core relationships are:

```
USER
 │
 └── INVESTIGATION
          │
          └── ALERT
                │
                └── TRANSACTION
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
       CUSTOMER   MERCHANT     DEVICE
```

And:

```
TRANSACTION
     ↓
RISK SCORE
     ↓
EXPLANATION
```

---

# 12. Database Schema

## `users`

Stores people who use the FraudShield dashboard.

| Field | Type | Purpose |
| --- | --- | --- |
| id | UUID | Primary key |
| name | VARCHAR | User name |
| email | VARCHAR | Login email |
| password_hash | VARCHAR | Hashed password |
| role | VARCHAR | analyst/admin/manager |
| is_active | BOOLEAN | Account status |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

---

# 13. `customers`

Represents customers whose transactions are being analyzed.

| Field | Type | Purpose |
| --- | --- | --- |
| id | UUID | Primary key |
| external_id | VARCHAR | Dataset/customer identifier |
| name | VARCHAR | Demo customer name |
| country | VARCHAR | Customer country |
| risk_level | VARCHAR | Current customer risk |
| created_at | TIMESTAMP | Creation time |

### Relationship

```
Customer 1 ──────── N Transactions
```

---

# 14. `merchants`

Represents transaction merchants.

| Field | Type |
| --- | --- |
| id | UUID |
| external_id | VARCHAR |
| name | VARCHAR |
| category | VARCHAR |
| country | VARCHAR |
| risk_level | VARCHAR |
| created_at | TIMESTAMP |

Relationship:

```
Merchant 1 ──────── N Transactions
```

---

# 15. `devices`

Stores device context.

| Field | Type |
| --- | --- |
| id | UUID |
| device_fingerprint | VARCHAR |
| device_type | VARCHAR |
| operating_system | VARCHAR |
| first_seen_at | TIMESTAMP |
| last_seen_at | TIMESTAMP |

Relationship:

```
Device 1 ──────── N Transactions
```

---

# 16. `transactions`

This is the central table.

| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Internal primary key |
| transaction_id | VARCHAR | Public transaction identifier |
| customer_id | UUID | Customer |
| merchant_id | UUID | Merchant |
| device_id | UUID | Device |
| amount | DECIMAL | Transaction amount |
| currency | VARCHAR(3) | Currency |
| transaction_type | VARCHAR | Card/UPI/etc. |
| location | VARCHAR | Transaction location |
| ip_address | INET | IP if available |
| timestamp | TIMESTAMP | Transaction time |
| status | VARCHAR | approved/flagged/reviewed |
| created_at | TIMESTAMP | Ingestion timestamp |

### Relationships

```
Customer ────┐
Merchant ────┼──→ Transaction
Device ──────┘
```

---

# 17. `transaction_features`

Stores the features generated for the ML model.

| Field | Type |
| --- | --- |
| id | UUID |
| transaction_id | UUID |
| amount_deviation | FLOAT |
| velocity_score | FLOAT |
| location_deviation | FLOAT |
| merchant_novelty | FLOAT |
| device_novelty | FLOAT |
| historical_frequency | FLOAT |
| created_at | TIMESTAMP |

This keeps your raw transaction data separate from ML-derived features.

---

# 18. `risk_scores`

Stores model results.

| Field | Type |
| --- | --- |
| id | UUID |
| transaction_id | UUID |
| fraud_probability | FLOAT |
| anomaly_score | FLOAT |
| final_score | FLOAT |
| risk_level | VARCHAR |
| model_version | VARCHAR |
| created_at | TIMESTAMP |

Example:

```
fraud_probability = 0.87
anomaly_score = 0.91
final_score = 89
risk_level = HIGH
```

---

# 19. `risk_explanations`

Stores explainability output.

| Field | Type |
| --- | --- |
| id | UUID |
| risk_score_id | UUID |
| feature_name | VARCHAR |
| feature_value | VARCHAR |
| contribution | FLOAT |
| direction | VARCHAR |
| explanation | TEXT |

Example:

```
feature = transaction_amount
contribution = +0.42
direction = risk_increasing
```

---

# 20. `alerts`

Represents actionable fraud alerts.

| Field | Type |
| --- | --- |
| id | UUID |
| transaction_id | UUID |
| risk_score_id | UUID |
| severity | VARCHAR |
| status | VARCHAR |
| title | VARCHAR |
| description | TEXT |
| created_at | TIMESTAMP |
| resolved_at | TIMESTAMP |
| assigned_to | UUID |

### Relationship

```
Transaction 1 ──────── N Alerts
```

For the MVP, you can enforce one primary alert per high-risk transaction if that simplifies the implementation.

---

# 21. `investigations`

Tracks analyst activity.

| Field | Type |
| --- | --- |
| id | UUID |
| alert_id | UUID |
| analyst_id | UUID |
| status | VARCHAR |
| decision | VARCHAR |
| notes | TEXT |
| started_at | TIMESTAMP |
| completed_at | TIMESTAMP |

Example:

```
Alert
 ↓
Investigation
 ↓
UNDER_REVIEW
 ↓
CLEARED / ESCALATED
```

---

# 22. `copilot_sessions`

Stores AI investigation sessions.

| Field | Type |
| --- | --- |
| id | UUID |
| investigation_id | UUID |
| user_id | UUID |
| created_at | TIMESTAMP |

---

# 23. `copilot_messages`

Stores individual copilot messages.

| Field | Type |
| --- | --- |
| id | UUID |
| session_id | UUID |
| role | VARCHAR |
| content | TEXT |
| created_at | TIMESTAMP |

Roles:

```
user
assistant
```

---

# 24. `model_versions`

Tracks ML model versions.

| Field | Type |
| --- | --- |
| id | UUID |
| model_name | VARCHAR |
| version | VARCHAR |
| algorithm | VARCHAR |
| accuracy | FLOAT |
| precision | FLOAT |
| recall | FLOAT |
| f1_score | FLOAT |
| artifact_path | VARCHAR |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |

This becomes useful when judges ask:

> "Which model generated this risk score?"
> 

You can answer:

> Model `fraud-xgb-v1`.
> 

---

# 25. `audit_logs`

Tracks important system actions.

| Field | Type |
| --- | --- |
| id | UUID |
| user_id | UUID |
| action | VARCHAR |
| entity_type | VARCHAR |
| entity_id | UUID |
| metadata | JSONB |
| created_at | TIMESTAMP |

Example:

```
ANALYST
   ↓
Viewed Alert TX10482
   ↓
Marked ESCALATED
```

---

# 26. Relationship Summary

```
users
 │
 ├─────────────── investigations
 │                       │
 │                       ▼
 │                     alerts
 │                       │
 │                       ▼
 │                  transactions
 │                   /    |    \
 │                  /     |     \
 ▼                 ▼      ▼      ▼
audit_logs     customers merchants devices
                       │
                       ▼
              transaction_features
                       │
                       ▼
                  risk_scores
                       │
                       ▼
               risk_explanations

investigations
      │
      ▼
copilot_sessions
      │
      ▼
copilot_messages
```

---

# 27. Environment Variables

Create:

```
.env
```

and **never commit it**.

Use:

```
# Application
APP_NAME=FraudShield AI
ENVIRONMENT=development
DEBUG=true

# Backend
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=change-this
CORS_ORIGINS=http://localhost:5173

# PostgreSQL
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fraudshield

# Redis
REDIS_URL=redis://localhost:6379/0

# Gemini
GEMINI_API_KEY=your_api_key_here

# ML
FRAUD_MODEL_PATH=./models_artifacts/fraud_model.pkl
ANOMALY_MODEL_PATH=./models_artifacts/anomaly_model.pkl
MODEL_VERSION=fraud-v1

# Risk
HIGH_RISK_THRESHOLD=70
MEDIUM_RISK_THRESHOLD=30

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# 28. `.env.example`

Commit this:

```
APP_NAME=
ENVIRONMENT=
DEBUG=

DATABASE_URL=
REDIS_URL=

SECRET_KEY=

GEMINI_API_KEY=

FRAUD_MODEL_PATH=
ANOMALY_MODEL_PATH=
MODEL_VERSION=

HIGH_RISK_THRESHOLD=
MEDIUM_RISK_THRESHOLD=

CORS_ORIGINS=
```

But **never commit actual API keys**.

---

# 29. Configuration Rules

### Secrets

Never put:

```
Gemini API key
Database password
JWT secret
```

inside source code.

Bad:

```python
GEMINI_API_KEY = "AIza..."
```

Good:

```python
settings.GEMINI_API_KEY
```

---

# 30. API Design

Your core APIs should look like:

```
POST   /api/v1/transactions
GET    /api/v1/transactions
GET    /api/v1/transactions/{id}

GET    /api/v1/alerts
GET    /api/v1/alerts/{id}
PATCH  /api/v1/alerts/{id}

GET    /api/v1/investigations/{id}
POST   /api/v1/investigations

POST   /api/v1/copilot/chat

GET    /api/v1/dashboard/summary
GET    /api/v1/dashboard/risk-trends

WS     /api/v1/ws/alerts

GET    /health
```

---

# 31. Most Important API

### `POST /transactions`

Flow:

```
POST transaction
       ↓
Validate
       ↓
Feature generation
       ↓
ML inference
       ↓
Risk calculation
       ↓
Explanation
       ↓
Save transaction
       ↓
Save risk
       ↓
Create alert if necessary
       ↓
WebSocket event
```

This is the **heart of the entire application**.

---

# 32. Real-Time Processing

For the hackathon, you can simulate incoming transactions.

Create:

```
scripts/simulate_transactions.py
```

It generates:

```
TX1001
TX1002
TX1003
TX1004
...
```

every few seconds.

Then:

```
Simulator
    ↓
POST /transactions
    ↓
Fraud Engine
    ↓
Risk Score
    ↓
WebSocket
    ↓
Dashboard
```

This makes the "real-time" requirement visible to the judges.

---

# 33. Security Requirements

Even for a hackathon, implement basic security.

### Must have

- Password hashing
- JWT authentication
- Role-based access
- Input validation
- Environment-based secrets
- CORS configuration
- API error handling
- Audit logging

### Don't build

- Custom cryptography
- Custom authentication algorithms
- Complex IAM infrastructure

Use established libraries.

---

# 34. Data Privacy

For the prototype:

**Do not use real customer financial information.**

Use:

- public datasets
- synthetic data
- anonymized identifiers

For example:

```
Customer: C10234
Device: DEV8891
Merchant: MER123
```

rather than actual personal information.

---

# 35. Docker Architecture

Your `docker-compose.yml` can contain:

```
services:

frontend
backend
postgres
redis
```

You don't necessarily need a separate ML container.

The ML engine can initially run inside the FastAPI backend.

### Simplified:

```
Docker Compose
│
├── frontend
├── backend
├── postgres
└── redis
```

This will dramatically reduce deployment complexity.

---

# 36. GitHub Architecture

Because Hack 2 Ignite explicitly requires a clear development history, keep the repository clean and make **genuine periodic commits during the 48-hour development period**.

A sensible progression is:

```
1. Initial project structure
2. Backend foundation
3. Database schema
4. Transaction API
5. Feature engineering
6. Fraud model
7. Risk engine
8. Explainability
9. Alert system
10. WebSocket
11. Dashboard
12. Investigation flow
13. Copilot
14. Testing
15. Final integration
```

Only commit work that actually happened at that point. **Do not manufacture commit timestamps or history.**

---

# 37. Architecture Priority for the 48 Hours

Don't build everything in the folder tree.

Build in this order:

### Phase 1

```
PostgreSQL
+
FastAPI
+
Transaction API
```

### Phase 2

```
ML model
+
Feature engineering
+
Risk engine
```

### Phase 3

```
Alerts
+
WebSocket
```

### Phase 4

```
React dashboard
```

### Phase 5

```
SHAP
+
Copilot
```

### Phase 6

```
Testing
+
Demo
+
PPT
```

---

# 38. MVP Architecture

If you're running out of time, reduce it to:

```
React
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
Python ML
  ↓
SHAP
```

and simulate real-time transactions through the API.

Redis/WebSocket can then be added once the core flow works.

**Never sacrifice the working fraud pipeline just to have more technologies in your architecture diagram.**

---

# 39. What I Would NOT Build in V1

Explicit architectural exclusions:

```
❌ Microservices everywhere
❌ Kubernetes
❌ Kafka cluster
❌ Blockchain
❌ Mobile application
❌ Banking core integration
❌ Automated transaction blocking
❌ Complex graph database
❌ Custom authentication
❌ Multi-cloud deployment
❌ Federated learning
❌ Massive LLM agent system
```

They add complexity without helping your core demonstration.

---

# 40. Final Architecture

The architecture I would actually approve for your Hack 2 Ignite build is:

```
                         ┌──────────────────┐
                         │   React + TS     │
                         │ Fraud Dashboard  │
                         └────────┬─────────┘
                                  │
                           REST / WebSocket
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │    Application   │
                         └────────┬─────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
               ▼                  ▼                  ▼
        ┌────────────┐    ┌──────────────┐   ┌─────────────┐
        │ PostgreSQL │    │ Fraud Engine │   │    Redis    │
        │            │    │              │   │             │
        │ Transaction│    │ XGBoost/RF   │   │ Real-time   │
        │ Alert      │    │ Isolation    │   │ events      │
        │ Investigation│  │ Forest       │   │ cache       │
        └────────────┘    └──────┬───────┘   └─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
              ┌──────────┐              ┌──────────────┐
              │   SHAP   │              │    Gemini    │
              │   XAI    │              │ Investigation│
              └──────────┘              │   Copilot    │
                                        └──────────────┘
```

## The core engineering principle

**Don't build a banking system. Build a convincing fraud-intelligence engine.**

Your minimum successful technical loop is:

> **Transaction → Features → ML → Risk Score → Explanation → Alert → Investigation**
> 

Everything else should support that loop.

And because the Hack 2 Ignite rules require the actual prototype development and significant development work to occur within the 48-hour window, this architecture should be treated as the **blueprint**, with implementation and commits beginning/continuing within the official window.