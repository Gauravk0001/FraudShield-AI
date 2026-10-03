# FraudShield AI
## Frontend Specification & Third-Party Integration Document

**Version:** 1.0  
**Product:** FraudShield AI  
**Frontend:** React + TypeScript  
**Styling:** Tailwind CSS  
**Charts:** ECharts / Recharts  
**Backend:** FastAPI  
**Database:** PostgreSQL  
**Real-time:** Redis + WebSocket  
**AI:** Gemini API  
**ML:** Python + XGBoost/Isolation Forest + SHAP

---

# 1. Product UI Vision

FraudShield AI is not a generic banking dashboard.

The interface should communicate:

> **Detect → Explain → Investigate → Decide**

The UI should allow a fraud analyst to understand a suspicious transaction within seconds.

The primary screen should answer four questions immediately:

1. **What is happening?**
2. **Which transactions are risky?**
3. **Why are they risky?**
4. **What should I investigate next?**

The visual language should therefore feel:

- Professional
- Security-focused
- Data-rich
- Calm
- Trustworthy
- Modern
- Fast
- Operational rather than decorative

Avoid excessive animations, neon colors, excessive gradients, and unnecessarily complicated dashboards.

---

# 2. Design System

## 2.1 Design principles

### Clarity

Every important number should have an obvious meaning.

### Hierarchy

High-risk information should visually stand out without making the entire dashboard look alarming.

### Consistency

The same risk level should always use the same visual treatment.

### Density

Fraud analysts need to inspect many transactions quickly, so tables can be information-dense while maintaining readable spacing.

### Explainability

Risk scores must always have an obvious path to:

> "Why did the system flag this?"

---

# 3. Color Palette

FraudShield AI should use a dark security-operations visual identity with restrained accent colors.

## Primary colors

| Token | Hex | Usage |
|---|---|---|
| Primary | `#2563EB` | Main actions |
| Primary Hover | `#1D4ED8` | Button hover |
| Primary Light | `#DBEAFE` | Selected states |
| Background | `#F8FAFC` | Main application background |
| Surface | `#FFFFFF` | Cards/panels |
| Surface Secondary | `#F1F5F9` | Secondary sections |
| Border | `#E2E8F0` | Borders/dividers |
| Text Primary | `#0F172A` | Main text |
| Text Secondary | `#475569` | Secondary text |
| Text Muted | `#94A3B8` | Supporting text |

---

# 4. Risk Colors

Risk colors are semantic and must remain consistent throughout the application.

| Risk | Hex | Usage |
|---|---|---|
| Critical | `#991B1B` | Severe security event |
| High | `#DC2626` | High-risk fraud |
| Medium | `#D97706` | Suspicious |
| Low | `#16A34A` | Low risk |
| Neutral | `#64748B` | Unknown / unavailable |

Do not use red for ordinary errors everywhere because users could confuse system errors with fraud alerts.

---

# 5. Status Colors

| Status | Hex |
|---|---|
| Success | `#16A34A` |
| Warning | `#D97706` |
| Error | `#DC2626` |
| Information | `#2563EB` |
| Neutral | `#64748B` |

---

# 6. Optional Operations Dark Theme

For the actual analyst workspace, a dark operations theme can be provided.

| Token | Hex |
|---|---|
| Dark Background | `#0B1220` |
| Dark Surface | `#111827` |
| Dark Surface Secondary | `#1F2937` |
| Dark Border | `#334155` |
| Dark Text | `#F8FAFC` |
| Dark Secondary Text | `#CBD5E1` |

The application should support one consistent theme rather than mixing light and dark components randomly.

---

# 7. Typography

## Primary font

**Inter**

Use Inter for:

- Navigation
- Tables
- Buttons
- Labels
- Dashboard values
- Forms
- Body text

## Font hierarchy

| Element | Size | Weight |
|---|---:|---:|
| Page title | 28–32px | 700 |
| Section title | 20–24px | 600 |
| Card title | 16–18px | 600 |
| Body | 14–16px | 400 |
| Small text | 12–13px | 400 |
| Table text | 13–14px | 400/500 |
| KPI number | 28–36px | 700 |

