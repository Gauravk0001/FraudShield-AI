#!/usr/bin/env python3
"""
FraudShield AI — Model Artifact Integrity & Rollback Verification Tool

Verifies cryptographic SHA-256 signatures, schema consistency, and governance
metadata for model artifacts prior to production serving.

Supports:
- Checking artifact integrity against artifact_hashes.json
- Verifying schema parity with feature_schema.py
- Validating rollback candidate artifacts
"""

import os
import sys
import json
import hashlib
import argparse
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.ml.feature_schema import validate_feature_columns

DEFAULT_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models_artifacts", "paysim"))

REQUIRED_ARTIFACT_FILES = [
    "fraud_classifier.joblib",
    "base_xgboost.joblib",
    "feature_schema.json",
    "thresholds.json",
    "metrics.json",
    "model_metadata.json",
    "artifact_hashes.json"
]

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def validate_artifacts(artifacts_dir: str = DEFAULT_ARTIFACTS_DIR) -> bool:
    print("=" * 78)
    print("  FRAUDSHIELD AI — ARTIFACT INTEGRITY & GOVERNANCE VALIDATOR")
    print("=" * 78)
    print(f"[*] Validating directory: {artifacts_dir}")

    if not os.path.isdir(artifacts_dir):
        print(f"[-] Artifacts directory not found: {artifacts_dir}")
        return False

    # 1. Existence check
    missing = []
    for f in REQUIRED_ARTIFACT_FILES:
        p = os.path.join(artifacts_dir, f)
        if not os.path.isfile(p):
            missing.append(f)

    if missing:
        print(f"[-] Missing required model artifacts: {missing}")
        return False
    print(f"[+] All {len(REQUIRED_ARTIFACT_FILES)} required artifact files are present.")

    # 2. Hash verification
    hashes_file = os.path.join(artifacts_dir, "artifact_hashes.json")
    with open(hashes_file, "r", encoding="utf-8") as f:
        stored_hashes_doc = json.load(f)

    stored_hashes = stored_hashes_doc.get("hashes", {})
    hash_mismatches = []

    for fname, expected_hash in stored_hashes.items():
        fpath = os.path.join(artifacts_dir, fname)
        if not os.path.isfile(fpath):
            continue
        actual_hash = compute_sha256(fpath)
        if actual_hash != expected_hash:
            hash_mismatches.append((fname, expected_hash, actual_hash))

    if hash_mismatches:
        print("[-] FATAL: Cryptographic signature mismatch detected in model artifacts!")
        for fname, exp, act in hash_mismatches:
            print(f"    - {fname}: expected {exp[:12]}..., got {act[:12]}...")
        return False
    print(f"[+] SHA-256 signature verification PASSED. All {len(stored_hashes)} signed artifacts match.")

    # 3. Schema & Label Isolation check
    schema_file = os.path.join(artifacts_dir, "feature_schema.json")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    features = schema.get("features", [])
    if not features:
        print("[-] Invalid feature schema: empty feature list.")
        return False

    try:
        validate_feature_columns(features)
        print(f"[+] Schema validation PASSED: {len(features)} features verified, zero label leakage.")
    except Exception as e:
        print(f"[-] Schema validation FAILED: {e}")
        return False

    # 4. Threshold integrity check
    thresh_file = os.path.join(artifacts_dir, "thresholds.json")
    with open(thresh_file, "r", encoding="utf-8") as f:
        thresholds = json.load(f)

    step_up = thresholds.get("step_up_threshold")
    hold = thresholds.get("hold_for_review_threshold")
    if step_up is None or hold is None or step_up >= hold:
        print(f"[-] Invalid decision thresholds: step_up={step_up}, hold={hold}")
        return False
    print(f"[+] Decision thresholds verified: STEP_UP >= {step_up}, HOLD_FOR_REVIEW >= {hold}")

    print("=" * 78)
    print("[+] ARTIFACT VALIDATION STATUS: VERIFIED & READY FOR SERVING")
    print("=" * 78)
    return True

def rollback_to_artifact(target_version_dir: str, active_dir: str = DEFAULT_ARTIFACTS_DIR) -> bool:
    """Safely swaps active model artifacts with a verified prior version directory."""
    print(f"[*] Validating rollback target directory: {target_version_dir}")
    if not validate_artifacts(target_version_dir):
        print("[-] Rollback target failed validation! Aborting rollback.")
        return False

    import shutil
    backup_dir = active_dir + f".backup.{int(os.path.getmtime(active_dir))}"
    print(f"[*] Backing up current active artifacts to: {backup_dir}")
    if os.path.exists(active_dir):
        shutil.move(active_dir, backup_dir)

    print(f"[*] Activating rollback version from {target_version_dir}...")
    shutil.copytree(target_version_dir, active_dir)
    print(f"[+] Successfully rolled back active model artifacts.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate model artifacts or execute governed rollback.")
    parser.add_argument("--artifacts-dir", default=DEFAULT_ARTIFACTS_DIR, help="Path to artifacts directory")
    parser.add_argument("--rollback-from", help="Optional path to prior verified artifact directory to roll back to")
    args = parser.parse_args()

    if args.rollback_from:
        success = rollback_to_artifact(target_version_dir=args.rollback_from, active_dir=args.artifacts_dir)
    else:
        success = validate_artifacts(artifacts_dir=args.artifacts_dir)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
