"""API router aggregation."""

from fastapi import APIRouter

from src.api.endpoints import auth, chat, documents, users

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(users.router, prefix="/users", tags=["users"])
