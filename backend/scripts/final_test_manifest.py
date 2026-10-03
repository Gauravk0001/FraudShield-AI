"""
FraudShield AI — Final Test Manifest Generator & Verifier
Generates and enforces cryptographic immutability of the final untouched temporal test set.
"""

import os
import sys
import json
import hashlib
import pandas as pd
from typing import Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
PARQUET_PATH = os.path.join(DATA_DIR, "causal_transactions.parquet")
MANIFEST_PATH = os.path.join(DATA_DIR, "final_test_manifest.json")

FEATURE_NAMES = [
    "amount",
    "transaction_type_encoded",
    "hour_of_day",
    "day_of_week",
    "transaction_velocity_1h",
    "transaction_velocity_24h",
    "avg_amount_customer_30d",
    "amount_deviation_ratio",
    "time_since_last_transaction_seconds",
    "is_new_device",
    "is_new_merchant",
    "location_changed"
]

def generate_manifest():
    if not os.path.exists(PARQUET_PATH):
        raise FileNotFoundError(f"Parquet file not found: {PARQUET_PATH}")

    df = pd.read_parquet(PARQUET_PATH)
    n_tot = len(df)
    val_end = int(n_tot * 0.85)
    df_test = df.iloc[val_end:].copy()

    # Compute Test Subset Hash
    test_bytes = df_test.to_csv(index=False).encode("utf-8")
    test_hash = hashlib.sha256(test_bytes).hexdigest()

    schema_str = ",".join(sorted(FEATURE_NAMES))
    schema_hash = hashlib.sha256(schema_str.encode("utf-8")).hexdigest()

    manifest = {
        "manifest_version": "2.0.0-forensic",
        "description": "Cryptographically locked final untouched temporal test set (last 15% of chronological timeline)",
        "dataset_source": "data/causal_transactions.parquet",
        "temporal_slice": "Last 15% chronological",
        "total_rows": len(df_test),
        "legitimate_count": int((df_test["is_fraud"] == 0).sum()),
        "fraud_count": int((df_test["is_fraud"] == 1).sum()),
        "fraud_rate": round(float(df_test["is_fraud"].mean()), 4),
        "test_data_sha256": test_hash,
        "feature_schema_sha256": schema_hash,
        "feature_count": len(FEATURE_NAMES),
        "start_timestamp": str(df_test["timestamp"].min()),
        "end_timestamp": str(df_test["timestamp"].max())
    }

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[SUCCESS] Final test manifest created at: {MANIFEST_PATH}")
    print(f" -> Test rows: {manifest['total_rows']}, Fraud: {manifest['fraud_count']} ({manifest['fraud_rate']*100:.2f}%)")
    print(f" -> SHA-256: {test_hash}")

def verify_manifest():
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")
    if not os.path.exists(PARQUET_PATH):
        raise FileNotFoundError(f"Parquet not found at {PARQUET_PATH}")

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    df = pd.read_parquet(PARQUET_PATH)
    n_tot = len(df)
    val_end = int(n_tot * 0.85)
    df_test = df.iloc[val_end:].copy()

    test_bytes = df_test.to_csv(index=False).encode("utf-8")
    current_hash = hashlib.sha256(test_bytes).hexdigest()

    if current_hash != manifest["test_data_sha256"]:
        raise ValueError(
            f"TEST SET INTEGRITY VIOLATION: Current test hash {current_hash} does not match manifest hash {manifest['test_data_sha256']}"
        )

    if len(df_test) != manifest["total_rows"]:
        raise ValueError(f"TEST ROW COUNT MISMATCH: Expected {manifest['total_rows']}, got {len(df_test)}")

    print(f"[PASS] Final test set verified against locked manifest ({manifest['total_rows']} rows, SHA-256 intact).")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_manifest()
    else:
        generate_manifest()
