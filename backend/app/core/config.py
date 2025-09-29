from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:admin@localhost:5432/twitter_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "Tv792EZJsq9Wmh66w_yTKeAoXaeoX7m2kuAUngu9WKU"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Twitter Clone"
    
    # CORS
    backend_cors_origins: list = ["http://localhost:3000", "*"]
    
    class Config:
        # env_file = ".env"
        case_sensitive = True

settings = Settings()