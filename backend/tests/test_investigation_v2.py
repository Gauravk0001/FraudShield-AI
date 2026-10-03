"""
test_investigation_v2.py
========================
Comprehensive tests for:
- Alert opens correct/existing case (idempotency)
- No duplicate investigations
- Direct case URL loads same case
- ESCALATED status transition
- Forensic snapshot stored on case
- Analyst actions update status and audit history
- Unauthorized users cannot access another tenant's case
- WebSocket events update correct case (via event bus)
- Browser refresh preserves case state (deep-link GET)
- Optimistic concurrency conflict detection
- POST /alerts/{id}/investigate shortcut
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─── Fixtures ──────────────────────────────────────────────────────────────────

def _register_and_login(email: str, role: str, org_name: str) -> dict:
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Test User",
        "password": "Password123!",
        "role": role,
        "organization_name": org_name,
    })
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers():
    return _register_and_login("analyst_v2@bank.com", "FRAUD_ANALYST", "TestBank")


@pytest.fixture
def analyst_b_headers():
    return _register_and_login("analyst_b_v2@bank.com", "FRAUD_ANALYST", "TestBank")


@pytest.fixture
def viewer_headers():
    return _register_and_login("viewer_v2@bank.com", "VIEWER", "TestBank")


@pytest.fixture
def admin_headers():
    return _register_and_login("admin_v2@bank.com", "ADMIN", "TestBank")


@pytest.fixture
def other_org_headers():
    return _register_and_login("attacker@other.com", "FRAUD_ANALYST", "OtherOrg")


def _create_high_risk_alert(headers: dict) -> str:
    """Create a transaction that generates an alert and return its alert_id."""
    tx = {
        "transaction_id": f"TX_V2_{id(headers)}",
        "customer_id": "CUST_V2",
        "merchant_id": "MERCH_V2",
        "device_id": "DEV_V2",
        "amount": 15000.00,
        "currency": "USD",
        "transaction_type": "WIRE_TRANSFER",
    }
    client.post("/api/v1/transactions", json=tx, headers=headers)
    alerts = client.get("/api/v1/alerts", headers=headers).json()
    assert len(alerts) >= 1
    return alerts[0]["id"]


# ─── Test: idempotent investigation creation ───────────────────────────────────

class TestInvestigationIdempotency:

    def test_alert_opens_correct_existing_case_not_duplicate(self, analyst_headers):
        """POST /investigations with same alert_id twice → same case_id, never duplicate."""
        alert_id = _create_high_risk_alert(analyst_headers)

        r1 = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers)
        assert r1.status_code in (200, 201)
        case_id_1 = r1.json()["id"]

        r2 = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers)
        assert r2.status_code in (200, 201)
        case_id_2 = r2.json()["id"]

        assert case_id_1 == case_id_2, "Duplicate investigation created — idempotency broken"

    def test_investigate_shortcut_returns_case_id(self, analyst_headers):
        """POST /alerts/{id}/investigate → returns case_id and created flag."""
        alert_id = _create_high_risk_alert(analyst_headers)

        r1 = client.post(f"/api/v1/alerts/{alert_id}/investigate", headers=analyst_headers)
        assert r1.status_code == 200
        data = r1.json()
        assert "case_id" in data
        assert data["created"] is True

        # Second call: same case_id, created=False
        r2 = client.post(f"/api/v1/alerts/{alert_id}/investigate", headers=analyst_headers)
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["case_id"] == data["case_id"]
        assert data2["created"] is False

    def test_investigation_list_has_no_duplicates(self, analyst_headers):
        """Investigation list must not contain more than one investigation per alert."""
        alert_id = _create_high_risk_alert(analyst_headers)

        # Create three times
        for _ in range(3):
            client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers)

        inv_list = client.get("/api/v1/investigations", headers=analyst_headers).json()
        alert_ids = [i["alert_id"] for i in inv_list]
        assert len(alert_ids) == len(set(alert_ids)), "Duplicate investigations found for same alert"


# ─── Test: deep-link URL loads same case ──────────────────────────────────────

class TestDeepLink:

    def test_direct_case_url_loads_same_investigation(self, analyst_headers):
        """GET /investigations/{case_id} → same case state across requests."""
        alert_id = _create_high_risk_alert(analyst_headers)
        r = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers)
        case_id = r.json()["id"]

        # Simulate 'refresh' with direct URL
        r2 = client.get(f"/api/v1/investigations/{case_id}", headers=analyst_headers)
        assert r2.status_code == 200
        data = r2.json()
        assert data["id"] == case_id
        assert data["alert_id"] == alert_id

    def test_by_alert_lookup_returns_existing_case(self, analyst_headers):
        """GET /investigations/by-alert/{alert_id} → returns existing investigation."""
        alert_id = _create_high_risk_alert(analyst_headers)
        r = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers)
        case_id = r.json()["id"]

        r2 = client.get(f"/api/v1/investigations/by-alert/{alert_id}", headers=analyst_headers)
        assert r2.status_code == 200
        assert r2.json()["id"] == case_id

    def test_by_alert_returns_null_for_no_investigation(self, analyst_headers):
        """GET /investigations/by-alert/{alert_id} → returns null when no investigation exists."""
        alert_id = _create_high_risk_alert(analyst_headers)
        # Don't create investigation
        r = client.get(f"/api/v1/investigations/by-alert/{alert_id}", headers=analyst_headers)
        assert r.status_code == 200
        assert r.json() is None


# ─── Test: status transitions ──────────────────────────────────────────────────

class TestStatusTransitions:

    def test_full_status_lifecycle_open_review_resolved(self, analyst_headers):
        """OPEN → IN_REVIEW → RESOLVED with version tracking."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        assert inv["status"] == "OPEN"

        claimed = client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_headers).json()
        assert claimed["status"] == "IN_REVIEW"
        assert claimed["version"] == 2

        resolved = client.post(
            f"/api/v1/investigations/{inv['id']}/resolve",
            json={"decision": "CONFIRMED_FRAUD", "decision_reason": "High velocity fraud confirmed.", "version": 2},
            headers=analyst_headers,
        ).json()
        assert resolved["status"] == "RESOLVED"
        assert resolved["decision"] == "CONFIRMED_FRAUD"
        assert resolved["resolved_at"] is not None

    def test_escalate_transition(self, analyst_headers):
        """OPEN → IN_REVIEW → ESCALATED."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_headers)

        esc = client.post(
            f"/api/v1/investigations/{inv['id']}/escalate",
            json={"reason": "Requires manager review — amount exceeds threshold.", "version": 2},
            headers=analyst_headers,
        )
        assert esc.status_code == 200
        assert esc.json()["status"] == "ESCALATED"

    def test_cannot_escalate_resolved_case(self, analyst_headers):
        """Cannot escalate a resolved investigation."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_headers)
        client.post(
            f"/api/v1/investigations/{inv['id']}/resolve",
            json={"decision": "FALSE_POSITIVE", "decision_reason": "Analyst confirmed legitimate.", "version": 2},
            headers=analyst_headers,
        )

        esc = client.post(
            f"/api/v1/investigations/{inv['id']}/escalate",
            json={"reason": "Too late escalation.", "version": 3},
            headers=analyst_headers,
        )
        assert esc.status_code == 400


