# FraudShield AI
## Complete Feature Ticket List

**Version:** 1.0  
**Product:** FraudShield AI  
**Architecture:** React + TypeScript + Tailwind + FastAPI + PostgreSQL + Redis + Python ML + SHAP + Gemini  
**Primary workflow:** Transaction → Features → ML → Risk Score → Explanation → Alert → Investigation → AI Assistance → Decision

---

# How to Use These Tickets

Each ticket is intentionally written as a prompt that can be given directly to an AI coding tool.

Recommended implementation order:

```text
Foundation
   ↓
Database
   ↓
Authentication
   ↓
Transaction ingestion
   ↓
ML engine
   ↓
Risk engine
   ↓
Alerts
   ↓
Real-time events
   ↓
Dashboard
   ↓
Investigation
   ↓
SHAP
   ↓
Gemini Copilot
   ↓
Testing + Demo polish
```

Priority labels:

- **MUST-HAVE** — Required for a functional launch/demo.
- **SHOULD-HAVE** — Important but can be deferred if time is limited.
- **NICE-TO-HAVE** — Add only after the core product works.

---

# EPIC 1 — Project Foundation

## Ticket FS-001 — Initialize Full-Stack Project

**Priority:** MUST-HAVE

### Description

Create the initial FraudShield AI repository using a modular monolith architecture.

Set up:

- React + TypeScript frontend
- FastAPI backend
- PostgreSQL
- Redis
- Docker Compose
- Environment configuration
- Git configuration
- Basic project documentation

Use the architecture defined for FraudShield AI and avoid unnecessary microservices.

### Acceptance Criteria

- [ ] Repository has `frontend/` and `backend/`.
- [ ] React application starts successfully.
- [ ] FastAPI application starts successfully.
- [ ] PostgreSQL container starts.
- [ ] Redis container starts.
- [ ] Docker Compose starts all required services.
- [ ] `.env` is ignored by Git.
- [ ] `.env.example` exists.
- [ ] No secrets are committed.
- [ ] `/health` endpoint returns successful status.
- [ ] README contains setup instructions.

### Dependencies

None.

---

# EPIC 2 — Database

## Ticket FS-002 — Create PostgreSQL Database Schema

**Priority:** MUST-HAVE

### Description

Implement the FraudShield AI PostgreSQL schema based on the product architecture.

Create tables for:

- Users
- Customers
- Merchants
- Devices
- Transactions
- Transaction features
- Risk scores
- Risk explanations
- Alerts
- Investigations
- Copilot sessions
- Copilot messages
- Model versions
- Audit logs

Create appropriate:

- Primary keys
- Foreign keys
- Unique constraints
- Indexes
- Timestamps

### Acceptance Criteria

- [ ] All required tables exist.
- [ ] Foreign-key relationships work.
- [ ] Transaction IDs are unique.
- [ ] Required fields cannot be null.
- [ ] Appropriate indexes exist for frequently queried fields.
- [ ] Database migrations can create the schema from an empty database.
- [ ] Database can be recreated without manual SQL edits.

### Dependencies

FS-001.

---

## Ticket FS-003 — Implement Database Access Layer

**Priority:** MUST-HAVE

### Description

Create the backend database connection and repository/data-access layer.

Implement:

- PostgreSQL connection
- Connection pooling
- Session management
- Transaction handling
- Clean shutdown
- Database health check

Keep database access outside API route logic wherever practical.

### Acceptance Criteria

- [ ] Backend connects successfully to PostgreSQL.
- [ ] Connection failures are handled cleanly.
- [ ] Database sessions are correctly opened and closed.
- [ ] API requests do not leak database connections.
- [ ] Transactions roll back after failures.
- [ ] `/health` reports database availability.

### Dependencies

FS-002.

---

# EPIC 3 — Authentication & Authorization

## Ticket FS-004 — Implement User Authentication

**Priority:** MUST-HAVE

### Description

Implement secure authentication using email/password authentication with short-lived JWT access tokens and protected refresh sessions.

Use secure password hashing such as Argon2id or bcrypt.

Implement:

- Login
- Logout
- Current-user endpoint
- Token expiration
- Refresh session
- Disabled-account handling

Never expose passwords or secrets.

### Acceptance Criteria

- [ ] Passwords are hashed.
- [ ] Passwords are never stored in plaintext.
- [ ] Login returns an authenticated session.
- [ ] Access tokens expire.
- [ ] Expired sessions are handled.
- [ ] Logout invalidates the appropriate session.
- [ ] Disabled users cannot log in.
- [ ] Invalid credentials return a generic error.
- [ ] Authentication secrets come from environment variables.
- [ ] Passwords/tokens are not logged.

### Dependencies

FS-002, FS-003.

---

## Ticket FS-005 — Implement Role-Based Access Control

**Priority:** MUST-HAVE

### Description

Implement the four FraudShield AI roles:

- Admin
- Fraud Analyst
- Risk Manager
- Viewer

