import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    # Register and login test user
    email = "fraud_tester@shield.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Fraud Tester",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Shield Bank"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()
    token = login_resp["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_transaction_validation_errors(auth_headers):
    # Reject negative amount
    invalid_tx = {
        "transaction_id": "TX_INVALID_001",
        "customer_id": "CUST_999",
        "merchant_id": "MERCH_999",
        "device_id": "DEV_999",
        "amount": -50.00,
        "currency": "USD",
        "transaction_type": "CARD_NOT_PRESENT"
    }
    resp = client.post("/api/v1/transactions", json=invalid_tx, headers=auth_headers)
    assert resp.status_code == 422 # Unprocessable entity validation error

def test_full_fraud_pipeline_execution(auth_headers):
    tx_payload = {
        "transaction_id": "TX_NORMAL_001",
        "customer_id": "CUST_1001",
        "merchant_id": "MERCH_5001",
        "device_id": "DEV_8001",
        "amount": 75.50,
        "currency": "USD",
        "transaction_type": "CARD_NOT_PRESENT",
        "location": "New York, US",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    resp = client.post("/api/v1/transactions", json=tx_payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["transaction_id"] == "TX_NORMAL_001"
    assert data["status"] in ["PROCESSED", "FLAGGED"]
    
    # Verify Risk Score & SHAP Explanation
    assert "risk_score" in data
    risk = data["risk_score"]
    assert 0.0 <= risk["fraud_probability"] <= 1.0
    assert 0.0 <= risk["anomaly_score"] <= 1.0
    assert 0.0 <= risk["risk_score"] <= 100.0
    assert risk["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    assert "explanation" in risk
    expl = risk["explanation"]
    assert "top_factors" in expl
    assert isinstance(expl["top_factors"], list)
    if len(expl["top_factors"]) > 0:
        factor = expl["top_factors"][0]
        assert "feature_name" in factor
        assert "contribution" in factor
        assert "direction" in factor

def test_transaction_idempotency(auth_headers):
    tx_payload = {
        "transaction_id": "TX_IDEMPOTENT_001",
        "customer_id": "CUST_1002",
        "merchant_id": "MERCH_5002",
        "device_id": "DEV_8002",
        "amount": 500.00,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER"
    }

    # Request 1
    resp1 = client.post("/api/v1/transactions", json=tx_payload, headers=auth_headers)
    assert resp1.status_code == 201
    id1 = resp1.json()["id"]

    # Request 2 (Duplicate)
    resp2 = client.post("/api/v1/transactions", json=tx_payload, headers=auth_headers)
    assert resp2.status_code == 201
    id2 = resp2.json()["id"]

    # Must return exact same transaction without creating duplicate DB entry
    assert id1 == id2
