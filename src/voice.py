"""ElevenLabs STT + TTS integration (Sprint 4).

STT: audio -> text via ElevenLabs Speech-to-Text
TTS: text -> audio via ElevenLabs text-to-speech with expressive voices.
API key is read from ELEVENLABS_API_KEY env var (user will supply later).
"""
import os
import requests

API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
BASE = "https://api.elevenlabs.io"
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "q5aR9u5Hgw9zqew8VadY")

# Emosi mapping per jenis respons (desain §12A.3)
EMOTION_SETTINGS = {
    "jawab": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.4, "use_speaker_boost": True},
    "tidak_berhak": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": False},
    "tidak_ditemukan": {"stability": 0.65, "similarity_boost": 0.75, "style": 0.2, "use_speaker_boost": False},
}


def tts(text: str, kondisi: str = "jawab") -> bytes | None:
    """Convert answer text to speech audio. Returns mp3 bytes or None if no key."""
    if not API_KEY:
        return None  # ponytail: silent no-op without key; voice optional per design
    settings = EMOTION_SETTINGS.get(kondisi, EMOTION_SETTINGS["jawab"])
    resp = requests.post(
        f"{BASE}/v1/text-to-speech/{DEFAULT_VOICE_ID}",
        headers={"xi-api-key": API_KEY},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": settings,
        },
    )
    resp.raise_for_status()
    return resp.content


def stt(audio_bytes: bytes, mime: str = "audio/webm") -> str | None:
    """Transcribe user speech to text. Returns transcript or None if no key."""
    if not API_KEY:
        return None
    resp = requests.post(
        f"{BASE}/v1/speech-to-text",
        headers={"xi-api-key": API_KEY},
        files={"audio": ("audio", audio_bytes, mime), "model_id": (None, "scribe_v1")},
    )
    resp.raise_for_status()
    return resp.json().get("text")
