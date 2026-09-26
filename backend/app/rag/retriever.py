"""
KAVACH RAG Retriever
Performs hybrid semantic and metadata-filtered similarity search against KAVACH security knowledge.
"""

import logging
from typing import List, Optional, Tuple, Any, Dict

from backend.app.rag.models import RetrievalResult
from backend.app.rag.embeddings import embedding_provider
from backend.app.rag.vector_store import vector_store
from backend.app.rag.document_loader import document_loader
from backend.app.rag.chunker import chunker

logger = logging.getLogger("kavach.rag.retriever")


class RagRetriever:
    """Orchestrates similarity search, thresholding, and ranking of security knowledge chunks."""

    async def ensure_index_ready(self) -> None:
        """Auto-builds index if not already present on disk."""
        if not vector_store.is_indexed():
            logger.info("RAG vector index is uninitialized. Initiating initial knowledge indexing...")
            await self.rebuild_index()

    async def rebuild_index(self) -> dict:
        """Loads all documents, chunks them, computes embeddings, and builds the vector index."""
        docs = document_loader.load_all_documents()
        chunks = chunker.chunk_all(docs)

        texts = [c.text for c in chunks]
        vectors, mode, model = await embedding_provider.get_embeddings_batch(texts)

        vector_store.build_index(chunks, vectors, model, mode)

        return {
            "documents_indexed": len(docs),
            "chunks_created": len(chunks),
            "embedding_model": model,
            "retrieval_mode": mode,
            "vector_store": vector_store.get_stats()
        }

    async def retrieve(
        self,
        query: str,
        top_k: int = 4,
        category_filter: Optional[str] = None,
        cwe_filter: Optional[str] = None,
        exclude_doc_ids: Optional[List[str]] = None,
        boost_cwe: Optional[str] = None,
        boost_keywords: Optional[List[str]] = None
    ) -> Tuple[List[RetrievalResult], str, str]:
        """
        Retrieves top-K relevant security knowledge chunks for the given query.
        Returns: (results, retrieval_mode, embedding_model)
        """
        if not query or not query.strip():
            return [], "NONE", "none"

        await self.ensure_index_ready()

        # Contextual finding-awareness heuristics if not explicitly supplied
        q_lower = query.lower()
        if "openapi" in q_lower or "api schema" in q_lower or "api doc" in q_lower or ("cwe-200" in q_lower and "header" not in q_lower):
            if exclude_doc_ids is None:
                # Do NOT use unrelated knowledge such as clickjacking or security-header guidance merely because it shares A05
                exclude_doc_ids = ["DOC-CWE-16-HEADERS"]
            if boost_cwe is None:
                boost_cwe = "CWE-200"
            if boost_keywords is None:
                boost_keywords = ["openapi", "schema", "api documentation", "reconnaissance", "cwe-200", "information exposure"]

        query_vec, mode, model = await embedding_provider.get_embedding(query)
        results = vector_store.similarity_search(
            query_vector=query_vec,
            top_k=top_k,
            score_threshold=0.10,
            category_filter=category_filter,
            cwe_filter=cwe_filter,
            exclude_doc_ids=exclude_doc_ids,
            boost_cwe=boost_cwe,
            boost_keywords=boost_keywords
        )

        logger.info("Retrieved %d relevant security chunks for query '%s' [Mode: %s].", len(results), query[:50], mode)
        return results, mode, model

    async def retrieve_for_finding(
        self,
        finding: Any,
        evidence: Optional[Any] = None,
        top_k: int = 4
    ) -> Tuple[List[RetrievalResult], str, str]:
        """
        Executes finding-aware RAG retrieval tailored to the specific finding domain.
        Prioritizes specific CWE taxonomy, suppresses unrelated shared-OWASP topics,
        and enforces evidence-bounded contextual retrieval.
        """
        title = getattr(finding, "title", None) or (finding.get("title") if isinstance(finding, dict) else "") or ""
        cwe_id = getattr(finding, "cwe_id", None) or (finding.get("cwe_id") if isinstance(finding, dict) else "") or ""
        cat = getattr(finding, "category", None) or (finding.get("category") if isinstance(finding, dict) else "") or ""
        owasp = getattr(finding, "owasp_category", None) or (finding.get("owasp_category") if isinstance(finding, dict) else "") or ""
        finding_id = getattr(finding, "id", None) or (finding.get("id") if isinstance(finding, dict) else "") or ""

        # Extract evidence text
        evidence_text = ""
        if evidence:
            if hasattr(evidence, "raw_data") and evidence.raw_data:
                evidence_text = str(evidence.raw_data)
            elif isinstance(evidence, dict):
                evidence_text = str(evidence.get("raw_data") or evidence.get("observed_output") or "")

        # Check if finding is API Documentation / OpenAPI Schema Exposure
        is_api_docs = (
            cwe_id == "CWE-200"
            or "api doc" in title.lower()
            or "openapi" in title.lower()
            or "api schema" in title.lower()
            or "interactive api" in title.lower()
            or "openapi.json" in evidence_text.lower()
            or "WM-API-DOCS" in finding_id
        )

        if is_api_docs:
            # Query focused on CWE-200, API documentation/schema exposure, information disclosure through public API specs
            # OWASP A05 is only contextual mapping
            query = (
                f"CWE-200 Public exposure of API schema interactive documentation OpenAPI json "
                f"information disclosure reconnaissance endpoint discovery {title}"
            )
            exclude_doc_ids = ["DOC-CWE-16-HEADERS"]
            boost_cwe = "CWE-200"
            boost_keywords = [
                "openapi", "api schema", "interactive documentation", "reconnaissance",
                "cwe-200", "information exposure", "schema reconnaissance"
            ]
            return await self.retrieve(
                query=query,
                top_k=top_k,
                exclude_doc_ids=exclude_doc_ids,
                boost_cwe=boost_cwe,
                boost_keywords=boost_keywords
            )

        # Standard finding query
        query = f"{title} {cat} {cwe_id} {owasp} {evidence_text[:150]}".strip()
        return await self.retrieve(
            query=query,
            top_k=top_k,
            boost_cwe=cwe_id or None
        )


rag_retriever = RagRetriever()
