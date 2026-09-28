"""Core RAG logic: retrieval + access control + 3-condition response"""
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from models import User, Level
import os
import json

COLLECTION = "documents"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
VECTOR_SIZE = 768


def get_qdrant():
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def dummy_embed(text: str):
    """ponytail: placeholder embedding until multilingual-e5-base is installed.
    Replace with sentence-transformers encode() when available."""
    import hashlib
    h = hashlib.sha256(text.encode()).digest()
    vec = [b / 255.0 for b in h]
    # pad/truncate to VECTOR_SIZE deterministically
    vec = (vec * (VECTOR_SIZE // len(vec) + 1))[:VECTOR_SIZE]
    return vec


def user_level_number(db: Session, user: User) -> int:
    """Resolve user's hierarchy level number from DB (trust boundary)."""
    if user.level_id is None:
        return 0
    level = db.query(Level).filter(Level.id == user.level_id).first()
    return level.angka if level else 0


def build_access_filter(user: User, db: Session):
    """Return Qdrant filter restricting chunks this user may READ (desain §2.4)."""
    conditions = []

    if user.role_type == "super_admin":
        return None  # no restriction

    # Department boundary is strict for both dept_admin and user
    dept_code = None
    if user.department_id:
        from models import Department
        dept = db.query(Department).filter(Department.id == user.department_id).first()
        dept_code = dept.kode if dept else None

    if dept_code is None:
        # No department -> nothing readable except super_admin
        conditions.append(FieldCondition(key="department", match=MatchValue(value="__none__")))
    else:
        conditions.append(FieldCondition(key="department", match=MatchValue(value=dept_code)))
        if user.role_type == "user":
            # User additionally bounded by min_level
            lvl = user_level_number(db, user)
            conditions.append(
                FieldCondition(key="min_level", range={"lte": lvl})  # gte->lte user sees <= level
            )

    return Filter(must=conditions) if conditions else None


def search_all(query_vec, k=4):
    """Search WITHOUT access filter — used only to test existence carefully."""
    client = get_qdrant()
    hits = client.search(collection_name=COLLECTION, query_vector=query_vec, limit=k)
    return [(h.score, h.payload) for h in hits]


def search_scoped(query_vec, access_filter, k=4, score_threshold=0.7):
    client = get_qdrant()
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=query_vec,
        query_filter=access_filter,
        limit=k,
        score_threshold=score_threshold,
    )
    return [(h.score, h.payload) for h in hits]


def ensure_collection(client):
    """BUG-010 fix: auto-create collection if missing (prevents silent 404)."""
    if not client.collection_exists(COLLECTION):
        from qdrant_client.models import VectorParams, Distance
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def decide_response(db: Session, user: User, question: str, k=4, threshold=0.7):
    """Core 3-condition logic (desain §6).

    Returns dict: {kondisi, chunks, pesan}
      kondisi: 'jawab' | 'tidak_berhak' | 'tidak_ditemukan'
    """
    query_vec = dummy_embed(question)

    # BUG-010 fix: ensure collection exists before searching
    client = get_qdrant()
    ensure_collection(client)

    # 1) Scoped search — what the user is allowed to read
    scoped = search_scoped(query_vec, build_access_filter(user, db), k=k, score_threshold=threshold)
    if scoped:
        return {"kondisi": "jawab", "chunks": [p for _, p in scoped], "pesan": None}

    # 2) Nothing readable. Did relevant docs exist at all?
    everything = search_all(query_vec, k=k)
    relevant = [(s, p) for s, p in everything if s >= threshold]
    if not relevant:
        return {"kondisi": "tidak_ditemukan", "chunks": [], "pesan": None}

    # 3) Relevant docs exist but user not entitled -> check hidden_existence
    top_payload = relevant[0][1]
    if top_payload.get("hidden_existence", False):
        return {"kondisi": "tidak_ditemukan", "chunks": [], "pesan": None}
    return {"kondisi": "tidak_berhak", "chunks": [], "pesan": None}
