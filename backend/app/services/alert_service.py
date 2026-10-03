import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertStatus
from app.models.transaction import Transaction
from app.models.risk import RiskScore, RiskLevel
from app.realtime.event_processor import publish_event
from app.realtime.websocket_manager import ws_manager
from app.core.config import settings
from app.core.logging import logger

def evaluate_and_create_alert(
    db: Session,
    transaction: Transaction,
    risk_score_obj: RiskScore,
    top_factors: List[Dict[str, Any]]
) -> Optional[Alert]:
    
    if risk_score_obj.risk_score < settings.RISK_THRESHOLD_MEDIUM:
        return None

    # Idempotency check: verify no alert exists for this transaction
    existing_alert = db.query(Alert).filter(Alert.transaction_id == transaction.id).first()
    if existing_alert:
        return existing_alert

    severity = risk_score_obj.risk_level
    title = f"High Risk Flagged: {transaction.currency} {transaction.amount:,.2f}" if severity in [RiskLevel.HIGH, RiskLevel.CRITICAL] else f"Medium Risk Transaction Flagged"
    
    factors_summary = [f.get("explanation", f.get("feature_name")) for f in top_factors] if top_factors else ["Elevated risk score detected"]
    description = f"Transaction {transaction.transaction_id} reached risk score {risk_score_obj.risk_score}/100 ({severity.value}). Factors: {', '.join(factors_summary[:3])}"

    alert = Alert(
        organization_id=transaction.organization_id,
        transaction_id=transaction.id,
        customer_id=transaction.customer_id,
        amount=transaction.amount,
        risk_score=risk_score_obj.risk_score,
        severity=severity,
        title=title,
        description=description,
        status=AlertStatus.NEW,
        primary_risk_factors=top_factors
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Redis event publication
    event_payload = {
        "alert_id": alert.id,
        "transaction_id": transaction.transaction_id,
        "customer_id": transaction.customer_id,
        "amount": transaction.amount,
        "risk_score": risk_score_obj.risk_score,
        "severity": severity.value,
        "title": title,
        "status": alert.status.value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    publish_event("ALERT_CREATED", event_payload)

    # Trigger async WebSocket broadcast if loop is running
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            ws_manager.broadcast_to_organization(
                transaction.organization_id,
                {"type": "ALERT_CREATED", "data": event_payload}
            )
        )
    except RuntimeError:
        # No async event loop currently running in worker thread
        pass
    except Exception as e:
        logger.debug(f"Async loop dispatch skipped: {e}")

    return alert
