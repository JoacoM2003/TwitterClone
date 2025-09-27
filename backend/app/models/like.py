from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint para evitar likes duplicados
    __table_args__ = (UniqueConstraint('user_id', 'tweet_id', name='unique_like'),)
    
    # Relaciones
    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")