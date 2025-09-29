from pydantic import BaseModel
from typing import List
from app.schemas.tweet import TweetWithReplyTo

class ThreadResponse(BaseModel):
    """Respuesta para un thread completo"""
    main_tweet: TweetWithReplyTo
    replies: List[TweetWithReplyTo]
    total_replies: int