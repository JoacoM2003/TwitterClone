from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserPublic

class TweetBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class TweetCreate(TweetBase):
    pass

class TweetUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None

class TweetInDB(TweetBase):
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Tweet(TweetInDB):
    author: UserPublic
    
    class Config:
        from_attributes = True