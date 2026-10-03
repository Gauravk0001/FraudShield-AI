"""
FraudShield AI — Production Feature & Prediction Drift Monitor
Calculates Population Stability Index (PSI), Kolmogorov-Smirnov (KS) statistics,
prediction distribution drift, and class-rate drift without automated retraining.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from app.core.logging import logger
from app.ml.feature_engineering import FEATURE_NAMES

# Standard Production PSI Thresholds
PSI_THRESHOLD_LOW = 0.10
PSI_THRESHOLD_MODERATE = 0.25

class DriftMonitor:
    """
    Production-grade distribution and prediction drift monitor for tabular fraud models.
    """
    def __init__(self, baseline_df: Optional[pd.DataFrame] = None, baseline_preds: Optional[np.ndarray] = None):
        self.baseline_df = baseline_df
        self.baseline_preds = baseline_preds
        self.feature_names = FEATURE_NAMES

    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray, num_bins: int = 10, epsilon: float = 1e-4) -> float:
        """
        Calculate the Population Stability Index (PSI) between baseline (expected) and current (actual).
        PSI = sum((Actual_i - Expected_i) * ln(Actual_i / Expected_i))
        """
        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        # Create quantile bins based on the expected (baseline) distribution
        quantiles = np.linspace(0, 100, num_bins + 1)
        bin_edges = np.percentile(expected, quantiles)
        bin_edges = np.unique(bin_edges)  # remove duplicate edges for discrete features

        if len(bin_edges) <= 1:
            # Constant or zero variance feature
            return 0.0

        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf

        expected_counts, _ = np.histogram(expected, bins=bin_edges)
        actual_counts, _ = np.histogram(actual, bins=bin_edges)

        expected_pct = expected_counts / len(expected)
        actual_pct = actual_counts / len(actual)

        # Apply epsilon smoothing to prevent div by 0 and log(0)
        expected_pct = np.clip(expected_pct, epsilon, None)
        actual_pct = np.clip(actual_pct, epsilon, None)

        # Normalize after clip
        expected_pct = expected_pct / np.sum(expected_pct)
        actual_pct = actual_pct / np.sum(actual_pct)

        psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(np.maximum(0.0, psi_val))

    def calculate_ks_statistic(self, baseline: np.ndarray, current: np.ndarray) -> Tuple[float, float]:
        """
        Calculates two-sample Kolmogorov-Smirnov statistic D and p-value.
        """
        if len(baseline) == 0 or len(current) == 0:
            return 0.0, 1.0
        res = stats.ks_2samp(baseline, current)
        return float(res.statistic), float(res.pvalue)

    def evaluate_feature_drift(self, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates drift for every individual feature in FEATURE_NAMES against baseline.
        """
        if self.baseline_df is None:
            raise ValueError("Baseline dataset is not set on DriftMonitor.")

        feature_reports = {}
        high_drift_features = []
        mod_drift_features = []

        for feat in self.feature_names:
            if feat not in self.baseline_df.columns or feat not in current_df.columns:
                continue

            base_vals = self.baseline_df[feat].dropna().values.astype(float)
            curr_vals = current_df[feat].dropna().values.astype(float)

            psi = self.calculate_psi(base_vals, curr_vals)
            ks_stat, ks_pval = self.calculate_ks_statistic(base_vals, curr_vals)

            if psi >= PSI_THRESHOLD_MODERATE:
                status = "HIGH_DRIFT"
                high_drift_features.append(feat)
            elif psi >= PSI_THRESHOLD_LOW:
                status = "MODERATE_DRIFT"
                mod_drift_features.append(feat)
            else:
                status = "LOW_DRIFT"

            feature_reports[feat] = {
                "psi": round(psi, 4),
                "ks_statistic": round(ks_stat, 4),
                "ks_pvalue": round(ks_pval, 6),
                "status": status,
                "baseline_mean": round(float(np.mean(base_vals)), 4) if len(base_vals) > 0 else 0.0,
                "current_mean": round(float(np.mean(curr_vals)), 4) if len(curr_vals) > 0 else 0.0,
            }

        overall_status = "LOW_DRIFT"
        if len(high_drift_features) > 0:
            overall_status = "HIGH_DRIFT"
        elif len(mod_drift_features) > 0:
            overall_status = "MODERATE_DRIFT"

        return {
            "overall_status": overall_status,
            "high_drift_count": len(high_drift_features),
            "moderate_drift_count": len(mod_drift_features),
            "high_drift_features": high_drift_features,
            "moderate_drift_features": mod_drift_features,
            "feature_metrics": feature_reports
        }

    def evaluate_prediction_drift(self, current_preds: np.ndarray) -> Dict[str, Any]:
        """
        Evaluates distribution shift in predicted fraud probabilities P(Y=1).
        """
        if self.baseline_preds is None:
            return {"status": "NO_BASELINE", "psi": 0.0, "ks_statistic": 0.0}

        psi = self.calculate_psi(self.baseline_preds, current_preds)
        ks_stat, ks_pval = self.calculate_ks_statistic(self.baseline_preds, current_preds)

        if psi >= PSI_THRESHOLD_MODERATE:
            status = "HIGH_DRIFT"
        elif psi >= PSI_THRESHOLD_LOW:
            status = "MODERATE_DRIFT"
        else:
            status = "LOW_DRIFT"

        return {
            "prediction_drift_status": status,
            "prediction_psi": round(psi, 4),
            "prediction_ks_statistic": round(ks_stat, 4),
            "prediction_ks_pvalue": round(ks_pval, 6),
            "baseline_mean_prob": round(float(np.mean(self.baseline_preds)), 4),
            "current_mean_prob": round(float(np.mean(current_preds)), 4)
        }

    def generate_drift_health_report(self, current_df: pd.DataFrame, current_preds: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Generates an end-to-end drift audit summary with governance recommendations.
        """
        feat_res = self.evaluate_feature_drift(current_df)
        pred_res = self.evaluate_prediction_drift(current_preds) if current_preds is not None else None

        recommendations = []
        if feat_res["overall_status"] == "HIGH_DRIFT":
            recommendations.append(
                f"ACTION REQUIRED: Significant feature shift detected in {feat_res['high_drift_count']} features "
                f"({', '.join(feat_res['high_drift_features'])}). Investigate upstream data pipeline or business behavior shifts."
            )
        elif feat_res["overall_status"] == "MODERATE_DRIFT":
            recommendations.append(
                f"MONITOR: Moderate distribution drift detected in {feat_res['moderate_drift_count']} features. "
                "Schedule model recalibration review."
            )
        else:
            recommendations.append("NOMINAL: Feature distributions are stable (PSI < 0.10).")

        if pred_res and pred_res.get("prediction_drift_status") == "HIGH_DRIFT":
            recommendations.append("HIGH ALERT: Model output distribution has shifted materially. Review operational threshold volume.")

        return {
            "overall_system_status": "HIGH_DRIFT" if (feat_res["overall_status"] == "HIGH_DRIFT" or (pred_res and pred_res.get("prediction_drift_status") == "HIGH_DRIFT")) else feat_res["overall_status"],
            "feature_drift": feat_res,
            "prediction_drift": pred_res,
            "recommendations": recommendations
        }
