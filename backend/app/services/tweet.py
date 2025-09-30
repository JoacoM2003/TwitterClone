from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.tweet import Tweet
from app.models.user import User
from app.models.follow import Follow
from app.schemas.tweet import TweetCreate, TweetUpdate

class TweetService:
    def create(self, db: Session, tweet_in: TweetCreate, author_id: int) -> Tweet:
        # Verificar que reply_to_id existe si se proporciona
        if tweet_in.reply_to_id:
            parent_tweet = db.query(Tweet).filter(Tweet.id == tweet_in.reply_to_id).first()
            if not parent_tweet:
                raise ValueError("Parent tweet not found")
        
        db_tweet = Tweet(
            content=tweet_in.content,
            image_url=tweet_in.image_url,
            author_id=author_id,
            reply_to_id=tweet_in.reply_to_id  # NUEVO
        )
        db.add(db_tweet)
        db.commit()
        db.refresh(db_tweet)
        return db_tweet
    
    def get(self, db: Session, tweet_id: int, current_user_id: Optional[int] = None):
        tweet = db.query(Tweet).options(
            joinedload(Tweet.author),
            joinedload(Tweet.reply_to).joinedload(Tweet.author)  # NUEVO: Cargar tweet padre
        ).filter(Tweet.id == tweet_id).first()
        
        if tweet:
            return self._enrich_tweet(db, tweet, current_user_id)
        return None
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 20, current_user_id: Optional[int] = None):
        tweets = (
            db.query(Tweet)
            .options(
                joinedload(Tweet.author),
                joinedload(Tweet.reply_to).joinedload(Tweet.author)
            )
            .filter(Tweet.author_id == user_id)
            .filter(Tweet.reply_to_id.is_(None))  # AGREGAR ESTE FILTRO
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
            .options(
                joinedload(Tweet.author),
                joinedload(Tweet.reply_to).joinedload(Tweet.author)
            )
            .filter(
                (Tweet.author_id.in_(following_ids)) | 
                (Tweet.author_id == user_id)
            )
            .filter(Tweet.reply_to_id.is_(None))  # AGREGAR ESTE FILTRO
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._enrich_tweet(db, tweet, user_id) for tweet in tweets]
    
    def get_all_public(self, db: Session, skip: int = 0, limit: int = 20, current_user_id: Optional[int] = None):
        tweets = (
            db.query(Tweet)
            .options(
                joinedload(Tweet.author),
                joinedload(Tweet.reply_to).joinedload(Tweet.author)
            )
            .filter(Tweet.reply_to_id.is_(None))  # AGREGAR ESTE FILTRO
            .order_by(Tweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._enrich_tweet(db, tweet, current_user_id) for tweet in tweets]
    
    # NUEVO: Obtener respuestas de un tweet
    def get_replies(self, db: Session, tweet_id: int, skip: int = 0, limit: int = 50, current_user_id: Optional[int] = None):
        """Obtener todas las respuestas directas a un tweet"""
        replies = (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(Tweet.reply_to_id == tweet_id)
            .order_by(Tweet.created_at.asc())  # Más antiguas primero en replies
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._enrich_tweet(db, reply, current_user_id) for reply in replies]
    
    # NUEVO: Obtener un thread completo
    def get_thread(self, db: Session, tweet_id: int, current_user_id: Optional[int] = None):
        """
        Obtener un thread completo:
        1. El tweet principal
        2. Todos los tweets padres (si es una respuesta)
        3. Todas las respuestas
        """
        # Obtener el tweet principal
        main_tweet = db.query(Tweet).options(
            joinedload(Tweet.author),
            joinedload(Tweet.reply_to).joinedload(Tweet.author)
        ).filter(Tweet.id == tweet_id).first()
        
        if not main_tweet:
            return None
        
        # Obtener la cadena de tweets padres (ir hacia arriba)
        parent_chain = []
        current_parent = main_tweet.reply_to
        while current_parent:
            parent_chain.insert(0, self._enrich_tweet(db, current_parent, current_user_id))
            current_parent = current_parent.reply_to
        
        # Obtener todas las respuestas (recursivamente)
        replies = self._get_replies_recursive(db, tweet_id, current_user_id)
        
        return {
            "parent_chain": parent_chain,
            "main_tweet": self._enrich_tweet(db, main_tweet, current_user_id),
            "replies": replies,
            "total_replies": len(replies)
        }
    
    def _get_replies_recursive(self, db: Session, tweet_id: int, current_user_id: Optional[int] = None, max_depth: int = 10, current_depth: int = 0):
        """Obtener respuestas recursivamente (con límite de profundidad)"""
        if current_depth >= max_depth:
            return []
        
        direct_replies = (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(Tweet.reply_to_id == tweet_id)
            .order_by(Tweet.created_at.asc())
            .all()
        )
        
        result = []
        for reply in direct_replies:
            enriched_reply = self._enrich_tweet(db, reply, current_user_id)
            # Agregar respuestas anidadas
            enriched_reply["nested_replies"] = self._get_replies_recursive(
                db, reply.id, current_user_id, max_depth, current_depth + 1
            )
            result.append(enriched_reply)
        
        return result
    
    # NUEVO: Contar respuestas
    def get_replies_count(self, db: Session, tweet_id: int) -> int:
        return db.query(Tweet).filter(Tweet.reply_to_id == tweet_id).count()
    
    def _enrich_tweet(self, db: Session, tweet: Tweet, current_user_id: Optional[int] = None):
        """Enriquecer tweet con información adicional"""
        from app.services.like import like_service
        from app.services.retweet import retweet_service

        tweet_data = {
            "id": tweet.id,
            "content": tweet.content,
            "image_url": tweet.image_url,
            "author_id": tweet.author_id,
            "reply_to_id": tweet.reply_to_id,
            "created_at": tweet.created_at,
            "author": tweet.author,
            "likes_count": like_service.get_likes_count(db, tweet.id),
            "retweets_count": retweet_service.get_retweets_count(db, tweet.id),
            "replies_count": self.get_replies_count(db, tweet.id),
            "is_liked_by_user": False,
            "is_retweeted_by_user": False
        }

        if tweet.reply_to:
            tweet_data["reply_to"] = {
                "id": tweet.reply_to.id,
                "content": tweet.reply_to.content,
                "author": tweet.reply_to.author,
                "created_at": tweet.reply_to.created_at
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