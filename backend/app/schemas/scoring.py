"""
FraudShield AI — Scoring API Request & Response Schemas

Defines Pydantic models with rich OpenAPI documentation and schema examples
for the dedicated POST /api/v1/score endpoint.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReasonItem(BaseModel):
    code: str = Field(..., description="Machine-readable reason code identifier", examples=["HIGH_AMOUNT_DEVIATION"])
    message: str = Field(..., description="Human-readable analyst explanation", examples=["The amount is substantially higher than this account's historical average."])

class ScoreRequest(BaseModel):
    # Common / Identifier
    transaction_id: Optional[str] = Field(None, description="Optional client transaction ID", examples=["tx_123"])
    amount: float = Field(..., gt=0.0, description="Transaction monetary amount", examples=[18500.00])
    currency: str = Field("USD", description="ISO currency code", examples=["USD"])

    # Native FraudShield format
    customer_id: Optional[str] = Field(None, description="Origin customer identifier", examples=["cust_101"])
    merchant_id: Optional[str] = Field(None, description="Destination merchant/account identifier", examples=["merch_wire_holdings"])
    device_id: Optional[str] = Field(None, description="Client hardware device identifier", examples=["dev_trusted_session"])
    transaction_type: Optional[str] = Field(None, description="Transaction transfer type", examples=["WIRE_TRANSFER"])
    location: Optional[str] = Field(None, description="Geo-location string", examples=["Singapore, SG"])
    timestamp: Optional[datetime] = Field(None, description="Transaction clock timestamp")

    # PaySim format
    step: Optional[int] = Field(None, description="PaySim simulated hour step (1 to 744)", examples=[145])
    type: Optional[str] = Field(None, description="PaySim transfer type (TRANSFER, CASH_OUT, PAYMENT, etc.)", examples=["TRANSFER"])
    nameOrig: Optional[str] = Field(None, description="PaySim origin account ID", examples=["C1234567890"])
    nameDest: Optional[str] = Field(None, description="PaySim destination account ID", examples=["M9876543210"])
    oldbalanceOrg: Optional[float] = Field(None, description="PaySim origin initial balance", examples=[18500.00])
    newbalanceOrig: Optional[float] = Field(None, description="PaySim origin post-transaction balance", examples=[0.00])
    oldbalanceDest: Optional[float] = Field(None, description="PaySim destination initial balance", examples=[0.00])
    newbalanceDest: Optional[float] = Field(None, description="PaySim destination post-transaction balance", examples=[18500.00])

    # Policy Override
    authorized_block_rule: bool = Field(False, description="Explicitly authorized policy rule allowing permanent blocking", examples=[False])

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "tx_123",
                "customer_id": "cust_101",
                "merchant_id": "merch_demo_holdings",
                "amount": 18500.00,
                "transaction_type": "WIRE_TRANSFER",
                "step": 145,
                "nameOrig": "C1234567890",
                "nameDest": "C9876543210",
                "oldbalanceOrg": 18500.00,
                "newbalanceOrig": 0.00
            }
        }
    }

class ScoreResponse(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier", examples=["tx_123"])
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated fraud probability", examples=[0.92])
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Unsupervised anomaly detector score", examples=[0.71])
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite risk score from 0 to 100", examples=[87.0])
    decision: str = Field(..., description="Advisory decision: APPROVE, STEP_UP, HOLD_FOR_REVIEW, or BLOCK", examples=["HOLD_FOR_REVIEW"])
    reasons: List[ReasonItem] = Field(..., description="Top three explainable reason codes assisting analyst review")
    latency_ms: float = Field(..., description="Inference and feature extraction execution time in milliseconds", examples=[14.2])
    model_version: str = Field(..., description="Identifier of the active ML model", examples=["paysim-v1"])
    active_data_source: str = Field(..., description="Active dataset source (paysim_synthetic or native)", examples=["paysim_synthetic"])
    degraded: bool = Field(..., description="True if fallback heuristics were used due to model failure", examples=[False])

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "tx_123",
                "fraud_probability": 0.92,
                "anomaly_score": 0.71,
                "risk_score": 87.0,
                "decision": "HOLD_FOR_REVIEW",
                "reasons": [
                    {
                        "code": "HIGH_AMOUNT_DEVIATION",
                        "message": "The amount is substantially higher than this account's historical average."
                    },
                    {
                        "code": "NEW_DESTINATION",
                        "message": "This is the first observed transfer to this destination."
                    },
                    {
                        "code": "ACCOUNT_EMPTIED",
                        "message": "The transaction nearly emptied the origin account."
                    }
                ],
                "latency_ms": 14.2,
                "model_version": "paysim-v1",
                "active_data_source": "paysim_synthetic",
                "degraded": False
            }
        }
    }
