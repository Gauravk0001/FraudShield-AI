import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.copilot import CopilotChatRequest, CopilotChatResponse
from app.services.copilot_service import extract_evidence_context, generate_copilot_response, stream_copilot_chunks

router = APIRouter()

@router.post("/chat", response_model=CopilotChatResponse)
def copilot_chat(
    payload: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    """
    POST /api/v1/copilot/chat
    AI Investigation Assistant endpoint. Receives questions and context parameters,
    sanitizes evidence context, and returns question-aware, evidence-backed analysis.
    """
    evidence = extract_evidence_context(
        db=db,
        organization_id=current_user.organization_id,
        investigation_id=payload.investigation_id,
        transaction_id=payload.transaction_id,
        message=payload.message
    )

    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history] if payload.history else None
    result = generate_copilot_response(
        message=payload.message,
        evidence=evidence,
        history=history_dicts
    )

    return CopilotChatResponse(
        response=result["response"],
        evidence_summary=evidence,
        disclaimer="AI-generated assistance. The human analyst remains responsible for the final investigation decision.",
        suggested_followups=result.get("suggested_followups", [])
    )

@router.post("/chat/stream")
def copilot_chat_stream(
    payload: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FRAUD_ANALYST, UserRole.RISK_MANAGER]))
):
    """
    POST /api/v1/copilot/chat/stream
    Streaming endpoint returning Server-Sent Events (SSE) for instant time-to-first-token.
    """
    evidence = extract_evidence_context(
        db=db,
        organization_id=current_user.organization_id,
        investigation_id=payload.investigation_id,
        transaction_id=payload.transaction_id,
        message=payload.message
    )

    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history] if payload.history else None

    def event_generator():
        # First event: evidence metadata
        yield f"data: {json.dumps({'type': 'metadata', 'evidence_summary': evidence})}\n\n"

        # Streamed token chunks
        for chunk in stream_copilot_chunks(payload.message, evidence, history_dicts):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
