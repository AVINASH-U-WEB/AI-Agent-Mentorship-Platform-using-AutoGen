import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Skill-Exchange Mentor Network"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./skill_exchange.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    SECRET_KEY: str = "a_very_secret_key_for_jwt_in_the_future"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    PWD_CONTEXT_SCHEMES: List[str] = ["bcrypt"]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Cached function to get settings instance."""
    return Settings()

settings = get_settings()