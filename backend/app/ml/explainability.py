import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import shap

from app.ml.feature_engineering import FEATURE_NAMES
from app.ml.fraud_classifier import get_base_xgboost_model
from app.core.logging import logger

HUMAN_EXPLANATIONS = {
    "amount": "Transaction amount compared to customer cohort",
    "amount_deviation_ratio": "Transaction amount significantly deviates from customer 30-day baseline",
    "transaction_velocity_1h": "High transaction frequency in the past 1 hour",
    "transaction_velocity_24h": "Elevated transaction frequency across the 24-hour window",
    "is_new_device": "Transaction initiated from a previously unobserved device",
    "is_new_merchant": "Transaction processed at an unfamiliar merchant for this customer",
    "location_changed": "Transaction origin location deviates from historical geography",
    "hour_of_day": "Transaction executed during off-peak night/early morning hours",
    "time_since_last_transaction_seconds": "Rapid succession of transactions detected",
    "transaction_type_encoded": "High-risk transaction mechanism (e.g. Wire Transfer / CNP)",
    "avg_amount_customer_30d": "Customer historic 30-day spending average benchmark",
    "day_of_week": "Unusual day-of-week pattern for this entity"
}

_explainer_cache = None

def get_tree_explainer() -> Optional[shap.TreeExplainer]:
    global _explainer_cache
    if _explainer_cache is None:
        base_model = get_base_xgboost_model()
        if base_model is not None:
            try:
                _explainer_cache = shap.TreeExplainer(base_model)
                logger.info("Initialized SHAP TreeExplainer on XGBoost booster")
            except Exception as e:
                logger.error(f"Failed to initialize SHAP TreeExplainer: {e}")
    return _explainer_cache

def generate_shap_explanation(
    features_dict: Dict[str, float]
) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Computes exact local SHAP feature attributions using TreeExplainer.
    Guarantees mathematical consistency: base_value + sum(shap_values) == margin prediction.
    """
    explainer = get_tree_explainer()
    shap_values_dict = {}
    top_factors = []

    try:
        df = pd.DataFrame([[float(features_dict.get(col, 0.0)) for col in FEATURE_NAMES]], columns=FEATURE_NAMES)
        
        if explainer is not None:
            # TreeExplainer calculates exact shap values
            raw_shap = explainer.shap_values(df)
            if isinstance(raw_shap, list):
                # Binary classification list format
                raw_shap = raw_shap[1] if len(raw_shap) > 1 else raw_shap[0]
            
            # Shape (1, n_features) -> 1D array
            vals = np.array(raw_shap).flatten()

            for idx, name in enumerate(FEATURE_NAMES):
                sv = float(vals[idx])
                shap_values_dict[name] = round(sv, 4)

                val = float(features_dict.get(name, 0.0))
                # Direction definition:
                # POSITIVE: increases fraud likelihood (sv > 0.02)
                # NEGATIVE: decreases fraud likelihood (sv < -0.02)
                # NEUTRAL: negligible contribution
                if sv > 0.02:
                    direction = "POSITIVE"
                elif sv < -0.02:
                    direction = "NEGATIVE"
                else:
                    direction = "NEUTRAL"

                top_factors.append({
                    "feature_name": name,
                    "feature_value": val,
                    "contribution": round(abs(sv), 4),
                    "signed_contribution": round(sv, 4),
                    "direction": direction,
                    "explanation": HUMAN_EXPLANATIONS.get(name, f"Signal from {name}")
                })

            # Sort top factors by signed contribution descending (strongest fraud drivers first)
            top_factors.sort(key=lambda x: x["signed_contribution"], reverse=True)

        else:
            # Fallback if tree explainer is not available
            for name in FEATURE_NAMES:
                val = float(features_dict.get(name, 0.0))
                shap_values_dict[name] = 0.0
                top_factors.append({
                    "feature_name": name,
                    "feature_value": val,
                    "contribution": 0.0,
                    "signed_contribution": 0.0,
                    "direction": "NEUTRAL",
                    "explanation": HUMAN_EXPLANATIONS.get(name, f"Feature {name}")
                })

    except Exception as e:
        logger.error(f"Error computing SHAP attributions: {e}")
        shap_values_dict = {col: 0.0 for col in FEATURE_NAMES}
        top_factors = [{
            "feature_name": "system_notice",
            "feature_value": 0.0,
            "contribution": 0.0,
            "signed_contribution": 0.0,
            "direction": "NEUTRAL",
            "explanation": "SHAP fallback attribution mode active"
        }]

    return shap_values_dict, top_factors[:5]
