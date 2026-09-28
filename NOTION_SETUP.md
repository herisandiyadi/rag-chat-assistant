# Notion Setup untuk RAG Chat Assistant

## Langkah Setup

### 1. Buat Page di Notion

1. Buka Notion workspace Anda
2. Buat halaman baru sebagai parent (misal: "Project RAG Chat Assistant")
3. Copy URL halaman tersebut
4. URL akan berformat: `https://www.notion.so/.../PARENT_PAGE_ID?...`
5. Extract `PARENT_PAGE_ID` (contoh: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### 2. Buat Integration Token

1. Buka [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Klik **New integration**
3. Name: `RAG Chat Assistant Bot`
4. Link workspace: Pilih workspace Anda
5. Copy **Internal Integration Token**
6. Paste dan simpan aman (tidak commit ke git!)

### 3. Share Page ke Integration

1. Buka halaman parent yang sudah dibuat
2. Klik **Share** di pojok kanan atas
3. Cari integration: `RAG Chat Assistant Bot`
4. Klik **Allow access**
5. Copy URL halaman lagi (untuk memastikan permissions updated)

### 4. Konfigurasi Environment Variables

```bash
# Di server atau local development
export NOTION_API_KEY="your_integration_token_here"
export NOTION_PARENT_PAGE_ID="your_parent_page_id_here"
```

### 5. Jalankan Script

```bash
cd /root/workspace/rag-assistant
python scripts/create_notion_page.py
```

## Output

Script akan:
1. Membuat halaman baru dengan title: "🚀 RAG Chat Assistant - Project Overview"
2. Upload konten: Quick Links, Tech Stack, Sprint Plan, Key Decisions, Team Coordination
3. Print URL halaman Notion yang sudah dibuat

## Troubleshooting

### Error: "notion_api_key not found"
→ Set environment variable: `export NOTION_API_KEY=...`

### Error: "notion_parent_page_id not found"
→ Set environment variable: `export NOTION_PARENT_PAGE_ID=...`

### Error: 403 Forbidden
→ Pastikan halaman parent sudah dishare ke integration

### Error: 400 Bad Request
→ Pastikan page ID format benar (UUID tanpa tanda `-` di URL)

## Page Structure

```
Project RAG Chat Assistant (parent)
└── 🚀 RAG Chat Assistant - Project Overview (child)
    ├── Quick Links
    ├── Architecture & Tech Stack
    │   └── Tech Stack
    ├── Documentation
    ├── Sprint Plan
    │   ├── Sprint 1 — Fondasi
    │   ├── Sprint 2 — Core RAG
    │   ├── Sprint 3 — Real-Time
    │   ├── Sprint 4 — Suara ElevenLabs
    │   └── Sprint 5 — Admin + Go-Live
    ├── Key Decisions
    │   ├── Access Control Model
    │   ├── 3 Kondisi Respons
    │   └── Hidden Existence Flag
    ├── Team Coordination
    └── Next Steps
```
