from fastapi import APIRouter
from sqlalchemy.orm import Session
from database import get_db
from models import Document, Chunk
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

router = APIRouter()

def get_qdrant_client():
    return QdrantClient(host="qdrant", port=6333)

@router.post("/ingest")
def ingest_document(doc_id: str, title: str, content: str, department: str, min_level: int = 1):
    """Ingest a document into the system (simplified for demo)"""
    client = get_qdrant_client()
    
    # Create collection if not exists
    try:
        client.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    except Exception:
        pass  # Collection already exists
    
    # Create chunk
    chunk = Chunk(
        doc_id=doc_id,
        teks=content,
        halaman=1
    )
    
    # Ingest to Qdrant (placeholder - real embedding would go here)
    point = PointStruct(
        id=1,
        vector=[0.1] * 768,  # Placeholder vector
        payload={
            "doc_id": doc_id,
            "judul": title,
            "teks": content[:500],
            "department": department,
            "min_level": min_level
        }
    )
    
    client.upsert(collection_name="documents", points=[point])
    
    return {"message": "Document ingested", "doc_id": doc_id}
