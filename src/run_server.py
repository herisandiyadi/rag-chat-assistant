import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine, Base
from endpoints.auth import router as auth_router
from endpoints.seed import router as seed_router
from endpoints.ingest import router as ingest_router
from endpoints.admin import router as admin_router
from rag import decide_response
from voice import tts as voice_tts

Base.metadata.create_all(bind=engine)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="RAG Chat Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")

app.include_router(auth_router, prefix="/auth")
app.include_router(seed_router, prefix="/seed")
app.include_router(ingest_router, prefix="/ingest")
app.include_router(admin_router, prefix="/admin")

# Mount Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# --- Socket.IO events (Sprint 3) ---
from auth import decode_access_token
from models import User, Department, Level


# --- Intent classification (BUG-003 fix) ---
# Natural conversation handling for greetings, small talk, and
# non-document questions so the assistant doesn't always answer from docs.
# Rewritten: the previous inline regex matched a bare letter "p" (so "s o p"
# was treated as a greeting) and missed short forms like "pgi"/"hii".
from smalltalk import handle_smalltalk


@sio.on("connect")
async def connect(sid, environ):
    pass

@sio.on("disconnect")
async def disconnect(sid):
    pass

@sio.on("auth")
async def auth_event(sid, data):
    token = data.get("token", "")
    payload = decode_access_token(token)
    if payload is None:
        await sio.emit("error", {"kode": "invalid_token", "pesan": "Token tidak valid"}, to=sid)
        return
    await sio.save_session(sid, {"user_id": payload.user_id})
    await sio.emit("status", {"tahap": "terautentikasi"}, to=sid)


@sio.on("chat:text")
async def chat_text(sid, data):
    session = await sio.get_session(sid)
    user_id = session.get("user_id") if session else None
    if not user_id:
        await sio.emit("error", {"kode": "unauthorized", "pesan": "Belum autentikasi"}, to=sid)
        return

    question = (data or {}).get("pertanyaan", "").strip()
    if not question:
        await sio.emit("error", {"kode": "empty", "pesan": "Pertanyaan kosong"}, to=sid)
        return

    # BUG-009 FIX: Greeting / small talk handled naturally, not via RAG
    smalltalk_reply = handle_smalltalk(question)
    if smalltalk_reply:
        await sio.emit("chat:token", {"token": smalltalk_reply}, to=sid)
        audio = voice_tts(smalltalk_reply, "jawab")
        if audio:
            await sio.emit("tts:audio", {"audio_len": len(audio)}, to=sid)
        await sio.emit("chat:done", {}, to=sid)
        return

    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            await sio.emit("error", {"kode": "unauthorized", "pesan": "User tidak valid"}, to=sid)
            return

        await sio.emit("status", {"tahap": "mencari dokumen"}, to=sid)
        try:
            result = decide_response(db, user, question)
        except Exception as e:
            pesan = "Maaf, saya tidak menemukan informasi terkait pertanyaan Anda."
            await sio.emit("chat:token", {"token": pesan}, to=sid)
            await sio.emit("chat:done", {}, to=sid)
            return

        if result["kondisi"] == "tidak_ditemukan":
            pesan = "Maaf, saya tidak menemukan informasi terkait pertanyaan Anda."
            await sio.emit("chat:token", {"token": pesan}, to=sid)
            audio = voice_tts(pesan, "tidak_ditemukan")
            if audio:
                await sio.emit("tts:audio", {"audio_len": len(audio)}, to=sid)
            await sio.emit("chat:done", {}, to=sid)
            return

        if result["kondisi"] == "tidak_berhak":
            pesan = "Maaf, informasi ini berada di luar hak akses Anda. Silakan hubungi admin bila memerlukannya."
            await sio.emit("chat:token", {"token": pesan}, to=sid)
            audio = voice_tts(pesan, "tidak_berhak")
            if audio:
                await sio.emit("tts:audio", {"audio_len": len(audio)}, to=sid)
            await sio.emit("chat:done", {}, to=sid)
            return

        # kondisi == 'jawab'
        await sio.emit("status", {"tahap": "sedang berpikir"}, to=sid)
        sources = [{"doc_id": c.get("doc_id"), "judul": c.get("judul"), "versi": c.get("versi", 1)} for c in result["chunks"]]
        await sio.emit("chat:sources", {"dokumen": sources}, to=sid)

        # ponytail: LLM stub until OPENAI_API_KEY set; replace call_llm with real streaming
        context_text = "\n\n".join(c.get("teks", "") or c.get("judul", "") for c in result["chunks"])
        jawaban = f"Berdasarkan dokumen terkait, berikut jawaban untuk '{question}':\n\n{context_text[:800]}"
        await sio.emit("chat:token", {"token": jawaban}, to=sid)
        audio = voice_tts(jawaban, "jawab")
        if audio:
            await sio.emit("tts:audio", {"audio_len": len(audio)}, to=sid)
        await sio.emit("chat:done", {}, to=sid)
    finally:
        db.close()


# FastAPI root/health routes must be defined on `app` BEFORE wrapping
@app.get("/")
async def root():
    return {"status": "ok", "service": "RAG Chat Assistant", "ui": "/static/index.html"}

@app.get("/health")
async def health():
    return {"status": "healthy"}