import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserRole
from app.models.investigation import InvestigationStatus
from app.models.audit import AuditLog

client = TestClient(app)

def register_and_login(email: str, role: str, org_name: str = "Enterprise Bank"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": f"{role.replace('_', ' ').title()}",
        "password": "Password123!",
        "role": role,
        "organization_name": org_name
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_role_permission_matrix_settings():
    admin_hdr = register_and_login("admin_user@bank.com", "ADMIN")
    rm_hdr = register_and_login("rm_user@bank.com", "RISK_MANAGER")
    analyst_hdr = register_and_login("analyst_user@bank.com", "FRAUD_ANALYST")
    viewer_hdr = register_and_login("viewer_user@bank.com", "VIEWER")

    # ADMIN: GET and PATCH allowed
    r = client.get("/api/v1/settings", headers=admin_hdr)
    assert r.status_code == 200
    r = client.patch("/api/v1/settings", json={"risk_threshold_medium": 35.0}, headers=admin_hdr)
    assert r.status_code == 200
    assert r.json()["risk_threshold_medium"] == 35.0

    # RISK_MANAGER: GET and PATCH allowed
    r = client.get("/api/v1/settings", headers=rm_hdr)
    assert r.status_code == 200
    r = client.patch("/api/v1/settings", json={"risk_threshold_medium": 40.0}, headers=rm_hdr)
    assert r.status_code == 200
    assert r.json()["risk_threshold_medium"] == 40.0

    # FRAUD_ANALYST: Forbidden on settings
    r = client.get("/api/v1/settings", headers=analyst_hdr)
    assert r.status_code == 403
    r = client.patch("/api/v1/settings", json={"risk_threshold_medium": 45.0}, headers=analyst_hdr)
    assert r.status_code == 403

    # VIEWER: Forbidden on settings
    r = client.get("/api/v1/settings", headers=viewer_hdr)
    assert r.status_code == 403
    r = client.patch("/api/v1/settings", json={"risk_threshold_medium": 45.0}, headers=viewer_hdr)
    assert r.status_code == 403

def test_role_permission_matrix_audit_logs():
    admin_hdr = register_and_login("admin_audit@bank.com", "ADMIN")
    rm_hdr = register_and_login("rm_audit@bank.com", "RISK_MANAGER")
    analyst_hdr = register_and_login("analyst_audit@bank.com", "FRAUD_ANALYST")
    viewer_hdr = register_and_login("viewer_audit@bank.com", "VIEWER")

    # ADMIN: Allowed
    r = client.get("/api/v1/audit-logs", headers=admin_hdr)
    assert r.status_code == 200

    # RISK_MANAGER, FRAUD_ANALYST, VIEWER: Forbidden
    r = client.get("/api/v1/audit-logs", headers=rm_hdr)
    assert r.status_code == 403
    r = client.get("/api/v1/audit-logs", headers=analyst_hdr)
    assert r.status_code == 403
    r = client.get("/api/v1/audit-logs", headers=viewer_hdr)
    assert r.status_code == 403

def test_role_permission_matrix_investigation_mutation():
    admin_hdr = register_and_login("admin_inv@bank.com", "ADMIN")
    analyst_hdr = register_and_login("analyst_inv@bank.com", "FRAUD_ANALYST")
    viewer_hdr = register_and_login("viewer_inv@bank.com", "VIEWER")

    # Ingest a high risk tx to generate an alert
    tx_payload = {
        "transaction_id": "TX_LIFECYCLE_ALERT_1",
        "customer_id": "CUST_LIFECYCLE_1",
        "merchant_id": "MERCH_CRYPTO_1",
        "amount": 15000.0,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
        "location": "Lagos, Nigeria",
        "device_id": "dev_unknown_999"
    }
    tx_resp = client.post("/api/v1/transactions", json=tx_payload, headers=admin_hdr)
    assert tx_resp.status_code == 201

    alerts_resp = client.get("/api/v1/alerts", headers=admin_hdr)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    # VIEWER: cannot create investigation
    r = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=viewer_hdr)
    assert r.status_code == 403

    # ANALYST: can create investigation
    inv_resp = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_hdr)
    assert inv_resp.status_code == 201
    inv_id = inv_resp.json()["id"]

    # VIEWER: cannot add note or resolve
    r = client.post(f"/api/v1/investigations/{inv_id}/notes", json={"note_text": "Viewer test"}, headers=viewer_hdr)
    assert r.status_code == 403
    r = client.post(f"/api/v1/investigations/{inv_id}/resolve", json={"decision": "CONFIRMED_FRAUD", "decision_reason": "Test", "version": 1}, headers=viewer_hdr)
    assert r.status_code == 403

    # ANALYST: can add note and resolve
    r_note = client.post(f"/api/v1/investigations/{inv_id}/notes", json={"note_text": "Analyst verified foreign IP"}, headers=analyst_hdr)
    assert r_note.status_code == 200
    assert r_note.json()["note_text"] == "Analyst verified foreign IP"

    r_res = client.post(f"/api/v1/investigations/{inv_id}/resolve", json={"decision": "CONFIRMED_FRAUD", "decision_reason": "Stolen credentials confirmed", "version": 1}, headers=analyst_hdr)
    assert r_res.status_code == 200
    assert r_res.json()["status"] == "RESOLVED"
    assert r_res.json()["decision"] == "CONFIRMED_FRAUD"