Create reusable backend authorization dependencies.

Enforce permissions server-side.

### Acceptance Criteria

- [ ] Every authenticated request identifies the current user.
- [ ] Role is retrieved server-side.
- [ ] Unauthorized roles receive HTTP 403.
- [ ] Viewers cannot modify investigations.
- [ ] Analysts cannot manage users.
- [ ] Risk Managers cannot manage users.
- [ ] Only authorized roles can access model management.
- [ ] Admin-only routes reject non-admin users.
- [ ] Frontend visibility does not replace backend authorization.

### Dependencies

FS-004.

---

## Ticket FS-006 — Implement Database Row-Level Security

**Priority:** SHOULD-HAVE

### Description

Implement PostgreSQL Row-Level Security for organization-scoped records.

Ensure users cannot access records belonging to another organization.

Apply appropriate policies to:

- Transactions
- Alerts
- Investigations
- Customers
- Merchants
- Devices
- Risk data

Use deny-by-default principles.

### Acceptance Criteria

- [ ] RLS is enabled on required tables.
- [ ] Organization boundaries are enforced.
- [ ] Users cannot retrieve another organization's transactions.
- [ ] Users cannot retrieve another organization's investigations.
- [ ] Viewer remains read-only.
- [ ] Tests verify cross-organization access is denied.

### Dependencies

FS-002, FS-004, FS-005.

---

# EPIC 4 — Transaction Processing

## Ticket FS-007 — Build Transaction Validation API

**Priority:** MUST-HAVE

### Description

Create:

`POST /api/v1/transactions`

Validate transaction input using Pydantic.

Validate:

- Transaction ID
- Customer
- Merchant
- Device
- Amount
- Currency
- Transaction type
- Location
- Timestamp

Reject invalid or dangerous input.

### Acceptance Criteria

- [ ] Valid transaction is accepted.
- [ ] Negative amounts are rejected.
- [ ] Zero amount is rejected if the business rule requires positive amounts.
- [ ] Invalid currency is rejected.
- [ ] Invalid transaction type is rejected.
- [ ] Invalid IDs are rejected.
- [ ] Invalid timestamps are rejected.
- [ ] Duplicate transaction IDs are handled.
- [ ] Validation errors have predictable API responses.
- [ ] No raw exceptions are exposed.

### Dependencies

FS-003.

---

## Ticket FS-008 — Implement Transaction Service

**Priority:** MUST-HAVE

### Description

Create the service responsible for processing incoming transactions.

The service should:

1. Validate transaction.
2. Check duplicate transaction ID.
3. Store transaction.
4. Generate features.
5. Send features to fraud detection.
6. Generate risk score.
7. Generate explanation.
8. Create alert if required.
9. Publish real-time event.

Design the workflow so individual failures can be handled safely.

### Acceptance Criteria

- [ ] Transaction is persisted.
- [ ] Transaction receives a processing status.
- [ ] Duplicate transactions are not accidentally created.
- [ ] Processing failures are recorded.
- [ ] Transaction processing does not silently mark failed ML inference as low risk.
- [ ] Service can be called from both API routes and automated simulation.

### Dependencies

FS-002, FS-003, FS-007.

---

# EPIC 5 — Feature Engineering

## Ticket FS-009 — Implement Transaction Feature Engineering

**Priority:** MUST-HAVE

### Description

Create the feature-engineering pipeline required by FraudShield AI.

Generate features such as:

- Amount deviation
- Transaction velocity
- Location deviation
- Merchant novelty
- Device novelty
- Historical frequency

Keep feature generation deterministic and reusable between training and inference.

### Acceptance Criteria

- [ ] Same input produces consistent feature structure.
- [ ] Required model features are generated.
- [ ] Missing historical information is handled safely.
- [ ] Numerical values are validated.
- [ ] Features are stored for auditability.
- [ ] Feature generation can be tested independently.

### Dependencies

FS-002, FS-008.

---

# EPIC 6 — Fraud Detection Engine

## Ticket FS-010 — Implement Supervised Fraud Classifier

**Priority:** MUST-HAVE

### Description

Implement the supervised fraud detection model using the selected tabular ML algorithm, such as XGBoost or Random Forest.

Create a reusable inference interface.

The model should return a fraud probability.

### Acceptance Criteria

- [ ] Model artifact can be loaded.
- [ ] Model version is tracked.
- [ ] Inference accepts the defined feature vector.
- [ ] Output probability is between 0 and 1.
- [ ] Invalid model output is rejected.
- [ ] Model failure does not produce a fake score.
- [ ] Model inference can be tested independently.

### Dependencies

FS-009.

---

## Ticket FS-011 — Implement Isolation Forest Anomaly Detection

**Priority:** MUST-HAVE

### Description

Implement Isolation Forest as the anomaly-detection component.

Return a normalized anomaly score suitable for the FraudShield risk engine.

### Acceptance Criteria

