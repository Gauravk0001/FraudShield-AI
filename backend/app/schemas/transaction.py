from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.transaction import TransactionStatus
from app.models.risk import RiskLevel

class TransactionCreate(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID from upstream system")
    customer_id: str = Field(..., description="Customer ID")
    merchant_id: str = Field(..., description="Merchant ID")
    device_id: str = Field(..., description="Device ID or fingerprint")
    amount: float = Field(..., gt=0, description="Transaction amount, must be greater than 0")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    transaction_type: str = Field(..., description="CARD_PRESENT, CARD_NOT_PRESENT, WIRE_TRANSFER, etc.")
    location: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[datetime] = None

class RiskExplanationResponse(BaseModel):
    top_factors: List[Dict[str, Any]]
    shap_values: Dict[str, float]

class RiskScoreResponse(BaseModel):
    fraud_probability: float
    anomaly_score: float
    risk_score: float
    risk_level: RiskLevel
    model_version: str
    behavioral_flags: Dict[str, Any]
    explanation: Optional[RiskExplanationResponse] = None

class TransactionResponse(BaseModel):
    id: str
    organization_id: str
    transaction_id: str
    customer_id: str
    merchant_id: str
    device_id: str
    amount: float
    currency: str
    transaction_type: str
    location: Optional[str]
    timestamp: datetime
    status: TransactionStatus
    created_at: datetime
    risk_score: Optional[RiskScoreResponse] = None

    model_config = ConfigDict(from_attributes=True)
