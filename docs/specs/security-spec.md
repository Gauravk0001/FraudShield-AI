# FraudShield AI
## Security & Access Document

**Document type:** Product Security & Access Specification  
**Product:** FraudShield AI  
**Version:** 1.0  
**Purpose:** Define how users log in, what they can access, how database access is restricted, how failures are handled, and what must be checked before launch.

---

# 1. Executive Summary

FraudShield AI handles transaction information, fraud-risk scores, alerts, investigations, explanations, and AI-assisted investigation conversations.

The most important security principle is:

> **Every user should have only the access they need to perform their job.**

FraudShield AI should use:

- Secure email/password authentication initially.
- Short-lived access tokens.
- Refresh-token-based sessions.
- Role-based access control.
- Database-level row-level security.
- Server-side permission checks.
- Strong password hashing.
- Audit logging for important actions.
- Rate limiting on login and sensitive APIs.
- Secure handling of AI requests.
- No secrets or API keys in the frontend.
- Synthetic/anonymized financial data during development and demos.

Security should not depend only on the React frontend hiding buttons. The backend and database must independently enforce permissions.

---

# 2. Recommended Authentication Method

## Recommended approach: JWT + secure refresh sessions

For the current hackathon/MVP stage, FraudShield AI should use:

**Email + password → backend authentication → short-lived access token → refresh session**

### Why this fits the product

FraudShield AI is a web application with:

- React frontend
- FastAPI backend
- PostgreSQL database
- Multiple user roles
- Analyst investigations
- Real-time alerts

A simple authentication system is therefore preferable to building a complicated identity platform.

The authentication flow should be:

```text
User
  ↓
Login
  ↓
FastAPI Authentication API
  ↓
Verify password
  ↓
Create access token + refresh session
  ↓
React application
  ↓
Authenticated API requests
```

## Access token

The access token should be short-lived.

Recommended starting point:

**15 minutes**

The frontend uses it when communicating with the backend.

If the access token expires, the application uses the refresh session to obtain a new one.

## Refresh session

Recommended:

**7–30 days**, depending on the desired user experience.

Refresh tokens should be:

- Random
- Revocable
- Stored securely
- Associated with a user/session
- Expired automatically
- Rotated when appropriate

Do not store long-lived authentication secrets in ordinary browser local storage if you can avoid it.

For a browser application, prefer a **Secure, HttpOnly, SameSite cookie** for the refresh session.

---

# 3. Password Security

Passwords must never be stored directly.

The database should contain something equivalent to:

```text
password_hash
```

not:

```text
password
```

Use a modern password hashing algorithm such as:

- Argon2id, or
- bcrypt if Argon2id is not practical.

Do not use:

- MD5
- SHA-1
- plain SHA-256
- Base64
- reversible encryption

for password storage.

## Password requirements

At minimum:

- Reasonable minimum length
- Reject obviously compromised/common passwords
- Do not impose unnecessarily complicated rules such as requiring five different symbol types
- Never reveal whether an email address exists during password-reset requests

---

# 4. Authentication Rules

## Login

A login request should:

1. Validate the email.
2. Validate the password field.
3. Look up the account.
4. Verify the password hash.
5. Check whether the account is active.
6. Check whether the account is locked or rate-limited.
7. Create an authenticated session.
8. Record the login event.

### Failed login

Return a generic message such as:

> "Invalid email or password."

Do not tell the attacker:

> "This email exists but the password is incorrect."

That information can be used to discover registered accounts.

---

# 5. Account Locking and Rate Limiting

Login endpoints must be protected against password guessing.

Example policy:

```text
5 failed attempts
        ↓
Temporary delay / rate limit
        ↓
Additional failures
        ↓
Temporary account lock
```

Do not permanently lock accounts based only on failed login attempts because an attacker could intentionally lock somebody else's account.

Use a combination of:

- IP-based rate limiting
- Account-based throttling
- Increasing delays
- Temporary lockouts
- Monitoring

