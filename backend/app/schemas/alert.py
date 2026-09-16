from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.alert import AlertStatus
from app.models.risk import RiskLevel

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to_user_id: Optional[str] = None

class AlertResponse(BaseModel):
    id: str
    organization_id: str
    transaction_id: str
    customer_id: str
    amount: float
    risk_score: float
    severity: RiskLevel
    title: str
    description: str
    status: AlertStatus
    assigned_to_user_id: Optional[str] = None
    primary_risk_factors: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
