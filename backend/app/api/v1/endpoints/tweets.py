from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.models.tweet import Tweet as TweetModel
from app.schemas.tweet import Tweet, TweetCreate, TweetUpdate
from app.services.tweet import tweet_service
from app.services.notification import notification_service
from app.models.follow import Follow

router = APIRouter()

@router.post("/", response_model=Tweet)
async def create_tweet(
    tweet_in: TweetCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = tweet_service.create(db, tweet_in=tweet_in, author_id=current_user.id)
    tweet_data = tweet_service.get(db, tweet.id, current_user.id)
    
    # Notificar a los seguidores si no es un reply
    if not tweet_in.reply_to_id:
        follower_ids = [f.follower_id for f in db.query(Follow).filter(Follow.followed_id == current_user.id).all()]
        if follower_ids:
            await notification_service.notify_new_tweet(db, tweet_data, current_user.id, follower_ids)
    else:
        parent_tweet = db.query(TweetModel).filter(TweetModel.id == tweet_in.reply_to_id).first()
        if parent_tweet and parent_tweet.author_id != current_user.id:
            await notification_service.notify_new_reply(
                db, 
                parent_tweet.id, 
                parent_tweet.author_id, 
                current_user.username,
                tweet_in.content
            )
    
    return tweet_data

@router.get("/")
def read_tweets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweets = tweet_service.get_all_public(db, skip=skip, limit=limit, current_user_id=current_user.id)
    return tweets

@router.get("/feed")
def read_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweets = tweet_service.get_feed(db, user_id=current_user.id, skip=skip, limit=limit)
    return tweets

@router.get("/{tweet_id}")
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

@router.get("/{tweet_id}/replies")
def get_tweet_replies(
    tweet_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = db.query(TweetModel).filter(TweetModel.id == tweet_id).first()
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    
    replies = tweet_service.get_replies(db, tweet_id=tweet_id, skip=skip, limit=limit, current_user_id=current_user.id)
    return replies

@router.get("/{tweet_id}/thread")
def get_tweet_thread(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    thread = tweet_service.get_thread(db, tweet_id=tweet_id, current_user_id=current_user.id)
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    
    return thread

@router.post("/{tweet_id}/reply")
async def reply_to_tweet(
    tweet_id: int,
    reply_data: TweetCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    parent_tweet = db.query(TweetModel).filter(TweetModel.id == tweet_id).first()
    if not parent_tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    
    reply_data.reply_to_id = tweet_id
    
    try:
        reply = tweet_service.create(db, tweet_in=reply_data, author_id=current_user.id)
        
        # Notificar al autor del tweet original
        if parent_tweet.author_id != current_user.id:
            await notification_service.notify_new_reply(
                db,
                parent_tweet.id,
                parent_tweet.author_id,
                current_user.username,
                reply_data.content
            )
        
        return tweet_service.get(db, reply.id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{tweet_id}", response_model=Tweet)
def update_tweet(
    tweet_id: int,
    tweet_in: TweetUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    tweet = db.query(TweetModel).filter(TweetModel.id == tweet_id).first()
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

@router.get("/user/{username}")
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