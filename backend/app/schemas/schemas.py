from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union

# Generic Response Wrapper
class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

# Assessment Schemas
class AssessmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    target_url: str = Field(..., min_length=4, max_length=255)
    description: Optional[str] = ""
    environment: str = Field("Testing Environment")  # Local Development, Testing Environment, Staging, Demo Environment
    scope: str = Field("Full Application")
    authorization_confirmed: bool = Field(...)
    modules_enabled: List[str] = Field(default_factory=lambda: ["Authentication", "API Security", "Security Headers"])
    is_demo: bool = False
    assessment_type: Optional[str] = "GENERIC_ASSESSMENT"
    parent_assessment_id: Optional[str] = None

class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str = "Assessment"
    target_url: str = "http://localhost:8000"
    description: Optional[str] = ""
    environment: Optional[str] = "Testing Environment"
    scope: Optional[str] = "Full Application"
    authorization_confirmed: Optional[bool] = True
    modules_enabled: Optional[List[str]] = ["Authentication", "API Security", "Client Security"]
    status: Optional[str] = "COMPLETED"
    progress: Optional[int] = 100
    current_stage: Optional[str] = "REPORT"
    started_at: Optional[str] = ""
    completed_at: Optional[str] = ""
    is_demo: Optional[bool] = False
    assessment_type: Optional[str] = "GENERIC_ASSESSMENT"
    parent_assessment_id: Optional[str] = None
    owner_id: Optional[str] = None
    total_findings: Optional[int] = 0
    confirmed_findings: Optional[int] = 0

# Discovery Schemas
class DiscoveryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    item_type: str
    name: str
    method: str
    path: str
    details: str
    security_relevance: str

# Evidence Schemas
class EvidenceCreate(BaseModel):
    finding_id: Optional[str] = None
    evidence_type: str
    source: Optional[str] = "Manual Probe"
    description: str
    raw_data: str
    validation_result: str  # CONFIRMED, UNCONFIRMED, INCONCLUSIVE, MANUAL REVIEW REQUIRED
    is_demo: bool = False
    what_found: Optional[str] = ""
    why_matters: Optional[str] = ""
    where_found: Optional[str] = ""
    confidence_level: Optional[str] = "HIGH"
    verification_command: Optional[str] = ""
    expected_output: Optional[str] = ""
    observed_output: Optional[str] = ""
    evidence_nature: Optional[str] = "REAL EVIDENCE"

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    finding_id: Union[str, None] = None
    evidence_type: Optional[str] = "PROBE"
    source: Optional[str] = "Local Probe"
    timestamp: Optional[str] = ""
    description: Optional[str] = ""
    raw_data: Optional[str] = ""
    validation_result: Optional[str] = "INCONCLUSIVE"
    integrity_hash: Optional[str] = ""
    is_demo: Optional[bool] = False
    what_found: Optional[str] = ""
    why_matters: Optional[str] = ""
    where_found: Optional[str] = ""
    confidence_level: Optional[str] = "HIGH"
    verification_command: Optional[str] = ""
    expected_output: Optional[str] = ""
    observed_output: Optional[str] = ""
    evidence_nature: Optional[str] = "REAL EVIDENCE"
    cwe_id: Optional[str] = ""
    owasp_category: Optional[str] = ""

    # Explicit Technical Protocol Evidence Fields
    http_method: Optional[str] = None
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    openapi_detected: Optional[bool] = None
    openapi_version: Optional[str] = None
    schema_title: Optional[str] = None
    unauthenticated: Optional[bool] = None
    authorization_state: Optional[str] = None

    # Evidence Lifecycle & Deduplication Fields
    lifecycle_status: Optional[str] = "CANONICAL"
    lifecycle_role: Optional[str] = ""
    is_canonical: Optional[bool] = True
    relationship_note: Optional[str] = ""

# Terminal Technical Verification Schema
class TerminalVerificationResponse(BaseModel):
    assessment_id: str
    evidence_id: str
    target: str
    timestamp: str
    check_name: str
    method: str
    verification_steps: List[str]
    command: str
    expected_output: str
    observed_output: str
    status: str
    integrity_hash: str
    evidence_nature: str
    cwe_id: Optional[str] = ""
    owasp_category: Optional[str] = ""

