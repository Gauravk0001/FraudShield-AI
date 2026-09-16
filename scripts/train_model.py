import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)
import xgboost as xgb

from generate_forensic_dataset import (
    generate_causal_synthetic_dataset,
    FEATURE_NAMES,
    verify_causality_and_leakage
)

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def train_and_save_production_pipeline(seed: int = 42) -> dict:
    """
    Trains the production XGBoost classifier and Isolation Forest using strictly causal temporal partitioning.
    Uses:
      - 70% historical for training
      - 15% chronological validation for probability calibration (Platt/Sigmoid) & threshold selection
      - 15% held-out chronological final test (untouched during tuning)
    """
    print(f"=== Generating Causal Dataset for Training (Seed: {seed}) ===")
    df = generate_causal_synthetic_dataset(n_customers=600, n_merchants=150, days=45, seed=seed)
    
    # Verify no leakage
    leakage_diag = verify_causality_and_leakage(df)
    if leakage_diag["target_leakage_detected"]:
        raise ValueError(f"Target leakage detected in dataset: {leakage_diag}")

    # Temporal split: 70% Train, 15% Validation/Calibration, 15% Final Test
    n_total = len(df)
    train_end = int(n_total * 0.70)
    val_end = int(n_total * 0.85)

    df_train = df.iloc[:train_end].copy()
    df_val = df.iloc[train_end:val_end].copy()
    df_test = df.iloc[val_end:].copy()

    X_train = df_train[FEATURE_NAMES]
    y_train = df_train["is_fraud"]

    X_val = df_val[FEATURE_NAMES]
    y_val = df_val["is_fraud"]

    X_test = df_test[FEATURE_NAMES]
    y_test = df_test["is_fraud"]

    print(f"Dataset Partitioning (Temporal):")
    print(f"  Train:      {len(X_train)} samples (Fraud: {y_train.sum()} / {y_train.mean():.2%})")
    print(f"  Validation: {len(X_val)} samples (Fraud: {y_val.sum()} / {y_val.mean():.2%})")
    print(f"  Test:       {len(X_test)} samples (Fraud: {y_test.sum()} / {y_test.mean():.2%})")

    # 1. Train Base XGBoost Classifier on Train split
    # Calculate scale_pos_weight for imbalance
    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    scale_pos = float(n_neg / max(1, n_pos))

    base_xgb = xgb.XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.05,
        scale_pos_weight=min(scale_pos, 8.0), # Controlled weighting
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=seed,
        eval_metric="logloss"
    )
    base_xgb.fit(X_train, y_train)

    # 2. Probability Calibration on Validation split (Platt Sigmoid Scaling)
    # Calibrate base model on validation split
    calibrated_clf = CalibratedClassifierCV(estimator=base_xgb, method='sigmoid', cv='prefit')
    calibrated_clf.fit(X_val, y_val)

    # 3. Validation Evaluation & Threshold Selection
    val_raw_prob = base_xgb.predict_proba(X_val)[:, 1]
    val_cal_prob = calibrated_clf.predict_proba(X_val)[:, 1]

    brier_uncal = float(brier_score_loss(y_val, val_raw_prob))
    brier_cal = float(brier_score_loss(y_val, val_cal_prob))
    print(f"\nCalibration Results (Validation Set):")
    print(f"  Brier Score (Uncalibrated): {brier_uncal:.4f}")
    print(f"  Brier Score (Calibrated):   {brier_cal:.4f}")

    # Threshold optimization on Validation split
    best_f1 = 0.0
    best_thresh = 0.50
    thresh_table = []
    for th in np.arange(0.05, 0.96, 0.05):
        th = round(float(th), 2)
        preds = (val_cal_prob >= th).astype(int)
        p = float(precision_score(y_val, preds, zero_division=0))
        r = float(recall_score(y_val, preds, zero_division=0))
        f = float(f1_score(y_val, preds, zero_division=0))
        thresh_table.append({"threshold": th, "precision": p, "recall": r, "f1": f})
        if f > best_f1:
            best_f1 = f
            best_thresh = th

    print(f"  Optimal Operating Threshold (from Validation F1): {best_thresh:.2f} (F1: {best_f1:.4f})")

    # 4. Final Untouched Evaluation on Chronological Test Set
    test_cal_prob = calibrated_clf.predict_proba(X_test)[:, 1]
    test_preds = (test_cal_prob >= best_thresh).astype(int)

    test_prec = float(precision_score(y_test, test_preds, zero_division=0))
    test_rec = float(recall_score(y_test, test_preds, zero_division=0))
    test_f1 = float(f1_score(y_test, test_preds, zero_division=0))
    test_roc_auc = float(roc_auc_score(y_test, test_cal_prob))
    test_pr_auc = float(average_precision_score(y_test, test_cal_prob))
    test_brier = float(brier_score_loss(y_test, test_cal_prob))

    # Confusion matrix
    from sklearn.metrics import confusion_matrix
    tn, fp, fn, tp = confusion_matrix(y_test, test_preds).ravel()
    test_fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    print(f"\nFinal Untouched Temporal Test Set Metrics:")
    print(f"  Precision: {test_prec:.4f}")
    print(f"  Recall:    {test_rec:.4f}")
    print(f"  F1-Score:  {test_f1:.4f}")
    print(f"  PR-AUC:    {test_pr_auc:.4f}")
    print(f"  ROC-AUC:   {test_roc_auc:.4f}")
    print(f"  FPR:       {test_fpr:.4%}")
    print(f"  Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

    # 5. Isolation Forest Anomaly Detector
    iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=seed)
    iso.fit(X_train[y_train == 0])

    # Save artifacts
    clf_path = os.path.join(ARTIFACTS_DIR, "fraud_classifier.joblib")
    iso_path = os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib")
    base_xgb_path = os.path.join(ARTIFACTS_DIR, "base_xgboost.joblib")
    meta_path = os.path.join(ARTIFACTS_DIR, "model_metadata.json")

    # Save calibrated classifier as production model
    joblib.dump(calibrated_clf, clf_path)
    joblib.dump(base_xgb, base_xgb_path)
    joblib.dump(iso, iso_path)

    # Sync to backend/models_artifacts if directory exists
    backend_artifacts = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "models_artifacts")
    if os.path.exists(backend_artifacts):
        joblib.dump(calibrated_clf, os.path.join(backend_artifacts, "fraud_classifier.joblib"))
        joblib.dump(base_xgb, os.path.join(backend_artifacts, "base_xgboost.joblib"))
        joblib.dump(iso, os.path.join(backend_artifacts, "isolation_forest.joblib"))

    metadata = {
        "version": "v2.0.0-forensic",
        "model_type": "Calibrated XGBoost Classifier (Platt Sigmoid)",
        "base_model": "XGBoost Classifier",
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "random_seed": seed,
        "operating_threshold": best_thresh,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "temporal_split": {
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            "fraud_prevalence_pct": round(float(df["is_fraud"].mean() * 100), 2)
        },
        "calibration": {
            "method": "sigmoid",
            "val_brier_uncalibrated": brier_uncal,
            "val_brier_calibrated": brier_cal
        },
        "metrics_on_untouched_temporal_test": {
            "precision": test_prec,
            "recall": test_rec,
            "f1_score": test_f1,
            "pr_auc": test_pr_auc,
            "roc_auc": test_roc_auc,
            "fpr": test_fpr,
            "brier_score": test_brier,
            "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}
        }
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    if os.path.exists(backend_artifacts):
        with open(os.path.join(backend_artifacts, "model_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    print(f"\n[OK] Production artifacts and metadata saved to {ARTIFACTS_DIR}")
    return metadata

if __name__ == "__main__":
    train_and_save_production_pipeline(seed=42)
