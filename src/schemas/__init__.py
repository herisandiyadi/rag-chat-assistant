"""Pydantic schemas for API requests/responses."""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Level schemas
class LevelOut(BaseModel):
    id: int
    angka: int
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
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    email: str = ""
    nama_lengkap: str = ""
    department_id: Optional[int] = None
    role_type: str = "user"
    level_id: Optional[int] = None


class UserOut(UserBase):
    id: int
    email: str = ""
    nama_lengkap: str = ""
    department_id: Optional[int] = None
    role_type: str
    level_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[str] = None
    nama_lengkap: Optional[str] = None
    department_id: Optional[int] = None
    role_type: Optional[str] = None
    level_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserList(BaseModel):
    total: int
    users: List[UserOut]


# Document schemas
class DocumentOut(BaseModel):
    id: int
    doc_id: str
    judul: str
    department_id: Optional[int] = None
    min_level: Optional[int] = 1
    hidden_existence: Optional[bool] = False
    versi: Optional[int] = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    total: int
    documents: List[DocumentOut]


# Chat schemas
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[Dict[str, Any]] = []
    status: str


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]


ACCESS_SUCCESS = "success"
ACCESS_DENIED = "access_denied"
NOT_FOUND = "not_found"