"""Seed data uji sesuai skema-database-postgresql.md §6.

Menjalankan langsung (host Python):
    python3 scripts/seed.py

Di dalam container nanti: python src/seed.py (saat image sudah stabil).
User dibuat via SQLAlchemy ORM agar tabel dibuat dulu bila belum ada.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.getcwd())

from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User uji (password = username, ganti di produksi!)
SEED_USERS = [
    # username,     role,          level, kode_dept
    ("superadmin",  "super_admin", None,  None),
    ("admin_hr",    "dept_admin",  3,     "hr"),
    ("manager_hr",  "user",        3,     "hr"),
    ("staff_hr",    "user",        1,     "hr"),
    ("manager_fin", "user",        3,     "finance"),
]

SEED_DEPARTMENTS = [
    ("hr", "Human Resources"),
    ("finance", "Finance"),
]

SEED_LEVELS = [
    (1, "Staff"),
    (2, "Supervisor"),
    (3, "Manager"),
]


async def seed():
    from src.core.db import engine, AsyncSessionLocal, Base
    # Import semua models agar create_all membuat semua tabel
    from src.models import user as m_user, department as m_dept  # noqa
    from src.models import level as m_level, document as m_doc  # noqa
    from src.models import audit_log as m_audit  # noqa
    from src.models.department import Department
    from src.models.level import Level
    from src.models.user import User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Levels
        for lvl, nama in SEED_LEVELS:
            if not await db.get(Level, lvl):
                db.add(Level(level=lvl, nama_jabatan=nama))
        await db.commit()

        # Departments
        for kode, nama in SEED_DEPARTMENTS:
            existing = (await db.execute(
                select(Department).where(Department.kode == kode)
            )).scalar_one_or_none()
            if not existing:
                db.add(Department(kode=kode, nama=nama))
        await db.commit()

        dept_ids = {}
        for kode, _ in SEED_DEPARTMENTS:
            d = (await db.execute(
                select(Department).where(Department.kode == kode)
            )).scalar_one()
            dept_ids[kode] = d.id
            print(f"[dept] {kode} -> {d.id}")

        # Users
        for username, role, level, dept_kode in SEED_USERS:
            existing = (await db.execute(
                select(User).where(User.username == username)
            )).scalar_one_or_none()
            if existing:
                print(f"[skip] {username} sudah ada")
                continue
            db.add(User(
                username=username,
                password_hash=pwd_context.hash(username + "123"),
                department_id=dept_ids[dept_kode] if dept_kode else None,
                role_type=role,
                level=level,
            ))
            print(f"[user] {username} / {username}123 ({role})")
        await db.commit()

    print("\n=== SEED SELESAI ===")
    print("Login (password = username + '123'):")
    for username, _, _, _ in SEED_USERS:
        print(f"  {username} / {username}123")


if __name__ == "__main__":
    asyncio.run(seed())
