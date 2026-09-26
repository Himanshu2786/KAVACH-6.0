"""
KAVACH RAG Vector Store
Local, persistent vector indexing engine using optimized NumPy cosine matrix operations
and optional FAISS indexing if installed.
"""

import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import numpy as np

from backend.app.rag.models import DocumentChunk, RetrievalResult

logger = logging.getLogger("kavach.rag.vector_store")

# Persist RAG vector index under backend/app/data/rag_index/
DEFAULT_INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rag_index")


class VectorStore:
    """Manages storage, persistence, and nearest-neighbor vector retrieval for RAG chunks."""

    def __init__(self, storage_dir: str = DEFAULT_INDEX_DIR):
        self.storage_dir = storage_dir
        self.vectors: Optional[np.ndarray] = None  # Shape: (N, Dim)
        self.chunks: List[DocumentChunk] = []
        self.metadata_info: Dict[str, Any] = {}
        self.last_indexed_at: Optional[str] = None
        self._faiss_index = None

        os.makedirs(self.storage_dir, exist_ok=True)
        self.load()

    @property
    def vectors_path(self) -> str:
        return os.path.join(self.storage_dir, "rag_vectors.npz")

    @property
    def metadata_path(self) -> str:
        return os.path.join(self.storage_dir, "rag_metadata.json")

    def is_indexed(self) -> bool:
        return self.vectors is not None and len(self.chunks) > 0

    def build_index(self, chunks: List[DocumentChunk], vectors: List[List[float]], embedding_model: str, retrieval_mode: str) -> None:
        """Constructs and normalizes the vector index from a batch of chunks and embeddings."""
        if not chunks or not vectors:
            logger.warning("Empty chunks or vectors supplied to build_index.")
            return

        self.chunks = chunks
        arr = np.array(vectors, dtype=np.float32)

        # Ensure unit L2 normalization along axis 1 for fast dot-product cosine similarity
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vectors = arr / norms

        self.last_indexed_at = datetime.utcnow().isoformat()
        self.metadata_info = {
            "embedding_model": embedding_model,
            "retrieval_mode": retrieval_mode,
            "chunks_count": len(chunks),
            "vector_dim": int(self.vectors.shape[1]),
            "last_indexed_at": self.last_indexed_at,
            "storage_version": "1.0.0"
        }

        # Optional FAISS acceleration if available
        try:
            import faiss
            dim = self.vectors.shape[1]
            self._faiss_index = faiss.IndexFlatIP(dim)
            self._faiss_index.add(self.vectors)
            logger.info("Initialized FAISS IndexFlatIP for %d chunks.", len(chunks))
        except ImportError:
            self._faiss_index = None
            logger.debug("FAISS not installed; running optimized NumPy vectorized cosine index.")

        self.save()
        logger.info("Successfully built KAVACH RAG vector index with %d chunks (dim=%d).", len(chunks), self.vectors.shape[1])

    def save(self) -> bool:
        """Persists vectors and metadata to disk."""
        if self.vectors is None or not self.chunks:
            return False

        try:
            # Save vectors to NPZ
            np.savez_compressed(self.vectors_path, vectors=self.vectors)

            # Save chunks metadata to JSON
            serialized_chunks = [c.model_dump() for c in self.chunks]
            payload = {
                "info": self.metadata_info,
                "chunks": serialized_chunks
            }
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            logger.info("RAG vector index saved to: %s", self.storage_dir)
            return True
        except Exception as e:
            logger.error("Failed saving RAG vector index: %s", e)
            return False

    def load(self) -> bool:
        """Loads existing vector index and chunk metadata from disk if available."""
        if not os.path.exists(self.vectors_path) or not os.path.exists(self.metadata_path):
            return False

        try:
            # Load vectors
            with np.load(self.vectors_path) as data:
                self.vectors = data["vectors"]

            # Load metadata
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.metadata_info = payload.get("info", {})
            self.last_indexed_at = self.metadata_info.get("last_indexed_at")
            self.chunks = [DocumentChunk(**c) for c in payload.get("chunks", [])]

            # Optional FAISS initialization
            try:
                import faiss
                dim = self.vectors.shape[1]
                self._faiss_index = faiss.IndexFlatIP(dim)
                self._faiss_index.add(self.vectors)
            except ImportError:
                self._faiss_index = None

            logger.info("Loaded RAG vector index: %d chunks (dim=%d).", len(self.chunks), self.vectors.shape[1])
            return True
        except Exception as e:
            logger.warning("Could not load RAG vector index from disk: %s", e)
            self.vectors = None
            self.chunks = []
            return False

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        score_threshold: float = 0.15,
        category_filter: Optional[str] = None,
        cwe_filter: Optional[str] = None,
        exclude_doc_ids: Optional[List[str]] = None,
        boost_cwe: Optional[str] = None,
        boost_keywords: Optional[List[str]] = None
    ) -> List[RetrievalResult]:
        """Performs cosine similarity search against the vector index with finding-aware boosting and filtering."""
        if self.vectors is None or len(self.chunks) == 0:
            logger.warning("Vector store is empty. No search performed.")
            return []

        q_arr = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 1e-6:
            q_arr = q_arr / q_norm

        scores: np.ndarray

        if self._faiss_index is not None:
            D, I = self._faiss_index.search(np.expand_dims(q_arr, axis=0), len(self.chunks))
            raw_scores = D[0]
            indices = I[0]
        else:
            # Vectorized matrix-vector dot product (cosine similarity)
            raw_scores = np.dot(self.vectors, q_arr)
            indices = np.argsort(-raw_scores)

        excluded = set(exclude_doc_ids or [])
        candidate_items = []

        for idx in indices:
            if idx < 0 or idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]

            # Exclusion filter
            if chunk.document_id in excluded:
                continue

            # Category filter if specified
            if category_filter and category_filter.lower() not in (chunk.category or "").lower():
                continue

            # CWE filter if specified
            if cwe_filter and chunk.cwe_id and chunk.cwe_id.lower() != cwe_filter.lower():
                continue

            score = float(raw_scores[idx]) if self._faiss_index is None else float(raw_scores[np.where(indices == idx)[0][0]])
            # Normalize cosine score from [-1, 1] to [0.0, 1.0]
            norm_score = max(0.0, min(1.0, (score + 1.0) / 2.0 if score < 1.0 else 1.0))

            # Apply finding-aware boosting
            if boost_cwe:
                if chunk.cwe_id and chunk.cwe_id.upper() == boost_cwe.upper():
                    norm_score = min(1.0, norm_score + 0.25)
                elif boost_cwe.lower() in chunk.text.lower():
                    norm_score = min(1.0, norm_score + 0.15)

            if boost_keywords:
                for kw in boost_keywords:
                    if kw.lower() in chunk.text.lower() or kw.lower() in chunk.title.lower():
                        norm_score = min(1.0, norm_score + 0.08)

            if norm_score < score_threshold:
                continue

            candidate_items.append((norm_score, chunk))

        # Sort candidates by final boosted/adjusted score
        candidate_items.sort(key=lambda x: x[0], reverse=True)

        results: List[RetrievalResult] = []
        seen_docs = set()

        for final_score, chunk in candidate_items:
            # Deduplicate near-identical document sections to maximize variety of retrieved context
            doc_key = f"{chunk.document_id}_{chunk.chunk_type}"
            if doc_key in seen_docs and len(results) >= 2:
                continue
            seen_docs.add(doc_key)

            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    title=chunk.title,
                    category=chunk.category,
                    cwe_id=chunk.cwe_id,
                    owasp_category=chunk.owasp_category,
                    source=chunk.source,
                    text=chunk.text,
                    score=round(final_score, 4),
                    chunk_type=chunk.chunk_type,
                    metadata=chunk.metadata
                )
            )

            if len(results) >= top_k:
                break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic statistics about the vector store."""
        return {
            "is_indexed": self.is_indexed(),
            "indexed_chunks_count": len(self.chunks),
            "vector_dimension": int(self.vectors.shape[1]) if self.vectors is not None else 0,
            "embedding_model": self.metadata_info.get("embedding_model", "none"),
            "retrieval_mode": self.metadata_info.get("retrieval_mode", "none"),
            "last_indexed_at": self.last_indexed_at,
            "storage_dir": self.storage_dir,
            "engine": "FAISS IndexFlatIP" if self._faiss_index is not None else "NumPy Vectorized Cosine Index"
        }


vector_store = VectorStore()
