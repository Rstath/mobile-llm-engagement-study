from typing import List

import numpy as np
import streamlit as st

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


@st.cache_resource
def load_embedder(model_name: str):
    if SentenceTransformer is None:
        return None

    try:
        return SentenceTransformer(model_name)
    except Exception:
        # Keep metrics working even when the model cannot be downloaded/loaded.
        return None


def simple_hash_embedding(text: str, dim: int = 256) -> np.ndarray:
    vec = np.zeros(dim)
    for word in text.lower().split():
        idx = abs(hash(word)) % dim
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def embed_texts(texts: List[str], embedder) -> np.ndarray:
    if embedder is None:
        return np.vstack([simple_hash_embedding(t) for t in texts])
    return np.array(embedder.encode(texts, normalize_embeddings=True))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