Use sentence case rather than excessive uppercase text.

---

# 8. Spacing System

Use a consistent 4px-based spacing system.

```text id="e4p9tq"
4px
8px
12px
16px
20px
24px
32px
40px
48px
64px
```

Recommended usage:

### 4px

Icon/text micro-spacing.

### 8px

Inside compact controls.

### 12px

Input internal spacing.

### 16px

Normal card padding.

### 24px

Large card padding / section spacing.

### 32px

Major dashboard sections.

### 48px+

Page-level spacing.

---

# 9. Border Radius

Use moderate rounding.

| Component | Radius |
|---|---:|
| Button | 8px |
| Input | 8px |
| Card | 12px |
| Modal | 16px |
| Badge | 9999px |
| Avatar | 50% |

Avoid excessive "bubble" styling.

---

# 10. Shadows

Use shadows sparingly.

### Small

For dropdowns and small floating controls.

### Medium

For cards that need elevation.

### Large

For modals/dialogs.

Most dashboard cards should rely on borders rather than heavy shadows.

---

# 11. Application Layout

Desktop layout:

```text id="l9v5sh"
┌───────────────────────────────────────────────────────┐
│                    TOP HEADER                         │
├───────────────┬───────────────────────────────────────┤
│               │                                       │
│   SIDEBAR     │              MAIN CONTENT             │
│               │                                       │
│ Dashboard     │                                       │
│ Transactions  │                                       │
│ Alerts        │                                       │
│ Investigate   │                                       │
│ Copilot       │                                       │
│               │                                       │
│ Settings      │                                       │
└───────────────┴───────────────────────────────────────┘
```

Recommended dimensions:

```text
Sidebar: 240–260px
Header: 64px
Main content: flexible
Page padding: 24–32px
```

---

# 12. Responsive Behavior

### Desktop

Primary target.

Use:

```text
≥ 1280px
```

for full dashboard layout.

### Tablet

At approximately:

```text
768–1279px
```

Collapse the sidebar.

### Mobile

Below approximately:

```text
768px
```

Use:

- Bottom navigation or drawer
- Stacked cards
- Horizontally scrollable tables
- Full-screen investigation panels
- Simplified charts

The analyst dashboard should remain usable but does not need to reproduce every desktop feature perfectly on mobile.

---

# 13. Navigation

Primary navigation:

```text id="z8k9fa"
Overview
Transactions
Alerts
Investigations
Copilot
Models
Audit Logs
Settings
```

Not every role sees every navigation item.

Example:

### Analyst

```text
Overview
Transactions
Alerts
Investigations
Copilot
```

### Risk Manager

```text
Overview
Transactions
Alerts
Investigations
Copilot
Models
```

### Admin

```text
Overview
Transactions
Alerts
Investigations
Copilot
Models
Audit Logs
Settings
```

---

# 14. Buttons

## Primary button

Usage:

- Create investigation
- Submit transaction
- Save changes
- Resolve investigation

Style:

```text
Background: #2563EB
Text: #FFFFFF
Radius: 8px
Height: 40px
Padding: 12px 16px
```

Hover:

```text
#1D4ED8
```

## Secondary button

White/light surface with border.

Use for:

- Cancel
- Back
- View details

## Destructive button

Use only for genuinely destructive operations.

```text
#DC2626
```

Never use a destructive button merely because an action is important.

---

# 15. Button States

Every interactive button should support:

```text
Default
Hover
Focus
Active
Disabled
Loading
```

Loading example:

```text
[ Processing... ]
```

Do not allow users to accidentally submit the same operation repeatedly.

---

# 16. Inputs

Inputs should have:

- Label
- Optional description
- Input
- Validation message

Example:

```text
Transaction Amount

[ ₹ 125,000.00                         ]

Amount must be greater than zero.
```

### Focus

Use a clear focus ring.

### Error

Use:

- Red border
- Error icon where useful
- Short explanation

