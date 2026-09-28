"""Chat service with RAG integration."""

import logging
from typing import AsyncGenerator, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.security import resolve_access_permission
from src.models.document import Document
from src.models.user import User
from src.rag.vector_search import get_vector_search
from src.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


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
        vector_search = get_vector_search()
        openai_service = OpenAIService()
        
        # Get user info
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Search for relevant chunks
        results = vector_search.search(
            query=question,
            department_filter=user.department_id,
            min_level_filter=user.level,
        )
        
        # Check access and categorize
        sources = []
        access_status = "not_found"
        
        if results:
            # Check access for each source
            for point in results:
                doc_id = point.payload.get("doc_id")
                doc = await db.query(Document).filter_by(doc_id=doc_id).first()
                
                if doc:
                    has_access, reason = resolve_access_permission(
                        user_department_id=user.department_id,
                        user_role_type=user.role_type,
                        user_level=user.level,
                        document_department_id=doc.department_id,
                        document_min_level=doc.min_level,
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