- [ ] Isolation Forest artifact loads.
- [ ] Inference works on valid feature vectors.
- [ ] Anomaly score is normalized consistently.
- [ ] Model failure is detected.
- [ ] Output is stored for the transaction.
- [ ] Model version is recorded.

### Dependencies

FS-009.

---

# EPIC 7 — Risk Engine

## Ticket FS-012 — Build Fraud Risk Scoring Engine

**Priority:** MUST-HAVE

### Description

Create a risk engine combining:

- Fraud probability
- Anomaly score
- Configured thresholds

Generate:

- Final score
- Risk level
- Model version

Risk levels:

```text
LOW
MEDIUM
HIGH
```

Support configurable thresholds.

### Acceptance Criteria

- [ ] Final score is generated.
- [ ] Score remains within 0–100.
- [ ] Risk level is assigned correctly.
- [ ] Thresholds are configurable.
- [ ] Invalid model values do not generate misleading risk levels.
- [ ] Risk score is stored in PostgreSQL.
- [ ] Model version is stored.

### Dependencies

FS-010, FS-011.

---

# EPIC 8 — Explainability

## Ticket FS-013 — Implement SHAP Explainability

**Priority:** MUST-HAVE

### Description

Generate SHAP explanations for model predictions.

Return the most important contributing features.

Each explanation should include:

- Feature name
- Feature value
- Contribution
- Direction
- Human-readable explanation

### Acceptance Criteria

- [ ] SHAP explanation can be generated for valid predictions.
- [ ] Top contributing features are returned.
- [ ] Contributions are stored.
- [ ] Feature values are stored.
- [ ] Explanation failure does not invalidate a successful risk score.
- [ ] UI receives structured explanation data.

### Dependencies

FS-010, FS-012.

---

# EPIC 9 — Alert Management

## Ticket FS-014 — Implement Automatic Alert Creation

**Priority:** MUST-HAVE

### Description

Create alerts automatically when a transaction crosses the configured risk threshold.

Alert should contain:

- Transaction ID
- Risk score
- Severity
- Title
- Description
- Status
- Created timestamp

### Acceptance Criteria

- [ ] High-risk transactions generate alerts.
- [ ] Alert is linked to transaction.
- [ ] Alert contains risk information.
- [ ] Duplicate transaction processing does not create duplicate alerts.
- [ ] Alert status starts correctly.
- [ ] Alert creation failure is logged.

### Dependencies

FS-012, FS-002.

---

## Ticket FS-015 — Build Alert API

**Priority:** MUST-HAVE

### Description

Implement:

```text
GET /api/v1/alerts
GET /api/v1/alerts/{id}
PATCH /api/v1/alerts/{id}
```

Support:

- Pagination
- Filtering
- Status
- Risk level
- Assignment

### Acceptance Criteria

- [ ] Authorized users can retrieve alerts.
- [ ] Pagination works.
- [ ] Filtering works.
- [ ] Unauthorized access is rejected.
- [ ] Alert status can be updated only by permitted roles.
- [ ] Invalid alert IDs return controlled 404 responses.

### Dependencies

FS-005, FS-014.

---

# EPIC 10 — Real-Time System

## Ticket FS-016 — Implement Redis Event Publishing

**Priority:** MUST-HAVE

### Description

Publish important system events to Redis.

At minimum:

```text
HIGH_RISK_TRANSACTION
ALERT_CREATED
ALERT_UPDATED
```

Use structured event payloads.

### Acceptance Criteria

- [ ] Events are published after successful processing.
- [ ] Event payload contains transaction/alert identifier.
- [ ] Event payload contains risk information.
- [ ] Redis failure is handled.
- [ ] PostgreSQL remains the source of truth.

### Dependencies

FS-014.

---

## Ticket FS-017 — Implement WebSocket Alert Stream

**Priority:** MUST-HAVE

### Description

Create a WebSocket endpoint that delivers real-time alert events to authenticated frontend users.

Support:

- Authentication
- Connection management
- Disconnection
- Reconnection
- Event delivery

### Acceptance Criteria

- [ ] Authorized client can connect.
- [ ] Unauthorized client is rejected.
- [ ] New high-risk alerts reach connected clients.
- [ ] Disconnects are handled.
- [ ] Server does not crash when a client disappears.
- [ ] Multiple clients can receive events.

### Dependencies

FS-005, FS-016.

---

# EPIC 11 — Frontend Foundation

## Ticket FS-018 — Build Frontend Design System

**Priority:** MUST-HAVE

### Description

Implement the FraudShield AI design system using React, TypeScript and Tailwind.

Create reusable:

- Button
- Input
- Select
- Card
- Badge
- Modal
- Table
- Skeleton
- Toast
- Empty state
- Error state

Use the defined color palette, typography, spacing and border-radius rules.

### Acceptance Criteria

- [ ] Components are reusable.
- [ ] Components have loading/disabled/error states where applicable.
- [ ] Risk colors are consistent.
- [ ] Components are keyboard accessible.
- [ ] Design tokens are centralized.
- [ ] No major page contains duplicated button/input styling.

