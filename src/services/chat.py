"""Chat service with RAG integration."""

import logging
import re
from typing import AsyncGenerator, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.db import get_db
from src.core.access import resolve_access_permission, resolve_user_level
from src.models.document import Document
from src.models.user import User
from src.rag.vector_search import get_vector_search
from src.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

# Sapaan sederhana — tidak perlu RAG search, cukup balas natural.
# Pola: hai, halo, hi, hello, selamat pagi/siang/sore/malam, halo apa kabar, dll.
GREETING_PATTERN = re.compile(
    r"^\s*(hai|haii|hai\s|halo|haloo|hi|hello|hei|hey|"
    r"selamat\s+(pagi|siang|sore|malam)|assalamu'alaikum|assalamualaikum)"
    r"[\s,.!?]*"
    r"(\s*(apa\s+kabar|kabar|semua|semua\s+nya|all|semua\s+baik))?"
    r"[\s,.!?]*$",
    re.IGNORECASE,
)

GREETING_RESPONSE = (
    "Hai! Ada yang bisa saya bantu? "
    "Anda dapat menanyakan seputar dokumen departemen sesuai level akses Anda."
)


def is_greeting(question: str) -> bool:
    """Deteksi sapaan atau basa-basi ringan (tidak butuh RAG)."""
    if not question:
        return False
    q = question.strip()
    # Sapaan pendek saja — kalau panjang, kemungkinan besar pertanyaan sungguhan
    if len(q) > 60:
        return False
    return bool(GREETING_PATTERN.match(q))


class ChatService:
    """Service for handling chat interactions with RAG."""

    @staticmethod
    async def ask_question(
        db: AsyncSession,
        user_id: str,
        question: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer based on RAG.

        Returns response with one of three statuses:
        - "success": Found relevant documents and user has access
        - "access_denied": Document exists but user lacks permission
        - "not_found": No relevant documents found
        """
        # Sapaan → balas natural, jangan cari dokumen (bug fix)
        if is_greeting(question):
            logger.info(f"Greeting detected for user {user_id}: {question!r}")
            return {
                "session_id": session_id or str(user_id),
                "answer": GREETING_RESPONSE,
                "sources": [],
                "status": "greeting",
            }

        vector_search = get_vector_search()
        openai_service = OpenAIService()

        # Get user info
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        # Resolve hierarki level (level_id -> angka dari tabel levels)
        user_level = await resolve_user_level(db, user)

        # Search Qdrant dengan filter department (level difilter setelah
        # metadatapath karena min_level bisa berubah via set_payload)
        results = vector_search.search(
            query=question,
            department_filter=user.department_id,
            min_level_filter=None,  # filter level di lapis aplikasi
        )

        # Check access and categorize
        sources = []
        access_status = "not_found"

        if results:
            # Check access for each source
            for point in results:
                doc_id = point.payload.get("doc_id")
                result = await db.execute(
                    select(Document).where(Document.doc_id == doc_id)
                )
                doc = result.scalar_one_or_none()

                if doc:
                    has_access, reason = resolve_access_permission(
                        user_department_id=user.department_id,
                        user_role_type=user.role_type,
                        user_level=user_level,
                        document_department_id=doc.department_id,
                        document_min_level=doc.min_level or 1,
                    )

                    if has_access:
                        sources.append({
                            "doc_id": doc_id,
                            "score": point.score,
                            "chunk_index": point.payload.get("chunk_index"),
                            "text_snippet": point.payload.get("text", "")[:200],
                        })
                        access_status = "success"
                    elif point.payload.get("hidden_existence", False):
                        # Hidden document - return not_found instead of access_denied
                        access_status = "not_found"
                        sources = []
                        break
                    else:
                        access_status = "access_denied"
                        sources.append({
                            "doc_id": doc_id,
                            "score": point.score,
                        })

        # Generate answer if we have access and sources
        answer = ""
        if access_status == "success" and sources:
            context = "\n\n".join([s["text_snippet"] for s in sources[:4]])
            answer = await openai_service.generate_answer(question, context)

        return {
            "session_id": session_id or str(user_id),
            "answer": answer,
            "sources": sources,
            "status": access_status,
        }

    @staticmethod
    async def stream_answer(
        db: AsyncSession,
        user_id: str,
        question: str,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream answer tokens in real-time."""
        # For now, return the full answer as a single token
        # Later can be enhanced with streaming from OpenAI API
        response = await ChatService.ask_question(db, user_id, question, session_id)

        # Simulate token streaming
        tokens = response["answer"].split()
        for token in tokens:
            yield token

        # Yield sources if available
        if response["sources"]:
            yield f"\n\nSources: {response['sources']}"
