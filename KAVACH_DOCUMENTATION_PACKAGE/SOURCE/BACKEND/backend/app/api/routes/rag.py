"""
KAVACH RAG API Routes
Exposes endpoints for querying the RAG pipeline, retrieving grounded security knowledge,
and inspecting index health/statistics.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Finding
from backend.app.rag.models import (
    RagQueryRequest,
    RagResponse,
    RagIndexStatus
)
from backend.app.rag.rag_pipeline import rag_pipeline
from backend.app.rag.vector_store import vector_store
from backend.app.rag.embeddings import embedding_provider
from backend.app.rag.retriever import rag_retriever
from backend.app.services.ollama_service import ollama_service

router = APIRouter(prefix="/rag", tags=["Security Intelligence RAG Pipeline"])


@router.get("/status", response_model=RagIndexStatus)
async def get_rag_status():
    """Returns real-time status of the local RAG vector index, embedding model, and retriever."""
    stats = vector_store.get_stats()
    is_semantic = await embedding_provider.check_semantic_availability()
    ollama_health = await ollama_service.check_health()

    return RagIndexStatus(
        is_ready=stats["is_indexed"],
        retrieval_mode=stats["retrieval_mode"] if stats["is_indexed"] else ("SEMANTIC_VECTOR" if is_semantic else "LEXICAL_FALLBACK"),
        embedding_provider="Local Ollama Embeddings" if is_semantic else "KAVACH Deterministic Vectorizer",
        embedding_model=stats["embedding_model"] if stats["is_indexed"] else embedding_provider.embedding_model,
        vector_store_type=stats["engine"],
        indexed_documents_count=17,
        indexed_chunks_count=stats["indexed_chunks_count"],
        index_file_path=stats["storage_dir"],
        last_indexed_at=stats["last_indexed_at"],
        ollama_available=ollama_health.get("status_code") == "ready",
        llm_model=ollama_service.selected_model,
        message="RAG Pipeline is operational with local vector retrieval." if stats["is_indexed"] else "RAG index is unbuilt. Call POST /api/rag/index to initialize."
    )


@router.post("/index")
async def rebuild_rag_index():
    """Rebuilds the local RAG vector index from all security knowledge documents."""
    try:
        stats = await rag_retriever.rebuild_index()
        return {
            "success": True,
            "message": "Successfully refreshed KAVACH RAG vector index.",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed building RAG index: {str(e)}")


@router.post("/query", response_model=RagResponse)
async def query_rag(req: RagQueryRequest):
    """Executes a security query through the RAG pipeline, returning top-K sources and grounded analysis."""
    try:
        response = await rag_pipeline.query(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query execution failed: {str(e)}")


@router.post("/analyze-finding", response_model=RagResponse)
async def analyze_finding_rag(finding_id: str, top_k: int = 4, db: Session = Depends(get_db)):
    """Runs grounded RAG analysis on a specific KAVACH finding, returning retrieved citations and grounded explanation."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found")

    evidence = finding.evidence_records[0] if finding.evidence_records else None
    response = await rag_pipeline.analyze_finding(finding, evidence, top_k=top_k)
    return response
