# Product Requirements Document

## **FraudShield AI**

### Real-Time AI Fraud Detection & Investigation Platform

**Version:** 1.0 — MVP

**Problem Statement:** FT-02

**Product Type:** B2B FinTech / Fraud Intelligence Platform

**Primary Users:** Fraud analysts, risk teams, financial institutions

**Development Constraint:** 48-hour hackathon MVP

---

# 1. Executive Summary

**FraudShield AI** is a real-time AI-powered fraud detection platform designed to identify suspicious financial transactions, assign a risk score, explain the reasons behind the risk, and help fraud analysts investigate flagged transactions.

Instead of relying on a single rule such as:

> "Transaction amount > ₹50,000 = fraud"
> 

the platform evaluates multiple signals together, including transaction amount, transaction frequency, merchant behaviour, location, device information and historical patterns.

The product converts raw transaction events into an actionable workflow:

```
Transaction
     ↓
Real-Time Processing
     ↓
Feature Engineering
     ↓
Fraud Detection
     ↓
Risk Score
     ↓
Explainability
     ↓
Alert
     ↓
Investigation
     ↓
Analyst Decision
```

The MVP is deliberately focused on **detection + explanation + investigation**, rather than attempting to become a complete banking fraud-prevention infrastructure.

---

# 2. Problem

Financial institutions process a large number of transactions continuously.

The challenge isn't simply identifying whether a transaction is technically valid.

A fraudulent transaction may:

- use valid credentials,
- originate from a legitimate account,
- resemble normal activity,
- occur within seconds,
- involve a previously unseen merchant/device/location,
- or become suspicious only when multiple transactions are considered together.

Therefore, the product needs to answer:

> **"Is this transaction behaving unusually enough that a fraud analyst should investigate it?"**
> 

And, equally importantly:

> **"Why did the system consider it suspicious?"**
> 

---

# 3. Target Users

## Primary User — Fraud Analyst

A fraud analyst monitors transaction activity and investigates suspicious events.

### Their needs

- See suspicious transactions immediately.
- Understand why a transaction was flagged.
- Prioritize high-risk transactions.
- Investigate customer/transaction history.
- Reduce time spent manually reviewing transactions.
- Make an informed decision.

---

## Secondary User — Risk Manager

A risk manager wants an overview of fraud patterns.

### Their needs

- Fraud trends.
- Risk distribution.
- Alert volume.
- Detection performance.
- High-risk merchants/customers.
- Model performance.

---

## Secondary User — System Administrator

Responsible for configuring the system.

### Their needs

- Manage users.
- Configure thresholds.
- Monitor system health.
- Manage model versions.
- Review system logs.

---

# 4. User Personas

### Persona 1 — Fraud Analyst

**Goal:** Quickly determine whether a flagged transaction requires investigation.

**Pain point:** Too many alerts and insufficient context.

---

### Persona 2 — Risk Manager

**Goal:** Understand overall fraud exposure.

**Pain point:** Raw transaction data doesn't provide a clear operational picture.

---

### Persona 3 — Administrator

**Goal:** Keep the fraud detection platform operational and configurable.

**Pain point:** Fraud systems can become difficult to manage as rules and models grow.

---

# 5. Product Goals

## Primary goal

Build a working prototype capable of:

> **Receiving transaction events → detecting suspicious behaviour → generating a risk score → explaining the score → alerting an analyst.**
> 

### Secondary goals

1. Demonstrate real-time detection.
2. Reduce unnecessary investigation effort.
3. Provide explainable AI output.
4. Give analysts a centralized investigation dashboard.
5. Create an architecture that can accept additional fraud-detection capabilities later.

---

# 6. Non-Goals

The MVP will **not** attempt to:

- Replace a bank's core transaction-processing system.
- Automatically block every suspicious transaction.
- Guarantee that a transaction is fraudulent.
- Provide legally binding fraud decisions.
- Replace human investigators.
- Build a complete banking platform.
- Integrate with real banking accounts.
- Process actual customer financial data.
- Build a production-grade payment gateway.

