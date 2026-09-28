"""Document ingestion pipeline."""

import logging
import uuid
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.models.document import Document
from src.rag.vector_search import get_vector_search
from src.services.document import DocumentService

logger = logging.getLogger(__name__)


class DocumentIngestor:
    """Service for ingesting documents into the RAG system."""
    
    def __init__(self):
        self.vector_search = get_vector_search()
    
    async def ingest_file(
        self,
        db: AsyncSession,
        file_path: str,
        department_id: int,
        min_level: int = 1,
        hidden_existence: bool = False,
        owner_admin_id: str = None,
    ) -> Dict[str, Any]:
        """
        Ingest a file into the RAG system.
        
        Steps:
        1. Read file content
        2. Extract text
        3. Chunk text
        4. Generate embeddings
        5. Store in Qdrant
        6. Create document record in PostgreSQL
        """
        # Step 1-2: Read and extract text
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Step 3: Chunk text
        chunks = DocumentService._chunk_text(text, chunk_size=500)
        
        # Step 4: Generate doc_id
        doc_id = str(uuid.uuid4())
        
        # Step 5: Store in Qdrant
        metadata = {
            "department_id": str(department_id),
            "doc_id": doc_id,
            "min_level": min_level,
            "hidden_existence": hidden_existence,
            "doc_title": file_path,
        }
        self.vector_search.add_chunks(doc_id, chunks, metadata)
        
        # Step 6: Create document record in PostgreSQL
        document = Document(
            doc_id=doc_id,
            judul=file_path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
            department_id=department_id,
            min_level=min_level,
            hidden_existence=hidden_existence,
            owner_admin_id=owner_admin_id,
            versi=1,
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        logger.info(f"Ingested {len(chunks)} chunks for doc_id: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "chunk_count": len(chunks),
            "document_id": document.id,
        }


def get_ingestor() -> DocumentIngestor:
    """Get document ingestor instance."""
    return DocumentIngestor()
