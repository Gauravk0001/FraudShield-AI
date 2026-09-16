import pytest
import os
import json
import numpy as np
import pandas as pd
import joblib
import shap
import xgboost as xgb
from datetime import datetime, timezone, timedelta

from app.ml.feature_engineering import extract_features, FEATURE_NAMES
from app.ml.fraud_classifier import predict_fraud_probability, get_fraud_model, get_base_xgboost_model
from app.ml.anomaly_detector import predict_anomaly_score, get_anomaly_model
from app.ml.explainability import generate_shap_explanation, get_tree_explainer
from app.services.risk_service import calculate_risk_score
from app.models.transaction import Transaction, TransactionStatus
from app.models.user import Organization
from app.models.risk import RiskLevel

# 1. Historical Feature Boundary Test
def test_causal_temporal_feature_boundaries(db_session):
    org = Organization(id="org_test_01", name="Test Org")
    db_session.add(org)
    db_session.commit()

    now = datetime.now(timezone.utc)
    t_past = now - timedelta(hours=2)
    t_curr = now
    
    # Insert a past transaction
    past_tx = Transaction(
        id="tx_boundary_past_01",
        organization_id="org_test_01",
        transaction_id="tx_boundary_past_01",
        customer_id="cust_bound_01",
        merchant_id="merch_bound_01",
        amount=100.0,
        currency="USD",
        transaction_type="CARD_PRESENT",
        device_id="dev_bound_01",
        location="New York, US",
        timestamp=t_past,
        status=TransactionStatus.PROCESSED
    )
    db_session.add(past_tx)
    db_session.commit()

    # Extract features for current transaction
    curr_data = {
        "customer_id": "cust_bound_01",
        "merchant_id": "merch_bound_01",
        "device_id": "dev_bound_01",
        "amount": 250.0,
        "transaction_type": "CARD_PRESENT",
        "location": "New York, US",
        "timestamp": t_curr
    }
    feats = extract_features(db_session, curr_data)

    # Velocity in past 1h should be 0 (since past tx was 2h ago)
    assert feats["transaction_velocity_1h"] == 0.0
    # Velocity in past 24h should be 1
    assert feats["transaction_velocity_24h"] == 1.0
    # Device was seen in the past
    assert feats["is_new_device"] == 0.0
    # Merchant was seen in the past
    assert feats["is_new_merchant"] == 0.0

# 2. Future Leakage Invariance Test
def test_future_leakage_invariance(db_session):
    org = Organization(id="org_test_02", name="Test Org 2")
    db_session.add(org)
    db_session.commit()

    t_base = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    tx_data = {
        "customer_id": "cust_invar_01",
        "merchant_id": "merch_invar_01",
        "device_id": "dev_invar_01",
        "amount": 500.0,
        "transaction_type": "ONLINE_PAYMENT",
        "location": "Chicago, US",
        "timestamp": t_base
    }
    
    feats_before = extract_features(db_session, tx_data)

    # Insert a FUTURE transaction (timestamp > t_base)
    future_tx = Transaction(
        id="tx_future_invar_01",
        organization_id="org_test_02",
        transaction_id="tx_future_invar_01",
        customer_id="cust_invar_01",
        merchant_id="merch_invar_01",
        amount=9999.0,
        currency="USD",
        transaction_type="WIRE_TRANSFER",
        device_id="dev_future_01",
        location="Tokyo, JP",
        timestamp=t_base + timedelta(hours=5),
        status=TransactionStatus.PROCESSED
    )
    db_session.add(future_tx)
    db_session.commit()

    # Re-extract features for original transaction
    feats_after = extract_features(db_session, tx_data)

    # Future transaction MUST NOT alter current transaction features
    assert feats_before == feats_after, "Future transaction leaked into prior transaction features!"