---

# 6. User Roles

FraudShield AI should initially have four roles:

1. **Admin**
2. **Fraud Analyst**
3. **Risk Manager**
4. **Viewer**

The role must be stored server-side and must never be trusted merely because the frontend says the user is an admin.

---

# 7. Role: Admin

## Purpose

The Admin manages the FraudShield AI environment and its users.

### Admin CAN

- Log in.
- View dashboard data.
- View transactions.
- View alerts.
- View investigations.
- Create users.
- Disable users.
- Change user roles.
- Reset user access.
- View audit logs.
- View system health.
- Configure approved system settings.
- View model versions.
- View security events.
- Assign analysts to investigations.

### Admin CANNOT

Even an Admin should not:

- Read users' passwords.
- Retrieve password hashes through normal APIs.
- Retrieve secret API keys.
- Modify immutable audit history.
- Directly manipulate transaction history through the UI.
- Automatically declare a transaction fraudulent without the application's normal investigation process.
- Bypass database security through the application.

### Important

The Admin role is powerful, but it should still be subject to auditing.

Every sensitive Admin action should create an audit event.

---

# 8. Role: Fraud Analyst

## Purpose

The Fraud Analyst investigates suspicious transactions.

### Analyst CAN

- Log in.
- View relevant dashboard information.
- View transactions.
- Search transactions.
- View fraud-risk scores.
- View anomaly scores.
- View SHAP explanations.
- View alerts.
- Claim/assign an investigation to themselves.
- Update investigation status.
- Add investigation notes.
- Record an investigation decision.
- Use the AI Copilot.
- View relevant transaction history.
- Resolve investigations according to permitted workflow.

### Analyst CANNOT

- Create or delete users.
- Change user roles.
- Disable accounts.
- Modify model configuration.
- Change fraud thresholds unless explicitly authorized.
- Delete transactions.
- Delete alerts.
- Modify historical risk scores.
- Modify audit logs.
- Retrieve system secrets.
- Access unrelated administrative settings.

---

# 9. Role: Risk Manager

## Purpose

The Risk Manager oversees fraud trends and risk decisions.

### Risk Manager CAN

- View dashboards.
- View transactions.
- View alerts.
- View investigations.
- Review analyst decisions.
- Review fraud explanations.
- Review model performance.
- Review risk trends.
- Reassign investigations.
- Approve/close investigations where the workflow permits.
- Add review notes.
- Use the AI Copilot.

### Risk Manager CANNOT

- Manage passwords.
- Retrieve secrets.
- Modify audit logs.
- Delete transaction records.
- Modify model artifacts directly.
- Change application security configuration unless explicitly granted Admin privileges.
- Bypass investigation history.

---

# 10. Role: Viewer

## Purpose

The Viewer provides read-only access.

Typical examples:

- Management
- Demonstration users
- Auditors with limited access
- Stakeholders

### Viewer CAN

- View approved dashboards.
- View permitted transaction information.
- View permitted alerts.
- View permitted risk summaries.

### Viewer CANNOT

- Create transactions through privileged APIs.
- Modify transactions.
- Create investigations.
- Modify investigations.
- Resolve alerts.
- Change users.
- Change roles.
- Change models.
- Change system settings.
- Use administrative functions.

---

# 11. Permission Matrix

