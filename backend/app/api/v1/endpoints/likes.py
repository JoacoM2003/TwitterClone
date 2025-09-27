from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.like import Like, LikeWithUser, LikeWithTweet
from app.schemas.user import UserPublic
from app.services.like import like_service

router = APIRouter()

@router.post("/{tweet_id}")
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    like = like_service.like_tweet(db, user_id=current_user.id, tweet_id=tweet_id)
    if not like:
        # Verificar si el tweet existe
        from app.services.tweet import tweet_service
        tweet = tweet_service.get(db, tweet_id)
        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tweet not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tweet already liked"
            )
    
    return {"message": "Tweet liked successfully"}

@router.delete("/{tweet_id}")
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = like_service.unlike_tweet(db, user_id=current_user.id, tweet_id=tweet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet not liked or not found"
        )
    
    return {"message": "Tweet unliked successfully"}

@router.get("/{tweet_id}", response_model=List[UserPublic])
def get_tweet_likes(
    tweet_id: int,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios que dieron like a un tweet"""
    likes = like_service.get_tweet_likes(db, tweet_id=tweet_id)
    return [like.user for like in likes]

@router.get("/user/{username}", response_model=List[LikeWithTweet])
def get_user_likes(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener tweets que le gustan a un usuario"""
    from app.services.user import user_service
    
    user = user_service.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    likes = like_service.get_user_likes(db, user_id=user.id, skip=skip, limit=limit)
    return likes