Never rely only on color to communicate an error.

---

# 17. Select / Dropdown

Use dropdowns for controlled values such as:

```text
Risk level
Transaction type
Currency
Investigation status
Assigned analyst
```

For long lists, provide search.

---

# 18. Cards

Cards are the primary information containers.

Recommended:

```text
Background: #FFFFFF
Border: #E2E8F0
Radius: 12px
Padding: 20–24px
```

Example KPI card:

```text
HIGH-RISK TRANSACTIONS

24

↑ 12.5%

Last 24 hours
```

The visual hierarchy should be:

```text
Label
↓
Important number
↓
Context
```

---

# 19. KPI Cards

Dashboard KPIs:

1. Total transactions
2. High-risk transactions
3. Active alerts
4. Open investigations
5. Fraud detection rate
6. Average detection latency

Avoid displaying too many KPIs.

The first dashboard view should focus on the most actionable metrics.

---

# 20. Risk Badge

Example:

```text
● HIGH
```

Use consistent semantic colors.

Recommended:

```text
HIGH      → red
MEDIUM    → amber
LOW       → green
UNKNOWN   → slate
```

Never use green to mean "fraud detected."

Green means low/healthy/successful state.

---

# 21. Tables

The transaction table is one of the most important components.

Columns:

```text
Transaction ID
Timestamp
Customer
Amount
Merchant
Risk Score
Risk Level
Status
Action
```

Example:

```text
TXN-84721
10:32:15
Customer 102
₹84,500
Online Store
91
HIGH
Flagged
View
```

Use:

- Sticky table header
- Sorting
- Filtering
- Pagination
- Search
- Row hover
- Click-to-investigate

---

# 22. Transaction Detail Panel

Selecting a transaction should reveal:

```text
Transaction
────────────────────────────

Transaction ID
TXN-84721

Amount
₹84,500

Customer
CUS-102

Merchant
MER-008

Timestamp
15 Sep 2026, 10:32

Risk Score
91 / 100

Risk Level
HIGH
```

Then:

```text
WHY WAS THIS FLAGGED?

• Unusual transaction amount
• New device
• Location deviation
• High transaction velocity
```

Then:

```text
[ Start Investigation ]
```

---

# 23. Risk Explanation Component

This is a core differentiator.

Display the top contributing factors.

Example:

```text
WHY THIS TRANSACTION IS HIGH RISK

██████████████  Amount deviation
██████████     Device novelty
████████       Transaction velocity
██████         Location deviation
```

Each factor should show:

- Feature name
- Value
- Contribution
- Direction
- Human-readable explanation

---

# 24. Investigation Workspace

The investigation page should be divided into three areas.

```text id="c93y7h"
┌────────────────────────────────────────────────────────┐
│ Investigation Header                                   │
├──────────────────────┬─────────────────────────────────┤
│                      │                                 │
│ Transaction Evidence │ AI Copilot                     │
│                      │                                 │
│ Risk Score           │ Chat                            │
│ SHAP Factors         │                                 │
│ Customer Information │                                 │
│ Transaction History  │                                 │
│                      │                                 │
├──────────────────────┴─────────────────────────────────┤
│ Investigation Notes / Decision                         │
└────────────────────────────────────────────────────────┘
```

The evidence area must remain visible while using Copilot.

---

# 25. AI Copilot UI

The Copilot should feel like an investigation assistant, not a generic chatbot.

Header:

```text
FraudShield Copilot
Investigation Assistant
```

Suggested quick actions:

```text
Explain this alert
Summarize evidence
What should I investigate next?
Show unusual behavior
Generate investigation summary
```

The AI response should clearly distinguish:

```text
Evidence
AI interpretation
Suggested next step
```

---

# 26. AI Trust Indicator

Show:

> AI-generated assistance — verify before making a decision.

This is particularly important for a fraud system.

The UI should never imply that the AI's answer is automatically correct.

---

# 27. Alerts Page

Structure:

