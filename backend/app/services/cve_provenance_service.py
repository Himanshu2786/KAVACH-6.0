import re
from typing import Dict, Any, Optional

class CVEProvenanceService:
    """
    KAVACH 5.0 Authoritative CVE & NVD Provenance Verification Engine.

    Strict Provenance Requirements:
    Every displayed NVD CVSS score and CVE relationship must satisfy ALL four criteria:
    1. Valid CVE Identifier (format: CVE-YYYY-NNNN+)
    2. Authoritative NVD Source / Reference URL (e.g. nvd.nist.gov or mitre.org)
    3. Matching Affected Product & Version Context (proven match against the assessed component)
    4. Verified Technical Relationship to the Finding (empirical proof linking the vulnerability)

    If any criterion is missing or unverified:
    - cve_id is None (or candidate is held in unverified status)
    - cve_status is "Not identified" (or "Version Verification Required" ONLY when candidate version relationship exists)
    - nvd_cvss is None (display: "Not available")
    - nvd_reference is None
    - Fabricated or default scores are strictly prohibited.
    """

    CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

    def evaluate_provenance(
        self,
        finding_id: str,
        category: str = "",
        affected_component: str = "",
        candidate_cve: Optional[str] = None,
        candidate_cvss: Optional[float] = None,
        candidate_reference: Optional[str] = None,
        candidate_version_status: Optional[str] = None,
        verified_match: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates candidate CVE/NVD records against strict provenance rules.
        """
        # Rule 1: Specific handling for API Schema & Documentation Exposure findings
        # Findings like WM-API-DOCS-A018 represent informational web surface exposures (CWE-200),
        # not a specific vulnerable software package with an NVD CVE entry.
        if (
            "API-DOCS" in (finding_id or "").upper() or
            "API Documentation" in (category or "") or
            "openapi" in (affected_component or "").lower()
        ):
            # Unrelated CVEs (such as OpenSSH, XZ, HTTP/2, etc.) cannot be attached to API docs exposures
            return {
                "cve_id": None,
                "cve_status": "Not identified",
                "nvd_cvss": None,
                "nvd_cvss_display": "Not available",
                "nvd_reference": None,
                "provenance_verified": False,
                "reason": "No confirmed specific CVE is associated with public /openapi.json schema exposure (CWE-200)."
            }

        # Rule 2: If no candidate CVE is provided at all
        if not candidate_cve or not candidate_cve.strip():
            return {
                "cve_id": None,
                "cve_status": "Not identified",
                "nvd_cvss": None,
                "nvd_cvss_display": "Not available",
                "nvd_reference": None,
                "provenance_verified": False,
                "reason": "No CVE record identified for this finding."
            }

        cve_clean = candidate_cve.strip().upper()

        # Rule 3: Validate CVE format
        if not self.CVE_REGEX.match(cve_clean):
            return {
                "cve_id": None,
                "cve_status": "Not identified",
                "nvd_cvss": None,
                "nvd_cvss_display": "Not available",
                "nvd_reference": None,
                "provenance_verified": False,
                "reason": f"Invalid CVE identifier format: '{candidate_cve}'."
            }

        # Rule 4: Verify NVD Reference/Source
        has_nvd_source = bool(
            candidate_reference and (
                "nvd.nist.gov" in candidate_reference.lower() or
                "cve.org" in candidate_reference.lower() or
                "cve.mitre.org" in candidate_reference.lower()
            )
        )

        # Rule 5: Version verification relationship
        if candidate_version_status and "VERSION VERIFICATION" in candidate_version_status.upper():
            # A candidate CVE exists with a version relationship that requires verification.
            # In this state, the CVE is noted as requiring verification, but unverified NVD CVSS is NOT asserted as confirmed.
            return {
                "cve_id": cve_clean,
                "cve_status": "Version Verification Required",
                "nvd_cvss": candidate_cvss if verified_match and has_nvd_source else None,
                "nvd_cvss_display": f"{candidate_cvss:.1f} / 10.0" if (candidate_cvss is not None and verified_match and has_nvd_source) else "Not available",
                "nvd_reference": candidate_reference if has_nvd_source else f"https://nvd.nist.gov/vuln/detail/{cve_clean}",
                "provenance_verified": bool(verified_match and has_nvd_source),
                "reason": "CVE software relationship requires explicit version verification."
            }

        # Rule 6: Fully confirmed match with all 4 criteria
        if verified_match and has_nvd_source and candidate_cvss is not None:
            return {
                "cve_id": cve_clean,
                "cve_status": "Confirmed Match",
                "nvd_cvss": float(candidate_cvss),
                "nvd_cvss_display": f"{float(candidate_cvss):.1f} / 10.0",
                "nvd_reference": candidate_reference,
                "provenance_verified": True,
                "reason": "Authoritative CVE and NVD CVSS verified with confirmed product/version match."
            }

        # Rule 7: Fallback when provenance cannot be established
        return {
            "cve_id": None,
            "cve_status": "Not identified",
            "nvd_cvss": None,
            "nvd_cvss_display": "Not available",
            "nvd_reference": None,
            "provenance_verified": False,
            "reason": "Incomplete provenance chain; NVD record unverified."
        }

    def get_provenance_for_finding(self, finding: Any) -> Dict[str, Any]:
        """
        Inspects a finding object or dict and evaluates authoritative CVE/NVD provenance.
        """
        f_id = getattr(finding, "id", None) or (finding.get("id") if isinstance(finding, dict) else "")
        category = getattr(finding, "category", None) or (finding.get("category") if isinstance(finding, dict) else "")
        component = getattr(finding, "affected_component", None) or (finding.get("affected_component") if isinstance(finding, dict) else "")
        
        # Check if finding already has candidate CVE info (e.g. from software scanner)
        cve = getattr(finding, "cve_id", None) or (finding.get("cve_id") if isinstance(finding, dict) else None)
        cve_stat = getattr(finding, "cve_status", None) or (finding.get("cve_status") if isinstance(finding, dict) else None)
        nvd_cvss = getattr(finding, "nvd_cvss", None) or (finding.get("nvd_cvss") if isinstance(finding, dict) else None)
        nvd_ref = getattr(finding, "nvd_reference", None) or (finding.get("nvd_reference") if isinstance(finding, dict) else None)

        return self.evaluate_provenance(
            finding_id=f_id,
            category=category,
            affected_component=component,
            candidate_cve=cve,
            candidate_cvss=nvd_cvss,
            candidate_reference=nvd_ref,
            candidate_version_status=cve_stat,
            verified_match=False
        )

cve_provenance_service = CVEProvenanceService()
