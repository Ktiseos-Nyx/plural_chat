"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# User/Auth Schemas
class UserBase(BaseModel):
    id: str
    system_name: Optional[str] = None

class UserCreate(BaseModel):
    pk_token: str

class User(UserBase):
    created_at: datetime
    last_sync: Optional[datetime] = None

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
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    member_id: int

class Message(MessageBase):
    id: int
    member_id: int
    member: Member
    timestamp: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenData(BaseModel):
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    pk_token: str

class LoginResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"
