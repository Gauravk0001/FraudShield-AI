from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionFeature, TransactionStatus
from app.models.risk import RiskScore, RiskExplanation, RiskLevel
from app.models.user import User
from app.ml.feature_engineering import extract_features
from app.ml.fraud_classifier import predict_fraud_probability
from app.ml.anomaly_detector import predict_anomaly_score
from app.ml.explainability import generate_shap_explanation
from app.services.risk_service import calculate_risk_score
from app.core.logging import logger

def process_transaction_pipeline(
    db: Session,
    tx_data: Dict[str, Any],
    organization_id: str
) -> Tuple[Transaction, bool]:
    tx_id_str = str(tx_data["transaction_id"])

    # 1. Idempotency Check
    existing_tx = db.query(Transaction).filter(
        Transaction.organization_id == organization_id,
        Transaction.transaction_id == tx_id_str
    ).first()

    if existing_tx:
        logger.info(f"Duplicate transaction ingested (idempotent return): {tx_id_str}")
        return existing_tx, True # (transaction, is_duplicate)

    tx_timestamp = tx_data.get("timestamp") or datetime.now(timezone.utc)

    # 2. Persist initial transaction entity
    new_tx = Transaction(
        organization_id=organization_id,
        transaction_id=tx_id_str,
        customer_id=str(tx_data["customer_id"]),
        merchant_id=str(tx_data["merchant_id"]),
        device_id=str(tx_data["device_id"]),
        amount=float(tx_data["amount"]),
        currency=str(tx_data.get("currency", "USD")),
        transaction_type=str(tx_data["transaction_type"]),
        location=tx_data.get("location"),
        ip_address=tx_data.get("ip_address"),
        timestamp=tx_timestamp,
        status=TransactionStatus.PENDING
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # 3. Extract features & save
    features = extract_features(db, tx_data)
    tx_feature_obj = TransactionFeature(
        transaction_id=new_tx.id,
        features_json=features
    )
    db.add(tx_feature_obj)

    # 4. Supervised Model inference
    fraud_prob, model_ver = predict_fraud_probability(features)

    # 5. Isolation Forest Anomaly Detection
    anomaly_score, iso_ver = predict_anomaly_score(features)

    # 6. Risk Scoring Engine
    risk_score, risk_level, behavioral_flags = calculate_risk_score(fraud_prob, anomaly_score, features)

    # 7. SHAP Explainability Engine
    shap_vals, top_factors = generate_shap_explanation(features)

    # 8. Persist Risk Score & Explanation
    risk_obj = RiskScore(
        transaction_id=new_tx.id,
        organization_id=organization_id,
        fraud_probability=fraud_prob,
        anomaly_score=anomaly_score,
        risk_score=risk_score,
        risk_level=risk_level,
        model_version=model_ver,
        behavioral_flags=behavioral_flags
    )
    db.add(risk_obj)
    db.commit()
    db.refresh(risk_obj)

    explanation_obj = RiskExplanation(
        risk_score_id=risk_obj.id,
        transaction_id=new_tx.id,
        shap_values=shap_vals,
        top_factors={"factors": top_factors}
    )
    db.add(explanation_obj)

    # 9. Trigger automatic Alert evaluation
    from app.services.alert_service import evaluate_and_create_alert
    evaluate_and_create_alert(
        db=db,
        transaction=new_tx,
        risk_score_obj=risk_obj,
        top_factors=top_factors
    )

    # Update Transaction status
    new_tx.status = TransactionStatus.FLAGGED if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else TransactionStatus.PROCESSED
    db.commit()
    db.refresh(new_tx)

    return new_tx, False
