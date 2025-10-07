from typing import List
from sqlalchemy.orm import Session
from app.models.notification import Notification as NotificationModel

class NotificationService:
    def create_notification(
        self, 
        db: Session, 
        user_id: int, 
        type: str, 
        message: str,
        related_id: int = None,
        related_username: str = None
    ) -> NotificationModel:
        """Crear una notificación"""
        notification = NotificationModel(
            user_id=user_id,
            type=type,
            message=message,
            related_id=related_id,
            related_username=related_username
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    def get_user_notifications(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50,
        unread_only: bool = False
    ) -> List[NotificationModel]:
        """Obtener notificaciones de un usuario"""
        query = db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(NotificationModel.is_read == False)
        
        return query.order_by(
            NotificationModel.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Marcar notificación como leída"""
        notification = db.query(NotificationModel).filter(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False
    
    def mark_all_as_read(self, db: Session, user_id: int):
        """Marcar todas como leídas"""
        db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False
        ).update({"is_read": True})
        db.commit()
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Contar notificaciones no leídas"""
        return db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False
        ).count()

notification_service = NotificationService()