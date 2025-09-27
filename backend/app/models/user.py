from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    bio = Column(String)
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    tweets = relationship("Tweet", back_populates="author")
    followers = relationship("Follow", foreign_keys="Follow.followed_id", back_populates="followed")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    likes = relationship("Like", back_populates="user")
    retweets = relationship("Retweet", back_populates="user")