from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate, UserPublic
from app.services.user import user_service
from app.services.notification import notification_service

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    from app.services.user import user_service
    current_user.followers_count = user_service.get_followers_count(db, current_user.id)
    current_user.following_count = user_service.get_following_count(db, current_user.id)
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user = user_service.update(db, db_user=current_user, user_in=user_in)
    return user

@router.get("/{username}", response_model=UserPublic)
def read_user(
    username: str,
    db: Session = Depends(get_db)
):
    user = user_service.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.followers_count = user_service.get_followers_count(db, user.id)
    user.following_count = user_service.get_following_count(db, user.id)
    
    return user

@router.post("/{username}/follow")
async def follow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_to_follow = user_service.get_by_username(db, username=username)
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_to_follow.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    success = user_service.follow_user(db, current_user.id, user_to_follow.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Notificar al usuario seguido
    await notification_service.notify_new_follower(
        db,
        user_to_follow.id,
        current_user.username
    )
    
    return {"message": "User followed successfully"}

@router.delete("/{username}/follow")
def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_to_unfollow = user_service.get_by_username(db, username=username)
    if not user_to_unfollow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_service.unfollow_user(db, current_user.id, user_to_unfollow.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    
    return {"message": "User unfollowed successfully"}

@router.get("/{username}/is-following")
def check_is_following(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_to_check = user_service.get_by_username(db, username=username)
    if not user_to_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    is_following = user_service.is_following(db, current_user.id, user_to_check.id)
    return {"is_following": is_following}