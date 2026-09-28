"""Embedding model management.

Model besar (multilingual-e5-base ~1GB) TIDAK dimuat saat startup —
lazy load saat pertama kali dipakai. Startup app tetap cepat (<5s),
port 8000 langsung melayani /health tanpa menunggu download model.
"""

import logging
import os
import threading
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Singleton embedding model wrapper (lazy-load, thread-safe)."""

    _instance: Optional["SentenceTransformer"] = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        """Get or create the embedding model instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    from sentence_transformers import SentenceTransformer
                    logger.info(f"Loading embedding model {settings.embedding_model} (first use)...")
                    cls._instance = SentenceTransformer(settings.embedding_model)
                    logger.info("Embedding model loaded")
        return cls._instance


def get_embedding_model():
    """Dependency function to get embedding model (lazy)."""
    return EmbeddingModel.get_model()


def warmup_if_available():
    """Warm-up model hanya jika cache lokal sudah ada (tanpa download)."""
    try:
        cache_dir = os.path.expanduser(
            os.environ.get("HF_HOME", "~/.cache/huggingface")
        )
        if os.path.isdir(cache_dir) and any(os.scandir(cache_dir)):
            get_embedding_model()
            return True
    except Exception as e:
        logger.warning(f"Embedding warmup skipped: {e}")
    return False