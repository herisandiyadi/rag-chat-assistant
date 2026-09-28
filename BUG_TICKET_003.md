# BUG-003: Greeting tidak dikenali — chat menjawab dari dokumen

**Ticket:** BUG-003
**Status:** ✅ RESOLVED
**Severity:** Medium (UX — percakapan terasa tidak natural)
**Reported by:** Sandi (user)
**Fixed by:** @developerofficer_bot (commit 4c74e48)
**Verified by:** @productmanagero_bot (PMO) — 2026-09-28

---

## Gejala

User mengetik `hai` → asisten membalas dengan pembahasan dokumen/modul,
bukan menyapa balik.

## Akar Masalah

`chat:text` handler langsung memanggil `decide_response()` (RAG) tanpa
mendeteksi intent percakapan. Sapaan/obrolan ringan diperlakukan sebagai
pertanyaan dokumen → retrieval → jawaban dari konteks dokumen.

## Perbaikan

Intent classification layer (`src/smalltalk.py`) ditambahkan SEBELUM RAG:

- `handle_smalltalk(question)` → cek greeting, thanks, how-are-you, who-are-you
- Jika match → balas natural, **skip** RAG sepenuhnya
- Jika tidak match → lanjut ke alur RAG seperti biasa

Kondisi yang ditangani:
| Input | Respons |
|-------|---------|
| `hai`, `halo`, `hi`, `selamat pagi` | Sapaan balik + tawaran bantuan |
| `terima kasih`, `makasih` | "Sama-sama!" |
| `apa kabar` | "Baik, terima kasih!" |
| `siapa kamu` | Perkenalan asisten RAG |

---

## Verifikasi (test end-to-end via Socket.IO)

Test di `/root/rag-chat-app/test_greeting_bug.py`:

```
[OK] login staff_hr
[OK] socket connected + auth

--- TEST 1: 'hai' ---
Reply: Halo! 👋 Saya asisten RAG internal Anda...
[PASS] greeting natural

--- TEST 2: 'terima kasih' ---
Reply: Sama-sama! 😊 Jangan ragu bertanya lagi...
[PASS] thanks natural

--- TEST 3: 'siapa kamu' ---
Reply: Saya asisten chat berbasis RAG...
[PASS] identity natural

--- TEST 4: doc question 'apa isi sop umum hr' ---
Statuses: ['mencari dokumen']
[PASS] doc question flows through RAG

--- TEST 5: 'HALO!' (caps) ---
Reply: Halo! 👋 ...
[PASS] caps greeting

=== ALL TESTS PASSED ===
```

**Catatan:** Test 4 (pertanyaan dokumen) statusnya `mencari dokumen` →
menandakan RAG tetap jalan untuk pertanyaan non-sapaan. Belum ada dokumen
ter-index di Qdrant, jadi jawaban akhir masih kosong (diluar scope bug ini —
bagian dari Sprint 2 ingestion).

---

## Regression Guard

Tes di atas harus tetap lulus setiap kali `handle_smalltalk` diubah.
Run: `python3 test_greeting_bug.py` (server harus jalan di :8000).
