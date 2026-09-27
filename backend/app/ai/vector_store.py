"""ChromaDB-backed candidate retrieval for amenity alternatives (Phase 9C).

Falls back to an in-memory cosine-similarity index (using the same embedding
function) if the chromadb package/client cannot initialize in this
environment, so retrieval remains fully functional and testable either way —
callers never notice the difference.
"""

import logging
from typing import List, Tuple

from app.ai.embeddings import embed_text, cosine_similarity
from app.core.config import settings

logger = logging.getLogger("vector_store")

_collection = None
_use_fallback = False
_fallback_store: dict[str, dict] = {}


def _get_collection():
    global _collection, _use_fallback
    if _collection is not None or _use_fallback:
        return _collection
    try:
        import chromadb

        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = client.get_or_create_collection(name="amenities")
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("ChromaDB unavailable (%s); using in-memory fallback index", exc)
        _use_fallback = True
        _collection = None
    return _collection


def upsert_amenity(amenity_id: int, name: str, category: str, description: str):
    text = f"{name} {category} {description}"
    vector = embed_text(text)
    collection = _get_collection()
    doc_id = str(amenity_id)
    if collection is not None:
        collection.upsert(
            ids=[doc_id],
            embeddings=[vector],
            metadatas=[{"amenity_id": amenity_id, "name": name, "category": category}],
        )
    else:
        _fallback_store[doc_id] = {
            "vector": vector,
            "amenity_id": amenity_id,
            "name": name,
            "category": category,
        }


def query_similar(
    text: str, top_k: int = 10, exclude_amenity_id: int | None = None
) -> List[Tuple[int, float]]:
    collection = _get_collection()
    vector = embed_text(text)
    results: List[Tuple[int, float]] = []
    if collection is not None:
        raw = collection.query(query_embeddings=[vector], n_results=top_k)
        ids = raw.get("ids", [[]])[0]
        distances = raw.get("distances", [[]])[0]
        for doc_id, dist in zip(ids, distances):
            similarity = max(0.0, 1.0 - dist)
            amenity_id = int(doc_id)
            if exclude_amenity_id and amenity_id == exclude_amenity_id:
                continue
            results.append((amenity_id, similarity))
    else:
        scored = []
        for doc_id, entry in _fallback_store.items():
            amenity_id = entry["amenity_id"]
            if exclude_amenity_id and amenity_id == exclude_amenity_id:
                continue
            similarity = cosine_similarity(vector, entry["vector"])
            scored.append((amenity_id, similarity))
        scored.sort(key=lambda x: x[1], reverse=True)
        results = scored[:top_k]
    return results
