from typing import Optional, List, Dict, Any
from ..db.database import db
from ..db.redis_cache import cache
from ..models.chat import MessageCreate, RoomCreate

async def create_room(room: RoomCreate, user_id: int) -> Optional[Dict[str, Any]]:
    """Create new chat room"""
    async with db.pool.acquire() as conn:
        room_id = await conn.fetchval(
            """
            INSERT INTO rooms (name, created_by)
            VALUES ($1, $2)
            RETURNING id
            """,
            room.name, user_id
        )

        room_record = await conn.fetchrow(
            "SELECT id, name, created_by, created_at FROM rooms WHERE id = $1",
            room_id
        )

        cache.delete("rooms:list")

        return dict(room_record)


async def get_room() -> List[Dict[str, Any]]:
    """Get all chat rooms"""
    #try cache first
    cache_key = "rooms:list"
    cached_rooms = cache.get(cache_key)

    if cached_rooms:
        return cached_rooms

    # Query database
    async with db.pool.acquire() as conn:
        rooms = await conn.fetch(
            """
            SELECT r.id, r.name, r.created_by, r.created_at, u.username as creator_name
            FROM rooms r
            JOIN users u ON r.created_by = u.id
            ORDER BY r.created_at DESC
            """
        )

        result = [dict(room) for room in rooms]

        # cache the result
        cache.set(cache_key, result)

        return result


async def create_message(message: MessageCreate, user_id: int) -> Optional[Dict[str, Any]]: 
    """Create new message in room"""
    async with db.pool.acquire() as conn:
        # Verify room exists
        room_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM rooms WHERE id = $1)",
            message.room_id
        )

        if not room_exists:
            return None

    # Insert message
    message_id = await conn.fetchval(
        """
        INSERT INTO messages (room_id, user_id, content)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        message.room_id, user_id, message.content
    )

    # Get complete message with username
    message_record = await conn.fetchrow(
        """
        SELECT m.id, m.room_id, m.user_id, m.content, m.created_at, u.username
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = $1
        """,
        message_id
    )

    # Invalidate message cache for this room
    cache.delete(f"room{message.room_id}:messages")

    return dict(message_record)


async def get_room_messages(room_id: int, page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
    """Get messages for a specific room with pagination"""
    offset = (page - 1) * page_size

    # For first page try cache
    cache_key = f"room:{room_id}:messages"
    if page == 1:
        cached_messages = cache.get(cache_key)
        if cached_messages:
            return cached_messages[:page_size] # To prevent sending more messages than needed bec there could be more in cache


    # Query database
    async with db.pool.acquire() as conn:
        # Verify room exists
        room_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM rooms WHERE id = $1)",
            room_id
        )

        if not room_exists:
            return []

        messages = await conn.fetch(
            """
            SELECT m.id, m.room_id, m.user_id, m.content, m.created_at, u.username
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_id = $1
            ORDER BY m.created_at DESC
            LIMIT $2 OFFSET $3
            """,
            room_id, page_size, offset
        )

        result = [dict(msg) for msg in messages]

        # Cache only first page result
        if page == 1:
            cache.set(cache_key, result)

        return result

