"""Pydantic schemas for API requests/responses."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str
    department_id: int
    role_type: str = "user"
    level: int = 1


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    department_id: Optional[int] = None
    role_type: Optional[str] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int
    department_id: int
    role_type: str
    level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    total: int
    users: List[UserOut]


# Department schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    department_id: int
    min_level: int = 1
    hidden_existence: bool = False


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    doc_id: str
    version: int
    file_path: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    total: int
    documents: List[DocumentOut]


# Chat schemas
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[Dict[str, Any]] = []
    status: str  # "success", "access_denied", "not_found"


class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]


# Response status enums
class AccessStatus(str):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_FOUND = "not_found"