| Capability | Admin | Risk Manager | Fraud Analyst | Viewer |
|---|---:|---:|---:|---:|
| Login | ✓ | ✓ | ✓ | ✓ |
| Dashboard | ✓ | ✓ | ✓ | ✓ |
| View transactions | ✓ | ✓ | ✓ | Limited |
| Search transactions | ✓ | ✓ | ✓ | Limited |
| View risk scores | ✓ | ✓ | ✓ | Limited |
| View SHAP explanations | ✓ | ✓ | ✓ | Optional |
| View alerts | ✓ | ✓ | ✓ | Limited |
| Investigate alerts | ✓ | ✓ | ✓ | ✗ |
| Add investigation notes | ✓ | ✓ | ✓ | ✗ |
| Resolve investigation | ✓ | ✓ | ✓* | ✗ |
| AI Copilot | ✓ | ✓ | ✓ | Optional |
| Manage users | ✓ | ✗ | ✗ | ✗ |
| Change roles | ✓ | ✗ | ✗ | ✗ |
| View audit logs | ✓ | Limited | ✗ | ✗ |
| Manage models | ✓ | Limited | ✗ | ✗ |
| Change security settings | ✓ | ✗ | ✗ | ✗ |
| Delete business records | Restricted | ✗ | ✗ | ✗ |

`*` Subject to the investigation workflow.

---

# 12. Important Access Principle

Never implement authorization like this:

```text
Frontend hides Admin button
        ↓
User cannot click Admin button
```

That is not security.

Instead:

```text
Frontend hides Admin button
        ↓
Backend checks role
        ↓
Database checks access
        ↓
Request allowed/denied
```

An attacker can directly call APIs without using the React interface.

Therefore:

> **Every sensitive API endpoint must perform server-side authorization.**

---

# 13. Database Row-Level Security

PostgreSQL should enforce another security layer using Row-Level Security (RLS).

RLS means:

> Even if someone manages to query the database through an application path, PostgreSQL can restrict which rows they are allowed to see or modify.

---

# 14. RLS Principles

The database should follow:

```text
User identity
     ↓
User role
     ↓
Organization/tenant
     ↓
Allowed rows
```

If FraudShield later becomes a multi-company SaaS platform, every business record should belong to an organization.

For example:

```text
organization_id
```

should be added to relevant tables.

This prevents:

```text
Company A user
       ↓
Company B transactions
```

from ever being returned.

---

# 15. Transactions RLS

A normal user should only access transactions belonging to their permitted organization.

Conceptually:

```text
SELECT transaction
WHERE transaction.organization_id
=
current_user.organization_id
```

### Additional restriction

Viewers should receive read-only access.

Analysts may read transactions but should not directly modify historical transaction records.

Risk Managers may review transactions but should not modify their underlying financial event.

Admins may have broader visibility but access should still be organization-scoped.

---

# 16. Alerts RLS

Alerts should inherit organization restrictions from their associated transaction.

A user must not be able to access:

```text
Company B alert
```

while belonging to:

```text
Company A
```

An alert should also have workflow permissions.

For example:

```text
Viewer → read
Analyst → read + investigate
Risk Manager → read + review
Admin → manage
```

---

# 17. Investigations RLS

Investigations require additional protection because they contain analyst notes and potentially sensitive reasoning.

Suggested rule:

### Analyst

Can access:

- investigations assigned to them
- investigations explicitly shared with their team
- investigations their organization permits

### Risk Manager

Can access investigations across their organization.

### Admin

Can access investigations across their organization for administrative purposes.

### Viewer

Read-only access only where explicitly permitted.

---

# 18. Copilot Data Protection

The AI Copilot should never automatically receive the entire database.

Bad design:

```text
Gemini
  ↓
Entire PostgreSQL database
```

Correct design:

```text
Investigation
      ↓
Relevant transaction
      ↓
Relevant risk evidence
      ↓
Relevant explanation
      ↓
Sanitized context
      ↓
Gemini
```

The Copilot should receive only the information necessary for the current investigation.

Do not send:

- Passwords
- Authentication tokens
- API keys
- Database credentials
- Unrelated customers
- Unrelated transactions
- Internal security secrets

---

# 19. AI Copilot Security

Gemini should be treated as an assistant, not an authority.

The AI should not be allowed to:

- Change a user's role.
- Delete transactions.
- Modify audit logs.
- Disable security.
- Automatically block customers.
- Execute arbitrary SQL.
- Execute arbitrary shell commands.
- Approve financial transactions.

