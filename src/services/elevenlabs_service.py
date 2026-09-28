import requests
from src.config import settings

def get_voice_stream(text: str, voice_id: str = None):
    """Get audio stream for text using ElevenLabs API."""
    v_id = voice_id or settings.ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}/stream"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024):
            yield chunk
