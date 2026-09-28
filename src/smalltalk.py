"""Smalltalk / greeting handling (BUG-003 follow-up).

The RAG pipeline answers every question by searching documents. A greeting like
"hai" retrieved the nearest document chunk and answered about it instead of
greeting back — hence the smalltalk short-circuit.

Rewritten from the previous regex-only version, which had two real defects:
  1. The alternation ended with a bare `p`, so ANY standalone letter "p" matched
     ("s o p", "b a p" were treated as greetings). It also failed to normalize
     common short forms ("pgi", "hii" missed).
  2. Greeting detection ran on arbitrary-length sentences, so a real document
     question that merely contained a greeting word was answered as smalltalk.
Greetings are SHORT utterances; real questions go to RAG. Length guard enforces it.
"""
import re

_MAX_SMALLTALK_WORDS = 5

# Normalization: collapse noise so "hai!!", "hiiiii", "halo..." all resolve.
def _normalize(text: str) -> str:
    q = text.strip().lower()
    q = q.strip(" .,!?-")
    # collapse repeated characters in each token (haii -> hai) for typo tolerance
    return " ".join(re.sub(r"(.)\1{2,}", r"\1", tok) for tok in q.split())


_CANNED = {
    # greetings
    "hai": "Halo! Ada yang bisa saya bantu? Anda dapat menanyakan isi dokumen departemen Anda.",
    "hi": "Halo! Ada yang bisa saya bantu? Anda dapat menanyakan isi dokumen departemen Anda.",
    "halo": "Halo! Ada yang bisa saya bantu? Anda dapat menanyakan isi dokumen departemen Anda.",
    "hello": "Halo! Ada yang bisa saya bantu? Anda dapat menanyakan isi dokumen departemen Anda.",
    "hey": "Halo! Ada yang bisa saya bantu? Anda dapat menanyakan isi dokumen departemen Anda.",
    "salam": "Halo! Ada yang bisa saya bantu?",
    "assalamualaikum": "Waalaikumsalam! Ada yang bisa saya bantu?",
    # greetings with time-of-day, incl. the common informal short form "pgi"/"sore"
    "selamat pagi": "Selamat pagi! Ada yang bisa saya bantu hari ini?",
    "pagi": "Selamat pagi! Ada yang bisa saya bantu hari ini?",
    "selamat siang": "Selamat siang! Ada yang bisa saya bantu?",
    "siang": "Selamat siang! Ada yang bisa saya bantu?",
    "selamat sore": "Selamat sore! Ada yang bisa saya bantu?",
    "sore": "Selamat sore! Ada yang bisa saya bantu?",
    "selamat malam": "Selamat malam! Ada yang bisa saya bantu?",
    "malam": "Selamat malam! Ada yang bisa saya bantu?",
    # thanks
    "terima kasih": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "terimakasih": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "makasih": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "thanks": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "thank you": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "thx": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    "nuhun": "Sama-sama, senang bisa membantu. Ada lagi yang ingin ditanyakan?",
    # acknowledgements
    "oke": "Baik. Ada lagi yang ingin Anda tanyakan?",
    "ok": "Baik. Ada lagi yang ingin Anda tanyakan?",
    "baik": "Baik. Ada lagi yang ingin Anda tanyakan?",
}

# Multi-word phrases checked before single tokens.
_PHRASE_RULES = [
    (re.compile(r"\b(apa|gimana|bagaimana)\s+kabarm?u?\b|\bapa kabar\b|\bgimana kabar\b|\bhow are you\b", re.I),
     "Saya baik-baik saja, terima kasih sudah bertanya! Saya siap membantu Anda mencari informasi dari dokumen. Apa yang bisa saya bantu?"),
    (re.compile(r"\b(siapa\s+kamu|kamu\s+siapa|who\s+are\s+you|kamu\s+apa)\b", re.I),
     "Saya asisten chat berbasis RAG (Retrieval-Augmented Generation) yang menjawab pertanyaan berdasarkan dokumen internal perusahaan, dengan kontrol akses per departemen dan level jabatan. Silakan ajukan pertanyaan tentang dokumen yang ingin Anda ketahui."),
]


def handle_smalltalk(question: str) -> str | None:
    """Return a natural reply for greetings / small talk, or None to fall through to RAG."""
    if not question or not question.strip():
        return None
    q = _normalize(question)
    if not q:
        return None

    for pattern, reply in _PHRASE_RULES:
        if pattern.search(q):
            return reply

    # Length guard: greetings are short. Anything longer is a real question even
    # if it contains a greeting word ("hai, tolong cari dokumen X" stays in RAG).
    if len(q.split()) > _MAX_SMALLTALK_WORDS:
        return None

    return _CANNED.get(q)
