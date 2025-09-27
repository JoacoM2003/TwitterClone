from pydantic import BaseModel
from typing import Optional, List
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
    likes_count: int = 0
    retweets_count: int = 0
    is_liked_by_user: Optional[bool] = False
    is_retweeted_by_user: Optional[bool] = False  # NUEVO
    
    class Config:
        from_attributes = True

class TweetWithDetails(Tweet):
    """Tweet con información detallada para feeds"""
    is_retweet: bool = False  # Si este "tweet" es en realidad un retweet
    retweet_author: Optional[UserPublic] = None  # Quien hizo el retweet
    retweet_comment: Optional[str] = None  # Comentario del retweet
    retweet_created_at: Optional[datetime] = None  # Cuándo se hizo el retweet