### Dependencies

FS-001.

---

# EPIC 12 — Authentication UI

## Ticket FS-019 — Build Login Experience

**Priority:** MUST-HAVE

### Description

Create the FraudShield AI login page.

Implement:

- Email input
- Password input
- Validation
- Loading state
- Error state
- Authentication
- Session initialization

### Acceptance Criteria

- [ ] User can log in.
- [ ] Invalid credentials show a safe error.
- [ ] Loading state prevents duplicate submissions.
- [ ] Successful login redirects to dashboard.
- [ ] Disabled user receives appropriate message.
- [ ] Authentication state persists appropriately.
- [ ] Logout works.

### Dependencies

FS-004, FS-018.

---

# EPIC 13 — Application Shell

## Ticket FS-020 — Build Main Application Layout

**Priority:** MUST-HAVE

### Description

Create:

- Sidebar
- Header
- User profile area
- Navigation
- Responsive layout
- Role-aware navigation

Navigation should automatically hide features the user cannot access while backend authorization remains authoritative.

### Acceptance Criteria

- [ ] Layout works on desktop.
- [ ] Sidebar works.
- [ ] Navigation changes based on role.
- [ ] Active page is highlighted.
- [ ] Mobile/tablet behavior is reasonable.
- [ ] Logout is accessible.

### Dependencies

FS-019.

---

# EPIC 14 — Dashboard

## Ticket FS-021 — Build Fraud Operations Dashboard

**Priority:** MUST-HAVE

### Description

Create the primary FraudShield dashboard.

Display:

- Total transactions
- High-risk transactions
- Active alerts
- Open investigations
- Fraud rate
- Risk trend
- Recent high-risk transactions
- Active investigations

Use ECharts or Recharts.

### Acceptance Criteria

- [ ] Dashboard loads data from the API.
- [ ] KPI cards display real values.
- [ ] Charts render correctly.
- [ ] Loading state exists.
- [ ] Empty state exists.
- [ ] API failure has retry functionality.
- [ ] High-risk information is visually prioritized.

### Dependencies

FS-018, FS-020, FS-012, FS-015.

---

## Ticket FS-022 — Implement Dashboard Risk Trends

**Priority:** SHOULD-HAVE

### Description

Create charts showing:

- Transaction volume
- High-risk transactions
- Risk trends over time

### Acceptance Criteria

- [ ] Data comes from backend API.
- [ ] Time range is clearly represented.
- [ ] Chart handles empty datasets.
- [ ] Chart handles API failure.
- [ ] Tooltips provide useful values.

### Dependencies

FS-021.

---

# EPIC 15 — Transactions

## Ticket FS-023 — Build Transaction Table

**Priority:** MUST-HAVE

### Description

Create the transaction-management screen.

Columns:

- Transaction ID
- Timestamp
- Customer
- Amount
- Merchant
- Risk score
- Risk level
- Status
- Action

Implement:

- Search
- Filtering
- Sorting
- Pagination

### Acceptance Criteria

- [ ] Transactions load from API.
- [ ] Search works.
- [ ] Filtering works.
- [ ] Pagination works.
- [ ] Risk badges are consistent.
- [ ] Loading state works.
- [ ] Empty state works.
- [ ] API errors are handled.

### Dependencies

FS-007, FS-018, FS-020.

---

## Ticket FS-024 — Build Transaction Detail View

**Priority:** MUST-HAVE

### Description

Create a transaction detail page/panel displaying:

- Transaction information
- Customer
- Merchant
- Device
- Risk score
- Fraud probability
- Anomaly score
- Risk level
- Risk explanations
- Investigation status

### Acceptance Criteria

- [ ] Transaction information loads correctly.
- [ ] Risk score is prominent.
- [ ] Risk explanation is visible.
- [ ] Missing explanation is handled gracefully.
- [ ] User can start an investigation if authorized.

### Dependencies

FS-023, FS-012, FS-013.

---

# EPIC 16 — Investigation

## Ticket FS-025 — Build Investigation Creation Workflow

**Priority:** MUST-HAVE

### Description

Allow authorized analysts/managers to create an investigation from an alert.

Workflow:

```text
Alert
 ↓
Start Investigation
 ↓
Investigation created
 ↓
Analyst assigned
```

### Acceptance Criteria

- [ ] Authorized user can create an investigation.
- [ ] Investigation is linked to the alert.
- [ ] Analyst assignment is recorded.
- [ ] Duplicate investigation creation is prevented.
- [ ] Unauthorized users cannot create investigations.

### Dependencies

FS-005, FS-015.

---

## Ticket FS-026 — Build Investigation Workspace

**Priority:** MUST-HAVE

### Description

Create the central investigation workspace.

Display:

- Transaction evidence
- Risk score
- Risk level
- SHAP explanations
- Customer information
- Transaction history
- Alert information
- Investigation notes
- Decision
- Status

