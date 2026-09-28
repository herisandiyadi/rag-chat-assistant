# DESIGN.md — RAG Chat Assistant (Internal Korporat)

> Sumber identitas visual produk. Setiap treatment di sini punya **alasan tertulis**;
> apa pun yang tidak ada alasannya adalah default dan harus dibuang (antislop, purpose test).
> Baca bersama `antislop.md` (core) + `antislop-ui.md`. Dokumen ini menjawab "Design Read".
>
> **Karakter produk:** tool internal karyawan untuk membaca dokumen & mengobrol dengan asisten,
> lintas departemen (HR/Finance/Legal/dst.), menangani dokumen sensitif dengan access control
> berjenjang. Sebagian besar layar adalah **signed-in app views** (mode operate + read),
> bukan halaman persuasi. Kata kuncinya: **kepercayaan, kerahasiaan, kejelasan** — bukan playful, bukan flashy.
>
> Status: Blueprint. Belum ada kode UI. Dokumen desain terkait:
> `ringkasan-arsitektur-final.md`, `desain-fitur-chat-assistant-rag.md`, `arsitektur-rag-chat-assistant.md`.

---

## 1. Prinsip Arah (yang membedakan dari "sterile default")

1. **Kejelasan di atas gaya.** Ini alat kerja, bukan showcase. Tiap elemen melayani sebuah keputusan atau sebuah bacaan.
2. **Warna membawa informasi, bukan dekorasi.** Accent dan warna status punya tugas; tidak ada yang tampil hanya "supaya terlihat didesain".
3. **Tenang secara default, ekspresif hanya di state nyata.** Halaman diam sampai ada state sistem yang benar-benar berubah (streaming, suara aktif, error).
4. **Jujur soal data & akses.** Angka nyata atau placeholder jujur; pesan penolakan sopan; empty state menyebut sebab + aksi berikutnya.

---

## 2. Tema

- **Light adalah default.** Alasan: audiens non-teknis lintas departemen membaca kutipan dokumen panjang berjam-jam; latar terang lebih nyaman untuk teks panjang (R-21). Ini bukan dev-tool, jadi dark-only tidak dibenarkan.
- **Dark tersedia via toggle yang berfungsi** (bukan hiasan). Preferensi disimpan per-user. Kedua tema wajib lolos kontras (§4, R-25/R-34).
- Semua token warna di §4 punya nilai light **dan** dark.

---

## 3. Tipografi

- **Typeface tunggal: IBM Plex Sans** untuk seluruh UI. Alasan tertulis: dirancang untuk konteks enterprise, netral-jelas tanpa jadi default AI (Inter/Geist/Space Grotesk dihindari, R-06); dukungan diakritik & keterbacaan Bahasa Indonesia baik; x-height nyaman untuk teks panjang.
- **Mono (IBM Plex Mono) hanya fungsional**, tidak pernah sebagai estetika: menampilkan `doc_id`, nomor versi, dan metadata teknis lain di mana keselarasan karakter menambah kejelasan. Bukan untuk heading atau body (R-06).
- **Hierarki lewat ukuran & weight**, bukan uppercase + letter-spacing lebar (dilarang, R-06).

Skala (rem, light & dark identik):

| Token | Ukuran | Weight | Pemakaian |
|-------|--------|--------|-----------|
| `text-display` | 1.75 | 600 | Judul halaman (jarang) |
| `text-title` | 1.25 | 600 | Judul panel / section |
| `text-body` | 1.0 | 400 | Isi jawaban, teks umum |
| `text-body-strong` | 1.0 | 500 | Penekanan dalam body |
| `text-label` | 0.875 | 500 | Label field, kolom tabel |
| `text-meta` | 0.8125 | 400 | Metadata, timestamp, sumber |
| `text-mono` | 0.8125 | 400 | `doc_id`, versi (IBM Plex Mono) |

- **Measure** body maksimal ~72ch supaya kutipan dokumen tetap terbaca.
- **Line-height** body 1.6 (teks panjang), heading 1.25.

---

## 4. Warna (Token)

Palet dibatasi: **neutral base + 1 accent + warna status fungsional** (R-29). Belum ada warna brand
resmi perusahaan; jika kelak ada, ganti `accent` dan `neutral` di sini sebagai satu-satunya titik ubah.

### 4.1 Neutral base — slate hangat (bukan putih steril)

