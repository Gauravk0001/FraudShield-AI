from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class CopilotChatRequest(BaseModel):
    investigation_id: Optional[str] = None
    transaction_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatMessage] = []

class CopilotChatResponse(BaseModel):
    response: str
    evidence_summary: Dict[str, Any]
    disclaimer: str = "AI-generated assistance. The human analyst remains responsible for the final decision."
    suggested_followups: List[str] = []