The AI should provide:

```text
Evidence
+
Explanation
+
Suggested investigation steps
```

The human analyst remains responsible for the final decision.

---

# 20. Risk Score Protection

Risk scores should be treated as system-generated evidence.

For example:

```text
Fraud probability: 0.94
Anomaly score: 0.88
Final risk score: 91
Risk level: HIGH
```

Users should not be able to directly change these values through ordinary APIs.

If a model changes:

```text
model_version = fraud-v2
```

should be recorded.

Historical risk scores should remain traceable.

---

# 21. Audit Logging

Important actions must be logged.

Examples:

```text
LOGIN_SUCCESS
LOGIN_FAILED
LOGOUT
PASSWORD_CHANGED
USER_CREATED
USER_DISABLED
ROLE_CHANGED
TRANSACTION_VIEWED
ALERT_CREATED
ALERT_ASSIGNED
INVESTIGATION_STARTED
INVESTIGATION_UPDATED
INVESTIGATION_RESOLVED
COPILOT_USED
MODEL_CHANGED
SECURITY_SETTING_CHANGED
```

An audit log should contain:

- User ID
- Action
- Entity type
- Entity ID
- Timestamp
- Relevant metadata
- Request/correlation ID where useful

Audit records should not be editable through normal application APIs.

---

# 22. Error Handling Philosophy

The application should follow three rules:

### Rule 1 — Do not expose secrets

Never return:

```text
database password
API key
stack trace
internal file path
SQL query
JWT secret
```

to the user.

### Rule 2 — Give users useful messages

Example:

> "We couldn't process this transaction. Please try again."

rather than:

> `psycopg2.errors.UniqueViolation...`

### Rule 3 — Log the technical details internally

The user receives:

```text
Something went wrong.
Reference: ERR-8F21
```

while the server logs the actual error.

---

# 23. Standard Error Response

Use one consistent structure.

Example:

```json
{
  "success": false,
  "error": {
    "code": "TRANSACTION_VALIDATION_FAILED",
    "message": "The transaction data is invalid.",
    "request_id": "req_12345"
  }
}
```

Do not expose internal exception details.

---

# 24. Authentication Errors

## Invalid credentials

HTTP:

```text
401 Unauthorized
```

Message:

> Invalid email or password.

Do not identify which field was incorrect.

---

# 25. Expired Session

HTTP:

```text
401 Unauthorized
```

Message:

> Your session has expired. Please sign in again.

The frontend should attempt a controlled token refresh.

If refresh fails:

```text
Clear authenticated session
↓
Return to login
```

---

# 26. Forbidden Access

If a user is authenticated but does not have permission:

HTTP:

```text
403 Forbidden
```

Message:

> You don't have permission to perform this action.

Do not reveal sensitive information about the protected resource.

---

# 27. Transaction Validation Errors

Examples:

- Missing amount
- Invalid currency
- Invalid timestamp
- Invalid transaction type
- Negative amount
- Impossible value
- Invalid customer ID
- Invalid merchant ID

Return:

```text
400 Bad Request
```

or:

```text
422 Unprocessable Entity
```

depending on the API design.

Example:

> "Transaction amount must be greater than zero."

---

# 28. Duplicate Transaction

If the same transaction identifier is submitted twice:

```text
409 Conflict
```

Example:

> "This transaction has already been processed."

Do not accidentally create duplicate alerts.

The transaction ID should have an appropriate database uniqueness constraint.

---

# 29. Database Failure

If PostgreSQL is unavailable:

User message:

> "The service is temporarily unavailable. Please try again."

Internally log:

```text
Database unavailable
Request ID
Endpoint
User ID
Timestamp
Exception
```

Do not expose:

```text
postgresql://username:password@...
```

---

# 30. Redis Failure

If Redis is unavailable:

The system should degrade gracefully where possible.

For example:

