from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User as UserModel
from app.services.hashtag import hashtag_service

router = APIRouter()

@router.get("/hashtags")
def get_trending_hashtags(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener hashtags trending"""
    return hashtag_service.get_trending(db, limit=limit)