# Re-Verification Schemas
class ReVerificationRequest(BaseModel):
    finding_id: Optional[str] = ""
    command_executed: Optional[str] = ""
    output_after: Optional[str] = ""
    force_status: Optional[str] = None  # STILL OBSERVED, IMPROVED, RESOLVED, NEEDS REVIEW

class ReVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    finding_id: str
    timestamp: str
    previous_status: str
    new_status: str
    command_executed: str
    output_before: str
    output_after: str
    summary: str
    target_url: Optional[str] = ""
    before_evidence_id: Optional[str] = ""
    after_evidence_id: Optional[str] = ""
    before_evidence_hash: Optional[str] = ""
    after_evidence_hash: Optional[str] = ""
    state_diff: Optional[str] = ""
    verification_verdict: Optional[str] = "VERIFIED_REMEDIATED"

# Finding Schemas
class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: Optional[str] = "GLOBAL"
    title: str
    description: Optional[str] = ""
    category: str
    affected_component: Optional[str] = ""
    base_severity: Optional[str] = "MEDIUM"
    priority: Optional[str] = "MEDIUM"
    priority_score: Optional[float] = 5.0
    priority_explanation: Optional[str] = ""
    status: Optional[str] = "POTENTIAL"
    evidence_status: Optional[str] = "NONE"
    ai_analysis_status: Optional[str] = "PENDING"
    ai_summary: Optional[str] = ""
    ai_hypothesis: Optional[str] = ""
    ai_confidence: Optional[float] = 0.0
    ai_reasoning_summary: Optional[str] = ""
    ai_potential_impact: Optional[str] = ""
    recommended_validation: Optional[List[str]] = []
    recommended_remediation: Optional[List[str]] = []
    cwe_id: Optional[str] = ""
    owasp_category: Optional[str] = ""
    priority_scale: Optional[str] = "10.0"
    priority_score_formatted: Optional[str] = "5.00 / 10.0"
    cve_id: Optional[str] = None
    cve_status: Optional[str] = "Not identified"
    nvd_cvss: Optional[float] = None
    nvd_cvss_display: Optional[str] = "Not available"
    nvd_reference: Optional[str] = None
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""
    evidence_records: List[EvidenceResponse] = []
    ai_provider: Optional[str] = "fallback"

# AI Structured Response Specification
class AIStructuredAnalysis(BaseModel):
    summary: str
    security_hypothesis: str
    affected_component: str
    potential_impact: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    reasoning_summary: str
    recommended_validation: List[str]
    recommended_remediation: List[str]
    ai_provider: Optional[str] = "fallback"

# System & Ollama Schemas
class OllamaStatusResponse(BaseModel):
    status: str  # "online" or "offline"
    base_url: str
    available_models: List[str]
    selected_model: str
    response_time_ms: Optional[float] = None
    message: Optional[str] = None

class ModelSelectionRequest(BaseModel):
    model_name: str

class SystemStatusResponse(BaseModel):
    frontend_status: str
    backend_status: str
    ollama_status: str
    ollama_model: str
    ollama_base_url: str
    database_status: str
    knowledge_engine: str
    assessment_engine: str
    validation_engine: str
    active_assessment_count: int
    total_findings_count: int

# Knowledge Record Schemas
class KnowledgeResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    related_owasp: str
    remediation: List[str]
    category: str

# Risk Prioritization Item
class RiskPrioritizationItem(BaseModel):
    finding_id: str
    title: str
    category: str
    affected_component: str
    base_severity: str
    calculated_priority: str
    priority_score: float
    priority_scale: Optional[str] = "10.0"
    priority_score_formatted: Optional[str] = "5.00 / 10.0"
    status: str
    evidence_strength: str
    component_criticality: str
    data_sensitivity: str
    exposure: str
    explanation: Dict[str, Any]
    cwe_id: Optional[str] = ""
    owasp_category: Optional[str] = ""
    cve_id: Optional[str] = None
    cve_status: Optional[str] = "Not identified"
    nvd_cvss: Optional[float] = None
    nvd_cvss_display: Optional[str] = "Not available"

# Audit Event Schema
class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Union[int, str]
    assessment_id: Optional[str] = None
    finding_id: Optional[str] = None
    module: Optional[str] = "CORE"
    event_type: str
    description: str
    evidence_id: Optional[str] = None
    status: Optional[str] = "SUCCESS"
    timestamp: str
    metadata_json: str

