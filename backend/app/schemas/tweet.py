from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserPublic

class TweetBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class TweetCreate(TweetBase):
    reply_to_id: Optional[int] = None  # NUEVO: ID del tweet al que responde
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Content cannot be empty')
        if len(v) > 280:
            raise ValueError('Content cannot be longer than 280 characters')
        return v

class TweetUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None

class TweetInDB(TweetBase):
    id: int
    author_id: int
    reply_to_id: Optional[int] = None  # NUEVO
    created_at: datetime
    
    class Config:
        from_attributes = True

class Tweet(TweetInDB):
    author: UserPublic
    likes_count: int = 0
    retweets_count: int = 0
    replies_count: int = 0  # NUEVO
    is_liked_by_user: Optional[bool] = False
    is_retweeted_by_user: Optional[bool] = False
    
    class Config:
        from_attributes = True

# NUEVO: Para mostrar el tweet original al que se responde
class TweetWithReplyTo(Tweet):
    reply_to: Optional['TweetSimple'] = None  # Tweet al que responde

# NUEVO: Versión simplificada de tweet para evitar recursión infinita
class TweetSimple(BaseModel):
    id: int
    content: str
    image_url: Optional[str] = None
    author_id: int
    author: UserPublic
    created_at: datetime
    
    class Config:
        from_attributes = True

# NUEVO: Para mostrar threads completos
class TweetWithThread(TweetWithReplyTo):
    replies: List['TweetWithReplyTo'] = []  # Respuestas a este tweet

# Resolver forward references
TweetWithReplyTo.model_rebuild()
TweetWithThread.model_rebuild()