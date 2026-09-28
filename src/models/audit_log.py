"""AuditLog model — dibuat baru oleh aplikasi (UUID vs integer mismatch
dihindari: audit_logs dibuat sendiri via create_all jika belum ada)."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from src.core.db import Base


class AuditLog(Base):
    """Audit log model for tracking user actions."""

    __tablename__ = "app_audit_logs"

    id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    aksi = Column(String(30), nullable=False, index=True)
    hasil = Column(String(30), nullable=False)
    pertanyaan = Column(Text, nullable=True)
    waktu = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, aksi='{self.aksi}', hasil='{self.hasil}')>"