"""Main RAG Chat Assistant Application"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from endpoints.auth import router as auth_router
from endpoints.seed import router as seed_router
from endpoints.ingest import router as ingest_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Chat Assistant API",
    description="Internal chat assistant with RAG and multi-department access control"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "RAG Chat Assistant API", "version": "1.0.0"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(seed_router, prefix="/seed")
app.include_router(ingest_router, prefix="/ingest")
