from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse, RiskScoreResponse, RiskExplanationResponse
from app.services.transaction_service import process_transaction_pipeline
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.transaction import Transaction
from app.models.risk import RiskScore, RiskExplanation, RiskLevel

router = APIRouter()

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def ingest_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    try:
        tx, is_dup = process_transaction_pipeline(
            db=db,
            tx_data=tx_in.model_dump(),
            organization_id=current_user.organization_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transaction processing error: {str(e)}"
        )

    # Format response
    risk_score_resp = None
    if tx.risk_score:
        expl_resp = None
        if tx.risk_score.explanation:
            expl_resp = RiskExplanationResponse(
                top_factors=tx.risk_score.explanation.top_factors.get("factors", []),
                shap_values=tx.risk_score.explanation.shap_values
            )
        
        risk_score_resp = RiskScoreResponse(
            fraud_probability=tx.risk_score.fraud_probability,
            anomaly_score=tx.risk_score.anomaly_score,
            risk_score=tx.risk_score.risk_score,
            risk_level=tx.risk_score.risk_level,
            model_version=tx.risk_score.model_version,
            behavioral_flags=tx.risk_score.behavioral_flags,
            explanation=expl_resp
        )

    return TransactionResponse(
        id=tx.id,
        organization_id=tx.organization_id,
        transaction_id=tx.transaction_id,
        customer_id=tx.customer_id,
        merchant_id=tx.merchant_id,
        device_id=tx.device_id,
        amount=tx.amount,
        currency=tx.currency,
        transaction_type=tx.transaction_type,
        location=tx.location,
        timestamp=tx.timestamp,
        status=tx.status,
        created_at=tx.created_at,
        risk_score=risk_score_resp
    )

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    risk_level: Optional[RiskLevel] = None,
    customer_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.organization_id == current_user.organization_id)

    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if merchant_id:
        query = query.filter(Transaction.merchant_id == merchant_id)
    if risk_level:
        query = query.join(RiskScore).filter(RiskScore.risk_level == risk_level)

    transactions = query.order_by(desc(Transaction.timestamp)).offset(skip).limit(limit).all()

    response_list = []
    for tx in transactions:
        risk_score_resp = None
        if tx.risk_score:
            expl_resp = None
            if tx.risk_score.explanation:
                expl_resp = RiskExplanationResponse(
                    top_factors=tx.risk_score.explanation.top_factors.get("factors", []),
                    shap_values=tx.risk_score.explanation.shap_values
                )
            
            risk_score_resp = RiskScoreResponse(
                fraud_probability=tx.risk_score.fraud_probability,
                anomaly_score=tx.risk_score.anomaly_score,
                risk_score=tx.risk_score.risk_score,
                risk_level=tx.risk_score.risk_level,
                model_version=tx.risk_score.model_version,
                behavioral_flags=tx.risk_score.behavioral_flags,
                explanation=expl_resp
            )

        response_list.append(TransactionResponse(
            id=tx.id,
            organization_id=tx.organization_id,
            transaction_id=tx.transaction_id,
            customer_id=tx.customer_id,
            merchant_id=tx.merchant_id,
            device_id=tx.device_id,
            amount=tx.amount,
            currency=tx.currency,
            transaction_type=tx.transaction_type,
            location=tx.location,
            timestamp=tx.timestamp,
            status=tx.status,
            created_at=tx.created_at,
            risk_score=risk_score_resp
        ))

    return response_list

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(
        Transaction.id == id,
        Transaction.organization_id == current_user.organization_id
    ).first()

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    risk_score_resp = None
    if tx.risk_score:
        expl_resp = None
        if tx.risk_score.explanation:
            expl_resp = RiskExplanationResponse(
                top_factors=tx.risk_score.explanation.top_factors.get("factors", []),
                shap_values=tx.risk_score.explanation.shap_values
            )
        
        risk_score_resp = RiskScoreResponse(
            fraud_probability=tx.risk_score.fraud_probability,
            anomaly_score=tx.risk_score.anomaly_score,
            risk_score=tx.risk_score.risk_score,
            risk_level=tx.risk_score.risk_level,
            model_version=tx.risk_score.model_version,
            behavioral_flags=tx.risk_score.behavioral_flags,
            explanation=expl_resp
        )

    return TransactionResponse(
        id=tx.id,
        organization_id=tx.organization_id,
        transaction_id=tx.transaction_id,
        customer_id=tx.customer_id,
        merchant_id=tx.merchant_id,
        device_id=tx.device_id,
        amount=tx.amount,
        currency=tx.currency,
        transaction_type=tx.transaction_type,
        location=tx.location,
        timestamp=tx.timestamp,
        status=tx.status,
        created_at=tx.created_at,
        risk_score=risk_score_resp
    )
