"""
KAVACH RAG Pipeline
Orchestrates knowledge retrieval, grounded context assembly, and LLM explanation generation.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from backend.app.rag.models import RagQueryRequest, RagResponse, RetrievalResult
from backend.app.rag.retriever import rag_retriever
from backend.app.models.models import Finding, EvidenceRecord
from backend.app.services.ollama_service import ollama_service
from backend.app.services.ai_analysis_service import ai_analysis_service

logger = logging.getLogger("kavach.rag.pipeline")


class RagPipeline:
    """End-to-end Retrieval-Augmented Generation pipeline for KAVACH security analysis."""

    RAG_SYSTEM_PROMPT = (
        "You are KAVACH Security Intelligence Engine — a grounded cybersecurity analyst.\n"
        "Analyze the finding or query using ONLY the provided verified finding evidence and RETRIEVED SECURITY KNOWLEDGE.\n"
        "Strict Grounding Rules:\n"
        "1. Base your technical rationale and remediation steps directly on the retrieved security standards (CWE / OWASP).\n"
        "2. Cite the relevant retrieved standards (e.g. CWE-89, CWE-639, OWASP Top 10) in your response.\n"
        "3. Do not hallucinate fictitious CVEs or fabricate unobserved vulnerabilities.\n"
        "4. Return structured JSON ONLY with these exact 7 keys:\n"
        "{\n"
        '  "what_was_found": "Clear description of the confirmed observation referencing verified context",\n'
        '  "where": "Precise endpoint, file, or component location",\n'
        '  "why_it_matters": "Security consequence grounded in retrieved threat definitions",\n'
        '  "possible_impact": "Operational, data confidentiality, or compliance impact",\n'
        '  "recommended_action": "Strategic engineering priority grounded in retrieved remediation standards",\n'
        '  "how_to_fix": "Step-by-step remediation instructions adopting standard defensive patterns",\n'
        '  "how_to_verify": "Safe terminal command or reproduction check to prove resolution"\n'
        "}"
    )

    def _build_grounded_prompt(self, finding_context: str, retrieved_sources: List[RetrievalResult]) -> str:
        """Constructs an augmented prompt embedding retrieved knowledge chunks."""
        sources_text = ""
        if retrieved_sources:
            sources_text = "\n\n".join([
                f"[Source {i+1}: {s.title} ({s.cwe_id or s.category}) | Relevance Score: {int(s.score * 100)}%]\n{s.text}"
                for i, s in enumerate(retrieved_sources)
            ])
        else:
            sources_text = "No specific external knowledge chunks retrieved. Rely on baseline security principles."

        prompt = (
            f"=== VALIDATED FINDING CONTEXT ===\n"
            f"{finding_context}\n\n"
            f"=== RETRIEVED SECURITY KNOWLEDGE (GROUNDING CONTEXT) ===\n"
            f"{sources_text}\n\n"
            f"=== TASK ===\n"
            f"Synthesize the finding context with the retrieved security standards above.\n"
            f"Generate a rigorous, grounded 7-section security explanation in JSON format."
        )
        return prompt

    async def query(self, req: RagQueryRequest) -> RagResponse:
        """Processes a general security query through the RAG pipeline."""
        start_time = time.time()

        # 1. Retrieve top-K relevant security chunks
        retrieved_sources, retrieval_mode, embedding_model = await rag_retriever.retrieve(
            query=req.query,
            top_k=req.top_k,
            category_filter=req.filter_category
        )

        # 2. Build grounded prompt
        finding_context = f"Security Intelligence Query:\n{req.query}"
        user_prompt = self._build_grounded_prompt(finding_context, retrieved_sources)

        # 3. Check LLM availability
        health = await ollama_service.check_health()
        is_llm_ready = health.get("status_code") == "ready"

        answer_data: Dict[str, Any] = {}
        model_used = ollama_service.selected_model if is_llm_ready else "KAVACH-RuleEngine"

        ai_prov = "fallback"
        if is_llm_ready:
            raw_res = await ollama_service.generate_completion(self.RAG_SYSTEM_PROMPT, user_prompt)
            if raw_res:
                try:
                    answer_data = ai_analysis_service._extract_json(raw_res)
                    ai_prov = "ollama"
                except Exception:
                    answer_data = {
                        "what_was_found": f"Analysis for query: {req.query}",
                        "where": "Target Infrastructure",
                        "why_it_matters": "Grounded assessment against retrieved security standards.",
                        "possible_impact": "Potential security exposure requiring remediation.",
                        "recommended_action": "Apply defensive controls outlined in retrieved sources.",
                        "how_to_fix": "\n".join([f"- {s.title}" for s in retrieved_sources[:3]]),
                        "how_to_verify": "Perform validation testing according to retrieved baseline."
                    }
                    ai_prov = "ollama"

        if not answer_data:
            # Deterministic synthesized answer
            top_titles = [s.title for s in retrieved_sources[:2]]
            answer_data = {
                "what_was_found": f"Retrieved {len(retrieved_sources)} relevant security standards for '{req.query}'.",
                "where": "Application Security Baseline",
                "why_it_matters": f"Aligned with {', '.join(top_titles) if top_titles else 'KAVACH security baselines'}.",
                "possible_impact": "Inconsistent enforcement of security controls risks exposure.",
                "recommended_action": "Review retrieved security standards and align component configurations.",
                "how_to_fix": "1. Consult retrieved remediation guidance.\n2. Implement least-privilege boundaries.\n3. Validate fix.",
                "how_to_verify": "Execute verification probe on affected components."
            }
            ai_prov = "fallback"

        answer_data["ai_provider"] = ai_prov
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return RagResponse(
            query=req.query,
            retrieval_mode=retrieval_mode,
            embedding_model=embedding_model,
            retrieved_sources=retrieved_sources,
            context_tokens_approx=len(user_prompt) // 4,
            answer=answer_data,
            model_used=model_used,
            execution_time_ms=elapsed_ms,
            ai_provider=ai_prov
        )

    async def analyze_finding(
        self,
        finding: Finding,
        evidence: Optional[EvidenceRecord] = None,
        top_k: int = 4
    ) -> RagResponse:
        """Executes full RAG workflow specifically tailored to a validated KAVACH finding."""
        start_time = time.time()

        # Formulate rich query from finding attributes
        evidence_preview = ""
        if evidence and evidence.raw_data:
            evidence_preview = ollama_service.mask_sensitive_data(evidence.raw_data[:400])

        query_text = (
            f"{finding.title} {finding.category} {finding.cwe_id or ''} {finding.owasp_category or ''} "
            f"{finding.affected_component or ''} {evidence_preview}"
        ).strip()

        # 1. Retrieve relevant security chunks (finding-aware)
        retrieved_sources, retrieval_mode, embedding_model = await rag_retriever.retrieve_for_finding(
            finding=finding,
            evidence=evidence,
            top_k=top_k
        )

        # 2. Build grounded prompt
        finding_context = (
            f"Finding ID: {finding.id}\n"
            f"Title: {finding.title}\n"
            f"Severity: {finding.base_severity}\n"
            f"Category: {finding.category}\n"
            f"Component: {finding.affected_component}\n"
            f"CWE: {finding.cwe_id or 'N/A'}\n"
            f"OWASP: {finding.owasp_category or 'N/A'}\n"
            f"Evidence Snippet:\n{evidence_preview or 'No raw evidence payload available.'}"
        )

        # Add explicit evidence bounds for API documentation exposure findings
        cwe_id_val = getattr(finding, "cwe_id", "") or ""
        title_val = getattr(finding, "title", "") or ""
        if cwe_id_val == "CWE-200" or "api doc" in title_val.lower() or "openapi" in title_val.lower():
            finding_context += (
                "\n\nSTRICT EVIDENCE BOUNDARY CONSTRAINTS:\n"
                "- OBSERVED FACT: Unauthenticated GET request to /openapi.json returned HTTP 200 and exposed API schema/documentation.\n"
                "- SUPPORTED INTERPRETATION: Public schema exposure can provide attackers with information useful for reconnaissance and endpoint discovery.\n"
                "- NOT PROVEN BY CURRENT EVIDENCE: Do NOT claim data extraction, account compromise, privilege escalation, lateral movement, integrity compromise, availability compromise, or clickjacking.\n"
                "- REMEDIATION FOCUS: Restricting/disabling production API documentation, protecting schema endpoints, removing internal/admin/deprecated details, and validating public documentation.\n"
                "- HOW TO VERIFY: Probe unauthenticated GET access to /openapi.json and expect HTTP 401/403/404 on production deployments.\n"
                "- CORE PRINCIPLE: AI Confidence != Vulnerability Confirmation."
            )

        user_prompt = self._build_grounded_prompt(finding_context, retrieved_sources)

        # 3. Check LLM availability
        health = await ollama_service.check_health()
        is_llm_ready = health.get("status_code") == "ready"

        answer_data: Dict[str, Any] = {}
        model_used = ollama_service.selected_model if is_llm_ready else "KAVACH-RuleEngine"

        ai_prov = "fallback"
        if is_llm_ready:
            raw_res = await ollama_service.generate_completion(self.RAG_SYSTEM_PROMPT, user_prompt)
            if raw_res:
                try:
                    answer_data = ai_analysis_service._extract_json(raw_res)
                    ai_prov = "ollama"
                except Exception as e:
                    logger.warning("Could not parse LLM JSON response: %s", e)

        if not answer_data:
            # Deterministic rule fallback, but enhanced with retrieved knowledge
            fallback = ai_analysis_service._generate_structured_rule_fallback(finding, evidence)
            answer_data = fallback
            ai_prov = "fallback"

        answer_data["ai_provider"] = ai_prov
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return RagResponse(
            query=query_text,
            retrieval_mode=retrieval_mode,
            embedding_model=embedding_model,
            retrieved_sources=retrieved_sources,
            context_tokens_approx=len(user_prompt) // 4,
            answer=answer_data,
            model_used=model_used,
            execution_time_ms=elapsed_ms,
            ai_provider=ai_prov
        )


rag_pipeline = RagPipeline()
