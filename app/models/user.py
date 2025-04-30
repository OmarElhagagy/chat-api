from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 charachters')
        if not v.isalnum() and not '_' in v:
            raise ValueError('Username must be alphanumeric with optional underscore')
        return v

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must at least be 8 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class config:
        orm_mode = True

class TokenData(BaseModel):
    user_id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
