from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document, Chunk
from auth import get_password_hash

router = APIRouter()

@router.post("/seed")
def seed(seed_data: bool = True, db: Session = Depends(get_db)):
    """Seed database with initial data"""
    try:
        # Import here to avoid circular dependency
        from seed_data import seed_data as seed_func
        result = seed_func(db)
        return {"message": "Seed completed", "success": result}
    except Exception as e:
        return {"message": f"Error seeding: {str(e)}", "success": False}
