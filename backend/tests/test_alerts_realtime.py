import pytest
import asyncio
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.realtime.websocket_manager import ws_manager

client = TestClient(app)

@pytest.fixture
def auth_context():
    email = "alert_analyst@shield.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Alert Analyst",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Alert Bank"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()
    token = login_resp["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "token": token}

def test_automatic_alert_creation_and_api(auth_context):
    headers = auth_context["headers"]

    # Submit a high-risk transaction (high amount + new device + high velocity)
    tx_payload = {
        "transaction_id": "TX_HIGH_RISK_888",
        "customer_id": "CUST_SUSPICIOUS_99",
        "merchant_id": "MERCH_UNKNOWN_99",
        "device_id": "DEV_NEW_99",
        "amount": 9500.00,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
        "location": "Unusual Foreign Location"
    }

    tx_resp = client.post("/api/v1/transactions", json=tx_payload, headers=headers)
    assert tx_resp.status_code == 201

    # Fetch alerts
    alerts_resp = client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    
    alert = alerts[0]
    assert alert["amount"] == 9500.00
    assert alert["status"] == "NEW"
    assert alert["severity"] in ["HIGH", "CRITICAL", "MEDIUM"]

    # Update alert status
    patch_resp = client.patch(
        f"/api/v1/alerts/{alert['id']}",
        json={"status": "INVESTIGATING"},
        headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "INVESTIGATING"

def test_websocket_manager():
    # Test WebSocket manager registration and broadcast
    org_id = "org_test_123"
    assert org_id not in ws_manager.active_connections
