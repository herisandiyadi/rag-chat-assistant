# BUG-003: Greeting "hai" menjawab tentang dokumen, bukan balas sapaan

**Severity:** High (UX)
**Status:** ✅ Fixed
**Reporter:** User (Sandi)
**Assignee:** @cybersecurity

## Deskripsi

Ketika user mengirim greeting sederhana seperti "hai", asisten tidak membalas dengan sapaan natural, melainkan langsung mencari dokumen dan menjawab tentang isi modul/data — terlihat seperti menjawab pertanyaan yang tidak ditanyakan.

## Root Cause

Modul `run_server.py` punya fungsi `handle_smalltalk()` dengan regex pattern greeting yang bermasalah:
```
\b(hai|halo|...|p)\b
```
- Trailing `|p\b` menyebabkan **false positive**: string seperti "s o p", "b a p" terdeteksi sebagai greeting.
- Sebaliknya, normalisasi tidak ada — input dengan tanda baca ("hai!!") atau typo ("hii") bisa miss.

## Fix

1. Ekstrak logika ke `src/smalltalk.py` — module terpisah, testable.
2. Tambahkan normalisasi: strip punctuation, collapse repeated chars ("haiii" → "hai").
3. Tambahkan length guard: greeting maksimal 5 kata. Pertanyaan dokumen panjang tidak di-shortcircuit meski mengandung kata greeting.
4. Dictionary-based exact match setelah normalisasi — lebih presisi dari regex.
5. Hapus alternatif `|p` yang buggy.

## Test Results

```
TEST 1: 'hai'               → "Halo! Ada yang bisa saya bantu?" ✅
TEST 2: 'apa itu SOP?'      → "Maaf, tidak ditemukan" (RAG, bukan smalltalk) ✅
TEST 3: 's o p'             → "Maaf, tidak ditemukan" (tidak false-positive) ✅
TEST 4: 'terima kasih'      → "Sama-sama, senang bisa membantu." ✅
```

## Related

- BUG-005/006/007/008: Security hardening (separate commit)
- BUG-010: Retrieval uses dummy embedding (separate issue)