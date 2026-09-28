
---
TICKET: RAG-001
Deskripsi: Greeting chat membalas data RAG bukannya menyapa user.
Prioritas: High
Reporter: Senior QA
Status: In Progress
---
Fix:
- Tambahkan logika sapaan khusus di socket_server.py yang bersifat early return
- Pastikan sapaan tidak memicu embedding/RAG pipeline.