```text
Alerts

[ Search ] [ Risk ] [ Status ] [ Date ]

──────────────────────────────────────────

HIGH   TXN-84721    ₹84,500    91    OPEN
HIGH   TXN-84711    ₹52,300    88    OPEN
MEDIUM TXN-84690    ₹18,000    54    REVIEW
```

Use visual priority to help analysts identify high-risk alerts.

---

# 28. Real-Time Alert Notification

When a high-risk transaction arrives:

```text
┌─────────────────────────────────┐
│ HIGH-RISK TRANSACTION            │
│                                  │
│ TXN-84721                        │
│ Risk Score: 91                  │
│ Amount: ₹84,500                 │
│                                  │
│ [Investigate]                   │
└─────────────────────────────────┘
```

Do not interrupt the analyst with excessive notifications.

Use notification grouping where possible.

---

# 29. Charts

Recommended charts:

### Transaction volume

Line chart.

### Risk distribution

Bar/donut chart.

### Risk trend

Line chart.

### Alert severity

Bar chart.

### Detection performance

Precision / recall / F1.

Avoid charts that don't answer an operational question.

---

# 30. Loading States

Never leave blank screens while data loads.

Use:

- Skeleton loaders
- Spinners for short actions
- Progress indicators for long operations

Example:

```text
████████████████
████████
██████████████
```

---

# 31. Empty States

Example:

```text
No active investigations

There are currently no investigations
requiring your attention.

[ View Transactions ]
```

Avoid:

> "No data."

Tell the user what the empty state means.

---

# 32. Error States

Example:

```text
Unable to load alerts

We couldn't retrieve the latest alerts.
Your existing data has not been deleted.

[ Try Again ]
```

Provide a retry action where appropriate.

---

# 33. Modal Rules

Use modals for:

- Confirmation
- Small forms
- Important warnings

Do not put entire workflows inside tiny modals.

Recommended:

```text
Width: 480–640px
Radius: 16px
Padding: 24px
```

For complex investigation workflows, use a dedicated page rather than a modal.

---

# 34. Confirmation Modal

For important actions:

```text
Resolve Investigation?

You are about to mark this investigation
as resolved.

Decision:
[ Confirmed Fraud ▼ ]

Notes:
[............................]

[Cancel] [Resolve Investigation]
```

The action should require deliberate confirmation.

---

# 35. Toast Notifications

Use toasts for short-lived feedback.

Examples:

```text
✓ Investigation created
✓ Alert assigned
✓ Transaction processed
```

Errors:

```text
⚠ Unable to save investigation
```

Do not use toasts for information that requires user action or long-term visibility.

---

# 36. Accessibility

Target WCAG 2.2 AA principles.

Requirements:

- Keyboard navigation
- Visible focus indicators
- Adequate contrast
- Semantic HTML
- Accessible labels
- Screen-reader-friendly controls
- Don't rely solely on color
- Appropriate ARIA where necessary

Example:

Do not communicate:

```text
Red = High
```

only through color.

Instead:

```text
HIGH
```

plus the visual treatment.

---

# 37. Frontend Architecture

Recommended structure:

```text
frontend/
├── src/
│   ├── app/
│   ├── components/
│   │   ├── ui/
│   │   ├── dashboard/
│   │   ├── transactions/
│   │   ├── alerts/
│   │   ├── investigations/
│   │   └── copilot/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   ├── layouts/
│   ├── routes/
│   └── main.tsx
```

---

# 38. State Management

Separate:

### Server state

Examples:

- Transactions
- Alerts
- Investigations
- Dashboard data

Use a server-state solution such as TanStack Query.

### UI state

Examples:

- Modal open/closed
- Selected transaction
- Sidebar state
- Filters

Use React state or a lightweight state store.

### Authentication state

Centralize authentication/session handling.

Do not duplicate authentication logic across pages.

---

# 39. API Client Architecture

Create one central API client.

Conceptually:

```text
apiClient
   ↓
Authentication
   ↓
Request
   ↓
Error handling
   ↓
Response normalization
```

Then domain services:

```text
transactionApi
alertApi
investigationApi
dashboardApi
copilotApi
```