This distinction is important.

The product provides **decision support**, not an unquestionable automated verdict.

---

# 7. Core Product Concept

FraudShield AI uses multiple signals to determine transaction risk.

For example:

```
Transaction Amount
       +
Transaction Velocity
       +
Location
       +
Device
       +
Merchant
       +
Historical Behaviour
       ↓
   Risk Engine
       ↓
Risk Score: 0–100
```

Example:

### Transaction

```
Amount: ₹97,500
Merchant: New
Device: New
Location: Unusual
Velocity: 7 transactions / 3 minutes
```

System:

```
Risk Score: 94/100
Risk Level: HIGH
```

Explanation:

```
• Unusually high transaction amount
• New device detected
• Unusual geographic location
• High transaction velocity
• Merchant not previously observed
```

---

# 8. Feature Requirements

## P0 — Must Have

These are essential for the MVP.

### 8.1 Real-Time Transaction Ingestion

The system must accept transaction events.

Example:

```json
{
  "transaction_id": "TX10482",
  "customer_id": "C1023",
  "amount": 97500,
  "merchant_id": "M882",
  "location": "Pune",
  "device_id": "D991",
  "timestamp": "2026-09-16T10:30:00"
}
```

The system should process the transaction immediately.

---

## 8.2 Transaction Validation

Before model processing:

- Validate required fields.
- Check data types.
- Detect missing/invalid values.
- Normalize transaction data.

Invalid transactions should not crash the system.

---

## 8.3 Feature Engineering

The system should derive useful fraud-related features.

Examples:

### Transaction-level

- Amount
- Transaction type
- Merchant
- Timestamp

### Behavioural

- Transactions per minute/hour
- Average transaction amount
- Deviation from historical amount
- Time since previous transaction

### Contextual

- New device
- New merchant
- Location deviation
- Transaction frequency

---

# 9. Fraud Detection Engine

The MVP should combine two complementary approaches.

## Layer 1 — Anomaly Detection

Example:

**Isolation Forest**

Purpose:

> Identify transactions that are unusual compared with observed behaviour.
> 

---

## Layer 2 — Supervised Fraud Model

Depending on dataset availability:

- Random Forest
- XGBoost/LightGBM
- Logistic Regression as baseline

Purpose:

> Estimate fraud probability based on learned patterns.
> 

---

## Combined Risk Engine

```
Anomaly Score
       +
Fraud Probability
       +
Behavioural Signals
       ↓
Risk Engine
       ↓
Risk Score 0–100
```

This makes the system more robust than relying on one algorithm.

---

# 10. Risk Scoring

Every processed transaction receives:

### Risk score

```
0–30      LOW
31–70     MEDIUM
71–100    HIGH
```

These thresholds should be configurable rather than permanently hard-coded.

Example:

```
TX10482

Risk Score: 94
Risk Level: HIGH
```

---

# 11. Explainable AI

This is a **must-have** rather than merely a cosmetic feature.

The analyst shouldn't see:

> "AI says fraud."
> 

They should see:

> **"These factors contributed to the elevated risk."**
> 

Use **SHAP or equivalent model-explanation techniques** where applicable.

Example:

```
Risk Contributors

Transaction amount       ██████████
Transaction velocity     ████████
New device               ██████
Location deviation       █████
Merchant novelty         ████
```

The exact explanation should correspond to the model/features actually used.

---

# 12. Real-Time Alerting

When risk exceeds the configured threshold:

```
🚨 HIGH-RISK TRANSACTION
```

The alert should contain:

- Transaction ID
- Customer ID
- Amount
- Risk score
- Timestamp
- Risk level
- Primary risk factors

---

# 13. Fraud Analyst Dashboard

The dashboard is the primary operational interface.

### Dashboard should show