### Acceptance Criteria

- [ ] All relevant evidence is visible.
- [ ] Investigation status is visible.
- [ ] Notes can be added by authorized users.
- [ ] Decision can be recorded according to workflow.
- [ ] Closed investigations cannot be improperly modified.
- [ ] Unauthorized access is blocked.

### Dependencies

FS-024, FS-025.

---

## Ticket FS-027 — Implement Investigation State Management

**Priority:** MUST-HAVE

### Description

Implement investigation states:

```text
OPEN
IN_REVIEW
RESOLVED
```

Implement valid transitions and prevent invalid transitions.

### Acceptance Criteria

- [ ] Valid transitions work.
- [ ] Invalid transitions are rejected.
- [ ] Resolved investigations cannot be accidentally reopened through ordinary updates.
- [ ] Status changes are audited.
- [ ] UI reflects current status.

### Dependencies

FS-025.

---

# EPIC 17 — AI Copilot

## Ticket FS-028 — Build Gemini Backend Integration

**Priority:** SHOULD-HAVE

### Description

Integrate Gemini into the FastAPI backend.

Create:

`POST /api/v1/copilot/chat`

The backend should construct a sanitized evidence context from the current investigation.

Gemini should receive:

- Relevant transaction information
- Risk score
- Risk factors
- SHAP explanations
- Analyst's question

Do not expose the Gemini API key to the frontend.

### Acceptance Criteria

- [ ] API key is server-side only.
- [ ] Investigation context is constructed server-side.
- [ ] Only necessary evidence is sent.
- [ ] Gemini response is returned safely.
- [ ] Gemini failure is handled.
- [ ] Timeout is handled.
- [ ] Rate limiting is handled.
- [ ] Secrets are never included in the prompt.

### Dependencies

FS-013, FS-026.

---

## Ticket FS-029 — Build Fraud Investigation Copilot UI

**Priority:** SHOULD-HAVE

### Description

Build a Copilot interface integrated into the investigation workspace.

Provide suggested prompts:

- Explain this alert
- Summarize evidence
- What should I investigate next?
- Show unusual behavior
- Generate investigation summary

Clearly label AI-generated content.

### Acceptance Criteria

- [ ] Analyst can submit a question.
- [ ] Response appears in conversation.
- [ ] Loading state exists.
- [ ] Timeout/error state exists.
- [ ] Investigation context is preserved.
- [ ] AI-generated content is clearly identified.
- [ ] UI does not expose API credentials.

### Dependencies

FS-028.

---

# EPIC 18 — Audit Logging

## Ticket FS-030 — Implement Audit Logging

**Priority:** MUST-HAVE

### Description

Create centralized audit logging for important security and business actions.

Record:

- User
- Action
- Entity
- Entity ID
- Timestamp
- Metadata
- Request ID

### Acceptance Criteria

- [ ] Login failures can be audited.
- [ ] Login successes can be audited.
- [ ] Role changes are audited.
- [ ] Alert updates are audited.
- [ ] Investigation updates are audited.
- [ ] Sensitive Admin actions are audited.
- [ ] Users cannot modify audit logs through normal APIs.
- [ ] Sensitive secrets are not stored in audit metadata.

### Dependencies

FS-002, FS-004.

---

## Ticket FS-031 — Build Audit Log Viewer

**Priority:** SHOULD-HAVE

### Description

Create an Admin-only audit log interface.

Support:

- Search
- Date filtering
- User filtering
- Action filtering
- Pagination

### Acceptance Criteria

- [ ] Only authorized users can access logs.
- [ ] Audit records are read-only.
- [ ] Filters work.
- [ ] Pagination works.
- [ ] Sensitive metadata is not exposed.

### Dependencies

FS-030, FS-020.

---

# EPIC 19 — Model Management

## Ticket FS-032 — Implement Model Version Tracking

**Priority:** SHOULD-HAVE

### Description

Track model versions used for fraud decisions.

Store:

- Model name
- Version
- Algorithm
- Metrics
- Artifact path
- Active status
- Creation timestamp

### Acceptance Criteria

- [ ] Every risk score identifies a model version.
- [ ] Active model can be identified.
- [ ] Historical model versions remain traceable.
- [ ] Model metadata is stored.
- [ ] Unauthorized users cannot modify models.

### Dependencies

FS-010, FS-011, FS-002.

---

# EPIC 20 — Real-Time Frontend

## Ticket FS-033 — Implement WebSocket Alert Client

**Priority:** MUST-HAVE

### Description

Create a React WebSocket hook for receiving real-time alerts.

Implement:

- Connection
- Authentication
- Reconnection
- Connection status
- Event parsing
- Event dispatching

### Acceptance Criteria

- [ ] Frontend connects after authentication.
- [ ] New high-risk alerts appear without page refresh.
- [ ] Connection status is visible.
- [ ] Reconnection works.
- [ ] Malformed events do not crash the application.
- [ ] WebSocket failure falls back to API refresh where appropriate.

