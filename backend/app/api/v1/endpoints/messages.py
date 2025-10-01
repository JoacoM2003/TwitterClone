from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.message import MessageCreate, Message, Conversation
from app.services.message import message_service

router = APIRouter()

@router.post("/send")
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Enviar un mensaje"""
    message = message_service.send_message(
        db,
        sender_id=current_user.id,
        receiver_username=message_data.receiver_username,
        content=message_data.content
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Notificar por WebSocket
    from app.core.websocket_manager import manager
    from app.services.user import user_service
    
    receiver = user_service.get_by_username(db, message_data.receiver_username)
    if receiver:
        await manager.send_personal_message({
            "type": "new_message",
            "data": {
                "message_id": message.id,
                "sender_username": current_user.username,
                "sender_name": current_user.full_name or current_user.username,
                "content": message.content,
                "created_at": message.created_at.isoformat()
            }
        }, receiver.id)
    
    return {"message": "Mensaje enviado", "message_id": message.id}

@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener todas las conversaciones del usuario"""
    conversations = message_service.get_conversations(db, current_user.id)
    
    result = []
    for conv, other_user, last_message, unread_count in conversations:
        result.append({
            "id": conv.id,
            "other_user": {
                "id": other_user.id,
                "username": other_user.username,
                "full_name": other_user.full_name,
                "avatar_url": other_user.avatar_url
            },
            "last_message": {
                "id": last_message.id,
                "content": last_message.content,
                "sender_id": last_message.sender_id,
                "created_at": last_message.created_at.isoformat()
            } if last_message else None,
            "unread_count": unread_count,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat()
        })
    
    return result

@router.get("/{username}")
def get_messages(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener mensajes de una conversación"""
    messages = message_service.get_messages(db, current_user.id, username, skip, limit)
    
    # Marcar como leídos
    message_service.mark_as_read(db, current_user.id, username)
    
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender": {
                "id": msg.sender.id,
                "username": msg.sender.username,
                "full_name": msg.sender.full_name
            },
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]

@router.post("/{username}/read")
def mark_as_read(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Marcar mensajes como leídos"""
    message_service.mark_as_read(db, current_user.id, username)
    return {"message": "Mensajes marcados como leídos"}