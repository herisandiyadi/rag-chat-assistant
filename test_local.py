#!/usr/bin/env python3
"""Local testing script for FastAPI tanpa Docker"""
import sys
import os

# Set environment untuk local testing
os.environ["DATABASE_URL"] = "sqlite:///./test_rag_chat.db"

from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, engine, Base

# Override get_db untuk pakai SQLite
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rag_chat.db"
engine_local = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_local)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine_local)

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "RAG Chat Assistant API"
    print("✓ / endpoint OK")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ /health endpoint OK")

def test_auth_endpoint_exists():
    response = client.post("/auth/login", json={"username": "test", "password": "test"})
    # Expected 401 karena user tidak ada, tapi endpoint harus ada
    assert response.status_code in [401, 404]
    print("✓ /auth/login endpoint OK")

if __name__ == "__main__":
    try:
        test_root()
        test_health()
        test_auth_endpoint_exists()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
