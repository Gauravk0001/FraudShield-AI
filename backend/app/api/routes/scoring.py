"""
FraudShield AI — Dedicated Scoring Route (POST /api/v1/score)

Handles low-latency real-time fraud scoring for both native FraudShield
and PaySim simulation transactions.

Features:
- Dual schema support (native & PaySim)
- Calibrated probability, anomaly score, and composite risk score (0-100)
- Cost-optimal advisory decisions (APPROVE, STEP_UP, HOLD_FOR_REVIEW)
- Safe degraded fallback (deterministic heuristics when models fail)
- Redis / WebSocket alert broadcasting for high-risk transactions
- In-memory & Redis observability metrics
"""

import os
import time
import uuid
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.schemas.scoring import ScoreRequest, ScoreResponse, ReasonItem
from app.services.decision_engine import decision_engine, Decision
from app.ml.fallback_rules import evaluate_deterministic_fallback
from app.ml.paysim_features import online_feature_store
from app.ml.feature_schema import validate_feature_columns
from app.services.metrics_service import metrics_registry
from app.realtime.event_processor import publish_event
from app.realtime.websocket_manager import ws_manager

router = APIRouter()

# Model Cache
_model_cache: Dict[str, Any] = {
    "classifier": None,
    "iso_forest": None,
    "feature_cols": None,
    "version": "paysim-v1",
    "is_balance_active": False,
    "loaded": False
}

def _get_active_models():
    """Lazily loads and caches the active PaySim model artifacts."""
    if _model_cache["loaded"]:
        return _model_cache["classifier"], _model_cache["iso_forest"], _model_cache["feature_cols"], _model_cache["version"]

    artifacts_candidates = [
        os.path.join(os.getcwd(), "backend", "models_artifacts", "paysim"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "models_artifacts", "paysim"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models_artifacts", "paysim")
    ]
    artifacts_dir = None
    for c in artifacts_candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "fraud_classifier.joblib")):
            artifacts_dir = c
            break

    if not artifacts_dir:
        logger.warning("PaySim model artifacts not found; falling back to deterministic rules.")
        metrics_registry.set_model_status("FAILED")
        return None, None, None, "v1-fallback"

    try:
        clf_path = os.path.join(artifacts_dir, "fraud_classifier.joblib")
        iso_path = os.path.join(artifacts_dir, "isolation_forest.joblib")
        schema_path = os.path.join(artifacts_dir, "feature_schema.json")

        classifier = joblib.load(clf_path)
        iso_forest = joblib.load(iso_path) if os.path.isfile(iso_path) else None

        import json
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)
        feature_cols = schema_data.get("features", [])
        validate_feature_columns(feature_cols)

        meta_path = os.path.join(artifacts_dir, "model_metadata.json")
        version = "paysim-v1"
        is_bal = False
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                version = meta.get("model_version", "paysim-v1")
                is_bal = meta.get("is_balance_derived_active", False)

        _model_cache["classifier"] = classifier
        _model_cache["iso_forest"] = iso_forest
        _model_cache["feature_cols"] = feature_cols
        _model_cache["version"] = version
        _model_cache["is_balance_active"] = is_bal
        _model_cache["loaded"] = True

        metrics_registry.set_model_status("LOADED", version=version)
        logger.info(f"Loaded PaySim scoring models ({version}, {len(feature_cols)} features).")
        return classifier, iso_forest, feature_cols, version

    except Exception as e:
        logger.error(f"Failed to load PaySim model artifacts: {e}")
        metrics_registry.set_model_status("FAILED")
        return None, None, None, "v1-error"

