"""User model — disesuaikan dengan skema PostgreSQL yang sudah berjalan
di container rag_postgres (integer PK, email, nama_lengkap, level_id)."""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship

from src.core.db import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    nama_lengkap = Column(String(200), nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    role_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="users")
    level_ref = relationship("Level", back_populates="users")

    __table_args__ = (
        CheckConstraint(
            "role_type IN ('super_admin', 'dept_admin', 'user')",
            name="chk_user_role_type",
        ),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"