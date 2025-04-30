from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class RoomBase(BaseModel):
    name: str

    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v) < 3 or len(v) > 100:
            raise ValueError('Room name must be between 3 and 100 characters')
        return v

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    created_by: int
    created_at: datetime

    class config:
        orm_mode = True

class MessageBase(BaseModel):
    content: str

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message content too long (Max 5000 characters)')
        return v

class MessageCreate(MessageBase):
    room_id: int

class Message(MessageBase):
    id: int
    room_id: int
    user_id: int
    created_at: datetime

    class config:
        orm_mode = True

class MessageResponse(Message):
    username: str
