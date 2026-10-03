from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.investigation import Investigation, InvestigationNote, InvestigationStatus, InvestigationDecision
from app.models.alert import Alert, AlertStatus
from app.models.user import User
from app.services.audit_service import log_audit_event
from app.core.logging import logger


def _load_investigation_with_relations(db: Session, investigation_id: str, org_id: str) -> Investigation:
    """Eagerly load investigation with alert and notes in a single query."""
    inv = (
        db.query(Investigation)
        .options(joinedload(Investigation.alert), joinedload(Investigation.notes))
        .filter(Investigation.id == investigation_id, Investigation.organization_id == org_id)
        .first()
    )
    return inv


def get_or_create_investigation_for_alert(
    db: Session,
    alert_id: str,
    user: User,
) -> tuple[Investigation, bool]:
    """
    Idempotent: returns (investigation, created).
    If an investigation already exists for this alert, returns it unchanged.
    Never creates duplicates.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.organization_id == user.organization_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    existing_inv = (
        db.query(Investigation)
        .options(joinedload(Investigation.alert), joinedload(Investigation.notes))
        .filter(Investigation.alert_id == alert_id)
        .first()
    )
    if existing_inv:
        return existing_inv, False

    inv = Investigation(
        organization_id=user.organization_id,
        alert_id=alert.id,
        transaction_id=alert.transaction_id,
        assigned_analyst_id=user.id,
        status=InvestigationStatus.OPEN,
        version=1,
        forensic_snapshot=_build_forensic_snapshot(alert),
    )
    db.add(inv)
    alert.status = AlertStatus.INVESTIGATING
    db.commit()
    db.refresh(inv)

    log_audit_event(
        db=db,
        action="INVESTIGATION_CREATED",
        entity_type="INVESTIGATION",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=inv.id,
        details={"alert_id": alert.id, "transaction_id": alert.transaction_id}
    )

    return inv, True


def _build_forensic_snapshot(alert: Alert) -> dict:
    """Build forensic snapshot dict from alert data for persistent display."""
    try:
        risk_factors = alert.primary_risk_factors or []
        return {
            "risk_score": alert.risk_score,
            "severity": alert.severity.value if alert.severity else None,
            "amount": alert.amount,
            "reason_codes": risk_factors,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.warning(f"Failed to build forensic snapshot: {e}")
        return {}


def create_investigation_from_alert(
    db: Session,
    alert_id: str,
    user: User
) -> Investigation:
    """Backwards-compatible wrapper — returns the investigation (existing or new)."""
    inv, _ = get_or_create_investigation_for_alert(db=db, alert_id=alert_id, user=user)
    return inv


def get_investigation_by_alert(db: Session, alert_id: str, org_id: str) -> Optional[Investigation]:
    """Look up existing investigation for a given alert_id."""
    return (
        db.query(Investigation)
        .options(joinedload(Investigation.alert), joinedload(Investigation.notes))
        .filter(Investigation.alert_id == alert_id, Investigation.organization_id == org_id)
        .first()
    )


def claim_investigation_concurrency_safe(
    db: Session,
    investigation_id: str,
    user: User
) -> Investigation:
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == user.organization_id
    ).with_for_update().first()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )

    if inv.status == InvestigationStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot claim a resolved investigation"
        )

    if inv.assigned_analyst_id and inv.assigned_analyst_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Investigation has already been claimed by another analyst"
        )

    inv.assigned_analyst_id = user.id
    inv.status = InvestigationStatus.IN_REVIEW
    inv.version += 1
    db.commit()
    db.refresh(inv)

    log_audit_event(
        db=db,
        action="INVESTIGATION_CLAIMED",
        entity_type="INVESTIGATION",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=inv.id
    )

    return inv


def escalate_investigation(
    db: Session,
    investigation_id: str,
    reason: str,
    expected_version: int,
    user: User
) -> Investigation:
    """Transition OPEN or IN_REVIEW → ESCALATED with optimistic concurrency."""
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == user.organization_id
    ).with_for_update().first()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    if inv.status == InvestigationStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot escalate a resolved investigation")

    if inv.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Investigation was updated by another user. Please reload and retry."
        )

    inv.status = InvestigationStatus.ESCALATED
    inv.version += 1
    db.commit()
    db.refresh(inv)

    log_audit_event(
        db=db,
        action="INVESTIGATION_ESCALATED",
        entity_type="INVESTIGATION",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=inv.id,
        details={"reason": reason}
    )

    return inv


def add_investigation_note(
    db: Session,
    investigation_id: str,
    note_text: str,
    user: User
) -> InvestigationNote:
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == user.organization_id
    ).first()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    if inv.status == InvestigationStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add notes to a resolved investigation")

    note = InvestigationNote(
        investigation_id=inv.id,
        author_id=user.id,
        note_text=note_text.strip()
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    log_audit_event(
        db=db,
        action="INVESTIGATION_NOTE_ADDED",
        entity_type="INVESTIGATION",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=inv.id,
        details={"note_id": note.id, "note_length": len(note.note_text)}
    )

    return note


def resolve_investigation_with_decision(
    db: Session,
    investigation_id: str,
    decision: InvestigationDecision,
    reason: str,
    expected_version: int,
    user: User
) -> Investigation:
    inv = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == user.organization_id
    ).first()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    if inv.status == InvestigationStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Investigation is already resolved")

    # Optimistic concurrency check
    if inv.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Investigation record was updated by another user. Please reload and retry."
        )

    inv.decision = decision
    inv.decision_reason = reason
    inv.status = InvestigationStatus.RESOLVED
    inv.resolved_at = datetime.now(timezone.utc)
    inv.version += 1

    # Update associated Alert status
    if inv.alert:
        inv.alert.status = AlertStatus.RESOLVED

    db.commit()
    db.refresh(inv)

    log_audit_event(
        db=db,
        action="INVESTIGATION_RESOLVED",
        entity_type="INVESTIGATION",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=inv.id,
        details={"decision": decision.value, "reason": reason}
    )

    return inv
