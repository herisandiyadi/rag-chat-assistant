"""Test bahwa sapaan TIDAK memanggil RAG/vector search sama sekali.

Pendekatan: monkeypatch get_vector_search() untuk raise AssertionError
jika dipanggil saat user menyapa. Jika ChatService tetap mengembalikan
jawaban natural tanpa error → bug fix terbukti bekerja.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.getcwd())

# Trigger agar get_vector_search ter-mock sebelum ask_question berjalan
import src.services.chat as chat_mod


def make_mock_db(user):
    """Mock AsyncSession minimal: hanya db.get(User, id) dipakai di jalur greeting."""
    class FakeDB:
        async def get(self, model, obj_id):
            return user
        async def execute(self, *a, **k):
            raise AssertionError("execute() tidak boleh dipanggil pada jalur greeting")
    return FakeDB()


class FakeUser:
    id = "user-123"
    username = "staff_hr"
    department_id = 1
    role_type = "user"
    level = 1


def run_test():
    original = chat_mod.get_vector_search

    def boom(*args, **kwargs):
        raise AssertionError("BUG: vector_search.search() dipanggil saat user menyapa!")

    chat_mod.get_vector_search = lambda: boom

    try:
        db = make_mock_db(FakeUser())
        resp = asyncio.run(chat_mod.ChatService.ask_question(
            db=db, user_id=FakeUser.id, question="hai", session_id=None
        ))
        assert resp["status"] == "greeting", f"status={resp['status']}"
        assert resp["sources"] == [], f"sources={resp['sources']}"
        assert resp["answer"], "answer kosong"
        assert isinstance(resp["answer"], str)
        print(f"  ✅ 'hai'        -> status={resp['status']}, sources={len(resp['sources'])}")
        print(f"     answer: {resp['answer']}")

        # Ulang untuk beberapa variasi sapaan
        for q in ["halo", "Selamat pagi", "Hai, apa kabar?", "hello"]:
            r = asyncio.run(chat_mod.ChatService.ask_question(
                db=db, user_id=FakeUser.id, question=q, session_id=None
            ))
            assert r["status"] == "greeting", f"{q}: status={r['status']}"
            print(f"  ✅ {q!r:22s} -> greeting, tanpa RAG search")

        # Pastikan pertanyaan sungguhan TIDAK masuk jalur greeting
        called = {"n": 0}

        class FakeVS:
            def search(self, *a, **k):
                called["n"] += 1
                return []

        chat_mod.get_vector_search = lambda: FakeVS()
        r = asyncio.run(chat_mod.ChatService.ask_question(
            db=db, user_id=FakeUser.id,
            question="berapa lama proses cuti?", session_id=None
        ))
        assert r["status"] == "not_found", f"expected not_found, got {r['status']}"
        print(f"  ✅ pertanyaan sungguhan tetap lewat RAG (search dipanggil {called['n']}x)")

    finally:
        chat_mod.get_vector_search = original

    print("\n=== INTEGRATION TEST PASSED: greeting tidak trigger RAG ===")


if __name__ == "__main__":
    run_test()
