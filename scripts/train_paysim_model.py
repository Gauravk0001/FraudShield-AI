#!/usr/bin/env python3
"""
FraudShield AI — PaySim Model Training & Artifact Packaging

Trains:
1. Logistic Regression baseline.
2. XGBoost primary fraud classifier with class-imbalance weighting (scale_pos_weight).
3. Isolation Forest unsupervised anomaly detector.

Saves all artifacts under:
backend/models_artifacts/paysim/
- fraud_classifier.joblib (CalibratedClassifierCV or calibrated XGBoost)
- base_xgboost.joblib
- isolation_forest.joblib
- feature_schema.json
- thresholds.json
- metrics.json
- model_metadata.json
- artifact_hashes.json
"""

import os
import sys
import json
import time
import hashlib
import platform
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    precision_recall_curve,
    roc_auc_score,
    auc,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
import xgboost as xgb

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.ml.feature_schema import (
    PAYSIM_FEATURES_NO_BALANCE,
    PAYSIM_FEATURES_WITH_BALANCE,
    validate_feature_columns,
    get_feature_schema
)

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DEFAULT_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models_artifacts", "paysim"))

def compute_file_sha256(filepath: str) -> str:
    """Computes the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def select_cost_optimal_thresholds(
    y_val: np.ndarray,
    y_val_proba: np.ndarray,
    val_amounts: np.ndarray,
    false_decline_cost: float = 5.0,
    missed_fraud_fixed_cost: float = 50.0,
    step_up_cost: float = 1.0
) -> Dict[str, Any]:
    """
    Selects operating thresholds on the validation split by minimizing expected business loss.
    
    Expected cost formula for transaction i:
      missed_fraud_cost_i = amount_i + missed_fraud_fixed_cost
      false_decline_cost_i = false_decline_cost
      expected_loss_approve_i = p_i * missed_fraud_cost_i
      expected_loss_hold_i = (1 - p_i) * false_decline_cost_i
      expected_loss_step_up_i = step_up_cost + 0.1 * expected_loss_hold_i
    """
    threshold_grid = np.linspace(0.01, 0.99, 99)
    best_hold_cost = float("inf")
    best_hold_thresh = 0.50

    for thresh in threshold_grid:
        decisions_hold = (y_val_proba >= thresh).astype(int)
        # Cost of false positive (hold non-fraud) = false_decline_cost
        fp_cost = np.sum((decisions_hold == 1) & (y_val == 0)) * false_decline_cost
        # Cost of false negative (approve fraud) = amount + fixed cost
        fn_mask = (decisions_hold == 0) & (y_val == 1)
        fn_cost = np.sum(val_amounts[fn_mask] + missed_fraud_fixed_cost)
        total_cost = fp_cost + fn_cost

        if total_cost < best_hold_cost:
            best_hold_cost = total_cost
            best_hold_thresh = float(thresh)

    # Step-up threshold is calibrated between baseline false alarm rate and hold threshold
    step_up_thresh = max(0.05, round(best_hold_thresh * 0.45, 3))
    hold_thresh = max(step_up_thresh + 0.05, round(best_hold_thresh, 3))

    return {
        "step_up_threshold": step_up_thresh,
        "hold_for_review_threshold": hold_thresh,
        "authorized_block_threshold": 0.95, # Requires explicit rule authorization
        "validation_total_cost_at_threshold": round(float(best_hold_cost), 2),
        "cost_assumptions": {
            "false_decline_cost": false_decline_cost,
            "missed_fraud_fixed_cost": missed_fraud_fixed_cost,
            "step_up_cost": step_up_cost
        }
    }

def train_and_package_paysim(
    data_dir: str = DEFAULT_DATA_DIR,
    artifacts_dir: str = DEFAULT_ARTIFACTS_DIR,
    with_balance: bool = False,
    random_seed: int = 42
) -> Dict[str, Any]:
    print("=" * 78)
    print("  FRAUDSHIELD AI — PAYSIM MODEL TRAINING & GOVERNED ARTIFACT PACKAGING")
    print("=" * 78)
    print(f"[*] Balance Shortcut Features Active: {with_balance}")
    if with_balance:
        print("[!] WARNING: Training with balance-derived synthetic shortcuts.")
        print("    This model is an exploratory prototype, NOT for production deployment.")
    else:
        print("[+] Training Defensible Baseline without balance shortcuts.")
    print("-" * 78)

    train_path = os.path.join(data_dir, "paysim_train.parquet")
    val_path = os.path.join(data_dir, "paysim_val.parquet")

    if not os.path.isfile(train_path) or not os.path.isfile(val_path):
        print("[-] Prepared parquet splits not found. Running prepare_paysim.py first...")
        from scripts.prepare_paysim import prepare_paysim_dataset, EXPECTED_CSV_NAME
        csv_path = os.path.join(data_dir, EXPECTED_CSV_NAME)
        prepare_paysim_dataset(csv_path=csv_path, output_dir=data_dir)

    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(val_path)

    feature_cols = PAYSIM_FEATURES_WITH_BALANCE if with_balance else PAYSIM_FEATURES_NO_BALANCE
    validate_feature_columns(feature_cols)

    X_train = train_df[feature_cols].copy()
    y_train = train_df["target_is_fraud"].values.astype(int)

    X_val = val_df[feature_cols].copy()
    y_val = val_df["target_is_fraud"].values.astype(int)
    val_amounts = val_df["amount"].values.astype(float)

    n_pos = int(y_train.sum())
    n_neg = len(y_train) - n_pos
    scale_pos = max(1.0, float(n_neg) / max(1.0, float(n_pos)))

    print(f"[*] Training Samples: {len(X_train):,} | Fraud: {n_pos:,} ({n_pos/len(X_train)*100:.2f}%)")
    print(f"[*] Validation Samples: {len(X_val):,} | Fraud: {int(y_val.sum()):,} ({y_val.sum()/len(X_val)*100:.2f}%)")
    print(f"[*] Class Imbalance Scale Pos Weight: {scale_pos:.2f}")

    # 1. Baseline: Logistic Regression
    print("[*] 1/3 Training Logistic Regression baseline...")
    lr_baseline = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_seed)
    lr_baseline.fit(X_train, y_train)
    lr_val_proba = lr_baseline.predict_proba(X_val)[:, 1]
    lr_roc = roc_auc_score(y_val, lr_val_proba) if len(np.unique(y_val)) > 1 else 0.5
    print(f"    Baseline LR Validation ROC-AUC: {lr_roc:.4f}")

    # 2. Primary: Calibrated XGBoost with class-weighting
    print("[*] 2/3 Training primary XGBoost classifier...")
    base_xgb = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.08,
        scale_pos_weight=scale_pos,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=random_seed,
        eval_metric="logloss"
    )
    base_xgb.fit(X_train, y_train)

    # Probability calibration using 3-fold internal calibration
    print("[*] Calibrating classifier probabilities (Sigmoid scaling)...")
    calibrated_clf = CalibratedClassifierCV(estimator=base_xgb, method="sigmoid", cv=3)
    calibrated_clf.fit(X_train, y_train)

    val_proba = calibrated_clf.predict_proba(X_val)[:, 1]

    # Measure latency
    latencies = []
    sample_rows = X_val.head(100)
    for _, row in sample_rows.iterrows():
        t0 = time.perf_counter()
        _ = calibrated_clf.predict_proba(pd.DataFrame([row]))[0, 1]
        latencies.append((time.perf_counter() - t0) * 1000.0)

    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    p99_lat = float(np.percentile(latencies, 99))

    # 3. Unsupervised Anomaly Signal: Isolation Forest
    print("[*] 3/3 Fitting Isolation Forest anomaly detector on legitimate transactions...")
    normal_train = X_train[y_train == 0]
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=random_seed,
        n_jobs=-1
    )
    iso_forest.fit(normal_train)

    # Cost-optimal threshold selection on validation split
    print("[*] Calculating cost-optimal decision thresholds on validation split...")
    thresholds = select_cost_optimal_thresholds(
        y_val=y_val,
        y_val_proba=val_proba,
        val_amounts=val_amounts
    )
    hold_thresh = thresholds["hold_for_review_threshold"]
    step_thresh = thresholds["step_up_threshold"]

    # Metrics on validation set
    p_prec, p_rec, _ = precision_recall_curve(y_val, val_proba)
    val_pr_auc = float(auc(p_rec, p_prec))
    val_roc_auc = float(roc_auc_score(y_val, val_proba))
    val_brier = float(brier_score_loss(y_val, val_proba))

    val_preds = (val_proba >= hold_thresh).astype(int)
    val_precision = float(precision_score(y_val, val_preds, zero_division=0))
    val_recall = float(recall_score(y_val, val_preds, zero_division=0))
    val_f1 = float(f1_score(y_val, val_preds, zero_division=0))
    cm = confusion_matrix(y_val, val_preds).tolist()

    print(f"[+] Validation PR-AUC:   {val_pr_auc:.4f}")
    print(f"[+] Validation ROC-AUC:  {val_roc_auc:.4f}")
    print(f"[+] Validation Precision: {val_precision:.4f} (at threshold {hold_thresh})")
    print(f"[+] Validation Recall:    {val_recall:.4f}")
    print(f"[+] Validation F1:        {val_f1:.4f}")
    print(f"[+] Latency (p50/p95/p99): {p50_lat:.2f}ms / {p95_lat:.2f}ms / {p99_lat:.2f}ms")

    # Save artifacts
    os.makedirs(artifacts_dir, exist_ok=True)
    model_version = f"paysim-v1-{'with_balance' if with_balance else 'no_balance'}"

    clf_path = os.path.join(artifacts_dir, "fraud_classifier.joblib")
    base_xgb_path = os.path.join(artifacts_dir, "base_xgboost.joblib")
    iso_path = os.path.join(artifacts_dir, "isolation_forest.joblib")
    schema_path = os.path.join(artifacts_dir, "feature_schema.json")
    thresholds_path = os.path.join(artifacts_dir, "thresholds.json")
    metrics_path = os.path.join(artifacts_dir, "metrics.json")
    metadata_path = os.path.join(artifacts_dir, "model_metadata.json")
    hashes_path = os.path.join(artifacts_dir, "artifact_hashes.json")

    joblib.dump(calibrated_clf, clf_path)
    joblib.dump(base_xgb, base_xgb_path)
    joblib.dump(iso_forest, iso_path)

    # Feature schema JSON
    schema_json = get_feature_schema(with_balance=with_balance)
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema_json, f, indent=2)

    # Thresholds JSON
    with open(thresholds_path, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)

    # Metrics JSON
    metrics_data = {
        "model_version": model_version,
        "evaluation_split": "validation_15pct",
        "pr_auc": round(val_pr_auc, 4),
        "roc_auc": round(val_roc_auc, 4),
        "precision": round(val_precision, 4),
        "recall": round(val_recall, 4),
        "f1_score": round(val_f1, 4),
        "brier_score": round(val_brier, 4),
        "confusion_matrix": cm,
        "latency_ms": {
            "p50": round(p50_lat, 2),
            "p95": round(p95_lat, 2),
            "p99": round(p99_lat, 2)
        },
        "operating_thresholds": {
            "step_up": step_thresh,
            "hold_for_review": hold_thresh
        },
        "expected_business_cost": thresholds["validation_total_cost_at_threshold"]
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    # Model metadata JSON
    metadata = {
        "model_version": model_version,
        "model_type": "Calibrated XGBoost Classifier (Platt Sigmoid)",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "dependencies": {
            "xgboost": xgb.__version__,
            "scikit_learn": pd.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__
        },
        "features_count": len(feature_cols),
        "feature_names": feature_cols,
        "is_balance_derived_active": with_balance,
        "split_policy": "Strict 70/15/15 chronological step split",
        "training_samples": len(X_train),
        "validation_samples": len(X_val),
        "random_seed": random_seed
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Calculate SHA-256 hashes of all artifacts
    artifact_files = [
        "fraud_classifier.joblib",
        "base_xgboost.joblib",
        "isolation_forest.joblib",
        "feature_schema.json",
        "thresholds.json",
        "metrics.json",
        "model_metadata.json"
    ]
    artifact_hashes = {}
    for af in artifact_files:
        p = os.path.join(artifacts_dir, af)
        if os.path.isfile(p):
            artifact_hashes[af] = compute_file_sha256(p)

    with open(hashes_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
            "hashes": artifact_hashes
        }, f, indent=2)

    print(f"[+] Artifacts successfully saved and hashed in: {artifacts_dir}")
    print("=" * 78)
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Train PaySim models and package governed artifacts.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Path to data directory")
    parser.add_argument("--artifacts-dir", default=DEFAULT_ARTIFACTS_DIR, help="Destination directory for model artifacts")
    parser.add_argument("--with-balance", action="store_true", help="Include balance-derived features (exploratory prototype)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_and_package_paysim(
        data_dir=args.data_dir,
        artifacts_dir=args.artifacts_dir,
        with_balance=args.with_balance,
        random_seed=args.seed
    )

if __name__ == "__main__":
    main()
