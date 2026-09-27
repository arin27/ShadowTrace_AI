"""
Retrieval layer.

Preferred path: sentence-transformers embeddings + a FAISS index (semantic
search). This is what the project is designed around and what runs when
the environment listed in requirements.txt is installed.

Fallback path: if sentence-transformers/FAISS are not importable (e.g. no
network to download the model, or the dependency isn't installed), the
retriever transparently falls back to TF-IDF + cosine similarity using
scikit-learn, which has no download dependency. The retrieval INTERFACE
(top-k chunks with a relevance score) is identical either way, so the rest
of the pipeline (context builder, analyst, evaluation) does not care which
backend served the query. The active backend is exposed via `.backend_name`
so the UI can be honest about which mode is running.
"""

from __future__ import annotations

from dataclasses import dataclass

from rag.ingestion import Chunk, load_and_chunk

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    _HAS_EMBEDDINGS = True
except Exception:
    _HAS_EMBEDDINGS = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as _np


@dataclass
class RetrievalResult:
    chunk: Chunk
    score: float


class Retriever:
    """Singleton-ish retriever: build once, query many times."""

    def __init__(self):
        self.chunks: list[Chunk] = load_and_chunk()
        self.backend_name = "unloaded"
        self._embed_model = None
        self._faiss_index = None
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        if _HAS_EMBEDDINGS:
            try:
                self._embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                texts = [c.text for c in self.chunks]
                embeddings = self._embed_model.encode(
                    texts, normalize_embeddings=True, show_progress_bar=False
                )
                embeddings = _np.asarray(embeddings, dtype="float32")
                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim)  # cosine sim via inner product on normalized vecs
                index.add(embeddings)
                self._faiss_index = index
                self.backend_name = "sentence-transformers + faiss (semantic embeddings)"
                return
            except Exception:
                pass  # fall through to TF-IDF

        self._build_tfidf_index()
        self.backend_name = "TF-IDF + cosine similarity (fallback, no embedding model available)"

    def _build_tfidf_index(self):
        texts = [c.text for c in self.chunks]
        self._tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=4000)
        self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int = 4) -> list[RetrievalResult]:
        if self._faiss_index is not None:
            q_emb = self._embed_model.encode(
                [query], normalize_embeddings=True, show_progress_bar=False
            )
            q_emb = _np.asarray(q_emb, dtype="float32")
            scores, idxs = self._faiss_index.search(q_emb, top_k)
            results = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx == -1:
                    continue
                results.append(RetrievalResult(chunk=self.chunks[idx], score=float(score)))
            return results

        # TF-IDF fallback
        q_vec = self._tfidf_vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._tfidf_matrix)[0]
        top_idx = sims.argsort()[::-1][:top_k]
        return [RetrievalResult(chunk=self.chunks[i], score=float(sims[i])) for i in top_idx
                if sims[i] > 0]


_retriever_singleton: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever_singleton
    if _retriever_singleton is None:
        _retriever_singleton = Retriever()
    return _retriever_singleton
