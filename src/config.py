"""Centralized config from environment variables (single source of truth)."""
import os
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


class Settings:
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ragchat")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "ragchat123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "rag_chat_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # JWT — no insecure fallback: production must set JWT_SECRET
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # Qdrant
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "documents")

    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Voice
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "q5aR9u5Hgw9zqew8VadY")

    # RAG tuning
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
    SEARCH_TOP_K: int = int(os.getenv("SEARCH_TOP_K", "4"))
    SEARCH_SCORE_THRESHOLD: float = float(os.getenv("SEARCH_SCORE_THRESHOLD", "0.7"))

    # CORS — comma-separated; '*' rejected in production guard below
    CORS_ORIGINS: list = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()
    ]


settings = Settings()
