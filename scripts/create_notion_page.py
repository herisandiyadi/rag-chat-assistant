#!/usr/bin/env python3
"""Script to populate Notion page with RAG Chat Assistant project overview."""

import os
import sys
import json
import requests
from datetime import datetime

# Configuration
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID")

if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY not found in environment")
    print("Set NOTION_API_KEY environment variable with your Notion integration token")
    sys.exit(1)

if not NOTION_PARENT_PAGE_ID:
    print("ERROR: NOTION_PARENT_PAGE_ID not found in environment")
    print("Set NOTION_PARENT_PAGE_ID with your parent page ID (e.g., from https://www.notion.so/...)")
    sys.exit(1)

print(f"Using Notion parent page: {NOTION_PARENT_PAGE_ID}")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.notion.com/v1"


def text_block(content: str) -> dict:
    """Helper to create properly formatted text object."""
    return {
        "type": "text",
        "text": {"content": content}
    }


def create_page(parent_id: str, title: str) -> str:
    """Create a new page and return its ID."""
    url = f"{BASE_URL}/pages"
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": [{
                "type": "text",
                "text": {"content": title}
            }]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["id"]


def append_blocks(page_id: str, blocks: list) -> None:
    """Append blocks to a page in batches."""
    batch_size = 100
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        url = f"{BASE_URL}/blocks/{page_id}/children"
        response = requests.patch(url, headers=HEADERS, json={"children": batch})
        if response.status_code != 200:
            print(f"Error at batch {i}: {response.status_code}")
            print(response.text)
            break
        print(f"Uploaded batch {i // batch_size + 1}")
        import time
        time.sleep(0.5)


def create_rag_project_page():
    """Create the RAG Chat Assistant project page."""
    page_title = "🚀 RAG Chat Assistant - Project Overview"
    
    # Create the page first
    page_id = create_page(NOTION_PARENT_PAGE_ID, page_title)
    print(f"Created page with ID: {page_id}")
    
    blocks = []
    
    # Header 1
    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {"rich_text": [text_block(page_title)]}
    })
    
    # Metadata
    blocks.extend([
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block(f"**Status:** In Progress (Sprint 1 - Fondasi)")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block(f"**Last Updated:** {datetime.utcnow().isoformat()}")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Quick Links
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("📋 Quick Links")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [
                text_block("• "),
                {
                    "type": "text",
                    "text": {"content": "GitHub Issue #1"},
                    "annotations": {"link": {"url": "https://github.com/herisandiyadi/unified-crm-platform/issues/1"}}
                }
            ]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block("• [Architecture Diagram](#architecture)")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block("• [Tech Stack](#tech-stack)")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block("• [Sprint Plan](#sprint-plan)")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Tech Stack
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("🏗️ Architecture & Tech Stack")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [text_block("Chat Assistant berbasis **RAG** (Retrieval-Augmented Generation) untuk internal korporat.")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Tech Stack")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Backend: FastAPI + python-socketio")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Auth: PostgreSQL (username/password + JWT)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Vector DB: Qdrant (self-host Docker)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Embedding: multilingual-e5-base (sentence-transformers)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("LLM: OpenAI GPT-4o-mini")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Audio: ElevenLabs STT + TTS ekspresif")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Frontend: Next.js (integrasikan dengan CRM)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Deploy: Docker Compose")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Documentation
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("📚 Documentation")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                text_block("• [Ringkasan Arsitektur Final]"),
                {
                    "type": "text",
                    "text": {"content": " (ikhtisar sistem & keputusan kunci)"}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                text_block("• [Desain Fitur RAG]"),
                {
                    "type": "text",
                    "text": {"content": " (logika fitur & access control)"}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                text_block("• [Skema Database]"),
                {
                    "type": "text",
                    "text": {"content": " (PostgreSQL schema & relasi)"}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                text_block("• [DESIGN.md]"),
                {
                    "type": "text",
                    "text": {"content": " (UI/UX design system)"}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                text_block("• [Sprint Plan]"),
                {
                    "type": "text",
                    "text": {"content": " (5 sprint plan - 10 minggu)"}
                }
            ]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Sprint Plan
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("🗓️ Sprint Plan")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Sprint 1 — Fondasi (Infra + DB + Auth + Ingestion)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Setup VPS Ubuntu 22.04 + Docker + Docker Compose")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("docker-compose.yml: postgres, qdrant, fastapi-app")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Implementasi skema PostgreSQL")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Seed data uji")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Login internal username/password → JWT")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Sprint 2 — Core RAG + Access Control (HIGH RISK)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Qdrant search dengan filter dept + min_level")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("3-kondisi respons: jawab / access_denied / not_found")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Sprint 3 — Real-Time + UI Chat")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("FastAPI + python-socketio")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("UI Chat sesuai DESIGN.md")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Sprint 4 — Suara ElevenLabs (HIGH RISK)")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("ElevenLabs STT + TTS ekspresif")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Sprint 5 — Panel Admin + Hardening + Go-Live")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Panel Admin Dokumen & User")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Audit log, rate limiting, backup, monitoring")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Key Decisions
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("🎯 Key Decisions")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Access Control Model")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("super_admin: Semua dept, Semua level")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("dept_admin: Dept sendiri, Semua level")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("user: Dept + level ≥ min_level")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("3 Kondisi Respons")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("✅ Jawaban — Dokumen ada & user berhak")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("🔒 Tidak memiliki akses — Dokumen ada tapi user tak berhak")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("❓ Data tidak ditemukan — Tidak ada dokumen relevan")]}
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [text_block("Hidden Existence Flag")]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [
                text_block("Untuk dokumen super rahasia: user tak berhak → ")
            ]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [
                {
                    "type": "text",
                    "text": {"content": "\"tidak ditemukan\", bukan \"tidak memiliki akses\""},
                    "annotations": {"bold": True}
                }
            ]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Team Coordination
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("👥 Team Coordination")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("@developer — Setup infra & implementasi backend")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("@researcherstaff_bot — Dokumentasi & Notion tracking")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("@pmo — Review feasibility & timeline")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("@product-owner — Alignment dengan user story")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Next Steps
    blocks.extend([
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [text_block("📝 Next Steps")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Setup VPS Ubuntu 22.04 + Docker")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Configure .env file dengan API keys")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Run docker compose up")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Implementasi skema PostgreSQL")]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [text_block("Seed data uji")]}
        },
        {"object": "block", "type": "divider", "divider": {}},
    ])
    
    # Footer
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [
            text_block(f"*Last updated: {datetime.utcnow().isoformat()}*")
        ]}
    })
    
    # Upload blocks
    print(f"Uploading {len(blocks)} blocks to Notion...")
    append_blocks(page_id, blocks)
    
    # Print page URL
    page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
    print(f"\n✅ Page created successfully!")
    print(f"View: {page_url}")
    
    return page_id


if __name__ == "__main__":
    try:
        page_id = create_rag_project_page()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
