from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.message import Message, Conversation
from app.models.user import User
from app.schemas.message import MessageCreate

class MessageService:
    def get_or_create_conversation(self, db: Session, user1_id: int, user2_id: int) -> Conversation:
        """Obtener o crear una conversación entre dos usuarios"""
        # Asegurar orden consistente (menor id primero)
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.user1_id == user1_id,
                Conversation.user2_id == user2_id
            )
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        return conversation
    
    def send_message(self, db: Session, sender_id: int, receiver_username: str, content: str) -> Optional[Message]:
        """Enviar un mensaje"""
        # Buscar el receptor
        receiver = db.query(User).filter(User.username == receiver_username).first()
        if not receiver:
            return None
        
        if receiver.id == sender_id:
            return None  # No puedes enviarte mensajes a ti mismo
        
        # Obtener o crear conversación
        conversation = self.get_or_create_conversation(db, sender_id, receiver.id)
        
        # Crear mensaje
        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    def get_conversations(self, db: Session, user_id: int) -> List[Tuple[Conversation, User, Optional[Message], int]]:
        """Obtener todas las conversaciones de un usuario con info del último mensaje"""
        conversations = db.query(Conversation).filter(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        ).options(
            joinedload(Conversation.user1),
            joinedload(Conversation.user2)
        ).all()
        
        result = []
        for conv in conversations:
            # Determinar el otro usuario
            other_user = conv.user2 if conv.user1_id == user_id else conv.user1
            
            # Obtener último mensaje
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()
            
            # Contar mensajes no leídos
            unread_count = db.query(Message).filter(
                and_(
                    Message.conversation_id == conv.id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            ).count()
            
            result.append((conv, other_user, last_message, unread_count))
        
        # Ordenar por último mensaje
        result.sort(key=lambda x: x[2].created_at if x[2] else x[0].created_at, reverse=True)
        
        return result
    
    def get_messages(self, db: Session, user_id: int, other_username: str, skip: int = 0, limit: int = 50) -> List[Message]:
        """Obtener mensajes de una conversación"""
        # Buscar el otro usuario
        other_user = db.query(User).filter(User.username == other_username).first()
        if not other_user:
            return []
        
        # Obtener conversación
        conversation = self.get_or_create_conversation(db, user_id, other_user.id)
        
        # Obtener mensajes
        messages = (
            db.query(Message)
            .options(joinedload(Message.sender))
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return list(reversed(messages))  # Invertir para mostrar más antiguos primero
    
    def mark_as_read(self, db: Session, user_id: int, other_username: str):
        """Marcar mensajes como leídos"""
        other_user = db.query(User).filter(User.username == other_username).first()
        if not other_user:
            return
        
        # Obtener conversación
        user1_id = min(user_id, other_user.id)
        user2_id = max(user_id, other_user.id)
        
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.user1_id == user1_id,
                Conversation.user2_id == user2_id
            )
        ).first()
        
        if not conversation:
            return
        
        # Marcar mensajes del otro usuario como leídos
        db.query(Message).filter(
            and_(
                Message.conversation_id == conversation.id,
                Message.sender_id == other_user.id,
                Message.is_read == False
            )
        ).update({"is_read": True})
        
        db.commit()

message_service = MessageService()