| Token | Light | Dark | Pemakaian |
|-------|-------|------|-----------|
| `bg-base` | `#F7F7F5` | `#16181B` | Latar aplikasi |
| `bg-surface` | `#FFFFFF` | `#1F2226` | Kartu, panel, bubble asisten |
| `bg-subtle` | `#EFEEEB` | `#282C31` | Baris zebra, area sekunder |
| `border` | `#E2E0DB` | `#333940` | Garis pemisah, border input |
| `text-primary` | `#1D2125` | `#ECEDEE` | Teks utama |
| `text-secondary` | `#5A6169` | `#A2A8AF` | Meta, label sekunder |

Slate diberi sedikit warmth (bukan abu-abu murni/biru) agar tidak jatuh ke "sterile default".

### 4.2 Accent — teal deep (interaktif, BUKAN "sukses")

| Token | Light | Dark | Pemakaian |
|-------|-------|------|-----------|
| `accent` | `#0F6E6E` | `#2AA1A1` | Tombol utama, link, state fokus/aktif |
| `accent-hover` | `#0B5A5A` | `#33B5B5` | Hover/pressed aksi utama |
| `accent-on` | `#FFFFFF` | `#0C1414` | Teks/ikon **di atas** fill accent (wajib dipakai pada fill; cek kontras ≥4.5:1) |

**Aturan accent (R-08/R-13, core "one deliberate accent"):** teal hadir di momen kunci saja —
tombol aksi primer, link, dan penanda fokus/aktif. **Bukan** penanda "berhasil", bukan warna
untuk ikon/badge/glow di mana-mana. Satu layar biasanya punya **satu** aksi ber-teal.

### 4.3 Status semantik (menandai state nyata, R-31)

Dipisah tegas dari accent supaya user tidak bingung "mana aksi, mana status".

| Kondisi | Token | Light | Dark | Catatan |
|---------|-------|-------|------|---------|
| 🔒 Tidak berhak (dokumen ada, user tak berhak) | `status-restricted` | `#9A6B00` (amber tua) | `#D9A63E` | Peringatan **sopan**, bukan error merah. User bisa minta akses ke admin. |
| ❓ Tidak ditemukan / kosong | `status-empty` | `= text-secondary` | `= text-secondary` | Netral. Ini kondisi **normal**, bukan alarm — tanpa warna alarm. |
| ✅ Jawaban berhasil | — | — | — | **Tanpa warna/badge khusus.** Teks jawaban biasa + blok sumber. Tidak ada "delta hijau". |
| Error sistem nyata (koneksi putus, upload gagal) | `status-error` | `#B42318` | `#E5675A` | Merah **hanya** di sini. |

`accent-on`-style pairing berlaku juga untuk badge/fill amber & merah: label di atas fill wajib
memakai pasangan on-color yang lolos kontras, bukan `text-secondary` generik.

### 4.4 Aturan warna mengikat

- Palet aktif per layar: neutral + teal + **maksimum** dua warna status yang relevan. Tidak ada 5–7 warna acak (R-29).
- Tidak ada gradient biru-ungu / blur radial / neon / pastel sebagai treatment utama (R-01). Tidak ada gradient sama sekali kecuali sebagai fungsi hierarki dengan alasan tertulis.
- Semua pasangan teks/latar lolos **≥4.5:1** (body) dan **≥3:1** (teks besar & border fungsional), di light **dan** dark (R-25/R-34).

---

## 5. Bentuk, Elevasi, Efek (dose caps)

Semua di bawah cap; bukan karakter halaman (R-10–R-13).

- **Radius:** skala kecil dan disengaja — `radius-sm 4px` (input, badge), `radius-md 8px` (kartu, bubble, modal). **Tidak** semua elemen pill. Pill (`radius-full`) hanya untuk badge status pendek bila perlu. (R-11)
- **Shadow:** penanda elevasi, bukan default. `shadow-raise` (halus) hanya untuk elemen yang benar-benar mengambang di atas halaman: modal, dropdown, popover. Kartu & panel **flat** dengan `border`. (R-12)
- **Glass (backdrop-blur):** default **tidak dipakai**. Boleh maksimum 1 elemen bila ada alasan (mis. bar suara mengambang di atas transkrip). (R-10)
- **Glow:** tidak dipakai. (R-13)
- **Grid/dot/blueprint background:** tidak dipakai (R-07).

---

## 6. Spacing & Rhythm — RHYTHM dial = 2

Layout app **konsisten & bisa ditebak** (tool kerja, bukan landing page). Variasi hanya di mana konten memang berbeda; bukan tiap section beda template, bukan pula seragam kaku.

