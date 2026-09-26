"""
KAVACH RAG Security Chunker
Splits security knowledge documents into high-value semantic retrieval chunks
while preserving complete metadata and contextual boundaries.
"""

from typing import List
from backend.app.rag.models import SecurityDocument, DocumentChunk


class SecurityChunker:
    """Splits security intelligence documents into semantic chunks tailored for vector retrieval."""

    def __init__(self, max_chunk_tokens: int = 350, chunk_overlap: int = 40):
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: SecurityDocument) -> List[DocumentChunk]:
        """Transforms a SecurityDocument into structured semantic chunks."""
        chunks: List[DocumentChunk] = []

        # 1. Main Definition & Threat Concept Chunk
        concept_text = (
            f"VULNERABILITY STANDARD: {doc.title}\n"
            f"Category: {doc.category} | Severity: {doc.severity}\n"
            f"Identifiers: {doc.cwe_id or 'N/A'} | {doc.owasp_category or 'N/A'}\n"
            f"Core Analysis:\n{doc.content}"
        )
        chunks.append(
            DocumentChunk(
                chunk_id=f"CHK-{doc.id}-CONCEPT",
                document_id=doc.id,
                title=f"{doc.title} — Overview & Threat Definition",
                text=concept_text.strip(),
                chunk_type="concept",
                source=doc.source,
                category=doc.category,
                cwe_id=doc.cwe_id,
                owasp_category=doc.owasp_category,
                metadata={
                    "severity": doc.severity,
                    "section": "concept",
                    "doc_title": doc.title
                }
            )
        )

        # 2. Remediation & Hardening Chunk (if remediation steps exist)
        if doc.remediation_steps:
            steps_formatted = "\n".join([f"{i+1}. {step}" for i, step in enumerate(doc.remediation_steps)])
            remediation_text = (
                f"REMEDIATION & HARDENING GUIDANCE FOR {doc.title} ({doc.cwe_id or doc.category}):\n"
                f"Recommended Engineering Actions:\n{steps_formatted}\n"
                f"Compliance & Reference Standards: {', '.join(doc.references) if doc.references else 'KAVACH Defensive Standard'}"
            )
            chunks.append(
                DocumentChunk(
                    chunk_id=f"CHK-{doc.id}-REMEDIATION",
                    document_id=doc.id,
                    title=f"{doc.title} — Step-by-Step Remediation",
                    text=remediation_text.strip(),
                    chunk_type="remediation",
                    source=doc.source,
                    category=doc.category,
                    cwe_id=doc.cwe_id,
                    owasp_category=doc.owasp_category,
                    metadata={
                        "severity": doc.severity,
                        "section": "remediation",
                        "doc_title": doc.title,
                        "steps_count": len(doc.remediation_steps)
                    }
                )
            )

        # 3. Verification & Testing Check Chunk
        probe_instruction = (doc.metadata or {}).get("verification_probe", "")
        probe_line = f"Recommended Probe Command: {probe_instruction}\n" if probe_instruction else ""
        verification_text = (
            f"SECURITY VERIFICATION PROBE FOR {doc.title} ({doc.cwe_id or doc.category}):\n"
            f"To verify defensive resolution, execute targeted security probes or regression checks against the affected endpoint.\n"
            f"{probe_line}"
            f"Ensure boundary validation returns appropriate defensive status codes (e.g. 401/403 for access control, "
            f"clean parameterized failure without error disclosure for injection flaws, or 401/403/404 for protected documentation endpoints)."
        )
        chunks.append(
            DocumentChunk(
                chunk_id=f"CHK-{doc.id}-VERIFY",
                document_id=doc.id,
                title=f"{doc.title} — Technical Verification & Validation",
                text=verification_text.strip(),
                chunk_type="verification",
                source=doc.source,
                category=doc.category,
                cwe_id=doc.cwe_id,
                owasp_category=doc.owasp_category,
                metadata={
                    "severity": doc.severity,
                    "section": "verification",
                    "doc_title": doc.title
                }
            )
        )

        return chunks

    def chunk_all(self, docs: List[SecurityDocument]) -> List[DocumentChunk]:
        """Processes a list of documents into an aggregated list of chunks."""
        all_chunks: List[DocumentChunk] = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks


chunker = SecurityChunker()
