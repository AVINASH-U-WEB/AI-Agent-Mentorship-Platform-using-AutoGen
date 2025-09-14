# app/core/security.py
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=settings.PWD_CONTEXT_SCHEMES, deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)