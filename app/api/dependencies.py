from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

from ..services.auth import decoded_access_token
from ..services.user_service import get_user_by_id
from ..db.redis_cache import cache

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get the current authenticated user"""
    # Try to use cache first
    cache_key = f"token:{token}"
    cached_user = cache.get(cache_key)
    
    if cached_user:
        return cached_user
    
    # Decode token
    token_data = decoded_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cache the result
    cache.set(cache_key, user, ttl=900)  # Cache for 15 minutes
    
    return user
