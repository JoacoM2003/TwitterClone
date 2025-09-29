from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Tweet(Base):
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    image_url = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    reply_to_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    author = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")
    retweets = relationship("Retweet", back_populates="tweet", cascade="all, delete-orphan")
    reply_to = relationship("Tweet", remote_side=[id], foreign_keys=[reply_to_id], backref="replies")