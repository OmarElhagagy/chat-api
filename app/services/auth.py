import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, cast
from passlib.context import CryptContext
from ..core.config import settings
from ..models.user import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(user_id: int, username: str) -> str:
    """Create JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decoded_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("sub")
        username = payload.get("username")

        if user_id is None and username is None:
            return None

        user_id = int(cast(str, username))
        username = cast(str, username)

        return TokenData(user_id=user_id, username=username)
    except jwt.PyJWTError:
        return None
