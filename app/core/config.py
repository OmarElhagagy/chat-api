import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:omaradel@localhost:5432/chatdb")

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mysecret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Cache settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600")) # 1 hour default

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

settings = Settings()
