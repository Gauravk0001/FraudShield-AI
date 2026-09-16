import os
import json
import hashlib
import pandas as pd
from datetime import datetime

def validate_dataset_integrity() -> bool:
    print("================================================================")
    print("   FRAUDSHIELD AI — DATASET INTEGRITY & METADATA VALIDATOR      ")
    print("================================================================\n")

    root_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(root_dir, "data")
    parquet_path = os.path.join(data_dir, "causal_transactions.parquet")
    meta_path = os.path.join(data_dir, "forensic_dataset_metadata.json")

    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Parquet dataset not found at: {parquet_path}")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Dataset metadata not found at: {meta_path}")

    # 1. Load metadata
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 2. Verify SHA-256 Hash
    hasher = hashlib.sha256()
    with open(parquet_path, "rb") as f:
        hasher.update(f.read())
    calc_hash = hasher.hexdigest()

    assert calc_hash == meta["sha256_hash"], f"SHA-256 mismatch! Metadata: {meta['sha256_hash']}, Calc: {calc_hash}"
    print(f"[PASS] Dataset SHA-256 Hash: {calc_hash[:16]}... (Matches metadata)")

    # 3. Load DataFrame and check shape & entities
    df = pd.read_parquet(parquet_path)
    
    assert len(df) == meta["transactions"], f"Row count mismatch! DF: {len(df)}, Meta: {meta['transactions']}"
    print(f"[PASS] Transaction Count: {len(df):,} (Matches metadata)")

    n_fraud = int(df["is_fraud"].sum())
    assert n_fraud == meta["fraudulent_transactions"], f"Fraud count mismatch! DF: {n_fraud}, Meta: {meta['fraudulent_transactions']}"
    n_legit = len(df) - n_fraud
    assert n_legit == meta["legitimate_transactions"], f"Legit count mismatch! DF: {n_legit}, Meta: {meta['legitimate_transactions']}"
    print(f"[PASS] Label Counts: Legit={n_legit:,}, Fraud={n_fraud:,} ({meta['fraud_rate_pct']}%)")

    # 4. Check Entities
    n_cust = int(df["customer_id"].nunique())
    assert n_cust == meta["customers"], f"Customer count mismatch! DF: {n_cust}, Meta: {meta['customers']}"
    n_merch = int(df["merchant_id"].nunique())
    assert n_merch == meta["merchants"], f"Merchant count mismatch! DF: {n_merch}, Meta: {meta['merchants']}"
    n_dev = int(df["device_id"].nunique())
    assert n_dev == meta["devices"], f"Device count mismatch! DF: {n_dev}, Meta: {meta['devices']}"
    print(f"[PASS] Unique Entities: Customers={n_cust:,}, Merchants={n_merch:,}, Devices={n_dev:,}")

    # 5. Check Topologies sum to 100%
    topo_pct_sum = sum(meta["fraud_topologies_percentages"].values())
    assert abs(topo_pct_sum - 100.0) < 0.1, f"Topology percentages do not sum to 100%! Sum: {topo_pct_sum}"
    print(f"[PASS] Fraud Topologies Validated: {len(meta['fraud_topologies_counts'])} topologies (Sum = {topo_pct_sum:.1f}%)")

    # 6. Check Chronological Monotonicity
    ts = pd.to_datetime(df["timestamp"])
    assert ts.is_monotonic_increasing, "Dataset is not strictly chronologically ordered!"
    print(f"[PASS] Chronological Ordering: Verified monotonic timestamp sequence ({meta['date_range']['start'][:10]} to {meta['date_range']['end'][:10]})")

    print("\n================================================================")
    print("   [SUCCESS] ALL DATASET INTEGRITY CHECKS PASSED (100% VALID)   ")
    print("================================================================\n")
    return True

if __name__ == "__main__":
    validate_dataset_integrity()