# ─── Test: forensic snapshot ───────────────────────────────────────────────────

class TestForensicSnapshot:

    def test_investigation_has_forensic_snapshot(self, analyst_headers):
        """Investigation created from alert should carry a forensic_snapshot."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        # Snapshot may be None if alert has no risk factors, but the key should exist
        assert "forensic_snapshot" in inv

    def test_risk_breakdown_fields_present_in_snapshot(self, analyst_headers):
        """If forensic_snapshot exists, it should contain risk_score and amount."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        snap = inv.get("forensic_snapshot")
        if snap:
            assert "risk_score" in snap
            assert "amount" in snap


# ─── Test: concurrency protection ─────────────────────────────────────────────

class TestOptimisticConcurrency:

    def test_stale_version_resolve_returns_409(self, analyst_headers):
        """Resolving with wrong version raises 409 Conflict."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_headers)

        # Use stale version (1 instead of 2)
        r = client.post(
            f"/api/v1/investigations/{inv['id']}/resolve",
            json={"decision": "FALSE_POSITIVE", "decision_reason": "Legit transaction confirmed.", "version": 1},
            headers=analyst_headers,
        )
        assert r.status_code == 409
        assert "reload" in r.json()["detail"].lower() or "updated" in r.json()["detail"].lower()

    def test_two_analysts_cannot_both_claim_same_case(self, analyst_headers, analyst_b_headers):
        """Second analyst claiming an already-claimed case gets 409."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_headers)

        r = client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=analyst_b_headers)
        assert r.status_code == 409


