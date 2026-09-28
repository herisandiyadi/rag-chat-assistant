"""Matriks access control model: resolve levels + access control.

Sengaja dipisah dari `core.security` untuk menghindari circular import
antara services <-> security <-> models <-> db.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def resolve_user_level(db: AsyncSession, user) -> int:
    """
    Resolve hierarki level (angka) dari user.level_id via tabel levels.

    Fallback chain:
    1. user.level_ref.angka  (relationship sudah dimuat)
    2. query tabel levels by level_id
    3. level_id itu sendiri (id == angka pada seed data)
    """
    level_ref = getattr(user, "level_ref", None)
    if level_ref is not None:
        return level_ref.angka

    if getattr(user, "level_id", None) is not None:
        from src.models.level import Level
        row = (await db.execute(
            select(Level).where(Level.id == user.level_id)
        )).scalar_one_or_none()
        if row is not None:
            return row.angka
        return user.level_id

    return 0


def resolve_access_permission(
    user_department_id,
    user_role_type,
    user_level,
    document_department_id,
    document_min_level,
) -> tuple[bool, str]:
    """
    Tentukan apakah user berhak mengakses dokumen.

    Returns: (has_access, reason)
    - (True, "allowed")              -> boleh
    - (False, "invalid")             -> data tidak lengkap (bukan dokumen, abaikan)
    - (False, "cross_department")    -> beda departemen, tolak
    - (False, "insufficient_level")  -> level di bawah min_level, tolak
    """
    # Super admin: akses penuh lintas departemen & level (CEK PERTAMA)
    if user_role_type == "super_admin":
        return True, "allowed"

    # Validasi input — dokumen tanpa departemen/min_level tidak bisa dinilai
    if user_department_id is None or document_department_id is None:
        return False, "invalid"
    if document_min_level is None:
        document_min_level = 1

    # Batas departemen tegas untuk role selain super_admin
    if user_department_id != document_department_id:
        return False, "cross_department"

    # dept_admin boleh lihat semua level di departemennya sendiri
    if user_role_type == "dept_admin":
        return True, "allowed"

    # user biasa: level harus >= min_level
    if user_level is None:
        user_level = 0
    if user_level < document_min_level:
        return False, "insufficient_level"

    return True, "allowed"