# 3. Customer-Grouped Split Verification
def test_customer_grouped_split_zero_leakage():
    from scripts.generate_forensic_dataset import generate_causal_synthetic_dataset
    from sklearn.model_selection import GroupShuffleSplit

    df = generate_causal_synthetic_dataset(n_customers=200, n_merchants=50, days=20, seed=42)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    
    tr_idx, te_idx = next(gss.split(df, groups=df["customer_id"]))
    train_custs = set(df.iloc[tr_idx]["customer_id"])
    test_custs = set(df.iloc[te_idx]["customer_id"])
    
    overlap = train_custs.intersection(test_custs)
    assert len(overlap) == 0, f"Customer leakage detected! {len(overlap)} overlapping customers."

# 4. Target Correlation & Leakage Diagnostic Test
def test_no_target_correlation_leakage():
    from scripts.generate_forensic_dataset import generate_causal_synthetic_dataset, verify_causality_and_leakage
    df = generate_causal_synthetic_dataset(n_customers=200, n_merchants=50, days=20, seed=42)
    diag = verify_causality_and_leakage(df)
    
    assert not diag["target_leakage_detected"], "Direct target leakage detected in dataset!"
    assert diag["max_correlation"] < 0.90, f"Suspiciously high feature correlation: {diag['max_correlation']}"

# 5. Hard Negatives & Overlapping Topology Test
def test_hard_negatives_and_overlapping_distributions():
    from scripts.generate_forensic_dataset import generate_causal_synthetic_dataset
    df = generate_causal_synthetic_dataset(n_customers=300, n_merchants=80, days=30, seed=42)

    # Check that legitimate transactions include high amounts
    legit_high = df[(df["is_fraud"] == 0) & (df["amount"] > 3000.0)]
    assert len(legit_high) > 0, "No hard negative legitimate high-value transactions found!"

    # Check that legitimate transactions include new devices
    legit_new_dev = df[(df["is_fraud"] == 0) & (df["is_new_device"] == 1.0)]
    assert len(legit_new_dev) > 0, "No legitimate new device transactions found!"

    # Check that fraud includes lower amounts (card testing/probes)
    fraud_low = df[(df["is_fraud"] == 1) & (df["amount"] < 100.0)]
    assert len(fraud_low) > 0, "No low-value card testing fraud transactions found!"

# 6. Fraud Probability Bounds Test
def test_fraud_probability_bounds():
    test_cases = [
        {"amount": 10.0, "is_new_device": 0.0, "location_changed": 0.0, "transaction_velocity_1h": 0.0},
        {"amount": 15000.0, "is_new_device": 1.0, "location_changed": 1.0, "transaction_velocity_1h": 6.0},
        {"amount": 0.0, "is_new_device": 0.0, "location_changed": 0.0, "transaction_velocity_1h": 0.0}
    ]
    for tc in test_cases:
        full_feats = {col: tc.get(col, 0.0) for col in FEATURE_NAMES}
        prob, version = predict_fraud_probability(full_feats)
        assert 0.0 <= prob <= 1.0, f"Probability out of bounds: {prob}"
        assert not np.isnan(prob)
        assert not np.isinf(prob)

# 7. Probability Calibration Monotonicity Test
def test_probability_calibration_monotonicity():
    clf = get_fraud_model()
    assert clf is not None, "Production calibrated classifier not loaded!"
    
    benign_feats = {
        "amount": 35.0,
        "transaction_type_encoded": 0.0,
        "hour_of_day": 14.0,
        "day_of_week": 2.0,
        "transaction_velocity_1h": 0.0,
        "transaction_velocity_24h": 1.0,
        "avg_amount_customer_30d": 50.0,
        "amount_deviation_ratio": 0.70,
        "time_since_last_transaction_seconds": 43200.0,
        "is_new_device": 0.0,
        "is_new_merchant": 0.0,
        "location_changed": 0.0
    }

    attack_feats = {
        "amount": 15500.0,
        "transaction_type_encoded": 2.0,
        "hour_of_day": 3.0,
        "day_of_week": 1.0,
        "transaction_velocity_1h": 6.0,
        "transaction_velocity_24h": 12.0,
        "avg_amount_customer_30d": 50.0,
        "amount_deviation_ratio": 310.0,
        "time_since_last_transaction_seconds": 45.0,
        "is_new_device": 1.0,
        "is_new_merchant": 1.0,
        "location_changed": 1.0
    }

    p_benign, _ = predict_fraud_probability(benign_feats)
    p_attack, _ = predict_fraud_probability(attack_feats)

    assert p_attack > p_benign, f"Calibrated probability failed monotonicity: attack={p_attack}, benign={p_benign}"
    assert p_attack > 0.80, f"Expected high calibrated fraud probability for attack, got: {p_attack}"
    assert p_benign < 0.05, f"Expected low calibrated fraud probability for benign, got: {p_benign}"

