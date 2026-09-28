"""Department model — sesuai schema DB berjalan (integer PK)."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.orm import relationship

from src.core.db import Base


class Department(Base):
    """Department model."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    kode = Column(String(10), unique=True, nullable=False, index=True)
    nama = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=True)

    # Relationships
    users = relationship("User", back_populates="department")
    documents = relationship("Document", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"