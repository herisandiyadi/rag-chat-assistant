"""Seed dokumen uji ke Qdrant (desain §17 verification fixtures).

Dokumen:
- SOP Umum HR        dept=hr       min_level=1  hidden=false
- Rahasia Gaji HR    dept=hr       min_level=3  hidden=false
- Rencana PHK        dept=hr       min_level=3  hidden=TRUE
- Laporan Keuangan   dept=finance  min_level=2  hidden=false
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag import get_qdrant, dummy_embed, COLLECTION, VECTOR_SIZE
from qdrant_client.models import VectorParams, Distance, PointStruct

DOCS = [
    {"doc_id": "sop-umum-hr", "judul": "SOP Umum HR", "department": "hr",
     "min_level": 1, "hidden_existence": False, "versi": 1,
     "teks": "SOP umum HR mencakup prosedur kehadiran, cuti, dan penilaian kinerja pegawai. Semua karyawan wajib mengisi presensi setiap hari kerja."},
    {"doc_id": "rahasia-gaji-hr", "judul": "Rahasia Gaji HR", "department": "hr",
     "min_level": 3, "hidden_existence": False, "versi": 1,
     "teks": "Kebijakan kenaikan gaji 2026 bersifat rahasia dan hanya boleh diakses oleh Manager HR. Rincian komponen tunjangan tercantum pada lampiran A."},
    {"doc_id": "rencana-phk", "judul": "Rencana Restrukturisasi & PHK 2026", "department": "hr",
     "min_level": 3, "hidden_existence": True, "versi": 1,
     "teks": "Dokumen rencana restrukturisasi dan pemutusan hubungan kerja 2026 sangat rahasia dan keberadaannya tidak boleh diketahui di luar manajemen puncak."},
    {"doc_id": "laporan-keuangan", "judul": "Laporan Keuangan", "department": "finance",
     "min_level": 2, "hidden_existence": False, "versi": 1,
     "teks": "Laporan keuangan kuartal menunjukkan pertumbuhan pendapatan. Rincian arus kas dan proyeksi triwulan berikutnya dilampirkan."},
]


def main():
    client = get_qdrant()
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION}' dibuat (size={VECTOR_SIZE})")
    else:
        print(f"Collection '{COLLECTION}' sudah ada")

    points = []
    for i, d in enumerate(DOCS, start=1):
        points.append(PointStruct(
            id=i,
            vector=dummy_embed(d["teks"]),
            payload=d,
        ))
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"{len(points)} dokumen uji di-upsert ke Qdrant")

    count = client.count(collection_name=COLLECTION)
    print(f"Total point di collection: {count.count}")


if __name__ == "__main__":
    main()
