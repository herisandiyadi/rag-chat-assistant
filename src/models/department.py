"""Department model definition."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.db import Base


class Department(Base):
    """Department model."""
    
    __tablename__ = "departments"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    kode = Column(String(50), unique=True, nullable=False, index=True)
    nama = Column(String(150), nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="department")
    documents = relationship("Document", back_populates="department")
    
    def __repr__(self) -> str:
        return f"<Department(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"
