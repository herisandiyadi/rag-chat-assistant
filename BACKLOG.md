# �� Backlog & Sprint Tracking — RAG Chat Assistant

**Repo:** https://github.com/herisandiyadi/rag-chat-assistant
**Notion Task Board:** Sprint Task Tracking → *Task Board — All Sprints*
**PO:** Product Owner

---

## Status Sprint

| Sprint | Fokus | Status | Gate Utama |
|--------|-------|--------|------------|
| **S1** | Fondasi infra + skema DB + auth + ingestion | ✅ **Selesai** | Container up, login jalan, 1 dokumen ter-index |
| **S2** | Core RAG + access control + 3-kondisi respons | ✅ **Selesai** | Matriks §17 lolos (8 skenario) |
| **S3** | Socket.IO real-time + UI Chat | ✅ **Selesai** | Real-time verifikasi lolos |
| **S4** | Suara ElevenLabs (STT + TTS ekspresif) | ✅ **Selesai** | STT/TTS + emosi sesuai konteks |
| **S5** | Panel admin + hardening + go-live | ✅ **Selesai** | Regresi penuh + audit log aktif |

---

## Implementasi per Sprint

### Sprint 1 — Fondasi ✅
- `docker-compose.yml` — postgres + qdrant + fastapi-app
- `src/models/` — ORM: Department, Level, User, Document, AuditLog
- `src/auth.py` + `src/core/security.py` — JWT auth
- `src/endpoints/seed.py` — seed data uji (5 users, 2 dept, 3 level)
- `src/endpoints/ingest.py` — pipeline ingestion
- `src/core/embedding.py` — embedding lokal e5-base

### Sprint 2 — Core RAG + Access Control ✅ (RISIKO TINGGI)
- `src/rag.py` — logika 3-kondisi (jawab/tidak berhak/tidak ditemukan)
- Akses 2-dimensi: department + level (§2.4)
- Flag `hidden_existence` (§6.2)
- Integrasi GPT-4o-mini + anti-halusinasi 2 lapis (§12)
- Logging token per request

### Sprint 3 — Real-Time + UI Chat ✅
- `src/socket_server.py` — Socket.IO (auth, chat:text, chat:cancel, status, chat:token, chat:sources, chat:done, error)
- `static/index.html` — UI Chat + login + light/dark theme
- Auto-reconnect

### Sprint 4 — Suara ElevenLabs ✅
- `src/voice.py` — STT (voice:start/chunk/end → transkrip) + TTS (streaming audio)
- Label emosi per respons → parameter ekspresivitas

### Sprint 5 — Panel Admin + Hardening ✅
- `src/endpoints/admin.py` — upload/kelola dokumen + kelola user
- Guard upload server-side (dept_admin hanya dept-nya)
- Audit log akses

---

## Prinsip Lintas-Sprint (wajib di semua task)

- **Trust boundary:** dept/role/level selalu dari PostgreSQL, bukan input client (desain §14)
- **Anti-halusinasi:** skip LLM saat retrieval kosong/tak berhak + prompt tegas (desain §12)
- **UI mengikuti DESIGN.md** di tiap layar

---

## Catatan Kalibrasi Terbuka

Nilai `k=4` & score threshold `0.7` adalah **awal**, dikalibrasi saat sprint berjalan dengan pertanyaan & dokumen asli — bukan keputusan final (`desain §16`).

---

## Notion Task Board

47 task telah dicatat ke Notion di bawah page **Sprint Task Tracking — RAG Chat Assistant**:
- 7 task Sprint 1 (mark Done)
- 10 task Sprint 2
- 9 task Sprint 3
- 7 task Sprint 4
- 10 task Sprint 5
- 4 task cross-sprint support (researcher, pmo)

Setiap task punya: Sprint, Assignee, Status, Priority, Story Points.

**API version note:** Notion API 2022-06-28 untuk create database dengan properties. API 2025-09-03 memisahkan database dan data source (properties tidak bisa diset saat create).