Do not scatter raw `fetch()` calls throughout React components.

---

# 40. Backend API Contract

The frontend communicates with:

```text
FastAPI
```

Base URL:

```text
/api/v1
```

---

# 41. Authentication API

## POST `/auth/login`

Request:

```json
{
  "email": "analyst@example.com",
  "password": "********"
}
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "name": "Analyst",
    "role": "fraud_analyst"
  }
}
```

The frontend should never display or log the password.

---

# 42. Current User

## GET `/auth/me`

Response:

```json
{
  "id": "uuid",
  "name": "Gaurav",
  "email": "analyst@example.com",
  "role": "fraud_analyst"
}
```

Used to initialize the application after authentication.

---

# 43. Transactions API

## POST `/transactions`

Purpose:

Submit a transaction for fraud analysis.

Request:

```json
{
  "transaction_id": "TXN-84721",
  "customer_id": "CUS-102",
  "merchant_id": "MER-008",
  "device_id": "DEV-11",
  "amount": 84500,
  "currency": "INR",
  "transaction_type": "CARD",
  "location": "Mumbai",
  "timestamp": "2026-09-15T10:32:15Z"
}
```

Expected response:

```json
{
  "id": "uuid",
  "transaction_id": "TXN-84721",
  "risk_score": 91,
  "risk_level": "HIGH",
  "fraud_probability": 0.94,
  "anomaly_score": 0.88,
  "alert_created": true
}
```

---

# 44. Get Transactions

## GET `/transactions`

Parameters:

```text
page
limit
search
risk_level
status
start_date
end_date
sort
```

Response:

```json
{
  "items": [],
  "page": 1,
  "limit": 25,
  "total": 240
}
```

---

# 45. Get Transaction

## GET `/transactions/{id}`

Returns:

- Transaction
- Customer
- Merchant
- Device
- Risk score
- Risk level
- Explanations
- Relevant history

---

# 46. Alerts API

## GET `/alerts`

Supports:

```text
risk level
status
date
assigned analyst
pagination
```

## GET `/alerts/{id}`

Returns:

- Alert
- Transaction
- Risk information
- Explanation
- Investigation status

---

# 47. Update Alert

## PATCH `/alerts/{id}`

Example:

```json
{
  "status": "IN_REVIEW",
  "assigned_to": "uuid"
}
```

The backend determines whether the user's role permits the operation.

---

# 48. Investigation API

## POST `/investigations`

Request:

```json
{
  "alert_id": "uuid"
}
```

Response:

```json
{
  "id": "uuid",
  "alert_id": "uuid",
  "status": "OPEN",
  "analyst_id": "uuid"
}
```

---

# 49. Get Investigation

## GET `/investigations/{id}`

Returns:

```text
Investigation
Transaction
Risk score
Explanations
Alert
Notes
Decision
Copilot session
```

---

# 50. Update Investigation

## PATCH `/investigations/{id}`

Example:

```json
{
  "status": "RESOLVED",
  "decision": "CONFIRMED_FRAUD",
  "notes": "Multiple anomalous indicators observed."
}
```

The backend validates the user's role and workflow state.

---

# 51. Dashboard API

## GET `/dashboard/summary`

Response:

```json
{
  "total_transactions": 12540,
  "high_risk_transactions": 124,
  "active_alerts": 37,
  "open_investigations": 18,
  "fraud_rate": 0.021
}
```

---

# 52. Dashboard Trends

## GET `/dashboard/risk-trends`

Response:

```json
{
  "points": [
    {
      "timestamp": "2026-09-15T10:00:00Z",
      "transactions": 120,
      "high_risk": 4
    }
  ]
}
```

The frontend converts this into charts.

---

# 53. Real-Time WebSocket

Endpoint:

```text
/ws/v1/alerts
```

or the versioned equivalent:

```text
/ws/api/v1/alerts
```

Use whichever exact routing convention is selected during implementation.

Event:

