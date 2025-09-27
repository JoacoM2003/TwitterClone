from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.tweet import Tweet, TweetCreate, TweetUpdate
from app.services.tweet import tweet_service

router = APIRouter()

@router.post("/", response_model=Tweet)
def create_tweet(
    tweet_in: TweetCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = tweet_service.create(db, tweet_in=tweet_in, author_id=current_user.id)
    return tweet_service.get(db, tweet.id, current_user.id)

@router.get("/")  # Remover response_model por ahora
def read_tweets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweets = tweet_service.get_all_public(db, skip=skip, limit=limit, current_user_id=current_user.id)
    return tweets

@router.get("/feed")  # Remover response_model por ahora
def read_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweets = tweet_service.get_feed(db, user_id=current_user.id, skip=skip, limit=limit)
    return tweets

@router.get("/{tweet_id}")  # Remover response_model por ahora
def read_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = tweet_service.get(db, tweet_id=tweet_id, current_user_id=current_user.id)
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    return tweet

@router.put("/{tweet_id}", response_model=Tweet)
def update_tweet(
    tweet_id: int,
    tweet_in: TweetUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    
    if tweet.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    tweet = tweet_service.update(db, db_tweet=tweet, tweet_in=tweet_in)
    return tweet_service.get(db, tweet.id, current_user.id)

@router.delete("/{tweet_id}")
def delete_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    success = tweet_service.delete(db, tweet_id=tweet_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found or not enough permissions"
        )
    
    return {"message": "Tweet deleted successfully"}

@router.get("/user/{username}")  # Remover response_model por ahora
def read_user_tweets(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    from app.services.user import user_service
    
    user = user_service.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    tweets = tweet_service.get_by_user(db, user_id=user.id, skip=skip, limit=limit, current_user_id=current_user.id)
    return tweets