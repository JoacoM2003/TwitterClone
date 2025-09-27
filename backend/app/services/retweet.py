from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.retweet import Retweet
from app.models.tweet import Tweet
from app.models.user import User

class RetweetService:
    def retweet(self, db: Session, user_id: int, tweet_id: int, comment: Optional[str] = None) -> Optional[Retweet]:
        # Verificar que el tweet existe
        tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
        if not tweet:
            return None
        
        # Verificar que no es su propio tweet (opcional, Twitter permite retweetear propios)
        # if tweet.author_id == user_id:
        #     return None
            
        # Verificar que no existe ya el retweet
        existing_retweet = db.query(Retweet).filter(
            and_(Retweet.user_id == user_id, Retweet.tweet_id == tweet_id)
        ).first()
        
        if existing_retweet:
            return None  # Ya existe el retweet
        
        # Crear el retweet
        retweet = Retweet(user_id=user_id, tweet_id=tweet_id, comment=comment)
        db.add(retweet)
        db.commit()
        db.refresh(retweet)
        return retweet
    
    def unretweet(self, db: Session, user_id: int, tweet_id: int) -> bool:
        retweet = db.query(Retweet).filter(
            and_(Retweet.user_id == user_id, Retweet.tweet_id == tweet_id)
        ).first()
        
        if not retweet:
            return False
        
        db.delete(retweet)
        db.commit()
        return True
    
    def get_tweet_retweets(self, db: Session, tweet_id: int) -> List[Retweet]:
        return (
            db.query(Retweet)
            .options(joinedload(Retweet.user))
            .filter(Retweet.tweet_id == tweet_id)
            .order_by(Retweet.created_at.desc())
            .all()
        )
    
    def get_user_retweets(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Retweet]:
        return (
            db.query(Retweet)
            .options(
                joinedload(Retweet.tweet).joinedload(Tweet.author),
                joinedload(Retweet.user)
            )
            .filter(Retweet.user_id == user_id)
            .order_by(Retweet.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_retweets_count(self, db: Session, tweet_id: int) -> int:
        return db.query(Retweet).filter(Retweet.tweet_id == tweet_id).count()
    
    def is_retweeted_by_user(self, db: Session, tweet_id: int, user_id: int) -> bool:
        retweet = db.query(Retweet).filter(
            and_(Retweet.user_id == user_id, Retweet.tweet_id == tweet_id)
        ).first()
        return retweet is not None
    
    def get_feed_with_retweets(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[dict]:
        """
        Obtener un feed que mezcle tweets originales y retweets
        Retorna una lista de diccionarios con la información necesaria para el frontend
        """
        from app.models.follow import Follow
        from app.services.like import like_service
        
        # IDs de usuarios seguidos + propio usuario
        following_ids_query = db.query(Follow.followed_id).filter(Follow.follower_id == user_id)
        following_ids = [f[0] for f in following_ids_query.all()]
        following_ids.append(user_id)  # Agregar propio usuario
        
        # Obtener tweets originales de usuarios seguidos
        original_tweets = (
            db.query(Tweet)
            .options(joinedload(Tweet.author))
            .filter(Tweet.author_id.in_(following_ids))
            .all()
        )
        
        # Obtener retweets de usuarios seguidos
        retweets = (
            db.query(Retweet)
            .options(
                joinedload(Retweet.tweet).joinedload(Tweet.author),
                joinedload(Retweet.user)
            )
            .filter(Retweet.user_id.in_(following_ids))
            .all()
        )
        
        # Combinar y formatear para el feed
        feed_items = []
        
        # Agregar tweets originales
        for tweet in original_tweets:
            # Agregar información de likes y retweets
            tweet.likes_count = like_service.get_likes_count(db, tweet.id)
            tweet.retweets_count = self.get_retweets_count(db, tweet.id)
            tweet.is_liked_by_user = like_service.is_liked_by_user(db, tweet.id, user_id)
            tweet.is_retweeted_by_user = self.is_retweeted_by_user(db, tweet.id, user_id)
            
            feed_items.append({
                'type': 'tweet',
                'tweet': tweet,
                'created_at': tweet.created_at
            })
        
        # Agregar retweets
        for retweet in retweets:
            # Agregar información de likes y retweets al tweet original
            retweet.tweet.likes_count = like_service.get_likes_count(db, retweet.tweet.id)
            retweet.tweet.retweets_count = self.get_retweets_count(db, retweet.tweet.id)
            retweet.tweet.is_liked_by_user = like_service.is_liked_by_user(db, retweet.tweet.id, user_id)
            retweet.tweet.is_retweeted_by_user = self.is_retweeted_by_user(db, retweet.tweet.id, user_id)
            
            feed_items.append({
                'type': 'retweet',
                'tweet': retweet.tweet,
                'retweet_author': retweet.user,
                'retweet_comment': retweet.comment,
                'created_at': retweet.created_at  # Usar fecha del retweet para ordenar
            })
        
        # Ordenar por fecha (más reciente primero)
        feed_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Aplicar paginación
        return feed_items[skip:skip + limit]

retweet_service = RetweetService()