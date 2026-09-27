"""Lightweight deterministic embedding function.

BLOCKER (see AGENT_CONTEXT.md): no network access to download a real
sentence-embedding checkpoint is available in this environment. This hashing-
trick embedding is a drop-in replacement behind the same interface so ChromaDB
retrieval, ranking, and tests are fully exercised; swapping in a real
sentence-transformers model later requires no changes outside this file.
"""

import hashlib
import re
from typing import List

VECTOR_DIM = 64


def embed_text(text: str) -> List[float]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vector = [0.0] * VECTOR_DIM
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        idx = int(digest, 16) % VECTOR_DIM
        vector[idx] += 1.0
    norm = sum(v * v for v in vector) ** 0.5
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return max(0.0, min(1.0, dot))
