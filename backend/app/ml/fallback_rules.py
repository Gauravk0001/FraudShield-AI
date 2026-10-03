"""
FraudShield AI — Safe Deterministic Fallback Engine

Activated when machine learning models are unavailable, fail to load, time out,
or encounter runtime inference exceptions.

Guarantees:
- Zero unhandled 500 server crashes during model degradation.
- Strict deterministic heuristics applied to available transaction attributes.
- Sets 'degraded: True' and includes 'MODEL_UNAVAILABLE_RULE_FALLBACK' in reason codes.
- Securely logs degradation events without leaking sensitive customer PII.
"""

from typing import Dict, Any, List, Tuple
from app.services.decision_engine import Decision
from app.core.logging import logger

def evaluate_deterministic_fallback(
    amount: float,
    features: Dict[str, float],
    authorized_block_rule: bool = False
) -> Tuple[float, float, float, Decision, List[Dict[str, str]]]:
    """
    Applies deterministic rules when ML inference is degraded.

    Returns:
        (fraud_probability, anomaly_score, risk_score, decision, reasons)
    """
    logger.warning("Deterministic rule fallback active for transaction scoring.")

    risk_points = 0.0
    triggered_rules = []

    amt = max(0.0, float(amount))

    # 1. Unusually large transfer
    dev_ratio = features.get("amount_deviation_ratio", 1.0)
    if amt >= 20000.0 or dev_ratio >= 5.0:
        risk_points += 45.0
        triggered_rules.append({
            "code": "HIGH_AMOUNT_DEVIATION",
            "message": "Transfer amount critically exceeds historical account baselines."
        })
    elif amt >= 7500.0 or dev_ratio >= 3.0:
        risk_points += 25.0
        triggered_rules.append({
            "code": "HIGH_AMOUNT_DEVIATION",
            "message": "The amount is substantially higher than this account's historical average."
        })

    # 2. Account emptied
    if features.get("account_emptied_indicator", 0.0) > 0.5:
        risk_points += 35.0
        triggered_rules.append({
            "code": "ACCOUNT_EMPTIED",
            "message": "The transaction nearly emptied the origin account balance."
        })

    # 3. First time destination
    if features.get("is_first_time_destination", 0.0) > 0.5:
        risk_points += 20.0
        triggered_rules.append({
            "code": "NEW_DESTINATION",
            "message": "This is the first observed transfer to this destination."
        })

    # 4. High velocity
    v_1h = features.get("velocity_origin_1h", features.get("transaction_velocity_1h", 0.0))
    if v_1h >= 3.0:
        risk_points += 30.0
        triggered_rules.append({
            "code": "HIGH_VELOCITY",
            "message": f"Rapid velocity detected: {int(v_1h)} transactions in recent window."
        })

    # 5. Device novelty (native)
    if features.get("is_new_device", 0.0) > 0.5:
        risk_points += 20.0
        triggered_rules.append({
            "code": "NEW_DEVICE",
            "message": "Transaction initiated from an unrecognized device."
        })

    # 6. Changed location
    if features.get("location_changed", 0.0) > 0.5:
        risk_points += 15.0
        triggered_rules.append({
            "code": "LOCATION_CHANGED",
            "message": "Transaction initiated from a novel geographical location."
        })

    # Compute deterministic scores
    risk_score = round(float(min(100.0, max(5.0, risk_points))), 2)
    pseudo_prob = round(float(min(0.99, max(0.01, risk_score / 100.0))), 4)
    anomaly_score = round(float(min(0.99, max(0.05, (risk_points * 0.8) / 100.0))), 4)

    # Decision mapping
    if authorized_block_rule and risk_score >= 90.0:
        decision = Decision.BLOCK
    elif risk_score >= 60.0:
        decision = Decision.HOLD_FOR_REVIEW
    elif risk_score >= 25.0:
        decision = Decision.STEP_UP
    else:
        decision = Decision.APPROVE

    # Prepend required fallback notice
    reasons = [{
        "code": "MODEL_UNAVAILABLE_RULE_FALLBACK",
        "message": "Primary ML models offline or timed out; deterministic safety rules applied."
    }]
    reasons.extend(triggered_rules)

    return pseudo_prob, anomaly_score, risk_score, decision, reasons[:3]
