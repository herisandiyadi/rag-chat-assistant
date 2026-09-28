"""Document management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core import security
from src.schemas import DocumentOut, DocumentCreate, DocumentList
from src.services.document import DocumentService

router = APIRouter()


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """List documents with pagination."""
    return await DocumentService.list_documents(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    department: str = None,
    min_level: int = 1,
    hidden_existence: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Upload a new document with metadata."""
    return await DocumentService.upload_document(
        db=db,
        user_id=current_user.id,
        file=file,
        department=department,
        min_level=min_level,
        hidden_existence=hidden_existence,
    )


@router.put("/{doc_id}", response_model=DocumentOut)
async def update_document(
    doc_id: int,
    min_level: int = None,
    hidden_existence: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Update document metadata."""
    return await DocumentService.update_document(
        db=db,
        user_id=current_user.id,
        doc_id=doc_id,
        min_level=min_level,
        hidden_existence=hidden_existence,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Delete a document."""
    return await DocumentService.delete_document(
        db=db,
        user_id=current_user.id,
        doc_id=doc_id,
    )
