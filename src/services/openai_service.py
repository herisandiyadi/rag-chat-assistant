"""OpenAI API service for LLM interactions."""

import logging
from typing import List, Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o-mini"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_answer(
        self,
        question: str,
        context: str,
        max_tokens: int = settings.max_response_tokens,
    ) -> str:
        """
        Generate answer using GPT-4o-mini with provided context.
        
        Args:
            question: User question
            context: Retrieved document chunks
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        prompt = f"""Kamu adalah asisten internal perusahaan yang membantu menjawab pertanyaan karyawan berdasarkan dokumen-dokumen resmi.

PENTING:
1. Jawab HANYA berdasarkan konteks yang diberikan
2. Jangan membuat-jawab informasi yang tidak ada di konteks
3. Jika jawaban tidak ada dalam konteks, katakan 'Maaf, saya tidak memiliki informasi yang cukup untuk menjawab pertanyaan ini.'
4. Jawab dalam bahasa yang sama dengan pertanyaan

Konteks dokumen:
{context}

Pertanyaan:
{question}

Jawaban:
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    
    async def get_token_count(self, text: str) -> int:
        """Estimate token count for text."""
        import tiktoken
        
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))


def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance."""
    return OpenAIService()
