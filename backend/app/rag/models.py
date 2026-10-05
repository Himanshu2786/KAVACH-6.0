"""
KAVACH RAG (Retrieval-Augmented Generation) Data Models
Defines typed structures for documents, chunks, embeddings, retrieval results, and RAG query responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SecurityDocument(BaseModel):
    """Represents an ingested security knowledge document (e.g. CWE, OWASP, Remediation Guide)."""
    id: str = Field(..., description="Unique document ID (e.g. DOC-CWE-89, DOC-OWASP-A01)")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full textual content of the security standard or guide")
    source: str = Field(..., description="Origin source (e.g. KAVACH Knowledge Engine, MITRE CWE, OWASP Foundation)")
    category: str = Field(..., description="Vulnerability or control category")
    cwe_id: Optional[str] = Field(None, description="Associated CWE identifier if applicable")
    owasp_category: Optional[str] = Field(None, description="Associated OWASP Top 10 category")
    severity: Optional[str] = Field("MEDIUM", description="Default risk rating or severity baseline")
    remediation_steps: List[str] = Field(default_factory=list, description="Step-by-step remediation procedures")
    references: List[str] = Field(default_factory=list, description="Authoritative security references or URLs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context parameters")


class DocumentChunk(BaseModel):
    """Represents a discrete semantic chunk of a security document suitable for vector embedding and retrieval."""
    chunk_id: str = Field(..., description="Unique chunk ID (e.g. CHK-CWE-89-01)")
    document_id: str = Field(..., description="Parent document identifier")
    title: str = Field(..., description="Title of the chunk or parent document")
    text: str = Field(..., description="Text content to be embedded and retrieved")
    chunk_type: str = Field("concept", description="Type of chunk: concept, remediation, impact, or verification")
    source: str = Field(..., description="Knowledge source")
    category: str = Field(..., description="Security category")
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """Represents a ranked, retrieved knowledge chunk returned by the RAG retriever."""
    chunk_id: str
    document_id: str
    title: str
    category: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    source: str
    text: str
    score: float = Field(..., description="Relevance score normalized between 0.0 and 1.0")
    chunk_type: str = "concept"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RagQueryRequest(BaseModel):
    """Request payload for querying the KAVACH RAG pipeline."""
    query: str = Field(..., description="Search query or finding description")
    finding_id: Optional[str] = Field(None, description="Optional Finding ID to auto-populate context")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of top relevant chunks to retrieve")
    filter_category: Optional[str] = Field(None, description="Optional category filter (e.g. Injection, Access Control)")


class RagResponse(BaseModel):
    """Grounded response returned by the RAG pipeline combining retrieved context and LLM analysis."""
    query: str
    retrieval_mode: str = Field(..., description="Retrieval mode: 'SEMANTIC_VECTOR' or 'LEXICAL_FALLBACK'")
    embedding_model: str = Field(..., description="Embedding model used (e.g. nomic-embed-text or local-hash)")
    retrieved_sources: List[RetrievalResult] = Field(default_factory=list, description="Top-K security knowledge chunks retrieved")
    context_tokens_approx: int = 0
    answer: Dict[str, Any] = Field(default_factory=dict, description="Structured 7-section grounded analysis from LLM")
    raw_answer: Optional[str] = None
    model_used: str = Field(..., description="LLM model or deterministic rule engine used")
    execution_time_ms: float = 0.0
    ai_provider: str = Field(default="fallback", description="AI provider: 'ollama' or 'fallback'")


class RagIndexStatus(BaseModel):
    """Real-time health and status of the local RAG vector index."""
    is_ready: bool
    retrieval_mode: str
    embedding_provider: str
    embedding_model: str
    vector_store_type: str
    indexed_documents_count: int
    indexed_chunks_count: int
    index_file_path: Optional[str] = None
    last_indexed_at: Optional[str] = None
    ollama_available: bool
    llm_model: str
    message: str