```json
{
  "event": "HIGH_RISK_TRANSACTION",
  "transaction_id": "TXN-84721",
  "risk_score": 91,
  "risk_level": "HIGH",
  "amount": 84500,
  "timestamp": "2026-09-15T10:32:15Z"
}
```

Frontend behavior:

```text
Receive event
      ↓
Update alert count
      ↓
Add alert
      ↓
Display notification
      ↓
Update dashboard
```

---

# 54. WebSocket Reliability

The frontend should support:

```text
CONNECTED
CONNECTING
DISCONNECTED
RECONNECTING
```

Use controlled exponential backoff.

If WebSocket is unavailable:

```text
Fallback → periodic API refresh
```

The UI should show a subtle status indicator:

```text
● Live
```

or:

```text
○ Reconnecting...
```

---

# 55. Gemini Integration

Gemini is the only major external AI service in the current MVP.

Its role:

> Investigation assistance and explanation summarization.

It should not perform primary fraud classification.

Architecture:

```text
React
  ↓
FastAPI
  ↓
Evidence Builder
  ↓
Gemini API
  ↓
FastAPI
  ↓
React
```

The React frontend should **never call Gemini directly**.

This protects the API key and allows the backend to control exactly what information is sent.

---

# 56. Gemini Request

Frontend:

## POST `/copilot/chat`

Request:

```json
{
  "investigation_id": "uuid",
  "message": "Explain why this transaction was flagged."
}
```

The backend retrieves the required evidence.

Example internal context:

```text
Transaction amount: 84500 INR
Amount deviation: High
Device novelty: High
Location deviation: Medium
Velocity score: High
Fraud probability: 0.94
Anomaly score: 0.88
Risk score: 91
```

Only the necessary information should be sent to Gemini.

---

# 57. Gemini Response

Backend returns a controlled response:

```json
{
  "message": "The transaction was flagged because several indicators...",
  "sources": [
    {
      "type": "risk_factor",
      "name": "amount_deviation"
    },
    {
      "type": "risk_factor",
      "name": "device_novelty"
    }
  ]
}
```

The frontend displays the response as an AI-generated investigation explanation.

---

# 58. Gemini Failure Handling

Possible failures:

```text
API unavailable
Timeout
Rate limit
Invalid API key
Malformed response
Content safety rejection
Network failure
```

Frontend message:

> "The investigation assistant is temporarily unavailable. You can continue reviewing the transaction manually."

The investigation page must remain functional.

---

# 59. Third-Party Services

Current MVP should minimize external dependencies.

## Service 1 — Gemini API

### Purpose

AI investigation assistant.

### Called by

FastAPI backend.

### Frontend calls

```text
POST /api/v1/copilot/chat
```

### Data sent

Only sanitized investigation evidence and the analyst's question.

### Data returned

AI-generated response.

### Frontend must not send

- Passwords
- JWTs
- API keys
- Database credentials
- Unrelated customer records
- Entire database
- Internal secrets

---

# 60. ECharts / Recharts

These are frontend libraries rather than external backend services.

### Purpose

Visualization.

Used for:

- Risk trends
- Transaction volume
- Alert distribution
- Model metrics

They do not require an external API in the normal architecture.

Data source:

```text
FastAPI
  ↓
JSON
  ↓
React
  ↓
ECharts/Recharts
```

---

# 61. Redis

Redis is an infrastructure service rather than a third-party SaaS API.

Purpose:

- Real-time event coordination
- Temporary caching
- WebSocket event distribution

Flow:

```text
Transaction
     ↓
FastAPI
     ↓
Risk Engine
     ↓
Redis event
     ↓
WebSocket manager
     ↓
React
```

Redis should not be treated as the permanent source of truth.

PostgreSQL remains the durable database.

---

# 62. PostgreSQL

PostgreSQL is the system of record.

Frontend should never connect directly to PostgreSQL.

Correct:

```text
React
 ↓
FastAPI
 ↓
PostgreSQL
```

Incorrect:

```text
React
 ↓
PostgreSQL
```

---

# 63. ML Integration

