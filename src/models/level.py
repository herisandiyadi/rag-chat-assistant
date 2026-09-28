"""Level model — sesuai schema DB berjalan (id PK, angka unik = hierarki level)."""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.core.db import Base


class Level(Base):
    """Level/jabatan (angka: 1=Staff, 2=Supervisor, 3=Manager)."""

    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    angka = Column(Integer, unique=True, nullable=False)
    nama_jabatan = Column(String(50), nullable=False)

    # Relationships
    users = relationship("User", back_populates="level_ref")

    def __repr__(self) -> str:
        return f"<Level(id={self.id}, angka={self.angka}, nama_jabatan='{self.nama_jabatan}')>"