```text
Redis unavailable
      ↓
Real-time alert delivery temporarily unavailable
      ↓
Transaction remains stored
      ↓
User can refresh dashboard
```

Do not lose the underlying transaction simply because the real-time notification system failed.

---

# 31. ML Model Failure

This is a critical failure point.

If the fraud model cannot load or inference fails:

**Do not invent a fraud score.**

Instead:

```text
Transaction received
       ↓
ML inference fails
       ↓
Record failure
       ↓
Mark transaction processing status
       ↓
Alert operator/system
```

Possible status:

```text
PROCESSING_ERROR
```

The system should clearly distinguish:

```text
LOW RISK
```

from:

```text
RISK UNKNOWN — MODEL ERROR
```

These are not the same thing.

---

# 32. SHAP Failure

SHAP explanations are useful but should not cause the entire fraud-processing pipeline to fail.

Recommended behavior:

```text
Fraud model succeeds
        ↓
Risk score generated
        ↓
SHAP fails
        ↓
Save risk score
        ↓
Mark explanation unavailable
        ↓
Continue alert workflow
```

User message:

> "Risk score generated. Detailed explanation is temporarily unavailable."

---

# 33. Gemini/API Failure

If the Copilot AI service is unavailable:

> "The AI investigation assistant is temporarily unavailable."

The analyst should still be able to:

- View the transaction
- View the risk score
- View SHAP explanations
- Investigate manually
- Update investigation status

The AI Copilot must never become a single point of failure.

---

# 34. AI Timeout

Set a reasonable timeout.

If Gemini does not respond within the configured period:

```text
Cancel request
↓
Log timeout
↓
Return controlled error
```

Do not keep a request hanging indefinitely.

---

# 35. Rate Limit Errors

For excessive requests:

```text
429 Too Many Requests
```

Message:

> "Too many requests. Please wait and try again."

Apply rate limits especially to:

- Login
- Password reset
- Copilot
- Transaction ingestion
- Search
- Expensive ML operations

---

# 36. WebSocket Failure

If real-time alerts disconnect:

```text
WebSocket disconnected
       ↓
Frontend detects connection loss
       ↓
Reconnect with controlled backoff
       ↓
If unavailable:
       ↓
Fallback to periodic API refresh
```

Do not assume the WebSocket is always connected.

---

# 37. File/Data Upload Failure

If future versions support CSV/PCAP/other uploads:

Validate:

- File type
- File size
- File name
- Content format
- Encoding
- Number of rows
- Malicious content
- Duplicate data

Never trust a file merely because its extension says:

```text
.csv
```

---

# 38. Unexpected Server Error

For unexpected failures:

```text
500 Internal Server Error
```

User sees:

> "Something went wrong. Please try again."

Server logs:

```text
request_id
timestamp
endpoint
user_id
exception
stack trace
service
```

Stack traces must never be returned to production users.

---

# 39. API Security

Every API should be categorized as:

```text
PUBLIC
AUTHENTICATED
ROLE-RESTRICTED
ADMIN-ONLY
```

Example:

| Endpoint | Access |
|---|---|
| `/health` | Public/limited |
| `/login` | Public |
| `/transactions` | Authenticated + role |
| `/alerts` | Authenticated + role |
| `/investigations` | Analyst/Manager/Admin |
| `/copilot/chat` | Authorized users |
| `/users` | Admin |
| `/audit-logs` | Admin |
| `/model-versions` | Admin/authorized Manager |

---

# 40. Input Validation

Never trust frontend validation.

The backend must validate every request.

Validate:

- Types
- Length
- Range
- Format
- IDs
- Enumerated values
- Dates
- Currency
- Amounts
- Pagination
- Search parameters

Use Pydantic models in FastAPI.

---

# 41. SQL Injection Protection

Never build SQL using string concatenation.

Bad:

```text
"SELECT * FROM users WHERE email = '" + email + "'"
```

Use parameterized queries/ORM mechanisms.

---

