from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.audit import AuditLog

router = APIRouter()

class AuditLogResponse(BaseModel):
    id: str
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    GET /api/v1/audit-logs
    Returns immutable audit log records for administrative review.
    """
    query = db.query(AuditLog).filter(AuditLog.organization_id == current_user.organization_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs
