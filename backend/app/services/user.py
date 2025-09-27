from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.follow import Follow
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, db_user: User, user_in: UserUpdate) -> User:
        update_data = user_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_followers_count(self, db: Session, user_id: int) -> int:
        return db.query(Follow).filter(Follow.followed_id == user_id).count()
    
    def get_following_count(self, db: Session, user_id: int) -> int:
        return db.query(Follow).filter(Follow.follower_id == user_id).count()
    
    def is_following(self, db: Session, follower_id: int, followed_id: int) -> bool:
        follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.followed_id == followed_id
        ).first()
        return follow is not None
    
    def follow_user(self, db: Session, follower_id: int, followed_id: int) -> bool:
        if self.is_following(db, follower_id, followed_id):
            return False
        
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.add(follow)
        db.commit()
        return True
    
    def unfollow_user(self, db: Session, follower_id: int, followed_id: int) -> bool:
        follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.followed_id == followed_id
        ).first()
        
        if not follow:
            return False
        
        db.delete(follow)
        db.commit()
        return True

user_service = UserService()