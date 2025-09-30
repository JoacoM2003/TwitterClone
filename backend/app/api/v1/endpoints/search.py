from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.models.tweet import Tweet as TweetModel
from app.schemas.user import UserPublic
from app.schemas.tweet import Tweet
from app.services.tweet import tweet_service

router = APIRouter()

@router.get("/users")
def search_users(
    q: str = Query(..., min_length=1, description="Búsqueda de usuarios"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Buscar usuarios por username o nombre completo"""
    users = (
        db.query(UserModel)
        .filter(
            or_(
                UserModel.username.ilike(f"%{q}%"),
                UserModel.full_name.ilike(f"%{q}%")
            )
        )
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url
        }
        for user in users
    ]

@router.get("/tweets")
def search_tweets(
    q: str = Query(..., min_length=1, description="Búsqueda de tweets"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Buscar tweets por contenido"""
    tweets = (
        db.query(TweetModel)
        .filter(TweetModel.content.ilike(f"%{q}%"))
        .order_by(TweetModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [tweet_service._enrich_tweet(db, tweet, current_user.id) for tweet in tweets]

@router.get("/hashtags")
def search_hashtags(
    q: str = Query(..., min_length=1, description="Búsqueda de hashtags"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Buscar tweets por hashtag"""
    # Buscar tweets que contengan el hashtag
    search_term = f"%#{q}%" if not q.startswith('#') else f"%{q}%"
    
    tweets = (
        db.query(TweetModel)
        .filter(TweetModel.content.ilike(search_term))
        .order_by(TweetModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [tweet_service._enrich_tweet(db, tweet, current_user.id) for tweet in tweets]