"""Test greeting via Socket.IO end-to-end."""
import asyncio, json
import socketio

API = "http://localhost:8000"
results = []

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("[connect] ok")

@sio.on("chat:token")
async def on_token(d):
    tok = d.get("token", "")
    results.append(tok)
    print(f"[chat:token] {tok}")

@sio.on("chat:sources")
async def on_sources(d):
    print(f"[chat:sources] {d}")

@sio.on("chat:done")
async def on_done(d):
    print("[chat:done]")

@sio.on("error")
async def on_error(d):
    print(f"[error] {d}")

async def main():
    await sio.connect(API, transports=["polling", "websocket"])
    
    # Login via HTTP
    import urllib.request
    def login(user, pw):
        req = urllib.request.Request(
            f"{API}/auth/login",
            data=json.dumps({"username": user, "password": pw}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["access_token"]
    
    token = login("super_admin", "admin123")
    print(f"[login] got token: {token[:20]}...")
    
    await sio.emit("auth", {"token": token})
    await asyncio.sleep(1)
    
    for q in ["hai", "halo", "selamat pagi", "apa kabar", "terima kasih", "resep rendang?"]:
        results.clear()
        print(f"\n--- Kirim: '{q}' ---")
        await sio.emit("chat:text", {"pertanyaan": q})
        await asyncio.sleep(3)
        full = "".join(results)
        print(f"=> JAWABAN: {full}")
        print(f"=> Apakah greeting? {'STUB' not in full and 'dokumen' in full.lower()}")
    
    await sio.disconnect()

asyncio.run(main())
