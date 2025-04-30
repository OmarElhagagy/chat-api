from typing import Optional, Dict, Any
from ..db.database import db
from ..db.redis_cache import cache
from ..models.user import UserCreate, UserResponse
from .auth import get_password_hash, verify_password


async def create_user(user: UserCreate) -> Optional[Dict[str, Any]]:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)

    async with db.pool.acquire() as conn:
        # check if username or email already exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = 2$",
            user.username, user.email
        )

        if existing:
            return None

        # Insert new user
        user_id = await conn.fetchval(
            """
            INSER INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            user.username, user.email, hashed_password
        )

        # Get the complete user record
        user_record = await conn.fetchrow(
            "SELECT id, username, email, created_at FROM users WHERE id = $1",
            user_id
        )

        return dict(user_record)

async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user and return user data if successful"""
    # Try to get from cache first
    cache_key = f"auth: {username}"
    cached_auth = cache.get(cache_key)

    if cached_auth and verify_password(password, cached_auth.get("password_hash")):
        return {
            "id": cached_auth["id"],
            "username": cached_auth["username"],
            "email": cached_auth["email"]
        }

    # Not in cache or password doesnt match, check database
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, username, email, password_hash FROM users WHERE username = $1",
            username
        )

        if not user:
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        # Cache successeful authentication
        cache.set(
            cache_key,
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "password_hash": user["password_hash"]
            },
            ttl=3600 # cache for 1 hour
        )

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }

async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    # Try cache first
    cache_key = f"user: {user_id}"
    cached_user = cache.get(cache_key)

    if cached_user:
        return cached_user

    # Query database
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, username, email, created_at FROM users WHERE id = $1",
            user_id
        )

        if user:
            user_dict = dict(user)
            #cache the result
            cache.set(cache_key, user_dict)
            return user_dict

        return None
