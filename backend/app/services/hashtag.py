import re
from typing import List
from sqlalchemy.orm import Session
from app.models.hashtag import Hashtag
from app.models.tweet import Tweet

class HashtagService:
    def extract_hashtags(self, text: str) -> List[str]:
        """Extraer hashtags de un texto"""
        # Regex para encontrar hashtags
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extraer menciones (@username) de un texto"""
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)
        return [username.lower() for username in mentions]
    
    def get_or_create_hashtag(self, db: Session, tag: str) -> Hashtag:
        """Obtener o crear un hashtag"""
        tag = tag.lower()
        hashtag = db.query(Hashtag).filter(Hashtag.tag == tag).first()
        
        if not hashtag:
            hashtag = Hashtag(tag=tag, count=1)
            db.add(hashtag)
            db.commit()
            db.refresh(hashtag)
        else:
            hashtag.count += 1
            db.add(hashtag)
            db.commit()
        
        return hashtag
    
    def process_tweet_hashtags(self, db: Session, tweet: Tweet, content: str):
        """Procesar y asociar hashtags a un tweet"""
        hashtags = self.extract_hashtags(content)
        
        for tag in hashtags:
            hashtag = self.get_or_create_hashtag(db, tag)
            if hashtag not in tweet.hashtags:
                tweet.hashtags.append(hashtag)
        
        db.commit()
    
    def process_tweet_mentions(self, db: Session, tweet: Tweet, content: str):
        """Procesar y crear menciones en un tweet"""
        from app.models.mention import Mention
        from app.models.user import User
        
        usernames = self.extract_mentions(content)
        
        for username in usernames:
            user = db.query(User).filter(User.username == username).first()
            if user and user.id != tweet.author_id:
                # Verificar que no exista ya la mención
                existing = db.query(Mention).filter(
                    Mention.tweet_id == tweet.id,
                    Mention.mentioned_user_id == user.id
                ).first()
                
                if not existing:
                    mention = Mention(
                        tweet_id=tweet.id,
                        mentioned_user_id=user.id
                    )
                    db.add(mention)
        
        db.commit()
    
    def get_trending(self, db: Session, limit: int = 10) -> List[dict]:
        """Obtener hashtags trending"""
        from datetime import datetime, timedelta
        
        # Hashtags más usados en las últimas 24 horas
        hashtags = (
            db.query(Hashtag)
            .order_by(Hashtag.count.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "tag": hashtag.tag,
                "count": hashtag.count,
                "tweets_count": len(hashtag.tweets)
            }
            for hashtag in hashtags
        ]

hashtag_service = HashtagService()