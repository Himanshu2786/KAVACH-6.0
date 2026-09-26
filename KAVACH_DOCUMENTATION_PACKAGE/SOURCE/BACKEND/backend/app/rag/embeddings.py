"""
KAVACH RAG Embeddings Provider
Handles vector generation via Ollama (nomic-embed-text) with graceful,
deterministic local lexical-vector fallback when Ollama or embedding models are offline.
"""

import math
import hashlib
import re
import logging
from typing import List, Optional, Tuple
import httpx
import numpy as np

from backend.app.core.config import settings

logger = logging.getLogger("kavach.rag.embeddings")

FALLBACK_VECTOR_DIM = 384


class EmbeddingProvider:
    """Manages embedding generation across Ollama semantic models and local fallback engines."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.embedding_model = "nomic-embed-text"
        self._semantic_available: Optional[bool] = None
        self._last_health_check = 0.0

    async def check_semantic_availability(self, force_refresh: bool = False) -> bool:
        """Probes Ollama to determine whether nomic-embed-text or embedding API is available."""
        if self._semantic_available is not None and not force_refresh:
            return self._semantic_available

        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                # Check tags first to see if nomic-embed-text or an embedding model is pulled
                tag_res = await client.get(f"{self.base_url}/api/tags")
                if tag_res.status_code != 200:
                    self._semantic_available = False
                    return False

                tags = tag_res.json().get("models", [])
                model_names = [m.get("name", "") for m in tags]
                has_nomic = any("nomic-embed-text" in name for name in model_names)

                # Attempt a 1-token test embedding probe
                probe_model = self.embedding_model if has_nomic else (model_names[0] if model_names else self.embedding_model)
                embed_res = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": probe_model, "prompt": "kavach"},
                    timeout=3.0
                )

                if embed_res.status_code == 200 and "embedding" in embed_res.json():
                    self.embedding_model = probe_model
                    self._semantic_available = True
                    logger.info("Ollama semantic embedding engine active with model: %s", self.embedding_model)
                    return True
        except Exception as e:
            logger.debug("Ollama embedding probe inactive: %s. Lexical fallback will be utilized.", e)

        self._semantic_available = False
        return False

    def _generate_deterministic_lexical_vector(self, text: str, dim: int = FALLBACK_VECTOR_DIM) -> List[float]:
        """
        Deterministic, high-entropy lexical feature hashing vectorizer.
        Projects text tokens into a normalized fixed-size hyper-sphere using n-gram subword hashing
        and term-frequency weighting.
        Guarantees identical vectors for identical text and meaningful overlap for related security terms.
        """
        vec = np.zeros(dim, dtype=np.float32)
        if not text or not text.strip():
            return vec.tolist()

        # Tokenize and extract character 3-grams and word tokens
        words = re.findall(r'[A-Za-z0-9_\-]+', text.lower())
        for w in words:
            # Word level hash
            h_word = int(hashlib.sha256(w.encode("utf-8")).hexdigest()[:8], 16)
            idx = h_word % dim
            sign = 1.0 if (h_word % 2 == 0) else -1.0
            vec[idx] += 1.5 * sign

            # Character trigrams for morphological and acronym similarity (e.g. sqli, idor, cwe)
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    trigram = w[i:i+3]
                    h_tri = int(hashlib.md5(trigram.encode("utf-8")).hexdigest()[:6], 16)
                    tri_idx = h_tri % dim
                    tri_sign = 1.0 if (h_tri % 2 == 0) else -1.0
                    vec[tri_idx] += 0.5 * tri_sign

        # L2-normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm

        return vec.tolist()

    async def get_embedding(self, text: str) -> Tuple[List[float], str, str]:
        """
        Generates vector representation for the given text.
        Returns: (embedding_vector, retrieval_mode, model_used)
        """
        is_semantic = await self.check_semantic_availability()

        if is_semantic:
            try:
                async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
                    res = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": self.embedding_model, "prompt": text[:2000]}
                    )
                    if res.status_code == 200:
                        vec = res.json().get("embedding", [])
                        if vec:
                            # Normalize
                            arr = np.array(vec, dtype=np.float32)
                            norm = np.linalg.norm(arr)
                            if norm > 1e-6:
                                arr = arr / norm
                            return arr.tolist(), "SEMANTIC_VECTOR", self.embedding_model
            except Exception as e:
                logger.warning("Semantic embedding query failed: %s. Falling back to deterministic lexical vector.", e)

        # Fallback
        fallback_vec = self._generate_deterministic_lexical_vector(text)
        return fallback_vec, "LEXICAL_FALLBACK", "kavach-lexical-hasher-v1"

    async def get_embeddings_batch(self, texts: List[str]) -> Tuple[List[List[float]], str, str]:
        """Generates embeddings for a batch of text chunks."""
        is_semantic = await self.check_semantic_availability()
        vectors: List[List[float]] = []

        if is_semantic:
            try:
                async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT * 2) as client:
                    for t in texts:
                        res = await client.post(
                            f"{self.base_url}/api/embeddings",
                            json={"model": self.embedding_model, "prompt": t[:2000]}
                        )
                        if res.status_code == 200:
                            v = res.json().get("embedding", [])
                            arr = np.array(v, dtype=np.float32)
                            norm = np.linalg.norm(arr)
                            if norm > 1e-6:
                                arr = arr / norm
                            vectors.append(arr.tolist())
                        else:
                            vectors.append(self._generate_deterministic_lexical_vector(t))
                return vectors, "SEMANTIC_VECTOR", self.embedding_model
            except Exception as e:
                logger.warning("Batch semantic embedding failed: %s. Using lexical vectorizer.", e)
                vectors = []

        # Local fallback for batch
        for t in texts:
            vectors.append(self._generate_deterministic_lexical_vector(t))
        return vectors, "LEXICAL_FALLBACK", "kavach-lexical-hasher-v1"


embedding_provider = EmbeddingProvider()