### Dependencies

FS-017, FS-020.

---

## Ticket FS-034 — Build Real-Time Alert Notification UI

**Priority:** MUST-HAVE

### Description

Display real-time high-risk transaction notifications.

Notification should show:

- Transaction ID
- Risk score
- Amount
- Risk level
- Investigation action

### Acceptance Criteria

- [ ] High-risk event produces notification.
- [ ] Notification links to transaction/investigation.
- [ ] Duplicate events do not spam notifications.
- [ ] Notification can be dismissed.
- [ ] Connection failures do not produce false notifications.

### Dependencies

FS-033, FS-024.

---

# EPIC 21 — Transaction Simulator

## Ticket FS-035 — Build Real-Time Transaction Simulator

**Priority:** SHOULD-HAVE

### Description

Create a development/demo script that generates synthetic transactions at configurable intervals.

Include both:

- Normal transactions
- Suspicious transactions

The simulator should send transactions through the real API instead of directly manipulating the database.

### Acceptance Criteria

- [ ] Simulator generates valid transactions.
- [ ] Simulator produces suspicious scenarios.
- [ ] Transactions go through the real API.
- [ ] Fraud detection processes them.
- [ ] High-risk events reach the dashboard.
- [ ] No real financial/customer data is used.

### Dependencies

FS-008, FS-012, FS-017.

---

# EPIC 22 — Error Handling

## Ticket FS-036 — Implement Global Backend Error Handling

**Priority:** MUST-HAVE

### Description

Create centralized FastAPI exception handling.

Return consistent error responses with:

- Error code
- User-safe message
- Request ID

Never return:

- Stack traces
- Database credentials
- API keys
- SQL queries
- Internal file paths

### Acceptance Criteria

- [ ] Validation errors are normalized.
- [ ] Authentication errors are normalized.
- [ ] Authorization errors are normalized.
- [ ] Database failures are normalized.
- [ ] ML failures are normalized.
- [ ] AI failures are normalized.
- [ ] Unexpected errors return safe 500 responses.
- [ ] Internal errors are logged.

### Dependencies

FS-003, FS-004.

---

## Ticket FS-037 — Implement Frontend API Error Handling

**Priority:** MUST-HAVE

### Description

Create a centralized frontend API error handler.

Map:

```text
401 → authentication handling
403 → permission error
404 → resource not found
409 → conflict
422 → validation
429 → rate limit
500 → server error
503 → service unavailable
```

### Acceptance Criteria

- [ ] Components do not duplicate HTTP error logic.
- [ ] User-friendly messages are shown.
- [ ] Retry is available where appropriate.
- [ ] Authentication failures are handled centrally.
- [ ] Technical server details are not shown.

### Dependencies

FS-018, FS-019.

---

# EPIC 23 — Security Hardening

## Ticket FS-038 — Implement API Rate Limiting

**Priority:** MUST-HAVE

### Description

Add rate limiting to sensitive APIs.

At minimum:

- Login
- Copilot
- Transaction ingestion

Return HTTP 429 when limits are exceeded.

### Acceptance Criteria

- [ ] Excessive login attempts are throttled.
- [ ] Copilot requests are throttled.
- [ ] Transaction ingestion has reasonable protection.
- [ ] HTTP 429 responses are consistent.
- [ ] Legitimate users can recover after the rate-limit window.

### Dependencies

FS-004, FS-028.

---

## Ticket FS-039 — Secure CORS and Production Configuration

**Priority:** MUST-HAVE

### Description

Configure production security settings.

Implement:

- Restricted CORS
- HTTPS-ready configuration
- Secure cookies where applicable
- Production debug mode disabled
- Secure headers
- Environment-based configuration

### Acceptance Criteria

- [ ] Production does not run with debug enabled.
- [ ] CORS does not allow arbitrary origins.
- [ ] Secrets come from environment configuration.
- [ ] Secure cookie settings are used where applicable.
- [ ] No credentials appear in frontend bundles.

### Dependencies

FS-001, FS-004.

---

# EPIC 24 — Testing

## Ticket FS-040 — Backend API Test Suite

**Priority:** MUST-HAVE

### Description

Create automated backend tests for the most important API behavior.

Test:

- Authentication
- Authorization
- Transactions
- Risk scoring
- Alerts
- Investigations
- Error handling

### Acceptance Criteria

- [ ] Tests run from a clean environment.
- [ ] Authentication tests exist.
- [ ] Unauthorized access tests exist.
- [ ] Transaction validation tests exist.
- [ ] Duplicate transaction test exists.
- [ ] Alert creation test exists.
- [ ] Investigation workflow tests exist.
- [ ] Error handling tests exist.

### Dependencies

FS-007, FS-012, FS-015, FS-027.

---

## Ticket FS-041 — Frontend Critical-Flow Tests

**Priority:** SHOULD-HAVE

