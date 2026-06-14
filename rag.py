"""Tiny semantic RAG over the local markdown knowledge base.

Embeds document chunks with sentence-transformers and ranks by cosine similarity.
Swap the model or add a vector DB later; the interface (build_index / search) stays the same.
"""
import os
import glob
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL = None
_CHUNKS = []          # list of {"source": str, "text": str}
_EMB = None           # np.ndarray [n_chunks, dim], L2-normalized


def _model():
    global _MODEL
    if _MODEL is None:
        # ~80MB, downloads once on first run
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def _chunk(text, size=120, overlap=20):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + size]))
        i += size - overlap
    return chunks


def build_index(data_dir="data"):
    """Read every .md in data_dir, chunk it, and embed the chunks."""
    global _CHUNKS, _EMB
    _CHUNKS = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for c in _chunk(text):
            _CHUNKS.append({"source": os.path.basename(path), "text": c})
    if _CHUNKS:
        _EMB = _model().encode(
            [c["text"] for c in _CHUNKS], normalize_embeddings=True
        )
    return len(_CHUNKS)


def search(query, k=3):
    """Return the top-k most similar chunks to the query."""
    if _EMB is None:
        build_index()
    q = _model().encode([query], normalize_embeddings=True)[0]
    scores = _EMB @ q
    top = np.argsort(-scores)[:k]
    return [
        {
            "source": _CHUNKS[i]["source"],
            "score": round(float(scores[i]), 3),
            "text": _CHUNKS[i]["text"],
        }
        for i in top
    ]


if __name__ == "__main__":
    n = build_index()
    print(f"indexed {n} chunks")
    for hit in search("how does an automated market maker price assets"):
        print(f"[{hit['score']}] {hit['source']}: {hit['text'][:80]}...")
