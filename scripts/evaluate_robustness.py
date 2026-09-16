import os
import json
import numpy as np
import pandas as pd
import joblib
import shap
import xgboost as xgb
from sklearn.inspection import permutation_importance
from datetime import datetime, timezone

from generate_forensic_dataset import FEATURE_NAMES, generate_causal_synthetic_dataset

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_artifacts")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

def evaluate_shap_and_feature_importances(base_xgb, X_val, y_val):
    print("\n--- 1. Evaluating Feature Importance (Gain vs Permutation vs SHAP) ---")
    
    # 1. XGBoost Gain Importance
    booster = base_xgb.get_booster()
    gain_scores = booster.get_score(importance_type="gain")
    total_gain = sum(gain_scores.values()) if gain_scores else 1.0
    gain_importance = {feat: round(float(gain_scores.get(feat, 0.0) / total_gain), 4) for feat in FEATURE_NAMES}

    # 2. Permutation Importance
    perm_res = permutation_importance(base_xgb, X_val, y_val, n_repeats=5, random_state=42, scoring="roc_auc")
    perm_importance = {feat: round(float(perm_res.importances_mean[i]), 4) for i, feat in enumerate(FEATURE_NAMES)}

    # 3. SHAP Global Importance (Mean Absolute SHAP)
    explainer = shap.TreeExplainer(base_xgb)
    shap_vals = explainer.shap_values(X_val)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    shap_importance = {feat: round(float(mean_abs_shap[i]), 4) for i, feat in enumerate(FEATURE_NAMES)}

    importance_df = pd.DataFrame({
        "Feature": FEATURE_NAMES,
        "XGBoost_Gain": [gain_importance[f] for f in FEATURE_NAMES],
        "Permutation_AUC_Drop": [perm_importance[f] for f in FEATURE_NAMES],
        "Mean_Abs_SHAP": [shap_importance[f] for f in FEATURE_NAMES]
    }).sort_values(by="Mean_Abs_SHAP", ascending=False)

    print(importance_df.to_string(index=False))

    # 4. SHAP Mathematical Additivity Verification
    print("\n--- 2. Validating SHAP Mathematical Consistency (Local Additivity) ---")
    # Margin output = explainer.expected_value + sum(shap_values)
    expected_val = float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    
    sample_sub = X_val.iloc[:100]
    sample_shap = explainer.shap_values(sample_sub)
    if isinstance(sample_shap, list):
        sample_shap = sample_shap[1] if len(sample_shap) > 1 else sample_shap[0]
    
    margin_preds = booster.predict(xgb.DMatrix(sample_sub), output_margin=True)
    
    reconstructed_margins = expected_val + np.sum(sample_shap, axis=1)
    max_additivity_error = float(np.max(np.abs(margin_preds - reconstructed_margins)))
    print(f"   Base Value (Expected Margin): {expected_val:.4f}")
    print(f"   Max Additivity Error across 100 samples: {max_additivity_error:.8e}")
    print(f"   Additivity Consistency Check: {'PASS (Exact Tree Additivity)' if max_additivity_error < 1e-4 else 'FAIL'}")

    return {
        "feature_importances": importance_df.to_dict(orient="records"),
        "shap_base_value": expected_val,
        "max_additivity_error": max_additivity_error,
        "additivity_verified": bool(max_additivity_error < 1e-4)
    }