# 42. XSS Protection

User-generated content includes:

- Investigation notes
- Copilot conversations
- Names
- Search input
- Merchant information

Do not render untrusted HTML directly.

The frontend should safely escape user-controlled content.

---

# 43. CORS

Only allow trusted frontend origins.

Development:

```text
http://localhost:5173
```

Production:

```text
https://your-real-domain.com
```

Do not use:

```text
allow_origins=["*"]
```

for authenticated production APIs unless there is a deliberate reason and appropriate controls.

---

# 44. Secrets Management

Never commit:

```text
.env
```

containing real secrets.

Never commit:

```text
GEMINI_API_KEY
SECRET_KEY
DATABASE_PASSWORD
JWT_SECRET
```

Use environment variables or a proper secret-management system.

GitHub should contain:

```text
.env.example
```

with placeholders.

---

# 45. Database Backup and Recovery

Before launch, establish:

- Automated backups
- Backup retention
- Restore testing
- Database recovery procedure

A backup that has never been restored/tested should not be considered a proven backup.

---

# 46. Data Retention

Define how long the system keeps:

- Transactions
- Alerts
- Investigations
- Copilot conversations
- Audit logs
- Model outputs

Do not retain data indefinitely without a reason.

For a production financial product, retention should eventually be aligned with the applicable legal and contractual requirements.

---

# 47. Edge Cases Before Launch

The following cases should be explicitly tested.

## Authentication

- Wrong password
- Wrong email
- Empty credentials
- Extremely long password
- Account disabled
- Repeated failed login
- Expired access token
- Invalid refresh token
- Revoked refresh token
- Logout from multiple devices
- Password changed while another session is active
- Deleted user attempting to log in

---

## Authorization

- Viewer attempts Admin API
- Analyst attempts user-management API
- User accesses another organization's transaction
- User modifies another analyst's investigation
- User changes their own role
- User changes another user's role
- Direct API call bypassing frontend restrictions
- Manipulated JWT claims
- Missing role
- Invalid role

---

## Transactions

- Duplicate transaction ID
- Zero amount
- Negative amount
- Extremely large amount
- Missing customer
- Missing merchant
- Unknown customer
- Unknown merchant
- Invalid currency
- Invalid timestamp
- Future transaction timestamp
- Very old transaction
- Duplicate submission
- Simultaneous duplicate submissions
- Corrupted transaction payload

---

## Fraud Detection

- Model unavailable
- Model produces invalid output
- Model returns NaN
- Model returns probability below 0
- Model returns probability above 1
- Missing feature
- Unexpected feature type
- New transaction category
- Model version missing
- Model artifact corrupted
- Extremely unusual transaction

---

## Risk Scoring

Test:

```text
Score = 0
Score = 1
Score = 29
Score = 30
Score = 69
Score = 70
Score = 99
Score = 100
```

Verify that risk levels are assigned correctly.

Also test what happens when:

```text
fraud_probability = NULL
anomaly_score = NULL
```

---

## SHAP

- Explanation generated successfully
- Explanation service fails
- Missing feature
- Model/explanation mismatch
- Explanation contains unexpected values
- Explanation takes too long

---

## Alerts

- High-risk transaction creates alert
- Medium-risk transaction does not create unnecessary high-priority alert
- Duplicate transaction does not create duplicate alerts
- Alert already resolved
- Two analysts try to claim the same investigation
- Alert assignment fails
- WebSocket disconnected
- Browser closed during investigation

---

## Investigation

- Analyst opens investigation twice
- Two analysts edit simultaneously
- Investigation already resolved
- Empty investigation notes
- Extremely long notes
- Unauthorized user accesses investigation
- Analyst attempts to modify a closed investigation
- Investigation assignment changes

---

## Gemini Copilot

