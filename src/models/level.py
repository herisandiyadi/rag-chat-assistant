"""Level/jabatan model definition."""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.core.db import Base


class Level(Base):
    """Level/jabatan model (1=Staff, 2=Supervisor, 3=Manager)."""
    
    __tablename__ = "levels"
    
    level = Column(Integer, primary_key=True, nullable=False)
    nama_jabatan = Column(String(100), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="level")
    
    def __repr__(self) -> str:
        return f"<Level(level={self.level}, nama_jabatan='{self.nama_jabatan}')>"
