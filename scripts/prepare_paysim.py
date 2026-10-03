#!/usr/bin/env python3
"""
FraudShield AI — PaySim Dataset Preparation & Chronological Split Pipeline

Prepares the PaySim synthetic transaction dataset into strictly non-overlapping
chronological splits for model training, threshold calibration, and final testing.

Splits:
- Train Split: First 70% of simulated steps (e.g., steps 1 to 520)
- Validation Split: Next 15% of simulated steps (e.g., steps 521 to 632)
- Locked Test Split: Final 15% of simulated steps (e.g., steps 633 to 744)

CRITICAL SAFETY & LEAKAGE PREVENTION:
- Ground-truth labels ('isFraud', 'isFlaggedFraud') are STRICTLY ISOLATED.
  They are saved only as targets for offline model evaluation, never as model features.
- Historical features use strictly prior events (step < current_step).
- Generates both with-balance and without-balance feature matrices.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

# Add backend to path for shared feature extraction
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.ml.feature_schema import (
    PAYSIM_FEATURES_NO_BALANCE,
    PAYSIM_FEATURES_WITH_BALANCE,
    validate_feature_columns
)
from app.ml.paysim_features import extract_paysim_batch_features

EXPECTED_COLUMNS = [
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud"
]

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
EXPECTED_CSV_NAME = "PS_20174392719_1491204439457_Log.csv"

def generate_synthetic_paysim_sample(output_csv_path: str, n_rows: int = 25000) -> str:
    """
    Generates a high-fidelity synthetic PaySim sample matching the exact 11-column
    PaySim Kaggle schema across steps 1 to 744, enabling zero-friction local testing
    when the 2GB raw file has not yet been downloaded.
    """
    print(f"[*] Generating reproducible synthetic PaySim sample ({n_rows} rows) across 744 steps...")
    np.random.seed(42)

    # 744 steps = 31 days of simulated hourly events
    steps = np.sort(np.random.randint(1, 744, size=n_rows))
    types = np.random.choice(["PAYMENT", "CASH_OUT", "CASH_IN", "TRANSFER", "DEBIT"], size=n_rows, p=[0.35, 0.35, 0.20, 0.08, 0.02])
    
    # Amounts: log-normal distribution with long tail
    amounts = np.round(np.random.lognormal(mean=6.5, sigma=1.8, size=n_rows), 2)
    amounts = np.clip(amounts, 1.0, 500000.0)

    # Origin accounts (500 distinct origins for rich velocity patterns)
    orig_ids = [f"C{np.random.randint(1000000, 9999999)}" for _ in range(500)]
    name_origs = np.random.choice(orig_ids, size=n_rows)

    # Destination accounts (mix of customers C and merchants M)
    dest_ids = [f"M{np.random.randint(1000000, 9999999)}" if i % 2 == 0 else f"C{np.random.randint(1000000, 9999999)}" for i in range(800)]
    name_dests = np.random.choice(dest_ids, size=n_rows)

    # Balances
    old_orig = np.round(np.random.lognormal(mean=7.0, sigma=2.0, size=n_rows), 2)
    new_orig = np.maximum(0.0, old_orig - amounts)
    old_dest = np.round(np.random.lognormal(mean=6.0, sigma=2.2, size=n_rows), 2)
    new_dest = old_dest + amounts

    # Fraud label: ~1.2% prevalence, realistic for financial transaction sets
    is_fraud = np.zeros(n_rows, dtype=int)
    for i in range(n_rows):
        t = types[i]
        amt = amounts[i]
        # In PaySim, fraud occurs primarily in TRANSFER and CASH_OUT
        if t in ["TRANSFER", "CASH_OUT"]:
            if amt > 20000 and np.random.random() < 0.15:
                is_fraud[i] = 1
                new_orig[i] = 0.0 # Emptied account shortcut
            elif np.random.random() < 0.02:
                is_fraud[i] = 1
                new_orig[i] = 0.0

    # isFlaggedFraud: simulation rule for transfers > 200,000
    is_flagged = np.zeros(n_rows, dtype=int)
    for i in range(n_rows):
        if types[i] == "TRANSFER" and amounts[i] > 200000:
            is_flagged[i] = 1

    sample_df = pd.DataFrame({
        "step": steps,
        "type": types,
        "amount": amounts,
        "nameOrig": name_origs,
        "oldbalanceOrg": old_orig,
        "newbalanceOrig": new_orig,
        "nameDest": name_dests,
        "oldbalanceDest": old_dest,
        "newbalanceDest": new_dest,
        "isFraud": is_fraud,
        "isFlaggedFraud": is_flagged
    })

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    sample_df.to_csv(output_csv_path, index=False)
    print(f"[+] Saved synthetic PaySim sample to: {output_csv_path} (Fraud count: {is_fraud.sum()})")
    return output_csv_path

def validate_source_columns(df: pd.DataFrame) -> None:
    """Validates that all expected PaySim columns are present."""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"PaySim dataset validation failed! Missing expected columns: {missing}")
    print(f"[+] Source schema validation PASSED. All {len(EXPECTED_COLUMNS)} columns present.")

def prepare_paysim_dataset(
    csv_path: str,
    output_dir: str = DEFAULT_DATA_DIR,
    max_rows: int = None
) -> Dict[str, Any]:
    """
    Main preparation pipeline:
    1. Validates columns
    2. Chronological step-based split (70% train, 15% val, 15% test)
    3. Causal feature engineering (strictly prior events)
    4. Enforces zero label leakage
    5. Saves parquet splits and split manifest
    """
    print("=" * 78)
    print("  FRAUDSHIELD AI — PAYSIM PREPARATION & LEAKAGE-FREE SPLIT PIPELINE")
    print("=" * 78)
    print("NOTICE: PaySim is a synthetic financial simulation.")
    print("Features derived from simulated balance arithmetic are explicitly tracked as shortcuts.")
    print("-" * 78)

    if not os.path.isfile(csv_path):
        sample_path = os.path.join(output_dir, "paysim_synthetic_sample.csv")
        print(f"[-] PaySim source file not found at '{csv_path}'.")
        csv_path = generate_synthetic_paysim_sample(sample_path, n_rows=25000)

    print(f"[*] Reading PaySim data from: {csv_path}")
    if max_rows:
        print(f"[*] Capping ingest to {max_rows:,} rows for rapid execution.")
        df = pd.read_csv(csv_path, nrows=max_rows)
    else:
        df = pd.read_csv(csv_path)

    print(f"[*] Ingested {len(df):,} total transaction records.")
    validate_source_columns(df)

    # Chronological sort
    df.sort_values(by=["step"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    min_step = int(df["step"].min())
    max_step = int(df["step"].max())
    step_range = max_step - min_step + 1

    train_step_cutoff = min_step + int(step_range * 0.70)
    val_step_cutoff = train_step_cutoff + int(step_range * 0.15)

    print(f"[*] Chronological Split Step Boundaries:")
    print(f"    Train Split: Steps {min_step} -> {train_step_cutoff} (First 70%)")
    print(f"    Validation Split: Steps {train_step_cutoff + 1} -> {val_step_cutoff} (Next 15%)")
    print(f"    Locked Test Split: Steps {val_step_cutoff + 1} -> {max_step} (Final 15%)")

    train_mask = df["step"] <= train_step_cutoff
    val_mask = (df["step"] > train_step_cutoff) & (df["step"] <= val_step_cutoff)
    test_mask = df["step"] > val_step_cutoff

    train_raw = df[train_mask].copy()
    val_raw = df[val_mask].copy()
    test_raw = df[test_mask].copy()

    # Safety assertion: zero split overlap
    assert len(set(train_raw["step"]).intersection(set(val_raw["step"]))) == 0, "Temporal overlap between train and val!"
    assert len(set(val_raw["step"]).intersection(set(test_raw["step"]))) == 0, "Temporal overlap between val and test!"

    print(f"[+] Splits created successfully:")
    print(f"    Train: {len(train_raw):,} rows | Fraud: {int(train_raw['isFraud'].sum()):,} ({train_raw['isFraud'].mean()*100:.2f}%)")
    print(f"    Val:   {len(val_raw):,} rows | Fraud: {int(val_raw['isFraud'].sum()):,} ({val_raw['isFraud'].mean()*100:.2f}%)")
    print(f"    Test:  {len(test_raw):,} rows | Fraud: {int(test_raw['isFraud'].sum()):,} ({test_raw['isFraud'].mean()*100:.2f}%)")

    # Feature extraction with causal ordering
    print("[*] Extracting causal features across train split...")
    train_features_no_bal, train_labels = extract_paysim_batch_features(train_raw, with_balance=False)
    train_features_with_bal, _ = extract_paysim_batch_features(train_raw, with_balance=True)

    print("[*] Extracting causal features across validation split...")
    val_features_no_bal, val_labels = extract_paysim_batch_features(val_raw, with_balance=False)
    val_features_with_bal, _ = extract_paysim_batch_features(val_raw, with_balance=True)

    print("[*] Extracting causal features across locked test split...")
    test_features_no_bal, test_labels = extract_paysim_batch_features(test_raw, with_balance=False)
    test_features_with_bal, _ = extract_paysim_batch_features(test_raw, with_balance=True)

    # Assert zero label leakage
    validate_feature_columns(train_features_no_bal.columns)
    validate_feature_columns(train_features_with_bal.columns)
    validate_feature_columns(val_features_no_bal.columns)
    validate_feature_columns(val_features_with_bal.columns)
    validate_feature_columns(test_features_no_bal.columns)
    validate_feature_columns(test_features_with_bal.columns)
    print("[+] Zero label leakage verification PASSED: labels completely absent from feature matrices.")

    # Save prepared dataset files
    os.makedirs(output_dir, exist_ok=True)
    
    # Save combined feature+target frames (label stored in isolated column 'target_is_fraud')
    train_save = train_features_with_bal.copy()
    train_save["target_is_fraud"] = train_labels.values
    val_save = val_features_with_bal.copy()
    val_save["target_is_fraud"] = val_labels.values
    test_save = test_features_with_bal.copy()
    test_save["target_is_fraud"] = test_labels.values

    # Also keep raw test split metadata (step, nameOrig, nameDest, amount, type) for simulator replay
    test_meta_cols = ["step", "type", "amount", "nameOrig", "nameDest", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFraud"]
    test_raw_subset = test_raw[test_meta_cols].copy()

    train_path = os.path.join(output_dir, "paysim_train.parquet")
    val_path = os.path.join(output_dir, "paysim_val.parquet")
    test_path = os.path.join(output_dir, "paysim_test.parquet")
    test_replay_path = os.path.join(output_dir, "paysim_test_replay.json")

    train_save.to_parquet(train_path, index=False)
    val_save.to_parquet(val_path, index=False)
    test_save.to_parquet(test_path, index=False)

    # Save first 500 test rows as JSON for rapid simulator replay
    replay_records = test_raw_subset.head(1000).to_dict(orient="records")
    with open(test_replay_path, "w", encoding="utf-8") as f:
        json.dump(replay_records, f, indent=2)

    manifest = {
        "dataset_name": "PaySim Financial Fraud Simulation",
        "is_synthetic": True,
        "source_file": os.path.basename(csv_path),
        "total_records": len(df),
        "split_policy": "Strict 70/15/15 chronological step split",
        "step_boundaries": {
            "min_step": min_step,
            "max_step": max_step,
            "train_cutoff": train_step_cutoff,
            "val_cutoff": val_step_cutoff
        },
        "splits": {
            "train": {
                "records": len(train_raw),
                "fraud_count": int(train_raw["isFraud"].sum()),
                "fraud_rate": float(train_raw["isFraud"].mean()),
                "path": os.path.basename(train_path)
            },
            "validation": {
                "records": len(val_raw),
                "fraud_count": int(val_raw["isFraud"].sum()),
                "fraud_rate": float(val_raw["isFraud"].mean()),
                "path": os.path.basename(val_path)
            },
            "test": {
                "records": len(test_raw),
                "fraud_count": int(test_raw["isFraud"].sum()),
                "fraud_rate": float(test_raw["isFraud"].mean()),
                "path": os.path.basename(test_path)
            }
        },
        "feature_variants": {
            "no_balance_features": PAYSIM_FEATURES_NO_BALANCE,
            "with_balance_features": PAYSIM_FEATURES_WITH_BALANCE
        }
    }

    manifest_path = os.path.join(output_dir, "paysim_split_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Saved train split to: {train_path}")
    print(f"[+] Saved validation split to: {val_path}")
    print(f"[+] Saved test split to: {test_path}")
    print(f"[+] Saved test replay records to: {test_replay_path}")
    print(f"[+] Saved split manifest to: {manifest_path}")
    print("=" * 78)
    return manifest

def main():
    parser = argparse.ArgumentParser(description="Prepare PaySim dataset with strict chronological splitting.")
    parser.add_argument("--csv", default=os.path.join(DEFAULT_DATA_DIR, EXPECTED_CSV_NAME), help="Path to raw PaySim CSV")
    parser.add_argument("--out-dir", default=DEFAULT_DATA_DIR, help="Destination directory for processed splits")
    parser.add_argument("--max-rows", type=int, default=None, help="Optional max row cap for rapid processing")
    args = parser.parse_args()

    prepare_paysim_dataset(csv_path=args.csv, output_dir=args.out_dir, max_rows=args.max_rows)

if __name__ == "__main__":
    main()
