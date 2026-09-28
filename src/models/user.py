"""User model definition."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship

from src.core.db import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=True,
    )
    role_type = Column(String(20), nullable=False)
    level = Column(Integer, ForeignKey("levels.level"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    department = relationship("Department", back_populates="users")
    level_ref = relationship("Level", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    documents = relationship("Document", back_populates="owner_admin")
    
    __table_args__ = (
        CheckConstraint(
            "role_type IN ('super_admin', 'dept_admin', 'user')",
            name="chk_user_role_type",
        ),
        CheckConstraint(
            "(role_type = 'super_admin' AND department_id IS NULL) OR "
            "(role_type IN ('dept_admin', 'user') AND department_id IS NOT NULL)",
            name="chk_dept_role",
        ),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
