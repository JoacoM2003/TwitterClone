from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.tweet import Tweet
from app.models.user import User
from app.models.follow import Follow
from app.schemas.tweet import TweetCreate, TweetUpdate

class TweetService:
    def create(self, db: Session, tweet_in: TweetCreate, author_id: int) -> Tweet:
        db_tweet = Tweet(
            content=tweet_in.content,
            image_url=tweet_in.image_url,
            author_id=author_id
        )
        db.add(db_tweet)
        db.commit()
        db.refresh(db_tweet)
        return db_tweet
    
    def get(self, db: Session, tweet_id: int) -> Optional[Tweet]:
        return db.query(Tweet).options(joinedload(Tweet.author)).filter(Tweet.id == tweet_id).first()
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Tweet]:
        return (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(Tweet.author_id == user_id)
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_feed(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Tweet]:
        # Obtener tweets de usuarios seguidos + propios tweets
        following_ids = db.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
        
        return (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(
                (Tweet.author_id.in_(following_ids)) | 
                (Tweet.author_id == user_id)
            )
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_all_public(self, db: Session, skip: int = 0, limit: int = 20) -> List[Tweet]:
        return (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update(self, db: Session, db_tweet: Tweet, tweet_in: TweetUpdate) -> Tweet:
        update_data = tweet_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tweet, field, value)
        db.add(db_tweet)
        db.commit()
        db.refresh(db_tweet)
        return db_tweet
    
    def delete(self, db: Session, tweet_id: int, user_id: int) -> bool:
        tweet = db.query(Tweet).filter(
            Tweet.id == tweet_id,
            Tweet.author_id == user_id
        ).first()
        
        if not tweet:
            return False
        
        db.delete(tweet)
        db.commit()
        return True

tweet_service = TweetService()