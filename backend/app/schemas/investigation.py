from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.investigation import InvestigationStatus, InvestigationDecision


class InvestigationCreate(BaseModel):
    alert_id: str = Field(..., description="Alert ID to investigate")


class InvestigationNoteCreate(BaseModel):
    note_text: str = Field(..., min_length=1, max_length=5000, description="Analyst note text")


class InvestigationDecisionUpdate(BaseModel):
    decision: InvestigationDecision
    decision_reason: str = Field(..., min_length=5, max_length=2000, description="Mandatory decision reason")
    version: int = Field(..., description="Optimistic concurrency locking version")


class InvestigationEscalateRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000, description="Reason for escalation")
    version: int = Field(..., description="Optimistic concurrency locking version")


class InvestigationNoteResponse(BaseModel):
    id: str
    investigation_id: str
    author_id: str
    note_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationResponse(BaseModel):
    id: str
    organization_id: str
    alert_id: str
    transaction_id: str
    assigned_analyst_id: Optional[str] = None
    status: InvestigationStatus
    decision: Optional[InvestigationDecision] = None
    decision_reason: Optional[str] = None
    version: int
    forensic_snapshot: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: List[InvestigationNoteResponse] = []

    model_config = ConfigDict(from_attributes=True)
