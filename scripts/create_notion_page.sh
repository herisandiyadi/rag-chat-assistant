#!/bin/bash
# Script to create Notion page for RAG Chat Assistant using ntn CLI or curl fallback

set -e

NOTION_API_KEY="${NOTION_API_KEY:-}"
NOTION_PARENT_PAGE_ID="${NOTION_PARENT_PAGE_ID:-}"

if [ -z "$NOTION_API_KEY" ]; then
    echo "ERROR: NOTION_API_KEY not found"
    echo "Set NOTION_API_KEY environment variable"
    exit 1
fi

if [ -z "$NOTION_PARENT_PAGE_ID" ]; then
    echo "ERROR: NOTION_PARENT_PAGE_ID not found"
    echo "Set NOTION_PARENT_PAGE_ID with your parent page ID"
    exit 1
fi

echo "Creating Notion page with parent: $NOTION_PARENT_PAGE_ID"

# Check if ntn is available
if command -v ntn >/dev/null 2>&1; then
    echo "Using ntn CLI..."
    
    # Export for ntn
    export NOTION_API_TOKEN="$NOTION_API_KEY"
    export NOTION_KEYRING=0
    
    # Create page
    PARENT_PAGE_ID="$NOTION_PARENT_PAGE_ID"
    PAGE_TITLE="🚀 RAG Chat Assistant - Project Overview"
    
    # Create page content as markdown
    cat > /tmp/rag_page.md << 'MDEOF'
# 🚀 RAG Chat Assistant - Project Overview

**Status:** In Progress (Sprint 1 - Fondasi)

**Last Updated:** 2026-09-28

---

## 📋 Quick Links

- [GitHub Issue #1](https://github.com/herisandiyadi/unified-crm-platform/issues/1)
- [Project Repo](https://github.com/herisandiyadi/rag-chat-assistant)

---

## 🏗️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | FastAPI + python-socketio |
| Auth | PostgreSQL + JWT |
| Vector DB | Qdrant |
| Embedding | multilingual-e5-base |
| LLM | OpenAI GPT-4o-mini |
| Audio | ElevenLabs STT + TTS |
| Frontend | Next.js (integrasikan CRM) |
| Deploy | Docker Compose |

---

## 📚 Documentation

| Dokumen | Deskripsi |
|---------|-----------|
| [Ringkasan Arsitektur Final](file:///root/workspace/rag_assistance/rag-assistance/ringkasan-arsitektur-final.md) | Ikhtisar sistem & keputusan kunci |
| [Desain Fitur RAG](file:///root/workspace/rag_assistance/rag-assistance/desain-fitur-chat-assistant-rag.md) | Logika fitur & access control |
| [Skema Database](file:///root/workspace/rag_assistance/rag-assistance/skema-database-postgresql.md) | PostgreSQL schema & relasi |
| [DESIGN.md](file:///root/workspace/rag_assistance/rag-assistance/DESIGN.md) | UI/UX design system |
| [Sprint Plan](file:///root/workspace/rag_assistance/rag-assistance/sprint-plan.md) | 5 sprint plan (10 minggu) |

---

## 🗓️ Sprint Plan

### Sprint 1 — Fondasi (Infra + DB + Auth + Ingestion)
- [ ] Setup VPS Ubuntu 22.04 + Docker + Docker Compose
- [ ] docker-compose.yml: postgres, qdrant, fastapi-app
- [ ] Implementasi skema PostgreSQL
- [ ] Seed data uji
- [ ] Login internal username/password → JWT
- [ ] Embedding lokal + ingestion 1 dokumen uji

### Sprint 2 — Core RAG + Access Control (HIGH RISK)
- [ ] Qdrant search dengan filter dept + min_level
- [ ] Logika akses 2-dimensi (dept + level)
- [ ] 3-kondisi respons: jawab / access_denied / not_found

### Sprint 3 — Real-Time + UI Chat
- [ ] FastAPI + python-socketio
- [ ] UI Chat sesuai DESIGN.md
- [ ] Status real-time

### Sprint 4 — Suara ElevenLabs (HIGH RISK)
- [ ] ElevenLabs STT + TTS ekspresif
- [ ] Tombol mic UI

### Sprint 5 — Panel Admin + Hardening + Go-Live
- [ ] Panel Admin Dokumen
- [ ] Panel Kelola User
- [ ] Audit log, rate limiting, backup, monitoring

---

## 👥 Team Coordination

| Role | Responsibility |
|------|----------------|
| @developer | Setup infra & implementasi backend |
| @researcherstaff_bot | Dokumentasi & Notion tracking |
| @pmo | Review feasibility & timeline |
| @product-owner | Alignment dengan user story |

---

## 📝 Next Steps

1. Setup VPS Ubuntu 22.04 + Docker
2. Configure .env dengan API keys (OpenAI, ElevenLabs)
3. Run: docker compose up
4. Setup Notion integration
MDEOF

    # Create page using ntn
    ntn api v1/pages \
        parent[page_id]="$PARENT_PAGE_ID" \
        properties[title][0][text][content]="$PAGE_TITLE" \
        markdown="$(cat /tmp/rag_page.md | sed 's/"/\\"/g' | tr '\n' ' ')"

    echo "✅ Page created successfully!"
    
else
    echo "Using curl fallback..."
    
    # Create page using curl
    curl -s -X POST "https://api.notion.com/v1/pages" \
        -H "Authorization: Bearer $NOTION_API_KEY" \
        -H "Notion-Version: 2025-09-03" \
        -H "Content-Type: application/json" \
        -d "{
            \"parent\": {\"page_id\": \"$NOTION_PARENT_PAGE_ID\"},
            \"properties\": {
                \"title\": [{\"type\": \"text\", \"text\": {\"content\": \"🚀 RAG Chat Assistant - Project Overview\"}}]
            }
        }" | tee /tmp/page_response.json

    PAGE_ID=$(cat /tmp/page_response.json | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$PAGE_ID" ]; then
        echo "✅ Page created with ID: $PAGE_ID"
        
        # Read markdown content and upload
        cat /tmp/rag_page.md > /tmp/rag_page_clean.md
        
        curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID/markdown" \
            -H "Authorization: Bearer $NOTION_API_KEY" \
            -H "Notion-Version: 2025-09-03" \
            -H "Content-Type: application/json" \
            -d "{\"markdown\": \"$(cat /tmp/rag_page_clean.md | sed 's/"/\\"/g' | tr '\n' ' ')\"}"
        
        echo "✅ Content uploaded!"
    fi
fi