# 8. Threshold Operating Behavior Test
def test_threshold_operating_behavior():
    meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts", "model_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
        thresh = meta.get("operating_threshold", 0.50)
        assert 0.05 <= thresh <= 0.95, f"Invalid operating threshold: {thresh}"

# 9. SHAP Mathematical Additivity Test
def test_shap_mathematical_additivity():
    explainer = get_tree_explainer()
    base_xgb = get_base_xgboost_model()
    assert explainer is not None and base_xgb is not None, "SHAP TreeExplainer or base booster not initialized"

    sample_df = pd.DataFrame([{
        "amount": 500.0,
        "transaction_type_encoded": 1.0,
        "hour_of_day": 14.0,
        "day_of_week": 3.0,
        "transaction_velocity_1h": 2.0,
        "transaction_velocity_24h": 4.0,
        "avg_amount_customer_30d": 65.0,
        "amount_deviation_ratio": 7.69,
        "time_since_last_transaction_seconds": 1800.0,
        "is_new_device": 1.0,
        "is_new_merchant": 0.0,
        "location_changed": 0.0
    }], columns=FEATURE_NAMES)

    raw_shap = explainer.shap_values(sample_df)
    if isinstance(raw_shap, list):
        raw_shap = raw_shap[1] if len(raw_shap) > 1 else raw_shap[0]
    
    sum_shap = float(np.sum(raw_shap[0]))
    base_val = float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    
    margin_pred = float(base_xgb.get_booster().predict(xgb.DMatrix(sample_df), output_margin=True)[0])
    additivity_error = abs((base_val + sum_shap) - margin_pred)

    assert additivity_error < 1e-4, f"SHAP additivity violated: error = {additivity_error}"

# 10. SHAP Directional Attribution Test
def test_shap_directional_attribution():
    suspicious_feats = {
        "amount": 15000.0,
        "transaction_type_encoded": 2.0,
        "hour_of_day": 3.0,
        "day_of_week": 1.0,
        "transaction_velocity_1h": 5.0,
        "transaction_velocity_24h": 8.0,
        "avg_amount_customer_30d": 65.0,
        "amount_deviation_ratio": 230.7,
        "time_since_last_transaction_seconds": 90.0,
        "is_new_device": 1.0,
        "is_new_merchant": 1.0,
        "location_changed": 1.0
    }

    shap_dict, top_factors = generate_shap_explanation(suspicious_feats)
    assert len(top_factors) > 0, "No top factors returned by SHAP"
    
    positive_factors = [tf for tf in top_factors if tf["direction"] == "POSITIVE"]
    assert len(positive_factors) > 0, "Expected positive SHAP attributions for high-risk features"

# 11. Isolation Forest Normalization Test
def test_isolation_forest_anomaly_normalization():
    test_feats = {col: 0.0 for col in FEATURE_NAMES}
    score, ver = predict_anomaly_score(test_feats)
    assert 0.0 <= score <= 1.0, f"Isolation Forest score not in [0, 1]: {score}"
    assert not np.isnan(score)

# 12. Composite Risk Engine Weighting Test
def test_composite_risk_engine_weights():
    features = {
        "is_new_device": 1.0,
        "is_new_merchant": 1.0,
        "location_changed": 1.0,
        "transaction_velocity_1h": 4.0,
        "amount_deviation_ratio": 10.0,
        "amount": 9000.0
    }
    fraud_prob = 0.95
    anomaly_score = 0.80

    risk_score, level, flags = calculate_risk_score(fraud_prob, anomaly_score, features)
    
    assert 0.0 <= risk_score <= 100.0
    assert level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert flags.get("new_device") is True
    assert flags.get("high_velocity_1h") is True

