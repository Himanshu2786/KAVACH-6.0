"""
KAVACH RAG Test Suite
Tests document loading, chunking, vector indexing, semantic/lexical retrieval,
and end-to-end grounded RAG pipeline execution.
"""

import pytest
import asyncio
import numpy as np

from backend.app.rag.models import SecurityDocument, DocumentChunk, RagQueryRequest
from backend.app.rag.document_loader import document_loader
from backend.app.rag.chunker import chunker
from backend.app.rag.embeddings import embedding_provider
from backend.app.rag.vector_store import vector_store
from backend.app.rag.retriever import rag_retriever
from backend.app.rag.rag_pipeline import rag_pipeline


def test_document_loading():
    """Verify security documents load from static intelligence and database."""
    async def _run():
        docs = document_loader.load_all_documents()
        assert len(docs) >= 7
        cwe_ids = [d.cwe_id for d in docs if d.cwe_id]
        assert "CWE-89" in cwe_ids
        assert "CWE-798" in cwe_ids
        assert "CWE-639" in cwe_ids
    asyncio.run(_run())


def test_chunking_and_metadata_preservation():
    """Verify chunker splits documents into semantic chunks retaining metadata."""
    async def _run():
        doc = SecurityDocument(
            id="TEST-DOC-01",
            title="Test Flaw Title",
            content="Test Flaw Content for RAG testing.",
            source="Test Knowledge Source",
            category="Test Category",
            cwe_id="CWE-999",
            owasp_category="OWASP-A01",
            remediation_steps=["Step 1: Test fix", "Step 2: Test verify"]
        )
        chunks = chunker.chunk_document(doc)
        assert len(chunks) >= 2  # Concept + Remediation + Verification

        concept_chunk = next(c for c in chunks if c.chunk_type == "concept")
        assert concept_chunk.cwe_id == "CWE-999"
        assert concept_chunk.source == "Test Knowledge Source"
        assert "Test Flaw Content" in concept_chunk.text

        rem_chunk = next(c for c in chunks if c.chunk_type == "remediation")
        assert "Step 1: Test fix" in rem_chunk.text
    asyncio.run(_run())


def test_vector_store_indexing_and_similarity():
    """Verify vector index builds, normalizes, and performs cosine search accurately."""
    async def _run():
        stats = await rag_retriever.rebuild_index()
        assert stats["documents_indexed"] >= 7
        assert stats["chunks_created"] >= 20
        assert vector_store.is_indexed() is True

        # Test similarity search
        q_vec, mode, model = await embedding_provider.get_embedding("SQL injection dynamic string concatenation")
        results = vector_store.similarity_search(q_vec, top_k=3)
        assert len(results) > 0
        assert results[0].score >= 0.5
    asyncio.run(_run())


def test_sql_injection_retrieval_ranking():
    """Verify SQL Injection query ranks CWE-89 as top relevant result."""
    async def _run():
        results, mode, model = await rag_retriever.retrieve(
            query="SQL injection flaw parameter unescaped quote syntax bypass",
            top_k=3
        )
        assert len(results) > 0
        top_cwe = results[0].cwe_id or results[0].title
        assert "CWE-89" in top_cwe or "SQL" in top_cwe
    asyncio.run(_run())


def test_credential_exposure_retrieval_ranking():
    """Verify exposed secret/AWS key query ranks credential exposure top."""
    async def _run():
        results, mode, model = await rag_retriever.retrieve(
            query="Exposed AWS Access Key AKIA credential leak in git commit",
            top_k=3
        )
        assert len(results) > 0
        top_result = results[0]
        assert "CWE-798" in (top_result.cwe_id or "") or "Secret" in top_result.title or "Credential" in top_result.title
    asyncio.run(_run())


def test_idor_retrieval_ranking():
    """Verify IDOR query ranks CWE-639 / Broken Access Control top."""
    async def _run():
        results, mode, model = await rag_retriever.retrieve(
            query="Insecure Direct Object Reference parameter tampering cross-tenant record",
            top_k=3
        )
        assert len(results) > 0
        top_result = results[0]
        assert "CWE-639" in (top_result.cwe_id or "") or "IDOR" in top_result.title or "Access Control" in top_result.category
    asyncio.run(_run())


def test_rag_pipeline_query_grounding():
    """Verify full RAG pipeline query returns retrieved sources and structured 7-section answer."""
    async def _run():
        req = RagQueryRequest(
            query="Explain SQL injection risks and step-by-step remediation",
            top_k=3
        )
        res = await rag_pipeline.query(req)
        assert res.query == req.query
        assert len(res.retrieved_sources) > 0
        assert res.retrieval_mode in ("SEMANTIC_VECTOR", "LEXICAL_FALLBACK")
        assert "what_was_found" in res.answer
        assert "how_to_fix" in res.answer
        assert "how_to_verify" in res.answer
    asyncio.run(_run())


def test_empty_query_handling():
    """Verify empty queries return clean empty result without crashing."""
    async def _run():
        results, mode, model = await rag_retriever.retrieve("", top_k=3)
        assert len(results) == 0
    asyncio.run(_run())