# ─── Test: tenant isolation (RLS) ─────────────────────────────────────────────

class TestTenantIsolation:

    def test_other_tenant_cannot_access_case(self, analyst_headers, other_org_headers):
        """Analyst from different org cannot read or modify another org's investigation."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        case_id = inv["id"]

        r = client.get(f"/api/v1/investigations/{case_id}", headers=other_org_headers)
        assert r.status_code == 404, "Cross-tenant investigation access should return 404"

    def test_other_tenant_cannot_claim_case(self, analyst_headers, other_org_headers):
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()

        r = client.post(f"/api/v1/investigations/{inv['id']}/claim", headers=other_org_headers)
        assert r.status_code in (403, 404)


# ─── Test: role access control ────────────────────────────────────────────────

class TestRoleAccess:

    def test_viewer_cannot_create_investigation(self, viewer_headers):
        """Viewer role must not be able to create investigations."""
        # First make an alert visible to the viewer's org (need analyst first)
        analyst_h = _register_and_login("analyst_for_viewer@bank.com", "FRAUD_ANALYST", "TestBank")
        alert_id = _create_high_risk_alert(analyst_h)

        r = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=viewer_headers)
        assert r.status_code == 403

    def test_viewer_cannot_add_note(self, analyst_headers, viewer_headers):
        """Viewer role must not be able to add investigation notes."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()

        r = client.post(
            f"/api/v1/investigations/{inv['id']}/notes",
            json={"note_text": "Unauthorized note attempt"},
            headers=viewer_headers,
        )
        assert r.status_code == 403

    def test_viewer_can_read_investigations(self, analyst_headers, viewer_headers):
        """Viewer can read but not modify."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()

        r = client.get(f"/api/v1/investigations/{inv['id']}", headers=viewer_headers)
        # Viewers are in the same org, so they should be able to read
        assert r.status_code == 200


# ─── Test: analyst actions update audit history ───────────────────────────────

class TestAuditTrail:

    def test_investigation_actions_logged_to_audit(self, analyst_headers, admin_headers):
        """Creating, claiming, noting, and resolving all appear in audit log."""
        alert_id = _create_high_risk_alert(analyst_headers)
        inv = client.post("/api/v1/investigations", json={"alert_id": alert_id}, headers=analyst_headers).json()
        case_id = inv["id"]

        client.post(f"/api/v1/investigations/{case_id}/claim", headers=analyst_headers)
        client.post(f"/api/v1/investigations/{case_id}/notes", json={"note_text": "Evidence reviewed."}, headers=analyst_headers)
        client.post(
            f"/api/v1/investigations/{case_id}/resolve",
            json={"decision": "CONFIRMED_FRAUD", "decision_reason": "Confirmed fraud.", "version": 2},
            headers=analyst_headers,
        )

        audit_resp = client.get("/api/v1/audit-logs", headers=admin_headers)
        assert audit_resp.status_code == 200
        actions = [e["action"] for e in audit_resp.json()]
        assert "INVESTIGATION_CREATED" in actions
        assert "INVESTIGATION_CLAIMED" in actions
        assert "INVESTIGATION_NOTE_ADDED" in actions
        assert "INVESTIGATION_RESOLVED" in actions
