from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from ..api.dependencies import get_current_user
from ..models.chat import RoomCreate, Room, MessageCreate, Message, MessageResponse
from ..services.chat_service import create_room, get_room, create_message, get_room_messages
from ..db.redis_cache import cache

router = APIRouter()

@router.post("/rooms", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    room_data: RoomCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new chat room"""
    room = await create_room(room_data, current_user["id"])
    return room

@router.get("/rooms", response_model=List[Room])
async def list_rooms(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get list of all chat rooms"""
    return await get_room()

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a message to a chat room"""
    message = await create_message(message_data, current_user["id"])
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return message

@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    room_id: int,
    page: int = 1,
    page_size: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get messages for a specific room with pagination"""
    messages = await get_room_messages(room_id, page, page_size)
    return messages
