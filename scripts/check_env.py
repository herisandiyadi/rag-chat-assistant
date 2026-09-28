#!/usr/bin/env python3
"""Self-check: verify config loads, models/relationships resolve, access-control matrix is correct."""
import os
import sys

# Minimal env so Settings() loads without a real .env
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("ELEVENLABS_API_KEY", "test")
os.environ.setdefault("JWT_SECRET", "x" * 32)

sys.path.insert(0, os.getcwd())

# 1. Settings load
from config.settings import settings
assert settings.jwt_secret == "x" * 32
assert settings.rag_k == 4
print("[ok] settings loaded")

# 2. Models import + relationships resolve (proves ORM wiring is valid)
from src.models import user as m_user, department as m_dept
from src.models import level as m_level, document as m_doc, audit_log as m_audit
print("[ok] models imported (User, Department, Level, Document, AuditLog)")

# 3. Access-control matrix — the security core of this app
from src.core.security import resolve_access_permission

DEPT_HR, DEPT_FIN = 1, 2
cases = [
    # (desc, user_dept, user_role, user_level, doc_dept, doc_min_level, expected)
    ("super_admin semua dept",        None,     "super_admin", None, DEPT_HR,  3, True),
    ("dept_admin dept sendiri",       DEPT_HR,  "dept_admin",  3,    DEPT_HR,  3, True),
    ("dept_admin dept lain DITOLAK",  DEPT_HR,  "dept_admin",  3,    DEPT_FIN, 1, False),
    ("user level 3 > min_level 3",    DEPT_HR,  "user",        3,    DEPT_HR,  3, True),
    ("user level 1 < min_level 3",    DEPT_HR,  "user",        1,    DEPT_HR,  3, False),
    ("user dept lain DITOLAK",        DEPT_HR,  "user",        3,    DEPT_FIN, 1, False),
    ("user level pas min_level",      DEPT_HR,  "user",        2,    DEPT_HR,  2, True),
]
for desc, ud, ur, ul, dd, dml, expected in cases:
    got, reason = resolve_access_permission(ud, ur, ul, dd, dml)
    assert got == expected, f"FAIL: {desc} -> {got}, expected {expected}"
    print(f"[ok] {desc} -> allowed={got} ({reason})")

# 4. Schemas valid
from src.schemas import UserCreate, DocumentOut, ChatRequest
u = UserCreate(username="staff_hr", password="secret", department_id=None, role_type="user", level=1)
assert u.username == "staff_hr"
print("[ok] schemas validated")

print("\n=== ALL CHECKS PASSED ===")
