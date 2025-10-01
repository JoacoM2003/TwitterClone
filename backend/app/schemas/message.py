from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserPublic

class MessageCreate(BaseModel):
    receiver_username: str
    content: str

class MessageInDB(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Message(MessageInDB):
    sender: UserPublic

class ConversationBase(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Conversation(ConversationBase):
    other_user: UserPublic
    last_message: Optional[Message] = None
    unread_count: int = 0