"""Audit log model definition."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.db import Base


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=True,
    )
    aksi = Column(String(30), nullable=False, index=True)
    hasil = Column(String(30), nullable=False)
    pertanyaan = Column(Text, nullable=True)
    
    waktu = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    document = relationship("Document", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, aksi='{self.aksi}', hasil='{self.hasil}')>"