def test_full_end_to_end_fraud_lifecycle(db_session):
    admin_hdr = register_and_login("admin_lifecycle@fintech.com", "ADMIN", "FinTech Global")
    analyst_hdr = register_and_login("analyst_lifecycle@fintech.com", "FRAUD_ANALYST", "FinTech Global")

    # 1. Normal Transaction (Low risk) -> No alert
    normal_tx = {
        "transaction_id": "TX_NORMAL_001",
        "customer_id": "CUST_NORMAL_1",
        "merchant_id": "MERCH_GROCERY_1",
        "amount": 25.50,
        "currency": "USD",
        "transaction_type": "CARD_PRESENT",
        "location": "New York, USA",
        "device_id": "dev_phone_trusted"
    }
    r_normal = client.post("/api/v1/transactions", json=normal_tx, headers=admin_hdr)
    assert r_normal.status_code == 201

    # 2. Fraudulent Transaction (High velocity, anomaly) -> Alert triggered
    fraud_tx = {
        "transaction_id": "TX_FRAUD_001",
        "customer_id": "CUST_VICTIM_100",
        "merchant_id": "MERCH_OFFSHORE_WIRE",
        "amount": 48500.0,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
        "location": "Unknown Location (TOR Exit Node)",
        "device_id": "dev_emulator_x86"
    }
    r_fraud = client.post("/api/v1/transactions", json=fraud_tx, headers=admin_hdr)
    assert r_fraud.status_code == 201
    fraud_data = r_fraud.json()
    assert fraud_data["risk_score"]["risk_score"] >= 70.0

    # 3. Verify Alert generated
    alerts_r = client.get("/api/v1/alerts", headers=analyst_hdr)
    assert alerts_r.status_code == 200
    alerts = alerts_r.json()
    fraud_alert = next((a for a in alerts if a["transaction_id"] == fraud_data["id"]), None)
    assert fraud_alert is not None
    assert fraud_alert["severity"] in ["HIGH", "CRITICAL"]

    # 4. Open Investigation Case
    inv_r = client.post("/api/v1/investigations", json={"alert_id": fraud_alert["id"]}, headers=analyst_hdr)
    assert inv_r.status_code == 201
    inv = inv_r.json()
    inv_id = inv["id"]

    # 5. Add Investigation Evidence Note
    note_r = client.post(
        f"/api/v1/investigations/{inv_id}/notes",
        json={"note_text": "SHAP feature analysis confirms TOR exit node and amount 12x above 30-day baseline."},
        headers=analyst_hdr
    )
    assert note_r.status_code == 200

    # 6. Resolve Case
    resolve_r = client.post(
        f"/api/v1/investigations/{inv_id}/resolve",
        json={
            "decision": "CONFIRMED_FRAUD",
            "decision_reason": "Compromised credential with unauthorized high-value transfer over darknet exit node.",
            "version": 1
        },
        headers=analyst_hdr
    )
    assert resolve_r.status_code == 200
    assert resolve_r.json()["status"] == "RESOLVED"
    assert resolve_r.json()["decision"] == "CONFIRMED_FRAUD"

    # 7. Audit Log Verification
    audit_r = client.get("/api/v1/audit-logs", headers=admin_hdr)
    assert audit_r.status_code == 200
    audit_logs = audit_r.json()
    actions = [l["action"] for l in audit_logs]
    assert "INVESTIGATION_NOTE_ADDED" in actions
    assert "INVESTIGATION_RESOLVED" in actions

def test_request_id_correlation_middleware():
    admin_hdr = register_and_login("admin_trace@bank.com", "ADMIN")
    
    # Request with custom X-Request-ID
    custom_trace_id = "trace-req-client-12345"
    resp = client.get("/api/v1/health", headers={"X-Request-ID": custom_trace_id})
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_trace_id

    # Request without custom header generates a UUID
    resp2 = client.get("/api/v1/health")
    assert resp2.status_code == 200
    assert "x-request-id" in resp2.headers
    assert len(resp2.headers["x-request-id"]) > 10

def test_tenant_isolation_rls():
    # Org Alpha
    admin_a = register_and_login("admin@orgalpha.com", "ADMIN", "Org Alpha")
    # Org Beta
    admin_b = register_and_login("admin@orgbeta.com", "ADMIN", "Org Beta")

    # Ingest Tx in Org Alpha
    tx_a = client.post("/api/v1/transactions", json={
        "transaction_id": "TX_ALPHA_001",
        "customer_id": "usr_alpha_1",
        "merchant_id": "merch_alpha_1",
        "amount": 999.0,
        "currency": "USD",
        "transaction_type": "CARD_NOT_PRESENT",
        "location": "California, USA",
        "device_id": "dev_alpha"
    }, headers=admin_a).json()

    # Org Beta should not see Org Alpha transactions
    txs_b = client.get("/api/v1/transactions", headers=admin_b).json()
    assert not any(t["id"] == tx_a["id"] for t in txs_b)

    # Org Beta should not see Org Alpha audit logs
    audit_b = client.get("/api/v1/audit-logs", headers=admin_b).json()
    assert not any(l["details"] and l["details"].get("user_id") == "usr_alpha_1" for l in audit_b)
