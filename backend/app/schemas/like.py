from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserPublic
from app.schemas.tweet import TweetInDB

class LikeBase(BaseModel):
    user_id: int
    tweet_id: int

class LikeCreate(BaseModel):
    tweet_id: int

class Like(BaseModel):
    id: int
    user_id: int
    tweet_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LikeWithUser(Like):
    user: UserPublic
    
class LikeWithTweet(Like):
    tweet: TweetInDB