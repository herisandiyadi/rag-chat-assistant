# Sprint Plan — RAG Chat Assistant (Internal Korporat)

> Rencana task per sprint. Basis urutan: `ringkasan-arsitektur-final.md §7` (roadmap 9-fase),
> dipetakan agresif ke **5 sprint × 2 minggu (~10 minggu)**.
> Acuan desain: `desain-fitur-chat-assistant-rag.md`, `arsitektur-rag-chat-assistant.md`, `DESIGN.md`.
> Dokumen ini **tidak menduplikasi** isi dokumen tsb — merujuk lewat pasal (§).
>
> Status: Blueprint. Belum ada kode. Kurs/biaya = estimasi perencanaan (verifikasi saat eksekusi).

---

## Ringkasan Peta Sprint

| Sprint | Fokus | Area risiko |
|--------|-------|-------------|
| **S1** | Fondasi infra + skema DB + auth + ingestion 1 dokumen | Setup |
| **S2** | Core RAG + logika akses 2-dimensi + 3-kondisi respons | **Tinggi (access control)** |
| **S3** | Socket.IO real-time (status + streaming) + UI Chat | Sedang |
| **S4** | Integrasi suara ElevenLabs (STT + TTS ekspresif) | **Tinggi (pihak ketiga)** |
| **S5** | Panel admin (dokumen + user) + hardening + go-live | Sedang |

Prinsip lintas-sprint: **trust boundary** (dept/role/level selalu dari PostgreSQL, `desain §14`),
**anti-halusinasi** (`desain §12`), dan **UI mengikuti `DESIGN.md`** di tiap layar.

---

## Sprint 1 — Fondasi (Infra + DB + Auth + Ingestion)

Menutup Fase 0–3 roadmap. Tujuan: sistem bisa login, resolve identitas, dan meng-index 1 dokumen uji.

### Infrastruktur
- [ ] Siapkan VPS Ubuntu 22.04 + Docker + Docker Compose (`arsitektur §7, §8`).
- [ ] `docker-compose.yml`: service `postgres`, `qdrant`, `fastapi-app` dengan named volume persist.
- [ ] Secret management via `.env` (tidak masuk git) — API key & DB password.
- [ ] Domain + SSL disiapkan (Nginx/Certbot) untuk WSS produksi (bisa ditunda ke S5 bila dev pakai localhost).

### Skema Database
- [ ] Implementasi skema PostgreSQL sesuai `skema-database-postgresql.md` (users, departments, levels, documents).
- [ ] Seed data uji sesuai `desain §17` (Super-admin, Admin-HR, Manager HR lvl3, Staff HR lvl1, Manager Finance lvl3).

### Auth
- [ ] Login internal username/password → sesi JWT (`desain §15`).
- [ ] Resolve `department` / `role_type` / `level` dari PostgreSQL saat sesi (trust boundary, `desain §14`).
- [ ] **UI Login** sesuai `DESIGN.md §8.1` — layar tunggal terfokus, error autentikasi aman (tidak bocor mana yang salah).

### Ingestion (dasar)
- [ ] Embedding lokal `multilingual-e5-base` (aturan: model ingestion = model query, `arsitektur §3.3`).
- [ ] Qdrant: koleksi tunggal, chunk + payload metadata (`department`, `min_level`, `hidden_existence`, `doc_id`, `versi`, `arsitektur §4.1` + `desain §4.2`).
- [ ] Pipeline ingest 1 dokumen uji (ekstrak → chunk 500–800 char → embed → store).

### DoD Sprint 1
- [ ] Semua container jalan via `docker compose up`, data persist setelah restart.
- [ ] User uji bisa login; identitas (dept/role/level) ter-resolve benar dari DB.
- [ ] 1 dokumen uji ter-index di Qdrant dengan metadata lengkap.
- [ ] UI Login lolos checklist `DESIGN.md §11` yang relevan (keyboard, kontras, tema).

---

## Sprint 2 — Core RAG + Access Control (RISIKO TINGGI)

Menutup Fase 4 roadmap + inti keamanan. Tujuan: pertanyaan teks menghasilkan 3-kondisi respons yang benar. Belum real-time/suara.

