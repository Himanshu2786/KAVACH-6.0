import json
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from backend.app.models.models import Finding, Assessment

class RiskService:
    SEVERITY_WEIGHTS = {
        "CRITICAL": 10.0,
        "HIGH": 8.0,
        "MEDIUM": 5.0,
        "LOW": 2.5,
        "INFO": 1.0
    }

    EVIDENCE_WEIGHTS = {
        "VERIFIED": 10.0,
        "CONFIRMED": 10.0,
        "AVAILABLE": 7.5,
        "EVIDENCE AVAILABLE": 7.5,
        "MANUAL_REVIEW_REQUIRED": 5.0,
        "REQUIRES MANUAL REVIEW": 5.0,
        "VALIDATING": 4.0,
        "UNDER ANALYSIS": 3.0,
        "POTENTIAL": 3.0,
        "UNVERIFIED": 0.5,
        "UNCONFIRMED": 0.5,
        "NONE": 0.0
    }

    def _assess_component_criticality(self, component: str) -> Tuple[float, str]:
        c = (component or "").lower()
        if any(k in c for k in ["auth", "login", "payment", "admin", "token", "session", "vault"]):
            return 10.0, "High Criticality (Core Identity / Security Boundary)"
        elif any(k in c for k in ["user", "order", "api", "query", "database", "account"]):
            return 7.5, "Medium-High Criticality (Business Logic / Data Layer)"
        elif any(k in c for k in ["header", "static", "docs", "asset", "ui"]):
            return 4.0, "Moderate Criticality (Presentation / Peripheral)"
        return 5.0, "Standard Criticality"

    def _assess_data_sensitivity(self, category: str, component: str) -> Tuple[float, str]:
        cat = (category or "").lower()
        if any(k in cat for k in ["access control", "injection", "authentication", "credential"]):
            return 9.5, "Restricted / Sensitive Data (PII, Credentials, Secrets)"
        elif any(k in cat for k in ["validation", "exposure"]):
            return 6.5, "Internal Operational Data"
        return 4.0, "Public / Telemetry Data"

    def calculate_finding_priority(self, finding: Finding, environment: str = "Testing Environment") -> Dict[str, Any]:
        """Calculates deterministic risk score and 'Why This Is Prioritized' breakdown."""
        # 1. Resolve base severity from persisted finding/risk data
        raw_sev = finding.base_severity or getattr(finding, "severity", None) or "MEDIUM"
        severity_str = str(raw_sev).upper()
        finding.base_severity = severity_str
        if hasattr(finding, "severity") and not getattr(finding, "severity", None):
            finding.severity = severity_str

        base_score = self.SEVERITY_WEIGHTS.get(severity_str, 5.0)

        # 2. Resolve finding status (Lifecycle state: CONFIRMED, STILL_OPEN, RESOLVED, etc.)
        status_str = (finding.status or "POTENTIAL").upper()

        # 3. Resolve evidence strength / status from persisted evidence records
        # Evidence strength = empirical technical verification level (VERIFIED, AVAILABLE, MANUAL_REVIEW_REQUIRED, UNVERIFIED, NONE)
        # Finding status = finding remediation / lifecycle state (CONFIRMED, STILL_OPEN, RESOLVED, etc.)
        raw_ev = getattr(finding, "evidence_status", None)
        if not raw_ev or str(raw_ev).upper() in ("NONE", "NULL", ""):
            records = getattr(finding, "evidence_records", []) or []
            if records and any(getattr(r, "validation_result", "") == "CONFIRMED" for r in records):
                finding.evidence_status = "VERIFIED"
            elif records and any(getattr(r, "validation_result", "") == "MANUAL REVIEW REQUIRED" for r in records):
                finding.evidence_status = "AVAILABLE"
            elif records:
                finding.evidence_status = "AVAILABLE"
            elif status_str == "CONFIRMED":
                finding.evidence_status = "VERIFIED"
            else:
                finding.evidence_status = "NONE"

        evidence_strength_str = (finding.evidence_status or "NONE").upper()
        evidence_score = self.EVIDENCE_WEIGHTS.get(evidence_strength_str, 3.0)

        comp_score, comp_desc = self._assess_component_criticality(finding.affected_component or "")
        data_score, data_desc = self._assess_data_sensitivity(finding.category or "", finding.affected_component or "")
        exposure_score = 9.0  # External API / Public Web
        exposure_desc = "External Web / Network Exposure"

        # Multi-factor formula:
        # Final Score = (Base * 0.30) + (Component * 0.25) + (Data * 0.20) + (Evidence * 0.15) + (Exposure * 0.10)
        composite = (
            (base_score * 0.30) +
            (comp_score * 0.25) +
            (data_score * 0.20) +
            (evidence_score * 0.15) +
            (exposure_score * 0.10)
        )

        # Environment multiplier
        env_lower = environment.lower()
        if "prod" in env_lower:
            env_mult = 1.0
        elif "staging" in env_lower:
            env_mult = 0.95
        else:
            env_mult = 0.90
        
        final_score = round(composite * env_mult, 2)

        # Map to priority tier
        if final_score >= 8.0:
            priority = "CRITICAL"
        elif final_score >= 6.5:
            priority = "HIGH"
        elif final_score >= 4.0:
            priority = "MEDIUM"
        elif final_score >= 2.0:
            priority = "LOW"
        else:
            priority = "INFO"

        explanation = {
            "base_severity": {
                "level": severity_str,
                "score": base_score,
                "weight": "30%",
                "rationale": f"Initial assessment baseline severity is {severity_str}."
            },
            "component_criticality": {
                "score": comp_score,
                "weight": "25%",
                "rationale": comp_desc
            },
            "data_sensitivity": {
                "score": data_score,
                "weight": "20%",
                "rationale": data_desc
            },
            "evidence_strength": {
                "level": evidence_strength_str,
                "score": evidence_score,
                "weight": "15%",
                "rationale": f"Evidence strength '{evidence_strength_str}' contributes {evidence_score:.1f} / 10.0 to prioritization."
            },
            "exposure": {
                "score": exposure_score,
                "weight": "10%",
                "rationale": exposure_desc
            },
            "environment_factor": {
                "multiplier": env_mult,
                "environment": environment
            },
            "summary_statement": f"Priority calculated deterministically as {priority} (Score: {final_score:.2f} / 10.0) driven by {severity_str} base severity and {comp_desc}."
        }

        return {
            "priority": priority,
            "priority_score": final_score,
            "priority_scale": "10.0",
            "priority_score_formatted": f"{final_score:.2f} / 10.0",
            "explanation": explanation
        }

    def prioritize_all_findings(self, db: Session, assessment_id: str) -> List[Dict[str, Any]]:
        from backend.app.models.models import EvidenceRecord
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        env = assessment.environment if assessment else "Testing Environment"
        findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()

        results = []
        for f in findings:
            # 1. Resolve base_severity if missing on model from severity column or assessment data
            if not f.base_severity:
                raw_sev = getattr(f, "severity", None) or "MEDIUM"
                f.base_severity = str(raw_sev).upper()
                if hasattr(f, "severity"):
                    f.severity = f.base_severity

            # 2. Resolve evidence_status from persisted evidence/validation records if missing
            if not f.evidence_status or f.evidence_status.upper() in ("NONE", "NULL"):
                records = getattr(f, "evidence_records", []) or []
                if not records:
                    records = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == f.id).all()
                if records and any(r.validation_result == "CONFIRMED" for r in records):
                    f.evidence_status = "VERIFIED"
                elif records and any(r.validation_result == "MANUAL REVIEW REQUIRED" for r in records):
                    f.evidence_status = "AVAILABLE"
                elif records:
                    f.evidence_status = "AVAILABLE"
                elif (f.status or "").upper() == "CONFIRMED":
                    f.evidence_status = "VERIFIED"
                else:
                    f.evidence_status = "NONE"

            res = self.calculate_finding_priority(f, env)
            f.priority = res["priority"]
            f.priority_score = res["priority_score"]
            f.priority_explanation = json.dumps(res["explanation"])

            from backend.app.services.cve_provenance_service import cve_provenance_service
            cve_prov = cve_provenance_service.get_provenance_for_finding(f)

            results.append({
                "finding_id": f.id,
                "title": f.title,
                "category": f.category,
                "affected_component": f.affected_component,
                "base_severity": f.base_severity,
                "calculated_priority": f.priority,
                "priority_score": f.priority_score,
                "priority_scale": "10.0",
                "priority_score_formatted": f"{f.priority_score:.2f} / 10.0",
                "status": f.status,
                "evidence_strength": f.evidence_status or "NONE",
                "component_criticality": res["explanation"]["component_criticality"]["rationale"],
                "data_sensitivity": res["explanation"]["data_sensitivity"]["rationale"],
                "exposure": res["explanation"]["exposure"]["rationale"],
                "cwe_id": getattr(f, "cwe_id", "") or "",
                "owasp_category": getattr(f, "canonical_owasp", None) or getattr(f, "owasp_category", "") or "",
                "cve_id": cve_prov["cve_id"],
                "cve_status": cve_prov["cve_status"],
                "nvd_cvss": cve_prov["nvd_cvss"],
                "nvd_cvss_display": cve_prov["nvd_cvss_display"],
                "explanation": res["explanation"]
            })

        db.commit()
        # Sort descending by priority score
        results.sort(key=lambda x: x["priority_score"], reverse=True)
        return results

risk_service = RiskService()
