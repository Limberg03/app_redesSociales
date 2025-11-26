from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Message Schemas ---
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    selected_networks: Optional[List[str]] = []

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Conversation Schemas ---
class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    # messages: List[MessageResponse] = [] # Opcional: incluir mensajes en la lista de conversaciones

    class Config:
        orm_mode = True

class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse]