```
┌───────────────────────────────────────────┐
│ FRAUDSHIELD AI                            │
├────────────┬────────────┬─────────────────┤
│ Transactions│ High Risk  │ Alerts          │
│ 12,842      │ 137        │ 284             │
├────────────┴────────────┴─────────────────┤
│                                           │
│      Transaction Risk Distribution        │
│                                           │
├───────────────────────────────────────────┤
│ Recent High-Risk Transactions             │
│                                           │
│ TX10482  ₹97,500   94   HIGH              │
│ TX10481  ₹12,200   82   HIGH              │
│ TX10479  ₹4,800    65   MEDIUM            │
└───────────────────────────────────────────┘
```

---

# 14. Transaction Investigation Page

Clicking an alert should open detailed information.

### Screen

```
Transaction #TX10482

₹97,500

HIGH RISK
94 / 100

─────────────────────

Customer
C1023

Merchant
M882

Device
D991

Location
Pune

─────────────────────

WHY FLAGGED?

✓ High transaction velocity
✓ New device
✓ Unusual location
✓ Amount deviation
✓ New merchant

─────────────────────

[ Investigate with AI ]

[ Mark Reviewed ]
[ Escalate ]
```

---

# 15. AI Investigation Copilot

### MVP status: **Must Have, but constrained**

The copilot should help the analyst understand an already-flagged transaction.

Example:

**Analyst:**

> Why was TX10482 flagged?
> 

**Copilot:**

> The transaction received a high risk score because its amount and transaction frequency differ significantly from the observed pattern, while the device, merchant and location signals also indicate unusual activity.
> 

The copilot should **not independently declare a transaction fraudulent**.

It should summarize evidence produced by the detection system.

---

# 16. Transaction Search & Filtering

Analysts should be able to filter:

- Risk level
- Transaction amount
- Date/time
- Merchant
- Customer
- Status
- Risk score

Example:

```
Risk: HIGH
Status: UNREVIEWED
Date: Today
```

---

# 17. Investigation Status

Each alert should have a lifecycle:

```
NEW
 ↓
UNDER REVIEW
 ↓
ESCALATED / CLEARED
```

This gives the prototype a genuine operational workflow rather than being only an ML demo.

---

# 18. Nice-to-Have Features

These should **not interfere with the core MVP**.

## P1

### Customer Risk Profile

```
Customer C1023

Normal avg transaction: ₹2,500
Current transaction: ₹97,500

Risk trend: Increasing
```

### Merchant Risk Profile

Show:

- Transaction volume
- Suspicious transaction percentage
- Risk history

### Device Intelligence

Detect:

- New device
- Multiple accounts using same device
- Device behaviour changes

### Transaction Graph

Visualize:

```
Customer
   │
   ├── Device
   │
   ├── Merchant
   │
   └── Location
```

This can help identify connected suspicious behaviour.

---

# 19. P2 — Future Features

These are **not part of the MVP**.

- Production banking integrations
- Advanced graph neural networks
- Federated learning
- Cross-bank fraud intelligence
- Automated transaction blocking
- Multi-country regulatory compliance
- Mobile applications
- Fully autonomous fraud response
- Enterprise SIEM integration
- Large-scale distributed infrastructure

---

# 20. End-to-End User Flow

## Step 1 — Transaction arrives

```
Payment Event
     ↓
FraudShield
```

---

## Step 2 — Validation

```
Is transaction valid?
      │
 ┌────┴────┐
NO        YES
│          │
Reject     Continue
```

---

## Step 3 — Feature generation

The system calculates behavioural and contextual features.

---

## Step 4 — AI detection

```
Features
   ↓
Anomaly Model
   +
Fraud Model
   ↓
Risk Engine
```

---

## Step 5 — Risk scoring

```
Risk = 94
```

---

## Step 6 — Explanation

SHAP/model analysis identifies the main contributing factors.

---

## Step 7 — Alert

```
🚨 HIGH-RISK TRANSACTION
```

---

## Step 8 — Analyst opens alert

Analyst sees:

- transaction information
- risk score
- explanation
- historical/contextual signals

---

## Step 9 — AI Copilot

Analyst asks:

> "Summarize this transaction."
> 

Copilot provides an evidence-based summary.

---

## Step 10 — Human decision

Analyst chooses:

```
CLEAR
   OR
ESCALATE
   OR
MARK FOR INVESTIGATION
```

---

# 21. MVP Definition

For the Hack 2 Ignite online round, the MVP is:

### **Must demonstrate this exact journey**

```
Generate Transaction
        ↓
Real-Time Processing
        ↓
AI Fraud Detection
        ↓
Risk Score
        ↓
Explainable Factors
        ↓
Real-Time Alert
        ↓
Analyst Dashboard
        ↓
Investigation
        ↓
AI Copilot
        ↓
Human Decision
```

If this works reliably, **stop adding features**.

That's your MVP.

---

# 22. Technical Architecture

```
                    TRANSACTION SOURCE
                           │
                           ▼
                    INGESTION LAYER
                           │
                           ▼
                  VALIDATION / NORMALIZATION
                           │
                           ▼
                   FEATURE ENGINE
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      ANOMALY DETECTION          FRAUD CLASSIFIER
      Isolation Forest           XGBoost / RF
              │                         │
              └────────────┬────────────┘
                           ▼
                       RISK ENGINE
                           │
                     RISK SCORE
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
         EXPLAINABILITY             ALERT ENGINE
             SHAP                      │
              │                        │
              └────────────┬───────────┘
                           ▼
                      FASTAPI
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
         React UI                    PostgreSQL
             │
             ▼
       Investigation UI
             │
             ▼
       Gemini Copilot
```

---

# 23. Suggested Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React + TypeScript |
| UI | Tailwind CSS |
| Charts | ECharts/Recharts |
| Backend | FastAPI |
| Database | PostgreSQL |
| Cache/stream | Redis |
| ML | Python + scikit-learn |
| Advanced model | XGBoost/LightGBM |
| Explainability | SHAP |
| AI Copilot | Gemini API |
| Real-time | WebSocket |
| Deployment | Docker |

### Important:

You **do not need every technology listed above**.

For a 48-hour hackathon:

**FastAPI + PostgreSQL + Python ML + React + WebSocket** is enough.

Add Redis only if it genuinely helps the real-time architecture.

---

# 24. Data Strategy

For the hackathon prototype, use a **publicly available fraud dataset or synthetic transaction data**, depending on the final implementation requirements.

The system should demonstrate both:

### Historical data

Used to train/validate the model.

### Live/simulated stream

Used to demonstrate real-time detection.

```
Historical Dataset
       ↓
Train Model
       ↓
Saved Model
       ↓
Live Transaction Simulator
       ↓
Real-Time Detection
```

This separation is important.

---

# 25. Success Metrics

Don't measure success only through:

> **Accuracy**
> 

Fraud datasets are often highly imbalanced, making accuracy potentially misleading.

The MVP should track:

### ML metrics

- Precision
- Recall
- F1-score
- ROC-AUC / PR-AUC where appropriate
- False-positive rate

### Product metrics

#### Detection latency

**Goal:** suspicious transaction → alert in seconds in the prototype.

#### Investigation time

Measure:

> How quickly can an analyst understand a flagged transaction?
> 

#### Explanation coverage

Percentage of alerts for which the system can provide meaningful model-based contributing factors.

#### Alert prioritization

Can the system surface high-risk transactions above lower-risk events?

---

# 26. Hackathon Success Criteria

For the competition itself, I'd define the following internal targets:

### Technical

```
✔ Real-time event processing
✔ Working ML detection
✔ Explainable risk score
✔ Stable API
✔ Functional dashboard
✔ End-to-end demo
```

### Product

```
✔ Clear user
✔ Clear problem
✔ Clear workflow
✔ Demonstrable impact
✔ Simple UX
```

### Presentation

A judge should understand the product within approximately **30–60 seconds** of seeing the demo.

---

# 27. North Star Metric

For a future production product, I would use:

## **Time-to-Action on High-Risk Transactions**

The goal isn't merely to generate more alerts.

It's to help an analyst go from:

**Suspicious transaction detected**

to:

**Understand → investigate → act**

faster.

---

# 28. Version 1 Deliberately Does NOT Build

