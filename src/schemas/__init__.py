"""Pydantic schemas for API requests/responses."""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Level schemas
class LevelOut(BaseModel):
    level: int
    nama_jabatan: str

    class Config:
        from_attributes = True


# Department schemas
class DepartmentBase(BaseModel):
    kode: str
    nama: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# User schemas (sesuai tabel users di skema PostgreSQL)
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    department_id: Optional[UUID] = None
    role_type: str = "user"
    level: Optional[int] = None


class UserUpdate(BaseModel):
    password: Optional[str] = None
    department_id: Optional[UUID] = None
    role_type: Optional[str] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: UUID
    department_id: Optional[UUID] = None
    role_type: str
    level: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    total: int
    users: List[UserOut]


# Document schemas
class DocumentBase(BaseModel):
    judul: str
    department_id: UUID
    min_level: int = 1
    hidden_existence: bool = False


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: UUID
    doc_id: str
    versi: int
    status: str
    nama_file: Optional[str] = None
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
    role: str
    content: str
    timestamp: datetime


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[Dict[str, Any]] = []
    status: str


class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]


# Response status constants
ACCESS_SUCCESS = "success"
ACCESS_DENIED = "access_denied"
NOT_FOUND = "not_found"
