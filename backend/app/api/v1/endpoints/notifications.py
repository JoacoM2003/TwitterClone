from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.services.notification import notification_service

router = APIRouter()

@router.get("/")
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener notificaciones del usuario"""
    notifications = notification_service.get_user_notifications(
        db, 
        current_user.id, 
        skip, 
        limit,
        unread_only
    )
    
    return [
        {
            "id": n.id,
            "type": n.type,
            "message": n.message,
            "related_id": n.related_id,
            "related_username": n.related_username,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener cantidad de notificaciones no leídas"""
    count = notification_service.get_unread_count(db, current_user.id)
    return {"count": count}

@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Marcar notificación como leída"""
    success = notification_service.mark_as_read(db, notification_id, current_user.id)
    if not success:
        return {"message": "Notificación no encontrada"}
    return {"message": "Marcada como leída"}

@router.post("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Marcar todas las notificaciones como leídas"""
    notification_service.mark_all_as_read(db, current_user.id)
    return {"message": "Todas marcadas como leídas"}