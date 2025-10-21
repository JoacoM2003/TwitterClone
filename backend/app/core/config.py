

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
from pydantic import Field

# load_dotenv()

import os
print("Render DATABASE_URL:", os.getenv("DATABASE_URL"))


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql://postgres:admin@localhost:5432/twitter_db", env="DATABASE_URL")

    # Redis
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Security
    secret_key: str = Field(default="Tv792EZJsq9Wmh66w_yTKeAoXaeoX7m2kuAUngu9WKU", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # API
    api_v1_str: str = Field(default="/api/v1", env="API_V1_STR")
    project_name: str = Field(default="Twitter Clone", env="PROJECT_NAME")

    # CORS
    backend_cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ], env="BACKEND_CORS_ORIGINS")

    # Environment
    environment: str = Field(default="production", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convertir Neon URL si es necesario
        if self.database_url and self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)

settings = Settings()

# DEBUG: Mostrar valores cargados
print("[CONFIG] database_url:", settings.database_url)
print("[CONFIG] redis_url:", settings.redis_url)
print("[CONFIG] secret_key:", settings.secret_key)
print("[CONFIG] algorithm:", settings.algorithm)
print("[CONFIG] access_token_expire_minutes:", settings.access_token_expire_minutes)
print("[CONFIG] api_v1_str:", settings.api_v1_str)
print("[CONFIG] project_name:", settings.project_name)
print("[CONFIG] backend_cors_origins:", settings.backend_cors_origins)
print("[CONFIG] environment:", settings.environment)