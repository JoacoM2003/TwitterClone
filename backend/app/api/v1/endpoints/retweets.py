from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.retweet import RetweetCreate, RetweetWithUser, RetweetWithTweet
from app.schemas.user import UserPublic
from app.services.retweet import retweet_service

router = APIRouter()

@router.post("/{tweet_id}")
def retweet(
    tweet_id: int,
    retweet_data: Optional[RetweetCreate] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    comment = retweet_data.comment if retweet_data else None
    retweet = retweet_service.retweet(
        db, 
        user_id=current_user.id, 
        tweet_id=tweet_id, 
        comment=comment
    )
    
    if not retweet:
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
                detail="Tweet already retweeted"
            )
    
    return {"message": "Tweet retweeted successfully"}

@router.delete("/{tweet_id}")
def unretweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = retweet_service.unretweet(db, user_id=current_user.id, tweet_id=tweet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet not retweeted or not found"
        )
    
    return {"message": "Retweet removed successfully"}

@router.get("/{tweet_id}", response_model=List[RetweetWithUser])
def get_tweet_retweets(
    tweet_id: int,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios que retweetearon un tweet"""
    retweets = retweet_service.get_tweet_retweets(db, tweet_id=tweet_id)
    return retweets

@router.get("/user/{username}", response_model=List[RetweetWithTweet])
def get_user_retweets(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener tweets que retweeteo un usuario"""
    from app.services.user import user_service
    
    user = user_service.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    retweets = retweet_service.get_user_retweets(db, user_id=user.id, skip=skip, limit=limit)
    return retweets