Skala spacing (px): `4, 8, 12, 16, 24, 32, 48`. Gunakan level berbeda untuk memisah vs mengelompok — bukan satu nilai untuk semua (R-05).

- Shell aplikasi (sidebar + header + area kerja) **stabil di semua layar** — user hafal tempatnya.
- Variasi yang dibenarkan: bubble chat user vs asisten, kartu status akses (🔒/❓), baris tabel vs form.
- Whitespace sebagai struktur, bukan padding seragam di segala tempat.

---

## 7. Motion — MOTION dial = 2 (fungsional)

Motion **hanya** menandai state sistem nyata; tidak ada loop/pulse/float/bounce dekoratif tanpa trigger (R-19). Durasi pendek (150–250ms), easing standar.

Motion yang dibenarkan (masing-masing menandai state nyata):

| Momen | Motion | Batas |
|-------|--------|-------|
| Transisi status real-time ("mendengarkan" → "mencari dokumen" → "sedang berpikir") | Fade/slide singkat antar label | Berhenti saat status final |
| Streaming token jawaban | Teks muncul bertahap saat token tiba | Berhenti di `chat:done` |
| Indikator suara aktif (STT/TTS berjalan) | Denyut halus pada indikator | **Hanya** selama sesi suara benar-benar aktif; berhenti total saat idle (R-31) |
| Transisi state (loading → konten, buka modal) | Fade/scale singkat | Sekali jalan, tidak berulang |

**Dilarang:** dot glowing berdenyut abadi yang tidak menandai apa-apa; elemen float/bounce terus-menerus; animasi bertumpuk (fade+scale+float sekaligus).

---

## 8. Prinsip per-Surface

Tiap layar dibangun di sekitar **keputusan utama** yang diambil user di situ, bukan shell default sidebar+stat+chart+tabel (antislop "App & Dashboard", C-3/R-20).

### 8.1 Login
- **Keputusan user:** masuk dengan kredensial internal. Itu saja.
- Layar tunggal terfokus: field username + password + satu tombol teal. Tanpa hero, tanpa ilustrasi dekoratif, tanpa "trusted by".
- State error autentikasi menyebut sebab yang aman ("Username atau password salah") — tidak membocorkan mana yang salah.

### 8.2 Chat Assistant — **layar utama** (semua role)
- **Keputusan user:** bertanya, membaca jawaban, memverifikasi sumber. Area chat adalah halaman; kontrol lain footnote.
- **Bubble:** asisten di `bg-surface`, user dibedakan halus (`bg-subtle` atau align berbeda) — variasi konten yang dibenarkan (RHYTHM 2).
- **Status real-time** tampil sebagai baris teks tenang di atas jawaban yang sedang dibentuk (§7), bukan spinner telanjang.
- **Tiga kondisi respons** (§4.3) dibedakan **dengan makna**, bukan sekadar warna:
  - ✅ Jawaban: teks biasa + **blok sumber** (judul dokumen, halaman) di bawahnya. `doc_id`/versi pakai `text-mono`.
  - 🔒 Tidak berhak: kartu `status-restricted` (amber), teks sopan sesuai tone produk, saran "hubungi admin". Nada tenang, bukan alarm.
  - ❓ Tidak ditemukan: teks `status-empty` netral, tanpa ikon alarm.
- **Kontrol suara:** tombol mic. Indikator "sedang merekam / sedang bicara" berdenyut **hanya selama aktif** (§7). Suara opsional — mode teks penuh harus utuh tanpa suara.
- **Empty state (percakapan baru):** sebut apa yang bisa ditanyakan + batas akses user ("Anda dapat menanyakan dokumen departemen [X] sesuai level Anda"), bukan "No data".

### 8.3 Panel Admin Dokumen (dept_admin & super_admin)
- **Keputusan user:** unggah dokumen, set `min_level`, set `hidden_existence`, kelola versi.
- **Daftar dokumen = halaman.** Kolom dipilih dari keputusan admin, field penentu di depan: **Judul · Departemen · min_level · hidden_existence · Versi · Aksi**. Bukan "Name/Status/Date/Actions" generik.
  - `min_level` ditampilkan sebagai label jelas (Staff/Supervisor/Manager), bukan angka telanjang.
  - `hidden_existence = true` diberi penanda ringkas (mis. badge "Tersembunyi") karena ini state keamanan nyata (R-31).
