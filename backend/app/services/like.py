from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.like import Like
from app.models.tweet import Tweet
from app.models.user import User

class LikeService:
    def like_tweet(self, db: Session, user_id: int, tweet_id: int) -> Optional[Like]:
        # Verificar que el tweet existe
        tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
        if not tweet:
            return None
            
        # Verificar que no existe ya el like
        existing_like = db.query(Like).filter(
            and_(Like.user_id == user_id, Like.tweet_id == tweet_id)
        ).first()
        
        if existing_like:
            return None  # Ya existe el like
        
        # Crear el like
        like = Like(user_id=user_id, tweet_id=tweet_id)
        db.add(like)
        db.commit()
        db.refresh(like)
        return like
    
    def unlike_tweet(self, db: Session, user_id: int, tweet_id: int) -> bool:
        like = db.query(Like).filter(
            and_(Like.user_id == user_id, Like.tweet_id == tweet_id)
        ).first()
        
        if not like:
            return False
        
        db.delete(like)
        db.commit()
        return True
    
    def get_tweet_likes(self, db: Session, tweet_id: int) -> List[Like]:
        return (
            db.query(Like)
            .options(joinedload(Like.user))
            .filter(Like.tweet_id == tweet_id)
            .order_by(Like.created_at.desc())
            .all()
        )
    
    def get_user_likes(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Like]:
        return (
            db.query(Like)
            .options(joinedload(Like.tweet).joinedload(Tweet.author))
            .filter(Like.user_id == user_id)
            .order_by(Like.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_likes_count(self, db: Session, tweet_id: int) -> int:
        return db.query(Like).filter(Like.tweet_id == tweet_id).count()
    
    def is_liked_by_user(self, db: Session, tweet_id: int, user_id: int) -> bool:
        like = db.query(Like).filter(
            and_(Like.user_id == user_id, Like.tweet_id == tweet_id)
        ).first()
        return like is not None

like_service = LikeService()