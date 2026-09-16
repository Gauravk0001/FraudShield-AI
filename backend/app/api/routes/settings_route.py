from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import require_role
from app.models.user import User, UserRole, Organization
from app.services.audit_service import log_audit_event

router = APIRouter()

class SystemSettingsResponse(BaseModel):
    organization_id: str
    organization_name: str
    environment: str
    project_name: str
    version: str
    risk_threshold_medium: float
    risk_threshold_high: float
    risk_threshold_critical: float
    xgboost_weight: float
    isolation_forest_weight: float
    rules_weight: float
    auto_create_alerts: bool
    session_expire_minutes: int
    gemini_copilot_enabled: bool
    gemini_api_key_configured: bool

    model_config = ConfigDict(from_attributes=True)

class SystemSettingsUpdate(BaseModel):
    risk_threshold_medium: Optional[float] = Field(None, ge=0.0, le=100.0)
    risk_threshold_high: Optional[float] = Field(None, ge=0.0, le=100.0)
    auto_create_alerts: Optional[bool] = None

@router.get("", response_model=SystemSettingsResponse)
def get_system_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    GET /api/v1/settings
    Returns platform settings and active operational configuration for administrative management.
    """
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    org_name = org.name if org else "Default Organization"

    return SystemSettingsResponse(
        organization_id=current_user.organization_id,
        organization_name=org_name,
        environment=settings.ENVIRONMENT,
        project_name=settings.PROJECT_NAME,
        version="1.0.0 Enterprise",
        risk_threshold_medium=settings.RISK_THRESHOLD_MEDIUM,
        risk_threshold_high=settings.RISK_THRESHOLD_HIGH,
        risk_threshold_critical=90.0,
        xgboost_weight=0.45,
        isolation_forest_weight=0.20,
        rules_weight=0.35,
        auto_create_alerts=True,
        session_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        gemini_copilot_enabled=bool(settings.GEMINI_API_KEY),
        gemini_api_key_configured=bool(settings.GEMINI_API_KEY)
    )

@router.patch("", response_model=SystemSettingsResponse)
def update_system_settings(
    settings_in: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    PATCH /api/v1/settings
    Allows Admins to adjust risk engine sensitivity thresholds and platform parameters.
    """
    changed_fields = {}
    
    if settings_in.risk_threshold_medium is not None:
        if settings_in.risk_threshold_high is not None and settings_in.risk_threshold_medium >= settings_in.risk_threshold_high:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medium risk threshold must be strictly less than High risk threshold"
            )
        elif settings_in.risk_threshold_medium >= settings.RISK_THRESHOLD_HIGH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medium risk threshold must be strictly less than current High threshold ({settings.RISK_THRESHOLD_HIGH})"
            )
        settings.RISK_THRESHOLD_MEDIUM = settings_in.risk_threshold_medium
        changed_fields["risk_threshold_medium"] = settings_in.risk_threshold_medium

    if settings_in.risk_threshold_high is not None:
        if settings_in.risk_threshold_high <= settings.RISK_THRESHOLD_MEDIUM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"High risk threshold must be strictly greater than Medium threshold ({settings.RISK_THRESHOLD_MEDIUM})"
            )
        settings.RISK_THRESHOLD_HIGH = settings_in.risk_threshold_high
        changed_fields["risk_threshold_high"] = settings_in.risk_threshold_high

    log_audit_event(
        db=db,
        action="SYSTEM_SETTINGS_UPDATED",
        entity_type="SYSTEM",
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_id="global_settings",
        details=changed_fields
    )

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    org_name = org.name if org else "Default Organization"

    return SystemSettingsResponse(
        organization_id=current_user.organization_id,
        organization_name=org_name,
        environment=settings.ENVIRONMENT,
        project_name=settings.PROJECT_NAME,
        version="1.0.0 Enterprise",
        risk_threshold_medium=settings.RISK_THRESHOLD_MEDIUM,
        risk_threshold_high=settings.RISK_THRESHOLD_HIGH,
        risk_threshold_critical=90.0,
        xgboost_weight=0.45,
        isolation_forest_weight=0.20,
        rules_weight=0.35,
        auto_create_alerts=True,
        session_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        gemini_copilot_enabled=bool(settings.GEMINI_API_KEY),
        gemini_api_key_configured=bool(settings.GEMINI_API_KEY)
    )
