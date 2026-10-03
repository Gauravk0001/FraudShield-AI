from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.core.logging import logger

def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None
) -> AuditLog:
    # Filter out sensitive fields like passwords/tokens if accidentally included
    sanitized_details = dict(details or {})
    for sensitive_key in ["password", "token", "access_token", "refresh_token", "secret", "gemini_key"]:
        if sensitive_key in sanitized_details:
            sanitized_details[sensitive_key] = "[REDACTED]"

    audit_entry = AuditLog(
        action=action,
        entity_type=entity_type,
        organization_id=organization_id,
        user_id=user_id,
        entity_id=entity_id,
        details=sanitized_details,
        ip_address=ip_address,
        request_id=request_id
    )
    db.add(audit_entry)
    try:
        db.commit()
        db.refresh(audit_entry)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist audit log: {e}")
    return audit_entry
