import os
import sys
import time
import json
from datetime import datetime, timezone

os.environ.setdefault("DB_TYPE", "sqlite")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import create_access_token
from fastapi.testclient import TestClient
from app.main import app
from seed_demo import seed_demo_environment

def run_10x_reliability_benchmark():
    print("============================================================")
    print("FRAUDSHIELD AI — 10X DEMO RELIABILITY & BENCHMARK SUITE")
    print("============================================================")

    client = TestClient(app)
    results = []

    # Get analyst token
    db = SessionLocal()
    analyst = db.query(User).filter(User.email == "analyst@shieldbank.com").first()
    token = create_access_token(subject=analyst.id, role=analyst.role.value, organization_id=analyst.organization_id)
    headers = {"Authorization": f"Bearer {token}"}
    db.close()

    for run_idx in range(1, 11):
        t_start = time.perf_counter()
        run_status = "PASS"
        err_msg = ""

        try:
            # 1. Ingest Hero Suspicious Transaction
            tx_id = f"benchmark_hero_run_{run_idx}_{int(time.time())}"
            t_ingest_start = time.perf_counter()
            tx_resp = client.post("/api/v1/transactions", headers=headers, json={
                "transaction_id": tx_id,
                "customer_id": "cust_101",
                "merchant_id": "merch_crypto_offshore_ltd",
                "device_id": f"dev_benchmark_novel_{run_idx}",
                "amount": 9850.00,
                "currency": "USD",
                "transaction_type": "WIRE_TRANSFER",
                "location": "Singapore, SG"
            })
            e2e_latency_ms = (time.perf_counter() - t_ingest_start) * 1000

            assert tx_resp.status_code == 201, f"Ingestion failed: {tx_resp.text}"
            tx_data = tx_resp.json()
            score = tx_data["risk_score"]["risk_score"]
            level = tx_data["risk_score"]["risk_level"]
            assert score >= 70.0, f"Expected HIGH risk >= 70, got {score}"

            # 2. Verify Alert was created
            alerts_resp = client.get("/api/v1/alerts?limit=100", headers=headers)
            assert alerts_resp.status_code == 200
            alerts = alerts_resp.json()
            matched_alerts = [a for a in alerts if a["transaction_id"] == tx_data["id"]]
            assert len(matched_alerts) > 0, "No alert created for high-risk transaction"
            alert_id = matched_alerts[0]["id"]

            # 3. Create Investigation
            inv_resp = client.post("/api/v1/investigations", headers=headers, json={
                "alert_id": alert_id
            })
            assert inv_resp.status_code == 201, f"Investigation creation failed: {inv_resp.text}"
            inv_id = inv_resp.json()["id"]

            # 4. Claim Investigation (concurrency test)
            claim_resp = client.post(f"/api/v1/investigations/{inv_id}/claim", headers=headers)
            assert claim_resp.status_code == 200, f"Claim failed: {claim_resp.text}"
            assert claim_resp.json()["status"] == "IN_REVIEW"

            # 5. Add Analyst Note
            note_resp = client.post(f"/api/v1/investigations/{inv_id}/notes", headers=headers, json={
                "note_text": f"Benchmark Run {run_idx}: Customer confirms unrecognized IP in Singapore. Initiating account freeze."
            })
            assert note_resp.status_code == 200

            # 6. Copilot Evidence Analysis
            copilot_resp = client.post("/api/v1/copilot/chat", headers=headers, json={
                "message": "Summarize evidence and top risk factors for resolution",
                "investigation_id": inv_id
            })
            assert copilot_resp.status_code == 200, f"Copilot failed: {copilot_resp.text}"
            assert len(copilot_resp.json().get("response", "")) > 10

            # 7. Final Resolution
            resolve_resp = client.post(f"/api/v1/investigations/{inv_id}/resolve", headers=headers, json={
                "decision": "CONFIRMED_FRAUD",
                "decision_reason": f"Benchmark Run {run_idx}: Unauthorized wire transfer confirmed. Account secured.",
                "version": claim_resp.json()["version"]
            })
            assert resolve_resp.status_code == 200, f"Resolve failed: {resolve_resp.text}"
            assert resolve_resp.json()["status"] == "RESOLVED"

        except Exception as ex:
            run_status = "FAIL"
            err_msg = str(ex)

        total_run_duration_ms = (time.perf_counter() - t_start) * 1000

        result_entry = {
            "run": run_idx,
            "status": run_status,
            "e2e_api_latency_ms": round(e2e_latency_ms, 2) if run_status == "PASS" else None,
            "total_lifecycle_ms": round(total_run_duration_ms, 2),
            "risk_score": score if run_status == "PASS" else None,
            "error": err_msg if err_msg else None
        }
        results.append(result_entry)

        status_flag = "[PASS]" if run_status == "PASS" else f"[FAIL: {err_msg}]"
        print(f"Run {run_idx:02d}/10: {status_flag} | Tx Ingest E2E: {result_entry['e2e_api_latency_ms']} ms | Full Lifecycle: {result_entry['total_lifecycle_ms']} ms | Score: {result_entry['risk_score']}")

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    avg_e2e = sum(r["e2e_api_latency_ms"] for r in results if r["e2e_api_latency_ms"]) / passed_count if passed_count else 0
    avg_lifecycle = sum(r["total_lifecycle_ms"] for r in results) / len(results)

    print("\n============================================================")
    print(f"BENCHMARK RESULT: {passed_count}/10 SUCCESSFUL RUNS ({passed_count/10*100:.0f}%)")
    print(f"Mean Ingestion API Latency: {avg_e2e:.2f} ms")
    print(f"Mean Full E2E Lifecycle Duration: {avg_lifecycle:.2f} ms")
    print("============================================================")

    return results

if __name__ == "__main__":
    run_10x_reliability_benchmark()