- Gemini unavailable
- API timeout
- API rate limit
- Invalid API key
- Empty prompt
- Extremely long prompt
- Malicious prompt injection
- Copilot asks for secret information
- Copilot receives unrelated customer data
- Copilot gives an incorrect recommendation
- Copilot response contains unsafe/untrusted content

---

## Database

- PostgreSQL unavailable
- Connection pool exhausted
- Database timeout
- Duplicate key
- Foreign-key violation
- Transaction rollback
- Partial transaction processing
- Migration failure
- Database disk/storage limit

---

## Redis

- Redis unavailable
- Connection timeout
- Lost WebSocket event
- Duplicate event
- Out-of-order event
- Expired cache
- Cache contains stale data

---

# 48. Race Conditions

This is particularly important for investigations.

Example:

```text
Analyst A → Claim investigation
Analyst B → Claim same investigation
```

Only one should succeed.

Use database transactions/locking or another reliable concurrency mechanism.

The application must not rely on:

```text
if status == "OPEN":
    assign()
```

without protecting the operation against simultaneous requests.

---

# 49. Idempotency

Transaction ingestion should support idempotency.

If the same transaction is submitted twice:

```text
Request 1 → Transaction created
Request 2 → Existing transaction detected
```

The system should not produce:

```text
2 transactions
2 risk scores
2 alerts
```

unless explicitly intended.

---

# 50. Logging Rules

Logs should help engineers investigate problems without exposing sensitive information.

Safe:

```text
User 123 failed login
Request ID abc123
Endpoint /login
Timestamp ...
```

Unsafe:

```text
password=MyPassword123
GEMINI_API_KEY=...
database_password=...
```

Never log passwords, tokens, API keys, or other authentication secrets.

---

# 51. Production Security Headers

The production frontend/API should use appropriate security headers, including protections against:

- Clickjacking
- MIME sniffing
- Unsafe content loading
- Insecure transport

HTTPS should be mandatory in production.

---

# 52. HTTPS

Production traffic should use:

```text
HTTPS
```

not:

```text
HTTP
```

This includes:

```text
Browser → Frontend
Frontend → API
API → external services
```

Local development can use HTTP where appropriate.

---

# 53. Security Testing Before Launch

At minimum perform:

### Authentication testing

Verify:

- Login
- Logout
- Token expiration
- Refresh
- Password handling
- Rate limiting

### Authorization testing

For every protected endpoint, test:

```text
Correct role → allowed
Wrong role → denied
Unauthenticated → denied
Wrong organization → denied
```

### Input testing

Try:

- Empty fields
- Huge strings
- Invalid IDs
- Special characters
- Unexpected JSON
- Invalid numbers
- SQL-like input
- HTML/JavaScript input

### API testing

Use the API directly rather than only clicking the UI.

The goal is to prove that:

> **Security remains active even when the frontend is bypassed.**

---

# 54. Launch Security Checklist

Before production launch, all of the following should be checked.

## Authentication

- [ ] Passwords are hashed.
- [ ] Access tokens expire.
- [ ] Refresh sessions are protected.
- [ ] Logout invalidates the session appropriately.
- [ ] Login rate limiting exists.
- [ ] Password-reset flow is protected.
- [ ] Disabled users cannot authenticate.

## Authorization

- [ ] Every protected API checks authentication.
- [ ] Every sensitive API checks role.
- [ ] Users cannot modify their own role.
- [ ] Viewers are read-only.
- [ ] Analysts cannot access admin functionality.
- [ ] Organization boundaries are enforced.

## Database

- [ ] RLS policies are enabled where required.
- [ ] Foreign keys exist.
- [ ] Unique transaction IDs are enforced.
- [ ] Sensitive records cannot be modified directly.
- [ ] Database credentials are not in GitHub.
- [ ] Backups exist.
- [ ] Restore procedure has been tested.

## AI

- [ ] Gemini key is server-side only.
- [ ] Copilot receives minimum necessary data.
- [ ] AI cannot execute arbitrary SQL.
- [ ] AI cannot change permissions.
- [ ] AI failure does not break fraud detection.
- [ ] AI output is treated as assistance, not ground truth.

