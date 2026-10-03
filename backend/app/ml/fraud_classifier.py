import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from app.core.logging import logger
from app.ml.feature_engineering import FEATURE_NAMES

def _find_artifacts_dir():
    candidates = [
        os.path.join(os.getcwd(), "models_artifacts"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "models_artifacts")
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.exists(os.path.join(c, "fraud_classifier.joblib")):
            return c
    return candidates[0]

ARTIFACTS_DIR = _find_artifacts_dir()
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "fraud_classifier.joblib")
BASE_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "base_xgboost.joblib")

_model_cache = None
_base_model_cache = None

def get_fraud_model():
    global _model_cache
    if _model_cache is None:
        if os.path.exists(MODEL_PATH):
            try:
                _model_cache = joblib.load(MODEL_PATH)
                logger.info(f"Loaded calibrated fraud classifier model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load fraud classifier model: {e}")
        else:
            logger.warning(f"Fraud model file not found at {MODEL_PATH}")
    return _model_cache

def get_base_xgboost_model():
    global _base_model_cache
    if _base_model_cache is None:
        if os.path.exists(BASE_MODEL_PATH):
            try:
                _base_model_cache = joblib.load(BASE_MODEL_PATH)
                logger.info(f"Loaded base XGBoost booster from {BASE_MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load base XGBoost booster: {e}")
        elif os.path.exists(MODEL_PATH):
            # Fallback to model in MODEL_PATH
            try:
                m = joblib.load(MODEL_PATH)
                if hasattr(m, "calibrated_classifiers_") and len(m.calibrated_classifiers_) > 0:
                    _base_model_cache = m.calibrated_classifiers_[0].estimator
                elif hasattr(m, "estimator"):
                    _base_model_cache = m.estimator
                else:
                    _base_model_cache = m
            except Exception as e:
                logger.error(f"Failed to extract base estimator from calibrated model: {e}")
    return _base_model_cache

def predict_fraud_probability(features_dict: Dict[str, float]) -> Tuple[float, str]:
    model = get_fraud_model()
    if model is None:
        logger.error("Fraud classifier unavailable, flagging controlled risk fallback.")
        return 0.50, "v2.0.0-fallback"

    try:
        df = pd.DataFrame([[features_dict.get(col, 0.0) for col in FEATURE_NAMES]], columns=FEATURE_NAMES)
        proba = model.predict_proba(df)[0, 1]
        return float(np.clip(proba, 0.0, 1.0)), "v2.0.0-forensic"
    except Exception as e:
        logger.error(f"Inference error in fraud classifier: {e}")
        return 0.50, "v2.0.0-error"
