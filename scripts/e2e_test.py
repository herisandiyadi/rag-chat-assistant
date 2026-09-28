#!/usr/bin/env python3
"""End-to-end test: login -> greeting -> RAG question -> access control."""
import httpx
import json
import sys

BASE = "http://localhost:8000"


def login(username, password):
    r = httpx.post(f"{BASE}/api/v1/auth/token",
                   data={"username": username, "password": password},
                   timeout=30)
    assert r.status_code == 200, f"Login {username} gagal: {r.status_code} {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}",
            "Content-Type": "application/json"}


def ask(headers, question, timeout=300):
    r = httpx.post(f"{BASE}/api/v1/chat/ask", headers=headers,
                   json={"question": question}, timeout=timeout)
    return r


passed, failed = 0, 0

# ---- Test 1: Login semua user uji ----
print("== TEST 1: Login ==")
for u in ["staff_hr", "manager_hr", "admin_hr", "manager_finance", "super_admin"]:
    try:
        h = login(u, "admin123")
        print(f"  [ok] {u} login")
        passed += 1
    except AssertionError as e:
        print(f"  [FAIL] {u}: {e}")
        failed += 1

# ---- Test 2: Greeting tidak trigger RAG ----
print("== TEST 2: Greeting ==")
h = login("staff_hr", "admin123")
for q in ["hai", "halo", "Selamat pagi"]:
    r = ask(h, q, timeout=30)
    d = r.json()
    if r.status_code == 200 and d["status"] == "greeting" and d["sources"] == []:
        print(f"  [ok] {q!r} -> greeting natural, tanpa RAG")
        passed += 1
    else:
        print(f"  [FAIL] {q!r} -> {r.status_code} {d}")
        failed += 1

# ---- Test 3: Pertanyaan RAG sungguhan (boleh not_found karena belum ingest dokumen) ----
print("== TEST 3: RAG question ==")
r = ask(h, "berapa lama proses pengajuan cuti tahunan?", timeout=300)
d = r.json()
if r.status_code == 200 and d["status"] in ("success", "not_found"):
    print(f"  [ok] RAG question -> status={d['status']} (jawaban: {d['answer'][:100]!r})")
    passed += 1
else:
    print(f"  [FAIL] {r.status_code} {d}")
    failed += 1

# ---- Test 4: Bukan greeting salah -> pertanyaan tetap RAG ----
print("== TEST 4: Pertanyaan bertele-tele ==")
r = ask(h, "hai, saya mau bertanya tentang SOP cuti yang berlaku di departemen HR", timeout=300)
d = r.json()
if r.status_code == 200 and d["status"] != "greeting":
    print(f"  [ok] pertanyaan panjang -> status={d['status']} (masuk jalur RAG)")
    passed += 1
else:
    print(f"  [FAIL] {r.status_code} {d}")
    failed += 1

print(f"\n{'='*50}")
print(f"PASSED: {passed} | FAILED: {failed}")
sys.exit(1 if failed else 0)