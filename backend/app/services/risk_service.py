from typing import Dict, Any, Tuple
from app.models.risk import RiskLevel
from app.core.config import settings

def calculate_risk_score(
    fraud_probability: float,
    anomaly_score: float,
    features_dict: Dict[str, float]
) -> Tuple[float, RiskLevel, Dict[str, Any]]:
    
    behavioral_flags = {}
    behavioral_boost = 0.0

    # Behavioral signal detection
    if features_dict.get("is_new_device", 0) > 0:
        behavioral_flags["new_device"] = True
        behavioral_boost += 0.35
    
    if features_dict.get("is_new_merchant", 0) > 0:
        behavioral_flags["new_merchant"] = True
        behavioral_boost += 0.25

    if features_dict.get("transaction_velocity_1h", 0) >= 3:
        behavioral_flags["high_velocity_1h"] = True
        behavioral_boost += 0.35

    if features_dict.get("amount_deviation_ratio", 1.0) >= 3.0 or features_dict.get("amount", 0) >= 5000.0:
        behavioral_flags["high_amount_deviation"] = True
        behavioral_boost += 0.50

    # Deterministic risk calculation: Fraud model 40%, Anomaly 20%, Behavioral signals 40%
    raw_risk = (fraud_probability * 40.0) + (anomaly_score * 20.0) + (min(behavioral_boost, 1.0) * 40.0)


    risk_score = round(float(min(100.0, max(0.0, raw_risk))), 2)

    # Determine risk level based on configurable thresholds
    if risk_score >= 90.0:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= settings.RISK_THRESHOLD_HIGH:
        risk_level = RiskLevel.HIGH
    elif risk_score >= settings.RISK_THRESHOLD_MEDIUM:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    return risk_score, risk_level, behavioral_flags
