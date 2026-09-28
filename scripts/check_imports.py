#!/usr/bin/env python3
"""Import smoke test — pastikan SEMUA modul bisа di-import sebelum Docker build.

Menangkap NameError/ImportError seperti: name 'Dict' is not defined,
cannot import name 'X' from 'src.schemas', dsb.
Dijalankan di host Python (venv punya deps-nya).
"""
import importlib
import os
import sys
import traceback

sys.path.insert(0, os.getcwd())

MODULES = [
    "config.settings",
    "src.core.db",
    "src.core.security",
    "src.core.access",
    "src.core.embedding",
    "src.core.logging",
    "src.schemas",
    "src.models.user",
    "src.models.department",
    "src.models.level",
    "src.models.document",
    "src.models.audit_log",
    "src.api.router",
    "src.api.endpoints.auth",
    "src.api.endpoints.chat",
    "src.api.endpoints.documents",
    "src.api.endpoints.users",
    "src.services.chat",
    "src.services.user",
    "src.services.document",
    "src.services.openai_service",
    "src.rag.vector_search",
    "src.ingestion.ingest",
    "src.main",
]

failed = []
for m in MODULES:
    try:
        importlib.import_module(m)
        print(f"  [ok] {m}")
    except Exception as e:
        failed.append((m, e))
        print(f"  [FAIL] {m}")

if failed:
    print("\n" + "=" * 60)
    print(f"{len(failed)} module gagal di-import:")
    for m, e in failed:
        print(f"\n--- {m} ---")
        # tampilkan baris terakhir traceback yang relevan
        tb = traceback.format_exc().strip().splitlines()
        print(f"{type(e).__name__}: {e}")
    sys.exit(1)

print("\n=== ALL MODULES IMPORT OK ===")