The frontend does not directly call XGBoost, Isolation Forest, or SHAP.

Correct architecture:

```text
React
 ↓
FastAPI
 ↓
Fraud Service
 ↓
ML Model
 ↓
Risk Engine
 ↓
SHAP
 ↓
API response
 ↓
React
```

This ensures model execution and sensitive data processing remain server-side.

---

# 64. API Error Contract

All APIs should return a predictable error structure.

Example:

```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to perform this action.",
    "request_id": "req_123"
  }
}
```

Frontend maps error codes to appropriate UI states.

---

# 65. Recommended Error Codes

```text
AUTH_INVALID_CREDENTIALS
AUTH_SESSION_EXPIRED
AUTH_ACCOUNT_DISABLED

FORBIDDEN
RESOURCE_NOT_FOUND

VALIDATION_FAILED
DUPLICATE_TRANSACTION

TRANSACTION_PROCESSING_FAILED
MODEL_UNAVAILABLE
MODEL_INFERENCE_FAILED
EXPLANATION_UNAVAILABLE

ALERT_UPDATE_FAILED
INVESTIGATION_CONFLICT

COPILOT_UNAVAILABLE
COPILOT_TIMEOUT
COPILOT_RATE_LIMITED

DATABASE_UNAVAILABLE
SERVICE_UNAVAILABLE
INTERNAL_ERROR
```

---

# 66. Frontend Error Mapping

Example:

```text
401
↓
Refresh session / redirect login

403
↓
Permission message

404
↓
Not found page

409
↓
Conflict message

422
↓
Validation errors

429
↓
Rate limit message

500
↓
Generic server error

503
↓
Service unavailable
```

---

# 67. Authentication UI

Login page:

```text
┌──────────────────────────────────┐
│                                  │
│          FraudShield AI          │
│     Fraud Intelligence Platform  │
│                                  │
│ Email                            │
│ [____________________________]   │
│                                  │
│ Password                         │
│ [____________________________]   │
│                                  │
│ [        Sign In               ] │
│                                  │
│ Forgot password?                 │
│                                  │
└──────────────────────────────────┘
```

Keep login simple.

Do not overload it with unnecessary UI.

---

# 68. Dashboard Information Hierarchy

Recommended order:

```text
1. Critical alerts
2. KPI summary
3. Risk trend
4. Recent high-risk transactions
5. Active investigations
6. Model performance
```

The first screen should prioritize action over analytics.

---

# 69. Performance Requirements

Target:

### Initial dashboard

Aim for:

```text
< 2–3 seconds
```

under reasonable deployment conditions.

### API requests

Normal requests should generally feel immediate.

### Real-time alerts

Target:

```text
Transaction processed
        ↓
Alert visible
```

within a few seconds under normal conditions.

---

# 70. Frontend Security Requirements

The frontend must:

- Never contain backend secrets.
- Never contain database credentials.
- Never call PostgreSQL directly.
- Never call Gemini directly with a secret API key.
- Validate input for usability.
- Rely on backend validation for security.
- Sanitize/render untrusted content safely.
- Handle expired sessions.
- Avoid storing sensitive information unnecessarily.
- Avoid logging authentication tokens.

---

# 71. Environment Variables

Frontend may contain public configuration such as:

```text
VITE_API_BASE_URL
```

It must NOT contain:

```text
VITE_GEMINI_API_KEY
DATABASE_PASSWORD
JWT_SECRET
SECRET_KEY
```

Anything shipped to the browser should be considered publicly visible.

---

# 72. Component Naming Convention

Use predictable component names:

```text
Button
Input
Select
Modal
Badge
Card
Table
DataTable
Skeleton
EmptyState
ErrorState
RiskBadge
RiskScore
TransactionCard
TransactionTable
AlertCard
AlertTable
InvestigationPanel
RiskExplanation
CopilotChat
```

---

# 73. Frontend Folder Ownership

```text
components/ui
```

Generic reusable components.

```text
components/transactions
```

Transaction-specific components.

```text
components/alerts
```

Alert-specific components.

