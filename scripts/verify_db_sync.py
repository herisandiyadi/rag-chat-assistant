"""Verifikasi model SQLAlchemy cocok dengan skema DB yang BERJALAN.

Bukan cuma import — tapi select sungguhan dari Postgres, join ke levels,
dan validasi login hash dari DB user uji.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.getcwd())

from sqlalchemy import select
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def main():
    from src.core.db import AsyncSessionLocal
    from src.models.user import User
    from src.models.level import Level
    from src.models.department import Department
    from src.models import document as _doc  # noqa: F401 — register Document di registry
    from src.models.document import Document
    from src.core.access import resolve_user_level, resolve_access_permission

    async with AsyncSessionLocal() as db:
        # 1. Semua user terbaca via ORM (model cocok dengan tabel)
        users = (await db.execute(select(User).order_by(User.id))).scalars().all()
        print(f"[ok] {len(users)} users terbaca dari Postgres via ORM:")
        for u in users:
            print(f"     - {u.username:16s} role={u.role_type:12s} dept={u.department_id} level_id={u.level_id}")

        # 2. Join/relationship levels -> resolve hierarki angka
        levels = (await db.execute(select(Level).order_by(Level.id))).scalars().all()
        print(f"[ok] {len(levels)} levels: " + ", ".join(f"{l.id}={l.angka}/{l.nama_jabatan}" for l in levels))

        # 3. resolve_user_level() bekerja
        print("[ok] resolve_user_level per user:")
        for u in users:
            lv = await resolve_user_level(db, u)
            print(f"     - {u.username:16s} -> level={lv}")

        # 4. Login hash verifikasi terhadap password uji admin123
        print("[ok] verifikasi password bcrypt (admin123):")
        ok = 0
        for u in users:
            if pwd_ctx.verify("admin123", u.password_hash):
                ok += 1
                print(f"     [MATCH] {u.username} / admin123")
            else:
                print(f"     [skip ] {u.username}")
        assert ok > 0, "Tidak ada user yang cocok dengan password admin123"

        # 5. Matriks akses dengan data NYATA dari DB
        print("[ok] matriks akses memakai data DB nyata:")
        depts = (await db.execute(select(Department))).scalars().all()
        hr = next(d for d in depts if d.kode == "hr")
        fin = next(d for d in depts if d.kode == "finance")
        staff = next(u for u in users if u.username == "staff_hr")
        mgr = next(u for u in users if u.username == "manager_hr")
        sup = next(u for u in users if u.username == "super_admin")

        staff_lv = await resolve_user_level(db, staff)
        mgr_lv = await resolve_user_level(db, mgr)

        # dokumen HR min_level 3 (rahasia)
        got, why = resolve_access_permission(staff.department_id, staff.role_type, staff_lv, hr.id, 3)
        print(f"     staff_hr (lv{staff_lv}) -> dokumen HR min_level 3: allowed={got} ({why})")
        assert got is False, "staff_hr tidak boleh baca dokumen min_level 3"

        got, why = resolve_access_permission(mgr.department_id, mgr.role_type, mgr_lv, hr.id, 3)
        print(f"     manager_hr (lv{mgr_lv}) -> dokumen HR min_level 3: allowed={got} ({why})")
        assert got is True, "manager_hr harus bisa baca dokumen min_level 3"

        got, why = resolve_access_permission(mgr.department_id, mgr.role_type, mgr_lv, fin.id, 1)
        print(f"     manager_hr -> dokumen Finance: allowed={got} ({why})")
        assert got is False, "manager_hr tidak boleh lintas departemen"

        got, why = resolve_access_permission(sup.department_id, sup.role_type, 999, fin.id, 3)
        print(f"     super_admin -> dokumen Finance min_level 3: allowed={got} ({why})")
        assert got is True, "super_admin harus bisa akses semua"

    print("\n=== DB SYNC VERIFIED ===")


if __name__ == "__main__":
    asyncio.run(main())
