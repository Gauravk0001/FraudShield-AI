#!/usr/bin/env python3
"""
FraudShield AI — Comprehensive Model Evaluation & Visual Reporting

Evaluates trained PaySim models on the locked final test split (15%)
and generates authoritative visual evaluation charts:
- reports/paysim/pr_curve.png
- reports/paysim/roc_curve.png
- reports/paysim/confusion_matrix.png
- reports/paysim/feature_importance.png
- reports/paysim/shap_summary.png
- reports/paysim/calibration_curve.png
- reports/paysim/metrics.json

CRITICAL POLICY:
- Evaluates on the locked final test set without data leakage.
- Reports real metrics derived from actual test execution. Zero fabrication.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_recall_curve,
    roc_curve,
    auc,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.ml.feature_schema import validate_feature_columns

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DEFAULT_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models_artifacts", "paysim"))
DEFAULT_REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports", "paysim"))

def compute_recall_at_fpr(y_true: np.ndarray, y_proba: np.ndarray, target_fpr: float) -> float:
    """Computes empirical recall at a fixed false positive rate (FPR)."""
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    # Find max TPR where FPR <= target_fpr
    valid_indices = np.where(fpr <= target_fpr)[0]
    if len(valid_indices) == 0:
        return 0.0
    return float(np.max(tpr[valid_indices]))

def evaluate_and_generate_reports(
    data_dir: str = DEFAULT_DATA_DIR,
    artifacts_dir: str = DEFAULT_ARTIFACTS_DIR,
    reports_dir: str = DEFAULT_REPORTS_DIR,
    split_name: str = "test"
) -> Dict[str, Any]:
    print("=" * 78)
    print(f"  FRAUDSHIELD AI — PAYSIM EVALUATION ON LOCKED {split_name.upper()} SPLIT")
    print("=" * 78)

    os.makedirs(reports_dir, exist_ok=True)

    # 1. Load Model & Artifacts
    clf_path = os.path.join(artifacts_dir, "fraud_classifier.joblib")
    base_xgb_path = os.path.join(artifacts_dir, "base_xgboost.joblib")
    schema_path = os.path.join(artifacts_dir, "feature_schema.json")
    thresholds_path = os.path.join(artifacts_dir, "thresholds.json")

    if not os.path.isfile(clf_path) or not os.path.isfile(schema_path):
        raise FileNotFoundError(f"Model artifacts not found in {artifacts_dir}. Please run train_paysim_model.py first.")

    model = joblib.load(clf_path)
    base_xgb = joblib.load(base_xgb_path) if os.path.isfile(base_xgb_path) else None

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    feature_cols = schema["features"]
    validate_feature_columns(feature_cols)

    thresholds = {}
    if os.path.isfile(thresholds_path):
        with open(thresholds_path, "r", encoding="utf-8") as f:
            thresholds = json.load(f)
    hold_thresh = thresholds.get("hold_for_review_threshold", 0.50)
    step_thresh = thresholds.get("step_up_threshold", 0.20)

    # 2. Load Evaluation Data Split
    test_parquet = os.path.join(data_dir, f"paysim_{split_name}.parquet")
    if not os.path.isfile(test_parquet):
        raise FileNotFoundError(f"Split file '{test_parquet}' not found. Please run prepare_paysim.py first.")

    df_test = pd.read_parquet(test_parquet)
    X_test = df_test[feature_cols].copy()
    y_test = df_test["target_is_fraud"].values.astype(int)
    test_amounts = df_test["amount"].values.astype(float) if "amount" in df_test.columns else np.ones(len(y_test))

    print(f"[*] Evaluated Samples: {len(X_test):,} | Fraud Cases: {int(y_test.sum()):,} ({y_test.mean()*100:.2f}%)")

    # 3. Model Inference & Latency
    print("[*] Running inference across evaluation split...")
    t0 = time.perf_counter()
    y_proba = model.predict_proba(X_test)[:, 1]
    total_time_ms = (time.perf_counter() - t0) * 1000.0

    # Individual latency benchmark
    latencies = []
    bench_sample = X_test.head(100)
    for _, row in bench_sample.iterrows():
        t_row = time.perf_counter()
        _ = model.predict_proba(pd.DataFrame([row]))[0, 1]
        latencies.append((time.perf_counter() - t_row) * 1000.0)

    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    p99_lat = float(np.percentile(latencies, 99))

    # 4. Comprehensive Metrics Computation
    precisions, recalls, _ = precision_recall_curve(y_test, y_proba)
    pr_auc_val = float(auc(recalls, precisions))
    roc_auc_val = float(roc_auc_score(y_test, y_proba))
    brier_val = float(brier_score_loss(y_test, y_proba))

    recall_at_1pct_fpr = compute_recall_at_fpr(y_test, y_proba, target_fpr=0.01)
    recall_at_01pct_fpr = compute_recall_at_fpr(y_test, y_proba, target_fpr=0.001)

    y_pred = (y_proba >= hold_thresh).astype(int)
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Cost computation
    false_decline_cost = thresholds.get("cost_assumptions", {}).get("false_decline_cost", 5.0)
    missed_fraud_fixed = thresholds.get("cost_assumptions", {}).get("missed_fraud_fixed_cost", 50.0)
    fp_cost = np.sum((y_pred == 1) & (y_test == 0)) * false_decline_cost
    fn_cost = np.sum(test_amounts[(y_pred == 0) & (y_test == 1)] + missed_fraud_fixed)
    total_cost = float(fp_cost + fn_cost)

    print(f"[+] PR-AUC:               {pr_auc_val:.4f}")
    print(f"[+] ROC-AUC:              {roc_auc_val:.4f}")
    print(f"[+] Precision:            {prec:.4f} (at threshold {hold_thresh})")
    print(f"[+] Recall:               {rec:.4f}")
    print(f"[+] F1-Score:             {f1:.4f}")
    print(f"[+] Recall @ 1.0% FPR:    {recall_at_1pct_fpr:.4f}")
    print(f"[+] Recall @ 0.1% FPR:    {recall_at_01pct_fpr:.4f}")
    print(f"[+] Brier Score:          {brier_val:.4f}")
    print(f"[+] Latency (p50/p95/p99): {p50_lat:.2f}ms / {p95_lat:.2f}ms / {p99_lat:.2f}ms")
    print(f"[+] Expected Cost:        ${total_cost:,.2f}")

    # 5. Visual Reports Generation
    print("[*] Generating visual evaluation reports...")

    # A. PR Curve
    plt.figure(figsize=(7, 5))
    plt.plot(recalls, precisions, color="#2563eb", lw=2, label=f"Calibrated XGBoost (PR-AUC = {pr_auc_val:.4f})")
    plt.axhline(y=y_test.mean(), color="#94a3b8", linestyle="--", label=f"No-Skill Baseline ({y_test.mean()*100:.2f}%)")
    plt.xlabel("Recall", fontsize=11)
    plt.ylabel("Precision", fontsize=11)
    plt.title(f"Precision-Recall Curve (PaySim {split_name.title()} Split)", fontsize=12, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower left")
    pr_path = os.path.join(reports_dir, "pr_curve.png")
    plt.tight_layout()
    plt.savefig(pr_path, dpi=200)
    plt.close()

    # B. ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color="#059669", lw=2, label=f"Calibrated XGBoost (ROC-AUC = {roc_auc_val:.4f})")
    plt.plot([0, 1], [0, 1], color="#94a3b8", linestyle="--", label="Random Chance (0.50)")
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate (Recall)", fontsize=11)
    plt.title(f"Receiver Operating Characteristic (PaySim {split_name.title()} Split)", fontsize=12, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower right")
    roc_path = os.path.join(reports_dir, "roc_curve.png")
    plt.tight_layout()
    plt.savefig(roc_path, dpi=200)
    plt.close()

    # C. Confusion Matrix Heatmap
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix (Threshold = {hold_thresh})", fontsize=12, fontweight="bold")
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ["Legitimate", "Fraud"])
    plt.yticks(tick_marks, ["Legitimate", "Fraud"])
    for i in range(2):
        for j in range(2):
            val = cm[i][j]
            color = "white" if val > (np.max(cm) / 2) else "black"
            plt.text(j, i, f"{val:,}", horizontalalignment="center", verticalalignment="center", color=color, fontweight="bold")
    plt.ylabel("True Label", fontsize=11)
    plt.xlabel("Predicted Recommendation", fontsize=11)
    cm_path = os.path.join(reports_dir, "confusion_matrix.png")
    plt.tight_layout()
    plt.savefig(cm_path, dpi=200)
    plt.close()

    # D. Feature Importance (from base XGBoost booster)
    if base_xgb is not None and hasattr(base_xgb, "feature_importances_"):
        plt.figure(figsize=(8, 6))
        importances = base_xgb.feature_importances_
        idx = np.argsort(importances)[::-1][:15]
        plt.barh(range(len(idx)), importances[idx][::-1], color="#4f46e5")
        plt.yticks(range(len(idx)), [feature_cols[i] for i in idx][::-1], fontsize=9)
        plt.xlabel("Feature Importance (Gini Gain)", fontsize=11)
        plt.title("Top Feature Importances (XGBoost)", fontsize=12, fontweight="bold")
        plt.grid(True, axis="x", alpha=0.3)
        fi_path = os.path.join(reports_dir, "feature_importance.png")
        plt.tight_layout()
        plt.savefig(fi_path, dpi=200)
        plt.close()

    # E. Calibration Curve
    prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10, strategy="uniform")
    plt.figure(figsize=(7, 5))
    plt.plot(prob_pred, prob_true, marker="o", color="#d97706", lw=2, label="Calibrated Model")
    plt.plot([0, 1], [0, 1], color="#94a3b8", linestyle="--", label="Perfectly Calibrated")
    plt.xlabel("Mean Predicted Probability", fontsize=11)
    plt.ylabel("Observed Fraction of Positives", fontsize=11)
    plt.title(f"Reliability Calibration Curve (Brier: {brier_val:.4f})", fontsize=12, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper left")
    cal_path = os.path.join(reports_dir, "calibration_curve.png")
    plt.tight_layout()
    plt.savefig(cal_path, dpi=200)
    plt.close()

    # F. SHAP Summary Plot
    try:
        import shap
        print("[*] Generating SHAP summary plot...")
        # Use TreeExplainer on small sample (200 rows)
        explainer = shap.TreeExplainer(base_xgb)
        sample_shap_X = X_test.head(150)
        shap_values = explainer.shap_values(sample_shap_X)
        plt.figure(figsize=(9, 6))
        shap.summary_plot(shap_values, sample_shap_X, show=False, max_display=12)
        shap_path = os.path.join(reports_dir, "shap_summary.png")
        plt.tight_layout()
        plt.savefig(shap_path, dpi=200, bbox_inches="tight")
        plt.close()
    except Exception as e:
        print(f"[-] SHAP summary generation skipped: {e}")

    # 6. Save authoritative metrics JSON
    metrics_summary = {
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "split_evaluated": split_name,
        "sample_count": len(X_test),
        "fraud_prevalence_pct": round(float(y_test.mean() * 100), 2),
        "is_synthetic_dataset": True,
        "metrics": {
            "pr_auc": round(pr_auc_val, 4),
            "roc_auc": round(roc_auc_val, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "recall_at_1pct_fpr": round(recall_at_1pct_fpr, 4),
            "recall_at_01pct_fpr": round(recall_at_01pct_fpr, 4),
            "brier_score": round(brier_val, 4)
        },
        "operating_thresholds": {
            "step_up": step_thresh,
            "hold_for_review": hold_thresh
        },
        "confusion_matrix": cm,
        "latency_ms": {
            "p50": round(p50_lat, 2),
            "p95": round(p95_lat, 2),
            "p99": round(p99_lat, 2)
        },
        "business_cost_usd": round(total_cost, 2),
        "visual_reports": [
            "reports/paysim/pr_curve.png",
            "reports/paysim/roc_curve.png",
            "reports/paysim/confusion_matrix.png",
            "reports/paysim/feature_importance.png",
            "reports/paysim/calibration_curve.png",
            "reports/paysim/shap_summary.png"
        ]
    }

    metrics_out = os.path.join(reports_dir, "metrics.json")
    with open(metrics_out, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    print(f"[+] Evaluation reports and metrics saved to: {reports_dir}")
    print("=" * 78)
    return metrics_summary

def main():
    parser = argparse.ArgumentParser(description="Evaluate PaySim model and generate visual reports.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Path to data directory")
    parser.add_argument("--artifacts-dir", default=DEFAULT_ARTIFACTS_DIR, help="Path to artifacts directory")
    parser.add_argument("--reports-dir", default=DEFAULT_REPORTS_DIR, help="Destination directory for reports")
    parser.add_argument("--split", default="test", choices=["test", "val"], help="Split to evaluate ('test' or 'val')")
    args = parser.parse_args()

    evaluate_and_generate_reports(
        data_dir=args.data_dir,
        artifacts_dir=args.artifacts_dir,
        reports_dir=args.reports_dir,
        split_name=args.split
    )

if __name__ == "__main__":
    main()
