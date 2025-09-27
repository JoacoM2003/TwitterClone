from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from app.schemas.user import UserPublic

class RetweetBase(BaseModel):
    tweet_id: int
    comment: Optional[str] = None

class RetweetCreate(RetweetBase):
    @validator('comment')
    def validate_comment(cls, v):
        if v and len(v) > 280:
            raise ValueError('Comment cannot be longer than 280 characters')
        return v

class Retweet(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class RetweetWithUser(Retweet):
    user: UserPublic

class RetweetWithTweet(Retweet):
    user: UserPublic
    tweet: 'TweetForRetweet'  # Forward reference

# Schema especial para tweets dentro de retweets (evitar recursión infinita)
class TweetForRetweet(BaseModel):
    id: int
    content: str
    image_url: Optional[str] = None
    author_id: int
    created_at: datetime
    author: UserPublic
    likes_count: int = 0
    retweets_count: int = 0
    
    class Config:
        from_attributes = True

# Actualizar forward reference
RetweetWithTweet.model_rebuild()