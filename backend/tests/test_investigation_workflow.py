import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def analyst_a_context():
    email = "analyst_a@shield.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Analyst A",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Investigation Bank"
    })
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "email": email}

@pytest.fixture
def analyst_b_context():
    email = "analyst_b@shield.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Analyst B",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Investigation Bank"
    })
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "email": email}

def test_investigation_full_lifecycle_and_concurrency(analyst_a_context, analyst_b_context):
    headers_a = analyst_a_context["headers"]
    headers_b = analyst_b_context["headers"]

    # 1. Trigger suspicious transaction to generate Alert
    tx_payload = {
        "transaction_id": "TX_INV_TEST_999",
        "customer_id": "CUST_INV_01",
        "merchant_id": "MERCH_INV_01",
        "device_id": "DEV_INV_01",
        "amount": 12500.00,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER"
    }
    client.post("/api/v1/transactions", json=tx_payload, headers=headers_a)

    # 2. Get Alert
    alerts = client.get("/api/v1/alerts", headers=headers_a).json()
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    # 3. Create Investigation
    inv_resp = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=headers_a)
    assert inv_resp.status_code == 201
    inv = inv_resp.json()
    inv_id = inv["id"]
    assert inv["status"] == "OPEN"

    # 4. Analyst A Claims Investigation
    claim_resp_a = client.post(f"/api/v1/investigations/{inv_id}/claim", headers=headers_a)
    assert claim_resp_a.status_code == 200
    assert claim_resp_a.json()["status"] == "IN_REVIEW"

    # 5. Analyst B Tries to Claim Same Investigation -> Fails with 409 Conflict (Race Condition Protection)
    claim_resp_b = client.post(f"/api/v1/investigations/{inv_id}/claim", headers=headers_b)
    assert claim_resp_b.status_code == 409

    # 6. Analyst A Adds Note
    note_resp = client.post(
        f"/api/v1/investigations/{inv_id}/notes",
        json={"note_text": "Verified customer identity via OTP. Transaction matches high-velocity pattern."},
        headers=headers_a
    )
    assert note_resp.status_code == 200

    # 7. Analyst A Resolves Investigation with Optimistic Locking Version Check
    curr_version = claim_resp_a.json()["version"]
    resolve_resp = client.post(
        f"/api/v1/investigations/{inv_id}/resolve",
        json={
            "decision": "CONFIRMED_FRAUD",
            "decision_reason": "High velocity wire transfer from new device verified as unauthorized compromise.",
            "version": curr_version
        },
        headers=headers_a
    )
    assert resolve_resp.status_code == 200
    resolved_inv = resolve_resp.json()
    assert resolved_inv["status"] == "RESOLVED"
    assert resolved_inv["decision"] == "CONFIRMED_FRAUD"

    # 8. Attempting to add note after resolution fails
    late_note = client.post(
        f"/api/v1/investigations/{inv_id}/notes",
        json={"note_text": "Late note attempt"},
        headers=headers_a
    )
    assert late_note.status_code == 400
