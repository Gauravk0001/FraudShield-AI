import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.core.database import SessionLocal
from app.models.transaction import Transaction
from app.services.copilot_service import extract_evidence_context, generate_copilot_response, stream_copilot_chunks

def profile_streaming_and_caching():
    print("=== STREAMING & CACHING PERFORMANCE BENCHMARK ===")
    db = SessionLocal()
    try:
        tx = db.query(Transaction).first()
        tx_id = tx.id if tx else None
        org_id = tx.organization_id if tx else "org_shield_bank"
        evidence = extract_evidence_context(db=db, organization_id=org_id, transaction_id=tx_id)
    finally:
        db.close()

    # Test 1: Progressive Streaming Token Latency
    print("\n1. Testing stream_copilot_chunks (Time to First Token)...")
    t0 = time.perf_counter()
    first_token_time = None
    chunks = []
    for item in stream_copilot_chunks("Why was this transaction flagged?", evidence):
        if first_token_time is None and item.get("type") == "chunk":
            first_token_time = time.perf_counter() - t0
        chunks.append(item)
    total_stream_time = time.perf_counter() - t0
    print(f"-> Time to first token: {first_token_time*1000:.2f} ms")
    print(f"-> Total stream generation time: {total_stream_time*1000:.2f} ms")
    print(f"-> Chunks yielded: {len(chunks)}")

    # Test 2: In-Memory Evidence Interpretation Cache
    print("\n2. Testing in-memory query cache...")
    t0 = time.perf_counter()
    res1 = generate_copilot_response("Summarize evidence", evidence)
    t_first = time.perf_counter() - t0

    t0 = time.perf_counter()
    res2 = generate_copilot_response("Summarize evidence", evidence)
    t_second = time.perf_counter() - t0
    print(f"-> First call time: {t_first:.3f} s")
    print(f"-> Cached repeat call time: {t_second*1000:.3f} ms (Speedup: {t_first/(t_second if t_second > 0 else 0.0001):.1f}x)")

if __name__ == "__main__":
    profile_streaming_and_caching()
