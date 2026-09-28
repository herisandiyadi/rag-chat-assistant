"""Socket.IO server + chat endpoint with streaming"""
import os
import json
import socketio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from dependencies import get_current_user
from models import User
from rag import decide_response, get_qdrant, COLLECTION, dummy_embed
from endpoints.auth import router as auth_router
from endpoints.seed import router as seed_router
from endpoints.ingest import router as ingest_router
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="RAG Chat Assistant")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, prefix="/auth")
app.include_router(seed_router, prefix="/seed")
app.include_router(ingest_router, prefix="/ingest")


@app.get("/")
async def root():
    return {"status": "ok", "service": "RAG Chat Assistant"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# --- LLM call (may be stubbed if no API key) ---
def call_llm(context_chunks, question, stream=False):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        # ponytail: stub response when no API key
        sources = ", ".join(c.get("judul", "?") for c in context_chunks)
        return f"[STUB] Berdasarkan dokumen ({sources}), jawaban untuk: {question}"
    client = OpenAI(api_key=api_key)
    context_text = "\n\n".join(c.get("teks", c.get("judul", "")) for c in context_chunks)
    messages = [
        {"role": "system", "content": f"Jawab HANYA dari konteks berikut. Jika tidak ada, jawab 'Data tidak ditemukan'. Jangan menambah pengetahuan sendiri.\n\nKonteks:\n{context_text}"},
        {"role": "user", "content": question},
    ]
    if stream:
        return client.chat.completions.create(model="gpt-4o-mini", messages=messages, stream=True, max_tokens=500)
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=500)
    return resp.choices[0].message.content


# --- Socket.IO events ---
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.on("auth")
async def auth(sid, data):
    token = data.get("token")
    if not token:
        await sio.emit("error", {"kode": "no_token", "pesan": "Token tidak diberikan"}, to=sid)
    # Store token in session for later use
    await sio.save_session(sid, {"token": token})
    await sio.emit("status", {"tahap": "terautentikasi"}, to=sid)


@sio.on("chat:text")
async def chat_text(sid, data):
    session = await sio.get_session(sid)
    token = session.get("token") if session else None
    if not token:
        await sio.emit("error", {"kode": "unauthorized", "pesan": "Belum autentikasi"}, to=sid)
        return

    question = data.get("pertanyaan", "")
    if not question:
        await sio.emit("error", {"kode": "empty", "pesan": "Pertanyaan kosong"}, to=sid)
        return

    # Greeting handling (exact match, hindari false-positive substring)
    GREETINGS = {"hai", "halo", "hello", "hi", "hey", "salam", "pagi", "siang", "sore", "malam",
                 "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
                 "assalamualaikum", "assalamu'alaikum"}
    q = question.strip().lower().rstrip("!?. ")
    if q in GREETINGS:
        balas = "Waalaikumsalam! " if q.startswith("assalamu") else ""
        await sio.emit("chat:token", {"token": f"{balas}Halo! Ada dokumen departemen apa yang bisa saya bantu cari hari ini?"}, to=sid)
        await sio.emit("chat:done", {}, to=sid)
        return

    # Get DB session and resolve user (trust boundary)
    db = next(get_db())
    try:
        user = get_current_user(token=token, db=db)
    except HTTPException:
        await sio.emit("error", {"kode": "invalid_token", "pesan": "Token tidak valid"}, to=sid)
        return

    await sio.emit("status", {"tahap": "mencari dokumen"}, to=sid)

    # 3-condition RAG logic
    result = decide_response(db, user, question)

    if result["kondisi"] == "tidak_ditemukan":
        await sio.emit("chat:token", {"token": "Maaf, saya tidak menemukan informasi terkait pertanyaan Anda."}, to=sid)
        await sio.emit("chat:done", {}, to=sid)
        return

    if result["kondisi"] == "tidak_berhak":
        await sio.emit("chat:token", {"token": "Maaf, informasi ini berada di luar hak akses Anda. Silakan hubungi admin bila memerlukannya."}, to=sid)
        await sio.emit("chat:done", {}, to=sid)
        return

    # kondisi == 'jawab' — call LLM with streaming
    await sio.emit("status", {"tahap": "sedang berpikir"}, to=sid)
    sources = [{"doc_id": c.get("doc_id"), "judul": c.get("judul"), "versi": c.get("versi", 1)} for c in result["chunks"]]
    await sio.emit("chat:sources", {"dokumen": sources}, to=sid)

    response = call_llm(result["chunks"], question, stream=True)
    if isinstance(response, str):
        await sio.emit("chat:token", {"token": response}, to=sid)
    else:
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                await sio.emit("chat:token", {"token": delta.content}, to=sid)

    await sio.emit("chat:done", {}, to=sid)