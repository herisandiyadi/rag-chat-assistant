"""Document model definition."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.db import Base


class Document(Base):
    """Document registry model (metadata stored in PostgreSQL, content in Qdrant)."""
    
    __tablename__ = "documents"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    doc_id = Column(String(150), unique=True, nullable=False, index=True)
    judul = Column(String(255), nullable=False)
    
    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=False,
    )
    min_level = Column(Integer, default=1, nullable=False)
    hidden_existence = Column(Boolean, default=False, nullable=False)
    
    owner_admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    versi = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    nama_file = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    department = relationship("Department", back_populates="documents")
    owner_admin = relationship("User", back_populates="documents")
    audit_logs = relationship("AuditLog", back_populates="document")
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived')", name="chk_doc_status"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, doc_id='{self.doc_id}', judul='{self.judul}')>"