### Retrieval
- [ ] Embed pertanyaan + search Qdrant top-k (`k=4` awal) + score threshold (`0.7` awal) — nilai **dikalibrasi saat uji**, bukan final (`desain §16`).
- [ ] Filter Qdrant `department` + `min_level` untuk jalur "berhak" (`desain §6.1`).

### Logika Akses (inti, `desain §2.4`)
- [ ] Aturan baca: `super_admin` (semua) / `dept_admin` (dept-nya) / `user` (dept + level ≥ min_level).
- [ ] Batas departemen tegas + batas level (`desain §14`).

### 3-Kondisi Respons (`desain §6`)
- [ ] ✅ Berhak → jawab dari konteks. 🔒 Ada tapi tak berhak → "tidak memiliki akses". ❓ Tak ada → "tidak ditemukan".
- [ ] Flag `hidden_existence` → user tak berhak dapat "tidak ditemukan", bukan "tidak memiliki akses" (`desain §6.2`).

### Generation + Anti-Halusinasi
- [ ] Integrasi GPT-4o-mini via API (`arsitektur §3.6`).
- [ ] Lapis 1: skip LLM saat retrieval kosong / tak berhak. Lapis 2: prompt tegas "jawab hanya dari konteks" (`desain §12`).
- [ ] Tone teks profesional–hangat; bahasa jawaban mengikuti bahasa pertanyaan (`desain §12A`).
- [ ] Batasi riwayat percakapan + `max_tokens` + logging token per request (`arsitektur §6` — prioritas #1 sebelum go-live).

### DoD Sprint 2
- [ ] **Seluruh matriks skenario `desain §17` lolos** (Staff HR, Manager HR, Manager Finance, Admin-HR, Super-admin, "resep rendang" → tidak ditemukan). Ini gate utama sprint.
- [ ] Logging token aktif; tidak ada chunk lintas-dept/over-level yang bocor ke LLM.

---

## Sprint 3 — Real-Time + UI Chat

Menutup Fase 5 roadmap. Tujuan: pengalaman chat teks penuh, real-time, sesuai `DESIGN.md`.

### Socket.IO (`desain §7`)
- [ ] Server FastAPI + python-socketio; event `auth`, `chat:text`, `chat:cancel` (client→server).
- [ ] Event server→client: `status`, `chat:token` (streaming), `chat:sources`, `chat:done`, `error`.
- [ ] Auto-reconnect + pemulihan koneksi.

### UI Chat (layar utama, `DESIGN.md §8.2`)
- [ ] Area chat sebagai halaman; bubble asisten vs user (variasi RHYTHM 2).
- [ ] Baris status real-time tenang ("mencari dokumen" → "sedang berpikir", motion §7), bukan spinner telanjang.
- [ ] 3-kondisi respons dibedakan dengan makna: jawaban + blok sumber (`doc_id`/versi `text-mono`); 🔒 kartu amber sopan; ❓ teks netral.
- [ ] Empty state percakapan baru: sebut yang bisa ditanyakan + batas akses user (`DESIGN.md §9`).
- [ ] Error state (koneksi putus) menyebut sebab + "menyambung kembali" (`status-error`).
- [ ] Tema light/dark toggle berfungsi; keyboard-only lolos (`DESIGN.md §2, §10`).

### DoD Sprint 3
- [ ] Verifikasi real-time `desain §17`: `status` berurutan; `chat:token` mengalir; koneksi pulih otomatis.
- [ ] UI Chat lolos checklist `DESIGN.md §11`.

---

## Sprint 4 — Suara ElevenLabs (RISIKO TINGGI: pihak ketiga)

Menutup Fase 5 (suara) roadmap. Tujuan: STT masuk + TTS ekspresif keluar, terintegrasi ke alur chat. Suara **opsional** — mode teks tetap utuh.

### STT (`desain §11`)
- [ ] Event `voice:start` / `voice:chunk` / `voice:end` (client→server).
- [ ] Audio user → ElevenLabs STT → transkrip → `stt:transcript` → masuk alur RAG.

### TTS Ekspresif (`desain §11, §12A.3`)
- [ ] Teks jawaban → ElevenLabs TTS streaming → `tts:audio` ke client.
- [ ] Label emosi per respons (jawaban/penolakan/tidak-ditemukan) → parameter ekspresivitas voice.
- [ ] Pesan penolakan & "tidak ditemukan" **juga** disuarakan, nada sopan-tenang (`desain §12A.2`).

### UI Suara (`DESIGN.md §8.2, §7`)
- [ ] Tombol mic; indikator "merekam/berbicara" berdenyut **hanya selama aktif**, berhenti saat idle (R-31/§7).
- [ ] Alur teks penuh tetap jalan tanpa suara (a11y, `DESIGN.md §10`).

### Biaya & Privasi (`desain §11, §13`)
- [ ] Verifikasi pricing resmi ElevenLabs; monitoring biaya TTS (tanpa batas panjang jawaban = risiko biaya, `desain §13`).
- [ ] Catat konsekuensi privasi: audio user dikirim ke pihak ketiga; API key aman.

### DoD Sprint 4
- [ ] Verifikasi suara `desain §17`: STT & TTS berfungsi; emosi voice menyesuaikan konteks; penolakan disuarakan.
- [ ] Kalibrasi ekspresi agar natural untuk konteks korporat (tidak berlebihan).

---

## Sprint 5 — Panel Admin + Hardening + Go-Live

Menutup Fase 6–7 roadmap. Tujuan: admin bisa kelola dokumen & user; sistem siap produksi.

### Panel Admin Dokumen (`DESIGN.md §8.3`, `desain §9`)
- [ ] Upload dokumen + set `department` / `min_level` / `hidden_existence`; guard dept server-side (dept_admin hanya dept-nya, `desain §14`).
- [ ] Daftar dokumen: kolom Judul · Departemen · min_level (label Staff/Supervisor/Manager) · hidden_existence (badge "Tersembunyi") · Versi · Aksi.
- [ ] Kelola versi: update (hapus chunk lama by `doc_id`, ingest baru, naikkan versi) & hapus (`arsitektur §9`).
- [ ] Ubah `min_level`/akses via `set_payload` tanpa re-embedding (`arsitektur §5.2`).
- [ ] Empty & loading (ingestion) state menyebut sebab + aksi (`DESIGN.md §9`).

### Panel Kelola User (`DESIGN.md §8.4`)
- [ ] dept_admin buat/nonaktifkan user di dept-nya; super_admin lintas dept (`desain §3`).
- [ ] Daftar user: Nama · Username · Departemen · Role · Level · Status aktif · Aksi.
- [ ] Placeholder jujur (bukan `John Doe`), sel kosong tetap kosong (`DESIGN.md §9`).

### Hardening (`arsitektur §10`, `desain §14`)
- [ ] Audit log akses (allowed/denied) + siapa upload/ubah `min_level`.
- [ ] Rate limit; validasi/sanitasi input.
- [ ] Backup berkala Qdrant & PostgreSQL.
- [ ] Nginx + SSL produksi (WSS) bila belum di S1.
- [ ] Monitoring biaya token & TTS aktif.

### DoD Sprint 5 (Go-Live)
- [ ] Guard upload `desain §17`: Admin-HR upload ke Finance → ditolak.
- [ ] Seluruh skenario `desain §17` masih lolos end-to-end (regresi).
- [ ] Semua surface lolos checklist `DESIGN.md §11`.
- [ ] Audit log, backup, rate limit, monitoring biaya berjalan.

---

## Di Luar Scope (ditakeout/ditunda — jangan muncul sbg nav mati)

Sesuai `desain §15, §16` — **tidak** dikerjakan di 5 sprint ini:
- Telegram gateway (ditakeout).
- Assignment per-user-spesifik (diganti mekanisme `min_level`).
- Level tambahan (Direktur/Kepala Divisi) — struktur siap diperluas.
- User lintas departemen (saat ini 1 user = 1 dept).
- Redis cache.

---

## Catatan Kalibrasi (terbuka, `desain §16`)

Nilai `k=4` & score threshold `0.7` adalah **awal**, dikalibrasi di S2 dengan pertanyaan & dokumen asli — bukan keputusan final di awal.
