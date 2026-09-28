from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# Association table for user departments (for multi-dept support)
user_departments = Table(
    'user_departments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)
)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(String(10), unique=True, index=True, nullable=False)
    nama = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="department")
    documents = relationship("Document", back_populates="department")


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    angka = Column(Integer, unique=True, nullable=False)
    nama_jabatan = Column(String(50), nullable=False)

    users = relationship("User", back_populates="level")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nama_lengkap = Column(String(200), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    role_type = Column(String(20), nullable=False, default="user")  # super_admin, dept_admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="users")
    level = relationship("Level", back_populates="users")
    owned_documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(255), unique=True, index=True, nullable=False)
    judul = Column(String(500), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    owner_admin_id = Column(Integer, ForeignKey("users.id"))
    min_level = Column(Integer, default=1)
    hidden_existence = Column(Boolean, default=False)
    versi = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="documents")
    owner = relationship("User", back_populates="owned_documents")
    chunks = relationship("Chunk", back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(255), ForeignKey("documents.doc_id"), nullable=False)
    teks = Column(String, nullable=False)
    halaman = Column(Integer)
    metadata_json = Column(String)  # JSON string for flexible metadata

    document = relationship("Document", back_populates="chunks")