## API

- [ ] Input validation exists.
- [ ] Rate limiting exists.
- [ ] CORS is restricted.
- [ ] HTTPS is enabled in production.
- [ ] Error responses do not expose stack traces.
- [ ] Request IDs exist for troubleshooting.

## Monitoring

- [ ] Authentication failures are logged.
- [ ] Permission failures are logged.
- [ ] Important Admin actions are audited.
- [ ] Model failures are logged.
- [ ] Database failures are monitored.
- [ ] AI failures are monitored.

---

# 55. Recommended Security Architecture

The final security model should look like this:

```text
                    USER
                      │
                      ▼
              ┌───────────────┐
              │ React Frontend│
              └───────┬───────┘
                      │
                 HTTPS + Token
                      │
                      ▼
              ┌───────────────┐
              │   FastAPI     │
              │ Authentication│
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ Authorization │
              │ RBAC + Rules  │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
     PostgreSQL     Redis       ML Engine
       + RLS                    + SHAP
          │
          ▼
     Audit Logging
          │
          ▼
      Monitoring

                    │
                    ▼
              Gemini Copilot
           Sanitized Evidence Only
```

---

# 56. Security Principles for FraudShield AI

The product should follow these principles from day one:

### 1. Least privilege

Give users only the access required for their job.

### 2. Deny by default

If permission is not explicitly granted, deny the request.

### 3. Server-side enforcement

Never trust the frontend to enforce security.

### 4. Defense in depth

Use multiple layers:

```text
Authentication
+
Authorization
+
RLS
+
Validation
+
Audit logging
+
Rate limiting
```

### 5. Fail safely

A failed ML or AI service should not automatically produce a false "safe" result.

### 6. Protect sensitive information

Only send the minimum necessary information to each service.

### 7. Keep humans responsible

FraudShield AI should support investigation rather than silently making irreversible financial decisions.

### 8. Make actions traceable

Important actions should be auditable.

### 9. Never trust external input

Transactions, user input, files, AI responses, and API requests must all be treated as untrusted.

### 10. Security must survive the UI being bypassed

A user with Postman/cURL should have no more permissions than the same user using React.

---

# 57. MVP Security Priorities

For the 48-hour Hack 2 Ignite implementation, do not spend most of the development time building enterprise-grade security infrastructure.

Prioritize these:

**P0 — Must have**

1. Secure password hashing
2. JWT authentication
3. Role-based authorization
4. Server-side permission checks
5. PostgreSQL constraints
6. Basic RLS/organization isolation
7. Input validation
8. Rate limiting on login
9. Secure environment variables
10. Audit logging
11. Safe error responses
12. HTTPS for deployed application

**P1 — Add if time allows**

13. Refresh-token rotation
14. Advanced session management
15. Security monitoring
16. More granular RLS
17. Automated security tests
18. More detailed audit reporting

**P2 — Production expansion**

19. SSO/OIDC
20. MFA
21. Enterprise identity management
22. Secrets manager
23. SIEM integration
24. Advanced anomaly detection for account activity
25. Formal penetration testing
26. Independent security audit

---

# 58. Final Security Requirement

The most important requirement for FraudShield AI is:

> **No user should be able to access, modify, or expose information simply by bypassing the frontend or manipulating an API request.**

The security architecture should therefore enforce access at multiple levels:

```text
Authentication
      ↓
Who are you?
      ↓
Authorization
      ↓
What are you allowed to do?
      ↓
Organization/RLS
      ↓
Which records can you access?
      ↓
Validation
      ↓
Is this request legitimate?
      ↓
Audit Log
      ↓
Can we prove what happened?
```

This provides a practical security foundation for the FraudShield AI MVP while leaving room to evolve into enterprise authentication, MFA, SSO, stronger tenant isolation, and formal compliance controls as the product grows.