import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from app.core.logging import logger
from app.ml.feature_engineering import FEATURE_NAMES

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib")

_iso_model_cache = None

def get_anomaly_model():
    global _iso_model_cache
    if _iso_model_cache is None:
        if os.path.exists(MODEL_PATH):
            try:
                _iso_model_cache = joblib.load(MODEL_PATH)
                logger.info(f"Loaded Isolation Forest model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load Isolation Forest model: {e}")
        else:
            logger.warning(f"Isolation Forest model file not found at {MODEL_PATH}")
    return _iso_model_cache

def predict_anomaly_score(features_dict: Dict[str, float]) -> Tuple[float, str]:
    model = get_anomaly_model()
    if model is None:
        return 0.30, "iso-v1.0.0-fallback"

    try:
        df = pd.DataFrame([[features_dict.get(col, 0.0) for col in FEATURE_NAMES]], columns=FEATURE_NAMES)
        # Isolation Forest decision_function outputs values where lower means more anomalous
        raw_score = model.decision_function(df)[0]
        # Normalize score into [0, 1] range where 1.0 is highly anomalous
        # decision_function typically ranges from -0.5 to +0.5
        normalized = 1.0 - (1.0 / (1.0 + np.exp(-5.0 * raw_score)))
        return float(np.clip(normalized, 0.0, 1.0)), "iso-v1.0.0"
    except Exception as e:
        logger.error(f"Inference error in anomaly detector: {e}")
        return 0.30, "iso-v1.0.0-error"
