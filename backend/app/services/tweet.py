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
    
    def get(self, db: Session, tweet_id: int, current_user_id: Optional[int] = None):
        tweet = db.query(Tweet).options(joinedload(Tweet.author)).filter(Tweet.id == tweet_id).first()
        if tweet:
            # Crear un objeto dict en lugar de modificar el objeto SQLAlchemy
            return self._enrich_tweet(db, tweet, current_user_id)
        return None
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 20, current_user_id: Optional[int] = None):
        tweets = (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(Tweet.author_id == user_id)
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._enrich_tweet(db, tweet, current_user_id) for tweet in tweets]
    
    def get_feed(self, db: Session, user_id: int, skip: int = 0, limit: int = 20):
        following_ids = db.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
        
        tweets = (
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
        
        return [self._enrich_tweet(db, tweet, user_id) for tweet in tweets]
    
    def get_all_public(self, db: Session, skip: int = 0, limit: int = 20, current_user_id: Optional[int] = None):
        tweets = (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._enrich_tweet(db, tweet, current_user_id) for tweet in tweets]
    
    def _enrich_tweet(self, db: Session, tweet: Tweet, current_user_id: Optional[int] = None):
        """Enriquecer tweet con información adicional"""
        from app.services.like import like_service
        from app.services.retweet import retweet_service  # Importar cuando implementes retweets
        
        # Crear dict con toda la información
        tweet_data = {
            "id": tweet.id,
            "content": tweet.content,
            "image_url": tweet.image_url,
            "author_id": tweet.author_id,
            "created_at": tweet.created_at,
            "author": tweet.author,
            "likes_count": like_service.get_likes_count(db, tweet.id),
            "retweets_count": 0,  # retweet_service.get_retweets_count(db, tweet.id) cuando implementes
            "is_liked_by_user": False,
            "is_retweeted_by_user": False
        }
        
        if current_user_id:
            tweet_data["is_liked_by_user"] = like_service.is_liked_by_user(db, tweet.id, current_user_id)
            tweet_data["is_retweeted_by_user"] = retweet_service.is_retweeted_by_user(db, tweet.id, current_user_id)
        
        return tweet_data
    
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