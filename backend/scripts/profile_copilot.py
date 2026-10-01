import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.transaction import Transaction
from app.core.security import create_access_token
from app.services.copilot_service import extract_evidence_context, generate_copilot_response

def profile_copilot():
    print("=== COPILOT DETAILED PROFILING TEST ===")
    t0 = time.perf_counter()

    # Step 1: Auth & Token Generation
    t_auth_start = time.perf_counter()
    token = create_access_token(subject="user_admin", role="ADMIN", organization_id="org_shield_bank")
    t_auth = time.perf_counter() - t_auth_start
    print(f"1. Authentication / Token time: {t_auth*1000:.2f} ms")

    # Step 2: Database & Context Retrieval
    db = SessionLocal()
    try:
        t_db_start = time.perf_counter()
        tx = db.query(Transaction).first()
        tx_id = tx.id if tx else None
        org_id = tx.organization_id if tx else "org_shield_bank"
        evidence = extract_evidence_context(db=db, organization_id=org_id, transaction_id=tx_id)
        t_db = time.perf_counter() - t_db_start
        print(f"2. Database & Context extraction time: {t_db*1000:.2f} ms (Target Tx: {tx_id})")
    finally:
        db.close()

    # Step 3: LLM / Generation Call
    print("3. Invoking generate_copilot_response()...")
    t_llm_start = time.perf_counter()
    result = generate_copilot_response(
        message="Explain why this transaction was flagged and summarize the risk signals.",
        evidence=evidence
    )
    t_llm = time.perf_counter() - t_llm_start
    print(f"3. LLM / Generation time: {t_llm:.2f} s")

    # Total
    t_total = time.perf_counter() - t0
    print(f"Total time: {t_total:.2f} s")
    print(f"Response preview:\n{result.get('response', '')[:250]}...")

if __name__ == "__main__":
    profile_copilot()
