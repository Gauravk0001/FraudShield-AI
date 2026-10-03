import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserRole
from app.core.security import verify_password, get_password_hash

client = TestClient(app)

def test_password_hashing():
    raw_password = "SecurePassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_user_registration_and_login():
    # Register user
    reg_data = {
        "email": "analyst_alpha@fraudshield.io",
        "full_name": "Alpha Analyst",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Bank Alpha"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    user_info = response.json()
    assert user_info["email"] == "analyst_alpha@fraudshield.io"
    assert user_info["role"] == "FRAUD_ANALYST"

    # Login with registered user
    login_data = {
        "email": "analyst_alpha@fraudshield.io",
        "password": "Password123!"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_data)
    assert login_resp.status_code == 200
    token_info = login_resp.json()
    assert "access_token" in token_info
    assert token_info["token_type"] == "bearer"

    # Test /me endpoint
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "analyst_alpha@fraudshield.io"

def test_invalid_login_and_unauthorized():
    # Login with wrong password
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "analyst_alpha@fraudshield.io",
        "password": "WrongPassword!"
    })
    assert login_resp.status_code == 401

    # Access /me without token
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401

def test_organization_isolation():
    # Register user in Org A
    user_a = client.post("/api/v1/auth/register", json={
        "email": "user_a@orga.com",
        "full_name": "User A",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Organization A"
    }).json()

    # Register user in Org B
    user_b = client.post("/api/v1/auth/register", json={
        "email": "user_b@orgb.com",
        "full_name": "User B",
        "password": "Password123!",
        "role": "FRAUD_ANALYST",
        "organization_name": "Organization B"
    }).json()

    # Verify they belong to distinct organizations
    assert user_a["organization_id"] != user_b["organization_id"]
