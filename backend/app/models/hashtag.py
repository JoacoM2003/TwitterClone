from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

# Tabla intermedia para relación many-to-many
tweet_hashtags = Table(
    'tweet_hashtags',
    Base.metadata,
    Column('tweet_id', Integer, ForeignKey('tweets.id', ondelete='CASCADE'), primary_key=True),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id', ondelete='CASCADE'), primary_key=True)
)

class Hashtag(Base):
    __tablename__ = "hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True, nullable=False)
    count = Column(Integer, default=0)  # Contador de usos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación many-to-many con tweets
    tweets = relationship("Tweet", secondary=tweet_hashtags, back_populates="hashtags")