### Description

Test the most important frontend flows.

Test:

```text
Login
→ Dashboard
→ Transaction
→ Alert
→ Investigation
→ Copilot
```

### Acceptance Criteria

- [ ] Login flow works.
- [ ] Protected routes work.
- [ ] Transaction details load.
- [ ] Alert interaction works.
- [ ] Investigation creation works.
- [ ] API errors do not crash pages.

### Dependencies

FS-019, FS-021, FS-024, FS-026.

---

# EPIC 25 — Demo & Launch

## Ticket FS-042 — Create Seed/Demo Data

**Priority:** MUST-HAVE

### Description

Create realistic synthetic data for demonstrations.

Include:

- Customers
- Merchants
- Devices
- Normal transactions
- Suspicious transactions
- Alerts
- Investigations

Never use real customer financial information.

### Acceptance Criteria

- [ ] Database can be populated with demo data.
- [ ] Data looks realistic enough for presentation.
- [ ] High-risk scenarios exist.
- [ ] Investigations exist.
- [ ] No real personal financial data is included.

### Dependencies

FS-002, FS-008, FS-014.

---

## Ticket FS-043 — Build End-to-End Demo Scenario

**Priority:** MUST-HAVE

### Description

Create a deterministic demo scenario showing the entire FraudShield workflow.

Scenario:

```text
Synthetic transaction
      ↓
Transaction API
      ↓
Feature engineering
      ↓
Fraud model
      ↓
Anomaly detection
      ↓
Risk score
      ↓
SHAP explanation
      ↓
Alert
      ↓
Real-time dashboard
      ↓
Investigation
      ↓
Copilot
      ↓
Analyst decision
```

### Acceptance Criteria

- [ ] Demo can be executed repeatedly.
- [ ] Suspicious transaction produces high-risk result.
- [ ] Explanation appears.
- [ ] Alert appears in real time.
- [ ] Investigation can be created.
- [ ] Copilot can summarize evidence when available.
- [ ] Final investigation decision can be recorded.

### Dependencies

FS-013, FS-017, FS-026, FS-029, FS-035.

---

## Ticket FS-044 — Production Readiness Review

**Priority:** MUST-HAVE

### Description

Perform a final technical and security review before launch.

Check:

- Authentication
- Authorization
- RLS
- Input validation
- Secrets
- CORS
- Error handling
- Database constraints
- ML failure handling
- AI failure handling
- WebSocket failure handling
- Logging
- Backup strategy

### Acceptance Criteria

- [ ] No known critical security issue remains.
- [ ] No secrets exist in repository.
- [ ] Protected APIs reject unauthorized requests.
- [ ] Error responses are safe.
- [ ] Critical workflows work from a clean deployment.
- [ ] Demo scenario works.
- [ ] README contains deployment/setup instructions.

### Dependencies

All MUST-HAVE tickets.

---

# PRIORITY SUMMARY

## MUST-HAVE — Launch Core

```text
FS-001  Project Foundation
FS-002  PostgreSQL Schema
FS-003  Database Access
FS-004  Authentication
FS-005  RBAC
FS-007  Transaction Validation
FS-008  Transaction Service
FS-009  Feature Engineering
FS-010  Fraud Classifier
FS-011  Isolation Forest
FS-012  Risk Engine
FS-013  SHAP
FS-014  Alert Creation
FS-015  Alert API
FS-016  Redis Events
FS-017  WebSocket Backend
FS-018  Frontend Design System
FS-019  Login UI
FS-020  App Shell
FS-021  Dashboard
FS-023  Transaction Table
FS-024  Transaction Detail
FS-025  Investigation Creation
FS-026  Investigation Workspace
FS-027  Investigation State
FS-030  Audit Logging
FS-033  WebSocket Frontend
FS-034  Real-Time Notifications
FS-036  Backend Error Handling
FS-037  Frontend Error Handling
FS-038  Rate Limiting
FS-039  Production Security
FS-040  Backend Tests
FS-042  Demo Data
FS-043  End-to-End Demo
FS-044  Production Review
```

---

# SHOULD-HAVE

```text
FS-006   Database RLS
FS-022   Risk Trend Charts
FS-028   Gemini Backend
FS-029   Copilot UI
FS-031   Audit Viewer
FS-032   Model Version Management
FS-035   Transaction Simulator
FS-041   Frontend Tests
```

---

# NICE-TO-HAVE

The following should only be built after all core functionality works.

## Ticket FS-045 — Customer Risk Profiles

**Priority:** NICE-TO-HAVE

Build a customer-level risk profile showing:

- Historical transactions
- Average amount
- Transaction frequency
- Risk history
- Device history
- Location history

### Dependencies

FS-023, FS-024.

---

## Ticket FS-046 — Merchant Risk Profiles

**Priority:** NICE-TO-HAVE

Build merchant-level fraud-risk analytics.

### Dependencies

FS-023, FS-024.

---