@router.post("", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
def score_transaction(
    tx_in: ScoreRequest,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """
    Dedicated transaction scoring endpoint.
    Accepts both native FraudShield transactions and PaySim synthetic transactions.
    """
    t0 = time.perf_counter()

    # Determine tenant organization
    org_id = "org_shield_bank" # Default tenant context

    # 1. Normalize input attributes
    tx_id = tx_in.transaction_id or f"tx_{uuid.uuid4().hex[:8]}"
    amount = float(tx_in.amount)
    orig_id = tx_in.nameOrig or tx_in.customer_id or "C_ANON"
    dest_id = tx_in.nameDest or tx_in.merchant_id or "M_ANON"
    tx_type = tx_in.type or tx_in.transaction_type or "PAYMENT"
    step = tx_in.step or 1

    payload_dict = tx_in.model_dump()
    payload_dict["nameOrig"] = orig_id
    payload_dict["nameDest"] = dest_id
    payload_dict["type"] = tx_type
    payload_dict["step"] = step

    active_source = "paysim_synthetic" if (tx_in.step is not None or tx_in.nameOrig is not None) else "native"

    # 2. Check for ML model availability
    classifier, iso_forest, feature_cols, model_version = _get_active_models()
    is_degraded = False

    if classifier is not None and feature_cols:
        try:
            # Extract features causal to this transaction
            with_balance = _model_cache.get("is_balance_active", False)
            features = online_feature_store.extract_online_features(payload_dict, with_balance=with_balance)

            # Construct DataFrame with exact column ordering
            input_df = pd.DataFrame([[features.get(c, 0.0) for c in feature_cols]], columns=feature_cols)

            # Supervised fraud probability
            proba = float(classifier.predict_proba(input_df)[0, 1])

            # Anomaly detector score
            if iso_forest is not None:
                raw_anomaly = float(iso_forest.decision_function(input_df)[0])
                anomaly_score = float(np.clip(1.0 - (1.0 / (1.0 + np.exp(-5.0 * raw_anomaly))), 0.0, 1.0))
            else:
                anomaly_score = round(float(np.clip(proba * 0.8, 0.0, 1.0)), 4)

            # Cost-based decision
            decision, risk_score, reasons = decision_engine.evaluate_decision(
                fraud_probability=proba,
                amount=amount,
                features=features,
                authorized_block_rule=tx_in.authorized_block_rule
            )

            # Commit transaction to online state store strictly AFTER scoring
            online_feature_store.commit_transaction(payload_dict)

        except Exception as e:
            logger.error(f"Inference exception during scoring: {e}. Falling back to deterministic rules.")
            is_degraded = True
            fallback_features = online_feature_store.extract_online_features(payload_dict, with_balance=False)
            proba, anomaly_score, risk_score, decision, reasons = evaluate_deterministic_fallback(
                amount=amount,
                features=fallback_features,
                authorized_block_rule=tx_in.authorized_block_rule
            )
    else:
        is_degraded = True
        fallback_features = online_feature_store.extract_online_features(payload_dict, with_balance=False)
        proba, anomaly_score, risk_score, decision, reasons = evaluate_deterministic_fallback(
            amount=amount,
            features=fallback_features,
            authorized_block_rule=tx_in.authorized_block_rule
        )

    latency_ms = round(float((time.perf_counter() - t0) * 1000.0), 2)

    # Record metrics
    metrics_registry.record_score(
        decision=decision.value,
        latency_ms=latency_ms,
        degraded=is_degraded,
        model_ver=model_version,
        data_source=active_source
    )

    # 3. Publish alert & broadcast event for high-risk decisions
    if decision in [Decision.HOLD_FOR_REVIEW, Decision.STEP_UP, Decision.BLOCK]:
        event_payload = {
            "transaction_id": tx_id,
            "customer_id": orig_id,
            "merchant_id": dest_id,
            "amount": amount,
            "decision": decision.value,
            "risk_score": risk_score,
            "fraud_probability": proba,
            "latency_ms": latency_ms,
            "reasons": reasons,
            "degraded": is_degraded,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        publish_event("TRANSACTION_SCORED", event_payload)

        # Trigger async WebSocket broadcast
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(
                ws_manager.broadcast_to_organization(
                    org_id,
                    {"type": "TRANSACTION_SCORED", "data": event_payload}
                )
            )
        except Exception:
            pass

    return ScoreResponse(
        transaction_id=tx_id,
        fraud_probability=round(proba, 4),
        anomaly_score=round(anomaly_score, 4),
        risk_score=risk_score,
        decision=decision.value,
        reasons=[ReasonItem(code=r["code"], message=r["message"]) for r in reasons],
        latency_ms=latency_ms,
        model_version=model_version,
        active_data_source=active_source,
        degraded=is_degraded
    )
