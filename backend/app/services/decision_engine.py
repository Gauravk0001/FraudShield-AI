"""
FraudShield AI — Cost-Based Decision Engine & Reason Code Explainer

Implements the expected-loss optimization policy:
  missed_fraud_cost = transaction_amount + MISSED_FRAUD_FIXED_COST ($50)
  false_decline_cost = FALSE_DECLINE_COST ($5)
  expected_missed_fraud_loss = p * missed_fraud_cost
  expected_false_decline_loss = (1 - p) * false_decline_cost

Decisions:
- APPROVE: Low risk recommendation.
- STEP_UP: Moderate risk recommendation prompting multi-factor challenge.
- HOLD_FOR_REVIEW: High risk recommendation pausing funds for human analyst triage.
- BLOCK: Exclusively requires an explicitly configured, authorized business rule.

CRITICAL SAFETY BOUNDARY:
FraudShield AI is an advisory decision-support system. It never permanently denies
a customer transaction autonomously without policy authorization.
"""

import os
import json
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from app.core.config import settings
from app.core.logging import logger

class Decision(str, Enum):
    APPROVE = "APPROVE"
    STEP_UP = "STEP_UP"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    BLOCK = "BLOCK"

class ReasonCodeItem:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code, "message": self.message}

def _load_persisted_thresholds() -> Dict[str, float]:
    """Loads cost-optimal thresholds from artifact file if available."""
    candidates = [
        os.path.join(os.getcwd(), "backend", "models_artifacts", "paysim", "thresholds.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts", "paysim", "thresholds.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "models_artifacts", "paysim", "thresholds.json"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {
                        "step_up_threshold": float(data.get("step_up_threshold", 0.05)),
                        "hold_for_review_threshold": float(data.get("hold_for_review_threshold", 0.10)),
                        "authorized_block_threshold": float(data.get("authorized_block_threshold", 0.95))
                    }
            except Exception as e:
                logger.warning(f"Could not parse thresholds file {p}: {e}")
    # Safe defaults
    return {
        "step_up_threshold": 0.05,
        "hold_for_review_threshold": 0.10,
        "authorized_block_threshold": 0.95
    }

class CostDecisionEngine:
    def __init__(self):
        self.thresholds = _load_persisted_thresholds()
        self.false_decline_cost = getattr(settings, "FALSE_DECLINE_COST", 5.0)
        self.missed_fraud_fixed_cost = getattr(settings, "MISSED_FRAUD_FIXED_COST", 50.0)
        self.step_up_cost = getattr(settings, "STEP_UP_COST", 1.0)

    def reload_thresholds(self) -> None:
        self.thresholds = _load_persisted_thresholds()

    def evaluate_decision(
        self,
        fraud_probability: float,
        amount: float,
        features: Dict[str, float],
        authorized_block_rule: bool = False
    ) -> Tuple[Decision, float, List[Dict[str, str]]]:
        """
        Calculates expected cost and maps to appropriate advisory recommendation.
        Returns: (Decision, risk_score_0_100, top_three_reasons)
        """
        p = max(0.0, min(1.0, float(fraud_probability)))
        amt = max(0.0, float(amount))

        # Expected loss calculations
        missed_fraud_cost = amt + self.missed_fraud_fixed_cost
        false_decline_cost = self.false_decline_cost

        expected_missed_fraud_loss = p * missed_fraud_cost
        expected_false_decline_loss = (1.0 - p) * false_decline_cost

        # Composite risk score (0-100)
        # Scaled smoothly using calibrated probability and loss ratio
        raw_risk = p * 100.0
        risk_score = round(float(min(100.0, max(0.0, raw_risk))), 2)

        # Decision policy
        step_thresh = self.thresholds.get("step_up_threshold", 0.05)
        hold_thresh = self.thresholds.get("hold_for_review_threshold", 0.10)
        block_thresh = self.thresholds.get("authorized_block_threshold", 0.95)

        # Authorized block condition: requires BOTH extreme score and explicit business rule
        if authorized_block_rule and p >= block_thresh:
            decision = Decision.BLOCK
        elif p >= hold_thresh or expected_missed_fraud_loss > expected_false_decline_loss * 2.0:
            decision = Decision.HOLD_FOR_REVIEW
        elif p >= step_thresh or expected_missed_fraud_loss > self.step_up_cost * 2.0:
            decision = Decision.STEP_UP
        else:
            decision = Decision.APPROVE

        # Generate top 3 explainable reason codes
        reasons = self._generate_reason_codes(p, amt, features, decision)
        return decision, risk_score, reasons[:3]

    def _generate_reason_codes(
        self,
        p: float,
        amount: float,
        features: Dict[str, float],
        decision: Decision
    ) -> List[Dict[str, str]]:
        reasons = []

        # 1. Amount deviation
        dev_ratio = features.get("amount_deviation_ratio", 1.0)
        if dev_ratio >= 3.0 or amount >= 10000.0:
            reasons.append({
                "code": "HIGH_AMOUNT_DEVIATION",
                "message": "The amount is substantially higher than this account's historical average."
            })

        # 2. Account emptied
        if features.get("account_emptied_indicator", 0.0) > 0.5:
            reasons.append({
                "code": "ACCOUNT_EMPTIED",
                "message": "The transaction nearly emptied the origin account balance."
            })

        # 3. New destination
        if features.get("is_first_time_destination", 0.0) > 0.5:
            reasons.append({
                "code": "NEW_DESTINATION",
                "message": "This is the first observed transfer to this destination."
            })

        # 4. High velocity
        v_1h = features.get("velocity_origin_1h", features.get("transaction_velocity_1h", 0.0))
        if v_1h >= 2.0:
            reasons.append({
                "code": "HIGH_VELOCITY",
                "message": f"Elevated origin account activity detected ({int(v_1h)} transactions in recent window)."
            })

        # 5. Device novelty (native)
        if features.get("is_new_device", 0.0) > 0.5:
            reasons.append({
                "code": "NEW_DEVICE",
                "message": "Access from an unrecognized hardware device ID."
            })

        # 6. Foreign / Changed location
        if features.get("location_changed", 0.0) > 0.5:
            reasons.append({
                "code": "LOCATION_CHANGED",
                "message": "Transaction initiated from a novel geographical location."
            })

        # 7. High-risk transfer type
        type_enc = features.get("type_encoded", features.get("transaction_type_encoded", 0.0))
        if type_enc in [3, 4, 2]: # CASH_OUT, TRANSFER, WIRE_TRANSFER
            reasons.append({
                "code": "HIGH_RISK_METHOD",
                "message": "Transaction utilizes an irreversible transfer or cash-out mechanism."
            })

        # Default fallbacks if fewer than 3 reasons triggered
        if len(reasons) < 3:
            if decision == Decision.HOLD_FOR_REVIEW:
                reasons.append({
                    "code": "ELEVATED_FRAUD_PROBABILITY",
                    "message": f"Statistical risk model assessed elevated fraud probability ({p*100:.1f}%)."
                })
            elif decision == Decision.STEP_UP:
                reasons.append({
                    "code": "STEP_UP_FRICTION_RECOMMENDED",
                    "message": "Transaction attributes exceed safe straight-through processing boundaries."
                })
            else:
                reasons.append({
                    "code": "TRANSACTION_CLEARED",
                    "message": "Transaction attributes consistent with baseline customer behavioral patterns."
                })

        return reasons

decision_engine = CostDecisionEngine()
