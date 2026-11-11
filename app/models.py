from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ConversationRequest(BaseModel):
    challenge_behavior: str = Field(min_length=3, max_length=5000)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=30)


class ConversationResponse(BaseModel):
    assistant_message: str
    suggested_intervention: str


class CaseCreateRequest(BaseModel):
    challenge_behavior: str = Field(min_length=3, max_length=5000)
    intervention: str = Field(min_length=3, max_length=10000)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=30)


class CaseCreateResponse(BaseModel):
    id: str
    created_at: datetime