```text
components/investigations
```

Investigation workflow.

```text
components/copilot
```

AI assistant UI.

This prevents the project from becoming a collection of unrelated components.

---

# 74. Design Tokens

Centralize values instead of scattering them throughout the application.

Example:

```text
colors.primary
colors.background
colors.surface
colors.text
colors.risk.high
colors.risk.medium
colors.risk.low

spacing.xs
spacing.sm
spacing.md
spacing.lg

radius.sm
radius.md
radius.lg
```

Tailwind configuration should reflect these design decisions.

---

# 75. Definition of Done

A frontend feature is not complete until it includes:

```text
Desktop layout
Responsive behavior
Loading state
Empty state
Error state
Success state
Disabled state
Permission handling
Keyboard accessibility
API failure handling
```

For example, "Alerts page complete" means more than displaying a table.

It must handle:

```text
Loading
↓
Success
↓
No alerts
↓
API failure
↓
Permission denied
↓
Pagination
↓
Filtering
↓
Real-time update
```

---

# 76. 48-Hour Hackathon Implementation Priority

## Phase 1

Build:

- Login
- App shell
- Sidebar
- Dashboard
- Transaction table
- Risk badges

## Phase 2

Build:

- Transaction detail
- Risk explanation
- Alerts
- Investigation page

## Phase 3

Build:

- WebSocket alerts
- Real-time dashboard updates
- Gemini Copilot

## Phase 4

Polish:

- Loading states
- Empty states
- Error handling
- Responsive design
- Accessibility
- Demo data
- Animations only where useful

---

# 77. Demo-Critical User Journey

The entire frontend should make this journey extremely smooth:

```text
Dashboard
   ↓
High-risk transaction appears
   ↓
Click transaction
   ↓
Risk Score = 91
   ↓
"Why flagged?"
   ↓
SHAP factors appear
   ↓
Start Investigation
   ↓
Open Copilot
   ↓
"Summarize the evidence"
   ↓
AI explanation
   ↓
Analyst records decision
   ↓
Resolve Investigation
```

This is the main product story.

---

# 78. Final Frontend Architecture

```text
                         ┌─────────────────────┐
                         │     React + TS       │
                         │                     │
                         │ Dashboard           │
                         │ Transactions        │
                         │ Alerts              │
                         │ Investigations      │
                         │ Copilot             │
                         └──────────┬──────────┘
                                    │
                           HTTPS REST / WebSocket
                                    │
                         ┌──────────▼──────────┐
                         │       FastAPI       │
                         │                     │
                         │ Auth                │
                         │ Transactions        │
                         │ Alerts              │
                         │ Investigations      │
                         │ Dashboard           │
                         │ Copilot             │
                         └──────┬─────┬────────┘
                                │     │
                    ┌───────────┘     └────────────┐
                    ▼                              ▼
             ┌─────────────┐                 ┌──────────┐
             │ PostgreSQL  │                 │  Redis   │
             │             │                 │          │
             │ Source of   │                 │ Realtime │
             │ Truth       │                 │ Events   │
             └─────────────┘                 └──────────┘
                    │
                    ▼
             ┌─────────────┐
             │ Fraud ML    │
             │             │
             │ XGBoost     │
             │ Isolation   │
             │ Forest      │
             │ SHAP        │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ Gemini API  │
             │             │
             │ Investigation│
             │ Assistant   │
             └─────────────┘
```

---

# 79. Final Product Design Principle

FraudShield AI should not look like a generic AI dashboard.

It should feel like a **fraud investigation workstation**.

The interface should consistently move the analyst through:

> **Signal → Evidence → Explanation → Investigation → Decision**

The most important screen is therefore not the login page or even the KPI dashboard.

It is the **investigation experience**.

If an evaluator sees a suspicious transaction arrive in real time, opens it, immediately understands its risk score and contributing factors, asks the Copilot for an evidence summary, and records an investigation decision, the frontend demonstrates the entire product value chain in one coherent flow.

That should be the primary UX story for the Hack 2 Ignite prototype.