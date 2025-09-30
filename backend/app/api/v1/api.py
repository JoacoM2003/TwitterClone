from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, tweets, likes, retweets, websocket, search, trending

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])  
api_router.include_router(tweets.router, prefix="/tweets", tags=["tweets"])
api_router.include_router(likes.router, prefix="/likes", tags=["likes"])
api_router.include_router(retweets.router, prefix="/retweets", tags=["retweets"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(search.router, prefix="/search", tags=["searchs"])
api_router.include_router(trending.router, prefix="/trending", tags=["trending"])