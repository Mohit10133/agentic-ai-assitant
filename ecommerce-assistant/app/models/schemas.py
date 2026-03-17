from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    domain: str = Field(..., description="auto, ecommerce, travel, or healthcare")
    user_id: str = Field(..., description="Demo user id")
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    intent: Optional[str] = None
