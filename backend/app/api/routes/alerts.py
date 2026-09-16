from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.schemas.alert import AlertResponse, AlertUpdate
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.alert import Alert, AlertStatus
from app.models.risk import RiskLevel
from app.services.audit_service import log_audit_event
from app.realtime.event_processor import publish_event

router = APIRouter()

@router.get("", response_model=List[AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[AlertStatus] = None,
    severity: Optional[RiskLevel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.organization_id == current_user.organization_id)

    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)

    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    return alerts

@router.get("/{id}", response_model=AlertResponse)
def get_alert(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(
        Alert.id == id,
        Alert.organization_id == current_user.organization_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert

@router.patch("/{id}", response_model=AlertResponse)
def update_alert(
    id: str,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    alert = db.query(Alert).filter(
        Alert.id == id,
        Alert.organization_id == current_user.organization_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    old_status = alert.status.value
    if alert_update.status is not None:
        alert.status = alert_update.status
    if alert_update.assigned_to_user_id is not None:
        alert.assigned_to_user_id = alert_update.assigned_to_user_id

    db.commit()
    db.refresh(alert)

    log_audit_event(
        db=db,
        action="ALERT_UPDATED",
        entity_type="ALERT",
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_id=alert.id,
        details={"old_status": old_status, "new_status": alert.status.value}
    )

    publish_event("ALERT_UPDATED", {
        "alert_id": alert.id,
        "new_status": alert.status.value,
        "assigned_to": alert.assigned_to_user_id
    })

    return alert
