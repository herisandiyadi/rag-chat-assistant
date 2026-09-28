"""Vector search and RAG orchestration."""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, ScoredPoint

from config.settings import settings
from src.core.embedding import get_embedding_model

logger = logging.getLogger(__name__)


class VectorSearch:
    """Vector search service using Qdrant."""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = "documents"
        self.embedding_model = get_embedding_model()
    
    async def search(
        self,
        query: str,
        department_filter: Optional[int] = None,
        min_level_filter: Optional[int] = None,
        k: int = settings.rag_k,
        score_threshold: float = settings.rag_score_threshold,
    ) -> List[ScoredPoint]:
        """
        Search for relevant document chunks (ASYNC wrapper).
        """
        # Jalankan di executor agar tidak memblokir event loop
        return await asyncio.to_thread(
            self._search_sync, query, department_filter, min_level_filter, k, score_threshold
        )

    def _search_sync(
        self, query, department_filter, min_level_filter, k, score_threshold
    ) -> List[ScoredPoint]:
        # Generate embedding for query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build filter
        must_conditions = []
        
        if department_filter is not None:
            must_conditions.append(
                FieldCondition(
                    key="department_id",
                    match=MatchValue(value=department_filter),
                )
            )
        
        if min_level_filter is not None:
            must_conditions.append(
                FieldCondition(
                    key="min_level",
                    match=MatchValue(value=min_level_filter),
                )
            )
        
        # Perform search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=Filter(must=must_conditions) if must_conditions else None,
            limit=k,
            score_threshold=score_threshold,
        )
        
        logger.info(f"Found {len(results)} relevant chunks")
        return results
    
    def create_collection(self):
        """Create Qdrant collection if not exists."""
        from qdrant_client.models import VectorParams, Distance
        
        if not self.client.collection_exists(self.collection_name):
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_model.get_sentence_transformer_kwargs()["prompt_name"] or 768,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    def add_chunks(self, doc_id: str, chunks: List[str], metadata: Dict[str, Any]):
        """Add document chunks to vector database."""
        import uuid
        
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "text": chunk,
                    "doc_id": doc_id,
                    "chunk_index": i,
                    **metadata,
                },
            })
        
        self.client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Added {len(points)} chunks for doc_id: {doc_id}")


def get_vector_search() -> VectorSearch:
    """Get vector search instance."""
    return VectorSearch()
