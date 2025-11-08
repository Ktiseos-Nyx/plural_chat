"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# User/Auth Schemas
class UserBase(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    system_name: Optional[str] = None
    theme_color: Optional[str] = None
    avatar_path: Optional[str] = None

class UserCreate(BaseModel):
    pk_token: str

class User(UserBase):
    created_at: datetime
    last_sync: Optional[datetime] = None
    last_login: Optional[datetime] = None
    totp_enabled: bool = False

    class Config:
        from_attributes = True


# Member Schemas
class MemberBase(BaseModel):
    name: str
    pronouns: Optional[str] = None
    color: Optional[str] = None
    avatar_path: Optional[str] = None
    description: Optional[str] = None
    pk_id: Optional[str] = None
    proxy_tags: Optional[str] = None

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    pronouns: Optional[str] = None
    color: Optional[str] = None
    avatar_path: Optional[str] = None
    description: Optional[str] = None
    proxy_tags: Optional[str] = None

class Member(MemberBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Channel Schemas
class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color
    emoji: Optional[str] = Field(None, max_length=10)

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    emoji: Optional[str] = Field(None, max_length=10)
    is_archived: Optional[bool] = None
    position: Optional[int] = None

class Channel(ChannelBase):
    id: int
    user_id: int
    is_default: bool
    is_archived: bool
    position: int
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0  # Computed field

    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    member_id: int
    channel_id: Optional[int] = None

class Message(MessageBase):
    id: int
    member_id: int
    channel_id: Optional[int] = None
    member: Member
    timestamp: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    pk_token: str

class LoginResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"