## Ticket FS-047 — Device Intelligence

**Priority:** NICE-TO-HAVE

Create a device intelligence view showing:

- Device novelty
- Customer associations
- Transaction history
- Risk history

### Dependencies

FS-009, FS-024.

---

## Ticket FS-048 — Transaction Relationship Graph

**Priority:** NICE-TO-HAVE

Visualize relationships between:

```text
Customer
   ↕
Device
   ↕
Transaction
   ↕
Merchant
```

Use the graph to identify suspicious relationships.

### Dependencies

FS-024.

---

# Recommended AI Coding Execution Order

Do **not** ask an AI coding tool to build all 48 tickets in one prompt.

Use incremental implementation.

## Sprint 1 — Foundation

```text
FS-001
FS-002
FS-003
FS-018
```

Result:

> Running full-stack skeleton.

---

## Sprint 2 — Security

```text
FS-004
FS-005
FS-006
FS-030
```

Result:

> Secure authenticated application.

---

## Sprint 3 — Fraud Engine

```text
FS-007
FS-008
FS-009
FS-010
FS-011
FS-012
FS-013
```

Result:

> Transaction → ML → Risk → Explanation.

---

## Sprint 4 — Alerts

```text
FS-014
FS-015
FS-016
FS-017
FS-033
FS-034
```

Result:

> Real-time fraud detection.

---

## Sprint 5 — Frontend

```text
FS-019
FS-020
FS-021
FS-023
FS-024
```

Result:

> Usable fraud operations dashboard.

---

## Sprint 6 — Investigation

```text
FS-025
FS-026
FS-027
```

Result:

> Complete investigation workflow.

---

## Sprint 7 — AI

```text
FS-028
FS-029
```

Result:

> AI investigation assistant.

---

## Sprint 8 — Hardening

```text
FS-036
FS-037
FS-038
FS-039
FS-040
FS-042
FS-043
FS-044
```

Result:

> Demo-ready, security-reviewed MVP.

---

# The Critical Product Dependency Chain

The most important dependency chain is:

```text
DATABASE
   ↓
AUTH
   ↓
TRANSACTION API
   ↓
FEATURE ENGINEERING
   ↓
FRAUD MODEL
   ↓
ANOMALY MODEL
   ↓
RISK ENGINE
   ↓
SHAP
   ↓
ALERTS
   ↓
REDIS
   ↓
WEBSOCKET
   ↓
DASHBOARD
   ↓
INVESTIGATION
   ↓
GEMINI COPILOT
```

Do not reverse this order unnecessarily.

For example, building a beautiful Copilot UI before the transaction/risk/investigation APIs exist creates mock functionality that later has to be rewritten.

---

# AI Coding Tool Instruction

Every ticket should be implemented with these rules:

```text
1. Inspect the existing project before changing anything.

2. Do not rewrite working functionality unnecessarily.

3. Follow the existing architecture.

4. Keep backend business logic out of API route handlers where practical.

5. Keep frontend API calls inside service/API modules.

6. Use TypeScript types for API responses.

7. Validate all backend input.

8. Never expose secrets.

9. Never bypass authorization.

10. Never fabricate ML results.

11. Never treat Gemini output as ground truth.

12. Add appropriate loading, empty, error and success states.

13. Add tests for important business logic.

14. Do not introduce unnecessary microservices.

15. Do not add dependencies unless they solve a real requirement.

16. Update documentation when architecture or API behavior changes.

17. Preserve existing functionality.

18. Before finishing, run the relevant tests/build/lint checks.

19. Report exactly what files were created or changed.

20. Report any unresolved issue instead of pretending the feature is complete.
```

---

# Final MVP Definition

FraudShield AI is launch-ready for the hackathon prototype when this complete journey works:

```text
                    USER
                     │
                     ▼
                  LOGIN
                     │
                     ▼
                DASHBOARD
                     │
                     ▼
             TRANSACTION ARRIVES
                     │
                     ▼
            FEATURE ENGINEERING
                     │
                     ▼
          ┌──────────┴──────────┐
          ▼                     ▼
     FRAUD MODEL          ANOMALY MODEL
          │                     │
          └──────────┬──────────┘
                     ▼
                 RISK ENGINE
                     │
                     ▼
                RISK SCORE
                     │
                     ▼
                SHAP EXPLANATION
                     │
                     ▼
                   ALERT
                     │
             ┌───────┴────────┐
             ▼                ▼
       WEB SOCKET          DATABASE
             │
             ▼
          DASHBOARD
             │
             ▼
        INVESTIGATION
             │
             ▼
       GEMINI COPILOT
             │
             ▼
       HUMAN DECISION
             │
             ▼
          RESOLUTION
```

The product's core MVP should therefore be judged by one question:

> **Can FraudShield AI take a transaction, detect suspicious behavior, explain the risk, alert an analyst in real time, help investigate it, and record the final decision?**

If the answer is yes, you have the complete core product.

Everything else should come after that.