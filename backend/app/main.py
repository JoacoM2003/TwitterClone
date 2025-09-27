from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.database import engine
from app.models import user, tweet, follow

# Crear tablas
user.Base.metadata.create_all(bind=engine)
tweet.Base.metadata.create_all(bind=engine)  
follow.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix=settings.api_v1_str)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.project_name} API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}