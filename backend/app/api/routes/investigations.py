from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.core.database import get_db
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
    InvestigationNoteCreate,
    InvestigationNoteResponse,
    InvestigationDecisionUpdate,
    InvestigationEscalateRequest,
)
from app.services.investigation_service import (
    get_or_create_investigation_for_alert,
    create_investigation_from_alert,
    claim_investigation_concurrency_safe,
    add_investigation_note,
    resolve_investigation_with_decision,
    escalate_investigation,
    get_investigation_by_alert,
)
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.investigation import Investigation, InvestigationStatus

router = APIRouter()


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_or_get_investigation(
    inv_in: InvestigationCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    """
    Idempotent: returns an existing investigation for the alert if one exists (200),
    or creates one and returns it (201).
    Returns the case_id for navigation to /investigations/{case_id}.
    """
    inv, created = get_or_create_investigation_for_alert(db=db, alert_id=inv_in.alert_id, user=current_user)
    if not created:
        response.status_code = status.HTTP_200_OK
    return inv


@router.get("", response_model=List[InvestigationResponse])
def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[InvestigationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(Investigation)
        .options(joinedload(Investigation.alert), joinedload(Investigation.notes))
        .filter(Investigation.organization_id == current_user.organization_id)
    )
    if status:
        query = query.filter(Investigation.status == status)

    return query.order_by(desc(Investigation.created_at)).offset(skip).limit(limit).all()


@router.get("/by-alert/{alert_id}", response_model=Optional[InvestigationResponse])
def get_investigation_for_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Look up existing investigation for a given alert_id.
    Returns null (204) if none exists. Used by frontend before navigation.
    """
    inv = get_investigation_by_alert(db=db, alert_id=alert_id, org_id=current_user.organization_id)
    if not inv:
        return None
    return inv


@router.get("/{id}", response_model=InvestigationResponse)
def get_investigation(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = (
        db.query(Investigation)
        .options(joinedload(Investigation.alert), joinedload(Investigation.notes))
        .filter(
            Investigation.id == id,
            Investigation.organization_id == current_user.organization_id
        )
        .first()
    )

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )
    return inv


@router.post("/{id}/claim", response_model=InvestigationResponse)
def claim_investigation(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    return claim_investigation_concurrency_safe(db=db, investigation_id=id, user=current_user)


@router.post("/{id}/escalate", response_model=InvestigationResponse)
def escalate(
    id: str,
    body: InvestigationEscalateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    """Transition OPEN or IN_REVIEW → ESCALATED with optimistic locking."""
    return escalate_investigation(
        db=db,
        investigation_id=id,
        reason=body.reason,
        expected_version=body.version,
        user=current_user
    )


@router.post("/{id}/notes", response_model=InvestigationNoteResponse)
def add_note(
    id: str,
    note_in: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    return add_investigation_note(db=db, investigation_id=id, note_text=note_in.note_text, user=current_user)


@router.post("/{id}/resolve", response_model=InvestigationResponse)
def resolve_investigation(
    id: str,
    decision_in: InvestigationDecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    return resolve_investigation_with_decision(
        db=db,
        investigation_id=id,
        decision=decision_in.decision,
        reason=decision_in.decision_reason,
        expected_version=decision_in.version,
        user=current_user
    )
