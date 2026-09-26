import uuid
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import Assessment, Finding
from backend.app.schemas.schemas import AssessmentCreate
from backend.app.core.audit import log_audit_event
from backend.app.core.time import ist_isoformat
from backend.app.services.discovery_service import discovery_service

STAGES = [
    "DISCOVER",
    "ASSESS",
    "CORRELATE",
    "ANALYZE",
    "VALIDATE",
    "PRIORITIZE",
    "REMEDIATE",
    "REPORT"
]

STAGE_PROGRESS = {
    "DISCOVER": 15,
    "ASSESS": 30,
    "CORRELATE": 45,
    "ANALYZE": 60,
    "VALIDATE": 75,
    "PRIORITIZE": 85,
    "REMEDIATE": 95,
    "REPORT": 100
}

class AssessmentService:
    def create_assessment(self, db: Session, data: AssessmentCreate, owner_id: Optional[str] = None, creator_id: Optional[str] = None) -> Assessment:
        if not data.authorization_confirmed:
            raise ValueError("Authorization Confirmation is required before initiating an assessment.")

        effective_owner = owner_id or creator_id
        assessment_id = f"ASM-{uuid.uuid4().hex[:8].upper()}"
        now_str = ist_isoformat()

        assessment = Assessment(
            id=assessment_id,
            name=data.name,
            target_url=data.target_url,
            description=data.description or "",
            environment=data.environment,
            scope=data.scope,
            authorization_confirmed=data.authorization_confirmed,
            modules_enabled=json.dumps(data.modules_enabled),
            status="RUNNING",
            progress=15,
            current_stage="DISCOVER",
            started_at=now_str,
            completed_at="",
            is_demo=data.is_demo,
            assessment_type="DEMO" if data.is_demo else (getattr(data, "assessment_type", "GENERIC_ASSESSMENT") or "GENERIC_ASSESSMENT"),
            parent_assessment_id=getattr(data, "parent_assessment_id", None),
            owner_id=effective_owner
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        log_audit_event(
            db=db,
            event_type="ASSESSMENT_CREATED",
            description=f"Security assessment {assessment.name} ({assessment.id}) created for target {assessment.target_url}. Environment: {assessment.environment}. Owner: {owner_id or 'SYSTEM'}.",
            assessment_id=assessment.id
        )

        # Automatically populate initial discovery items
        discovery_service.seed_demo_discovery(db, assessment.id)

        return assessment

    def get_all(self, db: Session, current_user = None) -> List[Assessment]:
        query = db.query(Assessment)
        # Multi-user isolation: Admin sees all; Team members see unowned/demo/shared + their own
        if current_user and getattr(current_user, "role", "") != "admin":
            user_id = getattr(current_user, "id", None)
            query = query.filter(
                (Assessment.owner_id == None) |
                (Assessment.owner_id == "") |
                (Assessment.owner_id == user_id) |
                (Assessment.is_demo == True)
            )
        return query.order_by(Assessment.started_at.desc()).all()

    def get_by_id(self, db: Session, assessment_id: str) -> Optional[Assessment]:
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    def advance_stage(self, db: Session, assessment_id: str, target_stage: str) -> Assessment:
        assessment = self.get_by_id(db, assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")

        if target_stage not in STAGES:
            raise ValueError(f"Invalid stage. Must be one of {STAGES}")

        old_stage = assessment.current_stage or "DISCOVER"
        # Normalize if old_stage was stored as legacy string "COMPLETE" (which is a status, not a stage)
        if old_stage == "COMPLETE":
            old_stage = "REPORT"
            assessment.current_stage = "REPORT"

        # If already at the target stage or already completed at REPORT, do not emit redundant/invalid transition
        if old_stage == target_stage or (assessment.status == "COMPLETED" and target_stage == "REPORT"):
            if assessment.current_stage != target_stage:
                assessment.current_stage = target_stage
                db.commit()
                db.refresh(assessment)
            return assessment

        assessment.current_stage = target_stage
        assessment.progress = STAGE_PROGRESS.get(target_stage, 50)
        
        if target_stage == "REPORT":
            assessment.status = "COMPLETED"
            assessment.completed_at = ist_isoformat()

        db.commit()
        db.refresh(assessment)

        log_audit_event(
            db=db,
            event_type="ASSESSMENT_STAGE_ADVANCED",
            description=f"Assessment stage advanced from {old_stage} to {target_stage} ({assessment.progress}%).",
            assessment_id=assessment.id
        )

        if target_stage == "ASSESS":
            try:
                from backend.app.services.security_module_runner import security_module_runner
                security_module_runner.run_modules_for_assessment(db, assessment)
            except Exception as e:
                log_audit_event(
                    db=db,
                    event_type="ASSESS_EXECUTION_ERROR",
                    description=f"Error executing security modules: {e}",
                    assessment_id=assessment.id,
                    status="FAILED"
                )

        return assessment

    def _build_dynamic_summary(self, findings: List[Finding]) -> str:
        """Dynamically generates an executive narrative reflecting the exact findings in scope."""
        if not findings:
            return "No security findings recorded for this target scope."

        confirmed = [f for f in findings if f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]
        has_still_open = any(f.status == "STILL_OPEN" for f in findings)
        categories = sorted(list(set(f.category for f in findings if f.category)))

        # Check for specific API schema / documentation findings
        api_doc_findings = [
            f for f in findings
            if any(k in f.title.lower() for k in ("api schema", "api documentation", "openapi", "swagger", "interactive api"))
            or ("documentation" in f.title.lower() and "api" in (f.title.lower() + " " + (f.category or "").lower()))
            or "openapi" in (f.affected_component or "").lower()
        ]

        if len(findings) == 1 and api_doc_findings:
            f = api_doc_findings[0]
            retest_clause = " The finding remains STILL_OPEN following empirical re-verification on the live endpoint." if has_still_open else ""
            return (
                f"Security assessment identified 1 confirmed API-security finding on the target scope "
                f"involving publicly accessible interactive API schema and documentation endpoints ({f.affected_component})."
                f"{retest_clause}"
            )

        # Check if findings are exclusively security headers
        is_only_headers = all(
            "header" in f.title.lower() or "hsts" in f.title.lower() or "csp" in f.title.lower() or f.category in ("Security Headers", "HTTP Headers")
            for f in findings
        )
        if is_only_headers:
            return f"Identified {len(findings)} security finding(s) relating to baseline HTTP transport and client defense headers."

        # Mixed / general findings
        parts = []
        if confirmed:
            parts.append(f"Security assessment identified {len(confirmed)} confirmed finding(s) supported by technical verification evidence")
        else:
            parts.append(f"Security assessment recorded {len(findings)} finding(s)")

        if categories:
            parts.append(f"across {', '.join(categories)}")

        summary_str = " ".join(parts) + "."
        if has_still_open:
            summary_str += " Empirical re-testing verified active finding(s) remain STILL_OPEN on the target."
        return summary_str

    def calculate_security_posture(self, db: Session, assessment_id: str) -> Dict[str, Any]:
        """Calculates deterministic overall security posture based on findings data."""
        findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
        if not findings:
            return {
                "posture": "SECURE",
                "risk_level": "LOW",
                "score": 95,
                "status_label": "No Vulnerabilities Identified",
                "summary": "No security findings recorded for this target scope."
            }

        confirmed_critical = [f for f in findings if f.base_severity == "CRITICAL" and f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]
        confirmed_high = [f for f in findings if f.base_severity == "HIGH" and f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]
        confirmed_medium = [f for f in findings if f.base_severity == "MEDIUM" and f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]
        confirmed_low = [f for f in findings if f.base_severity == "LOW" and f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]

        potential_critical = [f for f in findings if f.base_severity == "CRITICAL" and f.status not in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]
        potential_high = [f for f in findings if f.base_severity == "HIGH" and f.status not in ("CONFIRMED", "STILL_OPEN", "VERIFIED")]

        summary = self._build_dynamic_summary(findings)

        if confirmed_critical:
            posture = "CRITICAL RISK"
            risk_level = "CRITICAL"
            score = 35
            label = "Immediate Remediation Required"
        elif confirmed_high:
            posture = "HIGH RISK"
            risk_level = "HIGH"
            score = 52
            label = "Elevated Exposure"
        elif confirmed_medium:
            posture = "MODERATE RISK"
            risk_level = "MEDIUM"
            score = 70
            label = "Remediation & Hardening Required"
        elif potential_critical or potential_high:
            posture = "MODERATE RISK"
            risk_level = "MEDIUM"
            score = 68
            label = "Potential Threats Under Validation"
        elif confirmed_low:
            posture = "LOW RISK"
            risk_level = "LOW"
            score = 85
            label = "Defensive Hardening Recommended"
        else:
            posture = "INFORMATIONAL"
            risk_level = "LOW"
            score = 90
            label = "Observation Recorded"

        confirmed_count = len([f for f in findings if f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")])
        potential_count = len([f for f in findings if f.status in ("POTENTIAL", "UNDER ANALYSIS", "VALIDATING")])

        return {
            "posture": posture,
            "risk_level": risk_level,
            "score": score,
            "status_label": label,
            "summary": summary,
            "total_findings": len(findings),
            "confirmed_count": confirmed_count,
            "potential_count": potential_count
        }

assessment_service = AssessmentService()