def evaluate_counterfactual_perturbations(calibrated_clf, iso_model, base_xgb):
    print("\n--- 3. Running Counterfactual Perturbation Tests ---")
    explainer = shap.TreeExplainer(base_xgb)

    # Base Suspicious Transaction (High-Risk Account Takeover / Attack)
    base_tx = {
        "amount": 14500.0,
        "transaction_type_encoded": 2.0,  # WIRE_TRANSFER
        "hour_of_day": 3.0,               # 3 AM
        "day_of_week": 1.0,
        "transaction_velocity_1h": 5.0,
        "transaction_velocity_24h": 8.0,
        "avg_amount_customer_30d": 65.0,
        "amount_deviation_ratio": 219.69,
        "time_since_last_transaction_seconds": 120.0,
        "is_new_device": 1.0,
        "is_new_merchant": 1.0,
        "location_changed": 1.0
    }

    def score_tx(features):
        df_in = pd.DataFrame([[features[col] for col in FEATURE_NAMES]], columns=FEATURE_NAMES)
        prob = float(calibrated_clf.predict_proba(df_in)[0, 1])
        
        raw_iso = float(iso_model.decision_function(df_in)[0])
        norm_iso = float(1.0 - (1.0 / (1.0 + np.exp(-5.0 * raw_iso))))

        # Behavioral boost
        b_boost = 0.0
        if features["is_new_device"] > 0: b_boost += 0.30
        if features["is_new_merchant"] > 0: b_boost += 0.20
        if features["location_changed"] > 0: b_boost += 0.25
        if features["transaction_velocity_1h"] >= 3: b_boost += 0.35
        if features["amount_deviation_ratio"] >= 8.0 or features["amount"] >= 7500.0:
            b_boost += 0.50
        elif features["amount_deviation_ratio"] >= 3.0 or features["amount"] >= 3000.0:
            b_boost += 0.30

        raw_risk = (prob * 45.0) + (norm_iso * 20.0) + (min(1.0, b_boost) * 35.0)
        risk_score = round(float(np.clip(raw_risk, 0.0, 100.0)), 2)

        shap_v = explainer.shap_values(df_in)
        if isinstance(shap_v, list):
            shap_v = shap_v[1] if len(shap_v) > 1 else shap_v[0]
        top_shap = {FEATURE_NAMES[i]: round(float(shap_v[0, i]), 3) for i in range(len(FEATURE_NAMES))}
        # Sort by signed value
        top_shap_sorted = sorted(top_shap.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "fraud_probability": round(prob, 4),
            "anomaly_score": round(norm_iso, 4),
            "behavioral_boost": round(min(1.0, b_boost), 2),
            "risk_score": risk_score,
            "top_shap_contributors": top_shap_sorted
        }

    perturbations = [
        ("BASE_SUSPICIOUS (Hero Attack)", {}),
        ("Perturb: Amount $14,500 -> $45 (Normal)", {"amount": 45.0, "amount_deviation_ratio": 0.68}),
        ("Perturb: Device New -> Known Device", {"is_new_device": 0.0}),
        ("Perturb: Location Foreign -> Home Location", {"location_changed": 0.0}),
        ("Perturb: Velocity 5 -> 0 (Normal Pace)", {"transaction_velocity_1h": 0.0, "time_since_last_transaction_seconds": 43200.0}),
        ("Perturb: Hour 3 AM -> 2 PM (Normal Day)", {"hour_of_day": 14.0}),
        ("Perturb: All Normal (Benign Tx)", {
            "amount": 45.0,
            "transaction_type_encoded": 0.0,
            "hour_of_day": 14.0,
            "transaction_velocity_1h": 0.0,
            "transaction_velocity_24h": 1.0,
            "amount_deviation_ratio": 0.68,
            "time_since_last_transaction_seconds": 43200.0,
            "is_new_device": 0.0,
            "is_new_merchant": 0.0,
            "location_changed": 0.0
        })
    ]

    counterfactual_results = []
    for label, changes in perturbations:
        mod_tx = base_tx.copy()
        mod_tx.update(changes)
        res = score_tx(mod_tx)
        res["perturbation"] = label
        counterfactual_results.append(res)
        print(f"\n{label}:")
        print(f"  Probability: {res['fraud_probability']:.4f} | Anomaly: {res['anomaly_score']:.4f} | Risk Score: {res['risk_score']} | Top SHAP: {res['top_shap_contributors']}")

    return counterfactual_results