This section is extremely important.

## ❌ No real banking integration

We use simulated/public data.

## ❌ No automatic transaction blocking

The MVP recommends/alerts; humans remain in control.

## ❌ No guarantee of fraud

The system estimates risk.

## ❌ No complete AML platform

AML is much broader than this MVP.

## ❌ No mobile app

Web dashboard is sufficient.

## ❌ No multi-bank infrastructure

Out of scope for a 48-hour prototype.

## ❌ No massive microservice architecture

Keep the system simple and deployable.

## ❌ No blockchain

Blockchain doesn't provide an inherent benefit for the core FT-02 detection problem.

## ❌ No unnecessary LLM decision-making

LLM is an investigation assistant, not the primary fraud detector.

---

# 29. Key Product Differentiator

I would position the product around:

# **Detect → Explain → Investigate**

rather than simply:

# **Detect Fraud**

The differentiation becomes:

```
Traditional ML
      ↓
"Fraud probability = 91%"
```

versus:

```
FraudShield AI

Risk: 91/100
      ↓
WHY?
      ↓
5 contributing signals
      ↓
WHAT NOW?
      ↓
AI-assisted investigation
      ↓
Analyst decision
```

That gives you a complete product story.

---

# 30. Offline Round Strategy

The rulebook gives shortlisted teams a new feature/requirement/challenge to integrate into the existing prototype.

Therefore, **don't tightly couple the MVP**.

Design these as independent modules:

```
                    CORE
                     │
       ┌─────────────┼──────────────┐
       ↓             ↓              ↓
 Detection       Risk Engine    Explainability
       │             │              │
       └─────────────┼──────────────┘
                     ↓
                   API
                     ↓
                Dashboard
```

Then an offline requirement can become another module:

```
                 NEW OFFLINE FEATURE
                         │
                         ▼
                       API
                         │
                         ▼
                  Existing System
```

This directly prepares you for the second round.

---

# 31. Product Principles

### Principle 1 — Explainability over black box

Every high-risk alert should answer:

> **Why?**
> 

### Principle 2 — Human-in-the-loop

AI supports the analyst rather than pretending to be the final authority.

### Principle 3 — Real-time first

The core demonstration must show transaction → detection → alert quickly.

### Principle 4 — Evidence over hype

Every AI explanation should be grounded in actual transaction/model signals.

### Principle 5 — Modular architecture

Make the system easy to extend during the offline challenge.

### Principle 6 — MVP discipline

Don't sacrifice reliability for feature count.

---

# 32. Final MVP Scope

If I were the **Senior PM responsible for the 48-hour build**, I would freeze the MVP at these **10 capabilities**:

| # | Capability | Priority |
| --- | --- | --- |
| 1 | Transaction ingestion | 🔴 MUST |
| 2 | Data validation & feature engineering | 🔴 MUST |
| 3 | Fraud/anomaly model | 🔴 MUST |
| 4 | Risk scoring | 🔴 MUST |
| 5 | Explainability | 🔴 MUST |
| 6 | Real-time alerts | 🔴 MUST |
| 7 | Fraud dashboard | 🔴 MUST |
| 8 | Transaction investigation | 🔴 MUST |
| 9 | AI investigation copilot | 🔴 MUST |
| 10 | Analyst decision/status | 🔴 MUST |
| 11 | Customer risk profile | 🟡 NICE |
| 12 | Merchant intelligence | 🟡 NICE |
| 13 | Transaction graph | 🟡 NICE |
| 14 | Advanced automation | ⚪ FUTURE |

**The first 10 are the product. Everything else is optional.**

---

## 🚀 Product one-liner

> **FraudShield AI is a real-time fraud intelligence platform that detects suspicious transactions, explains the risk signals behind them, and helps fraud analysts investigate and prioritize threats faster.**
> 

And the core product loop is:

# **TRANSACTION → DETECT → SCORE → EXPLAIN → ALERT → INVESTIGATE → ACT**

That is the product I would build for **FT-02** within the Hack 2 Ignite constraints.