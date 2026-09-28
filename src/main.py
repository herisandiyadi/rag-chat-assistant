"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.api import router as api_router
from src.core.db import engine, Base
from src.core.logging import setup_logging
from src.models import department, document, level, user, audit_log  # noqa: F401

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting RAG Chat Assistant...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    
    # Load embedding model
    from src.core.embedding import get_embedding_model
    get_embedding_model()
    logger.info("Embedding model loaded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Chat Assistant...")


app = FastAPI(
    title="RAG Chat Assistant API",
    description="Internal korporat chat assistant with RAG and access control",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


app.include_router(api_router, prefix="/api/v1")