def evaluate_adversarial_edge_cases(calibrated_clf, iso_model):
    print("\n--- 4. Evaluating Adversarial Edge Cases & Boundary Conditions ---")
    
    edge_cases = [
        ("Zero Amount ($0.00)", {"amount": 0.0, "amount_deviation_ratio": 0.0}),
        ("Negative Amount (-$50.00)", {"amount": -50.0, "amount_deviation_ratio": 0.0}),
        ("Extreme Amount ($1,000,000.00)", {"amount": 1000000.0, "amount_deviation_ratio": 15000.0}),
        ("New Customer Cold-Start (No Prior History)", {
            "amount": 120.0,
            "transaction_velocity_1h": 0.0,
            "transaction_velocity_24h": 0.0,
            "avg_amount_customer_30d": 75.0,
            "amount_deviation_ratio": 1.58,
            "time_since_last_transaction_seconds": 86400.0,
            "is_new_device": 1.0,
            "is_new_merchant": 1.0,
            "location_changed": 0.0
        }),
        ("Rapid Duplicate Timestamp (t_diff = 0.1s)", {
            "amount": 50.0,
            "time_since_last_transaction_seconds": 0.1,
            "transaction_velocity_1h": 8.0,
            "transaction_velocity_24h": 12.0
        }),
        ("Unknown Transaction Type Encoded (99.0)", {
            "transaction_type_encoded": 99.0
        })
    ]

    default_base = {
        "amount": 65.0,
        "transaction_type_encoded": 1.0,
        "hour_of_day": 12.0,
        "day_of_week": 3.0,
        "transaction_velocity_1h": 0.0,
        "transaction_velocity_24h": 1.0,
        "avg_amount_customer_30d": 65.0,
        "amount_deviation_ratio": 0.98,
        "time_since_last_transaction_seconds": 21600.0,
        "is_new_device": 0.0,
        "is_new_merchant": 0.0,
        "location_changed": 0.0
    }

    edge_results = []
    for label, changes in edge_cases:
        tx = default_base.copy()
        tx.update(changes)
        
        df_in = pd.DataFrame([[tx[col] for col in FEATURE_NAMES]], columns=FEATURE_NAMES)
        
        # Test inference stability
        try:
            prob = float(calibrated_clf.predict_proba(df_in)[0, 1])
            raw_iso = float(iso_model.decision_function(df_in)[0])
            norm_iso = float(1.0 - (1.0 / (1.0 + np.exp(-5.0 * raw_iso))))
            
            is_valid = (not np.isnan(prob)) and (not np.isinf(prob)) and (0.0 <= prob <= 1.0)
            status = "PASS (Valid Bounded Inference)" if is_valid else "FAIL (Invalid Model Output)"
        except Exception as e:
            prob = None
            status = f"FAIL (Exception: {e})"

        edge_results.append({
            "test_case": label,
            "fraud_probability": round(prob, 4) if prob is not None else None,
            "status": status
        })
        print(f"  {label} -> Prob: {prob} | Status: {status}")

    return edge_results

if __name__ == "__main__":
    base_xgb = joblib.load(os.path.join(ARTIFACTS_DIR, "base_xgboost.joblib"))
    calibrated_clf = joblib.load(os.path.join(ARTIFACTS_DIR, "fraud_classifier.joblib"))
    iso_model = joblib.load(os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib"))

    df = generate_causal_synthetic_dataset(n_customers=600, n_merchants=150, days=45, seed=42)
    X_val = df.iloc[int(len(df)*0.70):int(len(df)*0.85)][FEATURE_NAMES]
    y_val = df.iloc[int(len(df)*0.70):int(len(df)*0.85)]["is_fraud"]

    feat_res = evaluate_shap_and_feature_importances(base_xgb, X_val, y_val)
    counter_res = evaluate_counterfactual_perturbations(calibrated_clf, iso_model, base_xgb)
    edge_res = evaluate_adversarial_edge_cases(calibrated_clf, iso_model)

    robustness_data = {
        "shap_and_importances": feat_res,
        "counterfactual_tests": counter_res,
        "edge_case_tests": edge_res
    }

    with open(os.path.join(DOCS_DIR, "robustness_and_explainability.json"), "w", encoding="utf-8") as f:
        json.dump(robustness_data, f, indent=2)

    print("\n[OK] Robustness and explainability validation complete. Results saved to docs/robustness_and_explainability.json")
