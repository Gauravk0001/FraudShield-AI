"""Regression coverage for frontend-facing API contracts and access controls."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.audit import AuditLog


client = TestClient(app)


def register_and_login(role: str, email: str, organization_name: str = "Frontend Test Bank"):
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": f"{role.title()} Frontend User",
            "password": "Password123!",
            "role": role,
            "organization_name": organization_name,
        },
    )
    assert registration.status_code == 201, registration.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert login.status_code == 200, login.text
    return registration.json(), {"Authorization": f"Bearer {login.json()['access_token']}"}


def transaction_payload(transaction_id: str, amount: float = 9500.0):
    return {
        "transaction_id": transaction_id,
        "customer_id": "CUST_FRONTEND_001",
        "merchant_id": "MERCH_FRONTEND_001",
        "device_id": "DEVICE_FRONTEND_001",
        "amount": amount,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
        "location": "Integration Test Location",
    }


def test_audit_logs_endpoint_matches_frontend_schema_and_requires_admin(db_session):
    _, admin_headers = register_and_login("ADMIN", "admin_frontend_contract@test.com")

    response = client.get("/api/v1/audit-logs?limit=50", headers=admin_headers)
    assert response.status_code == 200, response.text
    logs = response.json()
    assert logs
    assert {"id", "action", "timestamp", "created_at", "resource_type", "resource_id"}.issubset(logs[0])

    _, analyst_headers = register_and_login("FRAUD_ANALYST", "analyst_audit_forbidden@test.com")
    assert client.get("/api/v1/audit-logs", headers=analyst_headers).status_code == 403
    assert client.get("/api/v1/audit-logs").status_code == 401


def test_audit_logs_returns_a_legitimate_empty_list(db_session):
    admin, admin_headers = register_and_login("ADMIN", "admin_audit_empty@test.com", "Empty Audit Bank")
    db_session.query(AuditLog).filter(AuditLog.organization_id == admin["organization_id"]).delete()
    db_session.commit()

    response = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_transactions_endpoint_returns_real_pipeline_response_and_hides_other_organizations():
    _, source_headers = register_and_login("FRAUD_ANALYST", "transactions_source@test.com", "Source Bank")
    created = client.post(
        "/api/v1/transactions",
        json=transaction_payload("TX_FRONTEND_SOURCE"),
        headers=source_headers,
    )
    assert created.status_code == 201, created.text
    assert {"transaction_id", "amount", "timestamp", "status", "risk_score"}.issubset(created.json())

    transactions = client.get("/api/v1/transactions?limit=50", headers=source_headers)
    assert transactions.status_code == 200, transactions.text
    assert any(item["transaction_id"] == "TX_FRONTEND_SOURCE" for item in transactions.json())

    _, other_headers = register_and_login("FRAUD_ANALYST", "transactions_other@test.com", "Other Bank")
    other_transactions = client.get("/api/v1/transactions?limit=50", headers=other_headers)
    assert other_transactions.status_code == 200, other_transactions.text
    assert all(item["transaction_id"] != "TX_FRONTEND_SOURCE" for item in other_transactions.json())


def test_alerts_endpoint_returns_pipeline_alerts_for_the_current_organization():
    _, headers = register_and_login("FRAUD_ANALYST", "alerts_frontend_contract@test.com", "Alerts Contract Bank")
    created = client.post(
        "/api/v1/transactions",
        json=transaction_payload("TX_FRONTEND_ALERT"),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    response = client.get("/api/v1/alerts?limit=50", headers=headers)
    assert response.status_code == 200, response.text
    alerts = response.json()
    assert alerts
    assert {"transaction_id", "severity", "risk_score", "status", "created_at"}.issubset(alerts[0])
    assert any(alert["transaction_id"] == created.json()["id"] for alert in alerts)


def test_settings_route_resolves_for_admin_and_enforces_authentication_and_rbac():
    assert client.get("/api/v1/settings").status_code == 401

    _, admin_headers = register_and_login("ADMIN", "settings_admin@test.com", "Settings Test Bank")
    admin_response = client.get("/api/v1/settings", headers=admin_headers)
    assert admin_response.status_code == 200, admin_response.text
    assert {
        "organization_id",
        "risk_threshold_medium",
        "risk_threshold_high",
        "session_expire_minutes",
        "gemini_api_key_configured",
    }.issubset(admin_response.json())

    _, viewer_headers = register_and_login("VIEWER", "settings_viewer@test.com", "Settings Test Bank")
    assert client.get("/api/v1/settings", headers=viewer_headers).status_code == 403
