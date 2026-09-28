"""Admin panel endpoints (Sprint 5).

Document management: upload, list, update min_level, delete.
User management: create, deactivate, list per department.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document, Department, Level
from dependencies import get_current_active_user
from auth import get_password_hash
import uuid

router = APIRouter()


def require_admin(user: User = Depends(get_current_active_user)):
    if user.role_type not in ("super_admin", "dept_admin"):
        raise HTTPException(403, "Akses admin diperlukan")
    return user


@router.get("/documents")
def list_documents(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(Document)
    if user.role_type == "dept_admin":
        q = q.filter(Document.department_id == user.department_id)
    docs = q.all()
    return [{"doc_id": d.doc_id, "judul": d.judul, "min_level": d.min_level,
             "hidden_existence": d.hidden_existence, "versi": d.versi} for d in docs]


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    min_level: int = Form(1),
    hidden_existence: bool = Form(False),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # Guard: dept_admin hanya boleh dept-nya sendiri
    if user.role_type == "dept_admin":
        dept = db.query(Department).filter(Department.kode == department).first()
        if not dept or dept.id != user.department_id:
            raise HTTPException(403, "Anda hanya boleh upload ke departemen Anda sendiri")

    content = await file.read()
    doc_id = f"doc-{uuid.uuid4().hex[:12]}"
    # ponytail: real pipeline will chunk & embed; here we store metadata only
    doc = Document(
        doc_id=doc_id,
        judul=file.filename,
        department_id=dept.id if dept else None,
        owner_admin_id=user.id,
        min_level=min_level,
        hidden_existence=hidden_existence,
    )
    db.add(doc)
    db.commit()
    return {"doc_id": doc_id, "judul": file.filename, "min_level": min_level}


@router.patch("/documents/{doc_id}/access")
def update_access(
    doc_id: str,
    min_level: int = None,
    hidden_existence: bool = None,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Dokumen tidak ditemukan")
    if user.role_type == "dept_admin" and doc.department_id != user.department_id:
        raise HTTPException(403, "Di luar departemen Anda")
    if min_level is not None:
        doc.min_level = min_level
    if hidden_existence is not None:
        doc.hidden_existence = hidden_existence
    db.commit()
    return {"doc_id": doc_id, "min_level": doc.min_level, "hidden_existence": doc.hidden_existence}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Dokumen tidak ditemukan")
    if user.role_type == "dept_admin" and doc.department_id != user.department_id:
        raise HTTPException(403, "Di luar departemen Anda")
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}


@router.get("/users")
def list_users(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(User)
    if user.role_type == "dept_admin":
        q = q.filter(User.department_id == user.department_id)
    users = q.all()
    return [{"id": u.id, "username": u.username, "nama": u.nama_lengkap,
             "role": u.role_type, "dept_id": u.department_id, "level_id": u.level_id,
             "aktif": u.is_active} for u in users]


@router.post("/users/create")
def create_user(
    username: str,
    email: str,
    password: str,
    nama_lengkap: str,
    department_kode: str = None,
    level_angka: int = 1,
    role_type: str = "user",
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # Guard: dept_admin tidak boleh buat user di dept lain
    if user.role_type == "dept_admin" and department_kode:
        dept = db.query(Department).filter(Department.kode == department_kode).first()
        if not dept or dept.id != user.department_id:
            raise HTTPException(403, "Di luar departemen Anda")

    hashed = get_password_hash(password)
    dept_id = dept.id if dept else None
    level = db.query(Level).filter(Level.angka == level_angka).first()
    new_user = User(
        username=username, email=email, password_hash=hashed,
        nama_lengkap=nama_lengkap, department_id=dept_id,
        level_id=level.id if level else None, role_type=role_type, is_active=True
    )
    db.add(new_user)
    db.commit()
    return {"id": new_user.id, "username": username}