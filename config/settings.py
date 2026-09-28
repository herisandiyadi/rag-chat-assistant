"""Core application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # OpenAI
    openai_api_key: str

    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "pNInz6obpgDQ4cE13emk"
    elevenlabs_model_id: str = "eleven_turbo_v2"

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Application
    app_port: int = 8000
    host: str = "0.0.0.0"

    # Embedding model
    embedding_model: str = "intfloat/multilingual-e5-base"

    # RAG settings
    rag_k: int = 4
    rag_score_threshold: float = 0.7

    # Token limits
    max_context_tokens: int = 8000
    max_response_tokens: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()