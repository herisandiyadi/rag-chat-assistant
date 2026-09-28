"""Document model — sesuai schema DB berjalan (integer PK)."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship

from src.core.db import Base


class Document(Base):
    """Document registry (metadata di PostgreSQL, chunk/vector di Qdrant)."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    doc_id = Column(String(255), unique=True, nullable=False, index=True)
    judul = Column(String(500), nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    owner_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    min_level = Column(Integer, nullable=True, default=1)
    hidden_existence = Column(Boolean, nullable=True, default=False)
    versi = Column(Integer, nullable=True, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, doc_id='{self.doc_id}', judul='{self.judul}')>"