# 13. Counterfactual Benign Sensitivity Test
def test_counterfactual_benign_sensitivity():
    suspicious_feats = {
        "amount": 14000.0,
        "transaction_type_encoded": 2.0,
        "hour_of_day": 3.0,
        "day_of_week": 1.0,
        "transaction_velocity_1h": 5.0,
        "transaction_velocity_24h": 9.0,
        "avg_amount_customer_30d": 65.0,
        "amount_deviation_ratio": 215.0,
        "time_since_last_transaction_seconds": 60.0,
        "is_new_device": 1.0,
        "is_new_merchant": 1.0,
        "location_changed": 1.0
    }

    p_susp, _ = predict_fraud_probability(suspicious_feats)
    a_susp, _ = predict_anomaly_score(suspicious_feats)
    risk_susp, _, _ = calculate_risk_score(p_susp, a_susp, suspicious_feats)

    # Benign perturbation: amount $45, known device, home location, 0 velocity, card present
    benign_feats = {
        "amount": 45.0,
        "transaction_type_encoded": 0.0,
        "hour_of_day": 14.0,
        "day_of_week": 2.0,
        "transaction_velocity_1h": 0.0,
        "transaction_velocity_24h": 1.0,
        "avg_amount_customer_30d": 50.0,
        "amount_deviation_ratio": 0.90,
        "time_since_last_transaction_seconds": 43200.0,
        "is_new_device": 0.0,
        "is_new_merchant": 0.0,
        "location_changed": 0.0
    }

    p_benign, _ = predict_fraud_probability(benign_feats)
    a_benign, _ = predict_anomaly_score(benign_feats)
    risk_benign, _, _ = calculate_risk_score(p_benign, a_benign, benign_feats)

    assert risk_benign < risk_susp, f"Counterfactual failed: benign risk ({risk_benign}) >= suspicious risk ({risk_susp})"
    assert p_benign < p_susp, f"Counterfactual failed: benign prob ({p_benign}) >= suspicious prob ({p_susp})"

# 14. Adversarial Edge Cases Test
def test_adversarial_edge_cases():
    edge_cases = [
        {"amount": 0.0},
        {"amount": -100.0},
        {"amount": 1000000.0},
        {"transaction_velocity_1h": 999.0},
        {"time_since_last_transaction_seconds": 0.001}
    ]
    for ec in edge_cases:
        feats = {col: 0.0 for col in FEATURE_NAMES}
        feats.update(ec)
        prob, _ = predict_fraud_probability(feats)
        anom, _ = predict_anomaly_score(feats)
        risk, level, _ = calculate_risk_score(prob, anom, feats)
        
        assert 0.0 <= prob <= 1.0
        assert 0.0 <= anom <= 1.0
        assert 0.0 <= risk <= 100.0

# 15. Cold Start Unseen Customer Test
def test_cold_start_new_customer_behavior(db_session):
    tx_data = {
        "customer_id": "cust_brand_new_999",
        "merchant_id": "merch_brand_new_999",
        "device_id": "dev_brand_new_999",
        "amount": 85.0,
        "transaction_type": "CARD_PRESENT",
        "location": "Boston, US",
        "timestamp": datetime.now(timezone.utc)
    }
    feats = extract_features(db_session, tx_data)
    assert feats["is_new_device"] == 1.0
    assert feats["is_new_merchant"] == 1.0
    assert feats["transaction_velocity_1h"] == 0.0
    # Baseline cohort benchmark used for avg amount
    assert feats["avg_amount_customer_30d"] == 75.0

# 16. Model Artifact Metadata Compatibility Test
def test_model_artifact_metadata_compatibility():
    meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts", "model_metadata.json")
    assert os.path.exists(meta_path), "model_metadata.json does not exist"
    
    with open(meta_path, "r") as f:
        meta = json.load(f)

    assert "version" in meta
    assert "feature_names" in meta
    assert len(meta["feature_names"]) == len(FEATURE_NAMES)
    assert meta["feature_names"] == FEATURE_NAMES
    assert "operating_threshold" in meta
    assert "calibration" in meta