- **Upload:** form dengan field wajib (departemen, min_level, hidden_existence). Guard dept ditegakkan di server; UI dept_admin hanya menampilkan departemennya sendiri.
- **Empty state:** "Belum ada dokumen di departemen ini. Unggah dokumen pertama untuk mulai." + tombol unggah — sebut sebab + aksi (R-27).
- **Loading (ingestion/embedding):** sebut apa yang diproses ("Mengekstrak & meng-embed dokumen…"), bukan spinner kosong.

### 8.4 Panel Kelola User (dept_admin di dept-nya, super_admin lintas dept)
- **Keputusan user:** buat/nonaktifkan user, set level & role.
- **Daftar user:** kolom dari keputusan admin — **Nama · Username · Departemen · Role · Level · Status aktif · Aksi**. Status aktif/nonaktif ditandai jelas.
- Tanpa data palsu: sel kosong tetap kosong atau placeholder jujur (`email@domain.com`, `Nama Lengkap`), bukan `John Doe` (R-23/R-38).
- **Empty state:** "Belum ada user di departemen ini." + aksi tambah user.

---

## 9. Data, Empty, Loading, Error (mengikat semua surface)

- **Angka & konten nyata atau placeholder jujur.** Tidak ada metrik/feed/nama yang dikarang. Selama tahap blueprint, nilai contoh diberi label placeholder yang terlihat user (R-17/R-18/R-23/R-38).
- **Empty ≠ "No data".** Tiap empty state menyebut **sebab** + **satu aksi** yang mengisinya. First-run, hasil-filter-kosong, dan akses-ditolak adalah layar berbeda dan dibaca berbeda (R-27).
- **Loading menyebut apa yang dimuat** (menyambung ke status real-time chat, §7).
- **Error menyebut apa yang gagal + langkah berikutnya** (koneksi putus → "Koneksi terputus, mencoba menyambung kembali…"; pakai `status-error`).
- **Navigasi & kontrol nyata.** Tiap item nav & elemen interaktif punya destinasi/perilaku nyata, atau label "Segera hadir" yang jelas (R-24/R-26). Fitur yang ditakeout/ditunda (Telegram, level tambahan) tidak muncul sebagai nav mati.

---

## 10. Aksesibilitas (mengikat, C-4)

- Kontras lolos di light **dan** dark (§4.4).
- **Keyboard-only** harus bisa: fokus terlihat (pakai `accent`), urutan tab logis, mic & kirim pesan terjangkau tanpa mouse.
- Suara adalah **pelengkap, bukan syarat** — seluruh alur bisa dijalankan teks penuh (a11y + skenario tanpa audio).
- State (fokus, hover, disabled, error) punya penanda visual yang tidak hanya bergantung pada warna.
- Layar tetap utuh di setiap breakpoint (R-03/R-34).

---

## 11. UI Checklist (jalankan sebelum ship, ringkas dari antislop-ui)

- [ ] Palet dari dokumen ini (slate + teal), bukan gradient default. (R-01/R-29)
- [ ] Teal hanya di momen kunci; bukan penanda "sukses"; bukan di setiap elemen. (core, R-08)
- [ ] Tanpa emoji dekoratif di teks UI. (R-04)
- [ ] Layout app konsisten (RHYTHM 2); variasi hanya di mana konten beda. (R-05)
- [ ] Tanpa bentuk default AI: bento mosaic, fake terminal, tiga kolom pricing, left-stripe tanpa makna. (R-05/R-01)
- [ ] Setiap nav & kontrol punya destinasi/perilaku nyata atau "Segera hadir". (R-24/R-26)
- [ ] Motion = 2: fungsional, tanpa loop abadi; denyut suara hanya saat aktif. (R-19)
- [ ] Glass/glow/shadow/radius di bawah cap, bukan default halaman. (R-10–R-13)
- [ ] Tiap dot/penanda status menandai state nyata (min_level, hidden_existence, suara aktif), tanpa glow/pulse dekoratif. (R-31)
- [ ] Layar app dibangun di sekitar keputusan user, bukan shell sidebar+stat+chart+tabel. (C-3/R-20)
- [ ] Angka/feed/baris nyata atau placeholder berlabel; tidak ada metrik karangan. (R-17/R-18/R-38)
- [ ] Sel kosong tetap kosong / placeholder jujur, bukan `John Doe`. (R-23/R-38)
- [ ] Empty/loading/error menyebut sebab + aksi berikutnya, bukan "No data". (R-27)
- [ ] Utuh di tiap breakpoint & tema; lolos keyboard-only. (R-03/R-34/C-4)

---

*Titik ubah tunggal bila brand resmi muncul: token `accent` & `neutral` di §4. Sisanya mengikuti.*
