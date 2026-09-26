import uuid
import json
import re
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    user_id = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default="team_member")  # admin, team_member
    full_name = Column(String(100), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(String(50), default="")
    first_login_at = Column(String(50), nullable=True, default="")
    last_login_at = Column(String(50), nullable=True, default="")
    last_active_at = Column(String(50), nullable=True, default="")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    target_url = Column(String(255), nullable=False)
    description = Column(Text, default="")
    environment = Column(String(50), default="Testing Environment")
    scope = Column(String(255), default="Full Application")
    authorization_confirmed = Column(Boolean, default=False)
    modules_enabled = Column(Text, default="[]")  # JSON list
    status = Column(String(50), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED
    progress = Column(Integer, default=0)
    current_stage = Column(String(50), default="DISCOVER")
    started_at = Column(String(50), default="")
    completed_at = Column(String(50), default="")
    is_demo = Column(Boolean, default=False)
    assessment_type = Column(String(50), default="GENERIC_ASSESSMENT")
    parent_assessment_id = Column(String(50), nullable=True)
    owner_id = Column(String(50), nullable=True, default=None, index=True)

    findings = relationship("Finding", back_populates="assessment", cascade="all, delete-orphan")
    discovery_items = relationship("DiscoveryItem", back_populates="assessment", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="assessment", cascade="all, delete-orphan")


class DiscoveryItem(Base):
    __tablename__ = "discovery_items"

    id = Column(String(50), primary_key=True, index=True)
    assessment_id = Column(String(50), ForeignKey("assessments.id"), index=True)
    item_type = Column(String(50), nullable=False)  # endpoint, component, auth_point, input_surface, api_surface, user_role
    name = Column(String(150), nullable=False)
    method = Column(String(20), default="")
    path = Column(String(255), default="")
    details = Column(Text, default="")
    security_relevance = Column(String(50), default="MEDIUM")

    assessment = relationship("Assessment", back_populates="discovery_items")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(50), primary_key=True, index=True)
    assessment_id = Column(String(50), ForeignKey("assessments.id"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    category = Column(String(100), nullable=False)
    affected_component = Column(String(150), default="")
    base_severity = Column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    severity = Column(String(50), default="MEDIUM")       # Raw column in SQLite table
    priority = Column(String(50), default="MEDIUM")       # CRITICAL, HIGH, MEDIUM, LOW, INFO
    priority_score = Column(Float, default=5.0)
    priority_explanation = Column(Text, default="")        # JSON object or breakdown string
    
    # State machine
    # POTENTIAL, UNDER ANALYSIS, VALIDATING, EVIDENCE AVAILABLE, CONFIRMED, UNCONFIRMED, REQUIRES MANUAL REVIEW
    status = Column(String(50), default="POTENTIAL")
    evidence_status = Column(String(50), default="NONE")  # NONE, PENDING, AVAILABLE, VERIFIED
    ai_analysis_status = Column(String(50), default="PENDING") # PENDING, COMPLETED, FAILED, RULE_BASED_FALLBACK

    # AI Analysis & Hypothesis
    ai_summary = Column(Text, default="")
    ai_hypothesis = Column(Text, default="")
    ai_confidence = Column(Float, default=0.0)
    ai_reasoning_summary = Column(Text, default="")
    ai_potential_impact = Column(Text, default="")
    recommended_validation = Column(Text, default="[]")   # JSON list
    recommended_remediation = Column(Text, default="[]")  # JSON list

    # Knowledge mappings
    cwe_id = Column(String(50), default="")
    owasp_category = Column(String(100), default="")
    owasp_id = Column(String(100), default="")

    @property
    def canonical_owasp(self) -> str:
        cat = self.owasp_category or self.owasp_id or ""
        if self.cwe_id and self.cwe_id.upper() == "CWE-200":
            if not cat or "A01" in cat:
                return "OWASP-A05:2021 - Security Misconfiguration"
        return cat

    # Team Desk & Collaboration ("ASSIGN")
    assigned_to = Column(String(100), default="Unassigned")
    team_notes = Column(Text, default="")
    triage_status = Column(String(50), default="NEW")  # NEW, ASSIGNED, IN_PROGRESS, RESOLVED, FALSE_POSITIVE

    created_at = Column(String(50), default="")
    updated_at = Column(String(50), default="")

    assessment = relationship("Assessment", back_populates="findings")
    evidence_records = relationship("EvidenceRecord", back_populates="finding", cascade="all, delete-orphan")
    re_verifications = relationship("ReVerificationRecord", back_populates="finding", cascade="all, delete-orphan")


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id = Column(String(50), primary_key=True, index=True)
    finding_id = Column(String(50), ForeignKey("findings.id"), index=True)
    evidence_type = Column(String(100), nullable=False)
    source = Column(String(150), default="Local Probe")
    timestamp = Column(String(50), default="")
    description = Column(Text, default="")
    raw_data = Column(Text, default="")
    # CONFIRMED, UNCONFIRMED, INCONCLUSIVE, MANUAL REVIEW REQUIRED
    validation_result = Column(String(50), default="INCONCLUSIVE")
    integrity_hash = Column(String(64), default="")  # SHA-256
    is_demo = Column(Boolean, default=False)

    # KAVACH USP Fields
    what_found = Column(Text, default="")
    why_matters = Column(Text, default="")
    where_found = Column(String(255), default="")
    confidence_level = Column(String(50), default="HIGH")  # HIGH, MEDIUM, LOW
    verification_command = Column(Text, default="")
    expected_output = Column(Text, default="")
    observed_output = Column(Text, default="")
    evidence_nature = Column(String(50), default="REAL EVIDENCE")  # REAL EVIDENCE, TEST DATA, DEMO DATA

    finding = relationship("Finding", back_populates="evidence_records")

    @property
    def http_method(self) -> Optional[str]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            if "http_method" in d:
                return d.get("http_method")
        except Exception:
            pass
        if "GET" in (self.verification_command or "") or "Get" in (self.verification_command or ""):
            return "GET"
        if "HEAD" in (self.verification_command or ""):
            return "HEAD"
        if "POST" in (self.verification_command or ""):
            return "POST"
        if "GET " in self.raw_data or "HTTP/" in self.raw_data:
            return "GET"
        return None

    @property
    def http_status(self) -> Optional[int]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            if "http_status" in d:
                return int(d.get("http_status"))
        except Exception:
            pass
        m = re.search(r"HTTP/[^\s]+\s+(\d{3})", self.raw_data)
        if m:
            return int(m.group(1))
        return None

    @property
    def content_type(self) -> Optional[str]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            if "content_type" in d:
                return d.get("content_type")
        except Exception:
            pass
        m = re.search(r"(?i)content-type:\s*([^\r\n]+)", self.raw_data)
        if m:
            return m.group(1).strip()
        return None

    @property
    def openapi_detected(self) -> bool:
        if not self.raw_data:
            return False
        try:
            d = json.loads(self.raw_data)
            # Only claim detected if parsed/validated as OpenAPI
            if d.get("openapi_detected") is True or (d.get("schema_detected") is True and d.get("schema_version")):
                return True
            return False
        except Exception:
            pass
        # Plain text capture: Only claim detected if parsed/validated as OpenAPI
        text = self.raw_data.lower()
        if "openapi" in text and ("schema version" in text or "openapi 3" in text or "openapi:" in text):
            return True
        return False

    @property
    def openapi_version(self) -> Optional[str]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            ver = d.get("openapi_version") or d.get("schema_version")
            if ver:
                return ver
        except Exception:
            pass
        m = re.search(r"(?i)schema version:\s*([^\s|]+)", self.raw_data)
        if m:
            return m.group(1).strip()
        m2 = re.search(r"(?i)openapi\s+([0-9.]+)", self.raw_data)
        if m2:
            return m2.group(1).strip()
        return None

    @property
    def schema_title(self) -> Optional[str]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            if "schema_title" in d:
                return d.get("schema_title")
        except Exception:
            pass
        m = re.search(r"(?i)title:\s*([^|\r\n]+)", self.raw_data)
        if m:
            return m.group(1).strip()
        return None

    @property
    def unauthenticated(self) -> Optional[bool]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            if "unauthenticated" in d:
                return bool(d.get("unauthenticated"))
            if "auth_state" in d:
                return d.get("auth_state") == "UNAUTHENTICATED"
        except Exception:
            pass
        text = self.raw_data.lower()
        if "without authentication" in text or "unauthenticated" in text:
            return True
        return None

    @property
    def authorization_state(self) -> Optional[str]:
        if not self.raw_data:
            return None
        try:
            d = json.loads(self.raw_data)
            state = d.get("authorization_state") or d.get("authz_state")
            if state:
                return state
        except Exception:
            pass
        if "public" in self.raw_data.lower():
            return "PUBLIC"
        return None

    @property
    def is_canonical(self) -> bool:
        if (self.id or "").startswith("EVD-AFT-") or getattr(self, "source", "") == "Re-Test Verification Engine":
            return False
        if self.id == "EV-WM-API-DOCS-A018":
            return False
        if self.id == "EV-WM-API-DOCS-A018-GET":
            return True
        if "-GET" in (self.id or ""):
            return True
        # For general findings with multiple baseline evidence records:
        if getattr(self, "finding", None) and len(self.finding.evidence_records) > 1:
            baseline = [
                e for e in self.finding.evidence_records
                if not ((e.id or "").startswith("EVD-AFT-") or getattr(e, "source", "") == "Re-Test Verification Engine")
            ]
            if len(baseline) > 1:
                get_evds = [e for e in baseline if "-GET" in (e.id or "") or getattr(e, "http_method", None) == "GET"]
                if get_evds:
                    return self.id == get_evds[0].id
                return self.id == baseline[-1].id
        return True

    @property
    def lifecycle_status(self) -> str:
        if (self.id or "").startswith("EVD-AFT-") or getattr(self, "source", "") == "Re-Test Verification Engine":
            return "RETEST"
        if self.id == "EV-WM-API-DOCS-A018":
            return "HISTORICAL"
        if self.id == "EV-WM-API-DOCS-A018-GET":
            return "CANONICAL"
        if self.is_canonical:
            return "CANONICAL"
        return "HISTORICAL"

    @property
    def lifecycle_role(self) -> str:
        if self.lifecycle_status == "CANONICAL":
            return "CANONICAL_ACTIVE"
        elif self.lifecycle_status == "HISTORICAL":
            return "HISTORICAL_SUPERSEDED"
        elif self.lifecycle_status == "RETEST":
            return "RETEST_VERIFICATION"
        return "STANDARD"

    @property
    def relationship_note(self) -> str:
        if self.id == "EV-WM-API-DOCS-A018-GET":
            return "Canonical active evidence proving unauthenticated HTTP GET access to the live OpenAPI schema document."
        if self.id == "EV-WM-API-DOCS-A018":
            return "Historical original live probe artifact retained for cryptographic audit trail continuity (superseded by canonical GET validation)."
        if self.is_canonical:
            return "Canonical active vulnerability proof."
        if self.lifecycle_status == "RETEST":
            return "Deterministic post-remediation re-test verification record."
        return "Historical technical evidence artifact retained for audit continuity."


class ReVerificationRecord(Base):
    __tablename__ = "re_verifications"

    id = Column(String(50), primary_key=True, index=True)
    finding_id = Column(String(50), ForeignKey("findings.id"), index=True)
    timestamp = Column(String(50), default="")
    previous_status = Column(String(50), default="")
    new_status = Column(String(50), default="RESOLVED")  # VERIFIED_REMEDIATED, STILL_OPEN, UNABLE_TO_VERIFY, RESOLVED
    command_executed = Column(Text, default="")
    output_before = Column(Text, default="")
    output_after = Column(Text, default="")
    summary = Column(Text, default="")
    target_url = Column(String(255), default="")
    before_evidence_id = Column(String(50), default="")
    after_evidence_id = Column(String(50), default="")
    before_evidence_hash = Column(String(64), default="")
    after_evidence_hash = Column(String(64), default="")
    state_diff = Column(Text, default="")
    verification_verdict = Column(String(50), default="VERIFIED_REMEDIATED")

    finding = relationship("Finding", back_populates="re_verifications")


class KnowledgeRecord(Base):
    __tablename__ = "knowledge_records"

    id = Column(String(50), primary_key=True, index=True)  # e.g., CWE-89, OWASP-A01
    type = Column(String(50), nullable=False)              # CWE, OWASP
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    related_owasp = Column(String(100), default="")
    remediation = Column(Text, default="[]")                # JSON list
    category = Column(String(100), default="")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, index=True, default=lambda: f"AUD-{uuid.uuid4().hex[:12]}")
    assessment_id = Column(String(50), ForeignKey("assessments.id"), nullable=True, index=True)
    finding_id = Column(String(50), nullable=True, index=True)
    evidence_id = Column(String(50), nullable=True, default="")
    module = Column(String(50), default="CORE")
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(String(50), default="SUCCESS")
    timestamp = Column(String(50), default="")
    metadata_json = Column(Text, default="{}")
    actor = Column(String(100), default="SYSTEM")
    action = Column(String(255), default="EXECUTED")
    object = Column(String(255), default="SYSTEM")
    result = Column(String(50), default="SUCCESS")
    prev_hash = Column(Text, default="")
    event_hash = Column(Text, default="")
    details_json = Column(Text, default="{}")

    assessment = relationship("Assessment", back_populates="audit_events")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(50), nullable=False)
    created_at = Column(String(50), default="")
    expires_at = Column(String(50), default="")
    last_activity_at = Column(String(50), default="")
    ip_address = Column(String(100), default="")
    user_agent = Column(String(255), default="")
    is_active = Column(Boolean, default=True)


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(64), nullable=True)
    event_type = Column(String(100), nullable=False)
    timestamp = Column(String(50), nullable=False)
    assessment_id = Column(String(50), nullable=True)
    finding_id = Column(String(50), nullable=True)
    evidence_id = Column(String(50), nullable=True)
    module = Column(String(50), default="CORE")
    details_json = Column(Text, default="{}")
    status = Column(String(50), default="SUCCESS")


class UserFeedback(Base):
    __tablename__ = "user_feedbacks"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(50), nullable=False)
    assessment_id = Column(String(50), nullable=True)
    rating = Column(Integer, default=5)
    what_worked = Column(Text, default="")
    what_confusing = Column(Text, default="")
    what_slow = Column(Text, default="")
    bug_description = Column(Text, default="")
    suggestions = Column(Text, default="")
    created_at = Column(String(50), default="")
    updated_at = Column(String(50), default="")
