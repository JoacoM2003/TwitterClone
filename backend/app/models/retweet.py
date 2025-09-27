from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Retweet(Base):
    __tablename__ = "retweets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    comment = Column(Text, nullable=True)  # Para "quote tweets" con comentario
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint para evitar retweets duplicados del mismo tweet
    __table_args__ = (UniqueConstraint('user_id', 'tweet_id', name='unique_retweet'),)
    
    # Relaciones
    user = relationship("User", back_populates="retweets")
    tweet = relationship("Tweet", back_populates="retweets")