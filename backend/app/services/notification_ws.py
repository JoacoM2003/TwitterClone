from typing import Optional
from sqlalchemy.orm import Session
from app.core.websocket_manager import manager
from datetime import datetime

class NotificationServiceWs:
    async def notify_new_tweet(self, db: Session, tweet_data: dict, author_id: int, follower_ids: list):
        """Notificar a los seguidores sobre un nuevo tweet"""
        message = {
            "type": "new_tweet",
            "data": tweet_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_to_users(message, follower_ids)
    
    async def notify_new_like(self, db: Session, tweet_id: int, tweet_author_id: int, liker_username: str):
        """Notificar al autor del tweet que alguien dio like"""
        message = {
            "type": "new_like",
            "data": {
                "tweet_id": tweet_id,
                "username": liker_username,
                "message": f"{liker_username} liked your tweet"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(message, tweet_author_id)
    
    async def notify_new_retweet(self, db: Session, tweet_id: int, tweet_author_id: int, retweeter_username: str):
        """Notificar al autor del tweet que alguien hizo retweet"""
        message = {
            "type": "new_retweet",
            "data": {
                "tweet_id": tweet_id,
                "username": retweeter_username,
                "message": f"{retweeter_username} retweeted your tweet"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(message, tweet_author_id)
    
    async def notify_new_reply(self, db: Session, tweet_id: int, tweet_author_id: int, replier_username: str, reply_content: str):
        """Notificar al autor del tweet que alguien respondió"""
        message = {
            "type": "new_reply",
            "data": {
                "tweet_id": tweet_id,
                "username": replier_username,
                "reply_content": reply_content,
                "message": f"{replier_username} replied to your tweet"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(message, tweet_author_id)
    
    async def notify_new_follower(self, db: Session, followed_user_id: int, follower_username: str):
        """Notificar a un usuario que tiene un nuevo seguidor"""
        message = {
            "type": "new_follower",
            "data": {
                "username": follower_username,
                "message": f"{follower_username} started following you"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(message, followed_user_id)

notification_service_ws = NotificationServiceWs()