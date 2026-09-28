"""Embedding model management."""

from typing import Optional
from sentence_transformers import SentenceTransformer
from config.settings import settings


class EmbeddingModel:
    """Singleton embedding model wrapper."""
    
    _instance: Optional[SentenceTransformer] = None
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or create the embedding model instance."""
        if cls._instance is None:
            cls._instance = SentenceTransformer(settings.embedding_model)
        return cls._instance


def get_embedding_model() -> SentenceTransformer:
    """Dependency function to get embedding model."""
    return EmbeddingModel.get_model()
