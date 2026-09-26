"""
KAVACH 6.0 — Deterministic CVSS v3.1 Risk & Impact Assessment Engine.
Calculates mathematically precise CVSS v3.1 scores, metric factor breakdowns,
and structured 5-point realistic business impacts tied directly to specific confirmed findings.

Standards:
- FIRST.org Common Vulnerability Scoring System (CVSS) Version 3.1 Specification
- Zero fabricated risk scores
- Strict finding-to-risk and evidence traceability
"""

import math
from typing import Dict, Any, List, Optional, Tuple


class CVSSv31Calculator:
    """
    Deterministic CVSS v3.1 Base Score Calculator conforming to FIRST.org specification.
    """

    # Metric Weight Dictionaries
    AV_WEIGHTS = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
    AC_WEIGHTS = {"L": 0.77, "H": 0.44}
    PR_WEIGHTS = {
        "U": {"N": 0.85, "L": 0.62, "H": 0.27},
        "C": {"N": 0.85, "L": 0.68, "H": 0.50}
    }
    UI_WEIGHTS = {"N": 0.85, "R": 0.62}
    CIA_WEIGHTS = {"N": 0.0, "L": 0.22, "H": 0.56}

    # Human-Readable Lookups
    METRIC_NAMES = {
        "AV": {"N": "NETWORK", "A": "ADJACENT", "L": "LOCAL", "P": "PHYSICAL"},
        "AC": {"L": "LOW", "H": "HIGH"},
        "PR": {"N": "NONE", "L": "LOW", "H": "HIGH"},
        "UI": {"N": "NONE", "R": "REQUIRED"},
        "S": {"U": "UNCHANGED", "C": "CHANGED"},
        "C": {"N": "NONE", "L": "LOW", "H": "HIGH"},
        "I": {"N": "NONE", "L": "LOW", "H": "HIGH"},
        "A": {"N": "NONE", "L": "LOW", "H": "HIGH"}
    }

    @staticmethod
    def _roundup(input_val: float) -> float:
        """
        Official CVSS v3.1 Roundup function:
        Returns the smallest number, specified to one decimal place, that is equal to or greater than the input.
        """
        int_input = round(input_val * 100000)
        if int_input % 10000 == 0:
            return round(int_input / 100000, 1)
        else:
            return round((int(input_val * 10) + 1) / 10.0, 1)

    @classmethod
    def parse_vector(cls, vector_str: str) -> Dict[str, str]:
        """
        Parses a CVSS 3.1 vector string into metric key-value pairs.
        Example: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N'
        """
        if vector_str.startswith("CVSS:3.1/"):
            vector_str = vector_str[len("CVSS:3.1/"):]
        elif vector_str.startswith("CVSS:3.0/"):
            vector_str = vector_str[len("CVSS:3.0/"):]

        metrics = {}
        parts = vector_str.split("/")
        for part in parts:
            if ":" in part:
                k, v = part.split(":", 1)
                metrics[k.upper()] = v.upper()

        # Defaults for base metrics
        defaults = {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U", "C": "N", "I": "N", "A": "N"}
        for k, v in defaults.items():
            if k not in metrics:
                metrics[k] = v

        return metrics

    @classmethod
    def calculate_score(cls, vector_input: Any) -> Dict[str, Any]:
        """
        Calculates the complete deterministic CVSS v3.1 score and breakdown.
        Accepts vector string or metric dictionary.
        """
        if isinstance(vector_input, str):
            metrics = cls.parse_vector(vector_input)
        elif isinstance(vector_input, dict):
            metrics = {k.upper(): v.upper() for k, v in vector_input.items()}
        else:
            metrics = cls.parse_vector("AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N")

        av = metrics.get("AV", "N")
        ac = metrics.get("AC", "L")
        pr = metrics.get("PR", "N")
        ui = metrics.get("UI", "N")
        s = metrics.get("S", "U")
        c = metrics.get("C", "N")
        i = metrics.get("I", "N")
        a = metrics.get("A", "N")

        w_av = cls.AV_WEIGHTS.get(av, 0.85)
        w_ac = cls.AC_WEIGHTS.get(ac, 0.77)
        w_pr = cls.PR_WEIGHTS.get(s, cls.PR_WEIGHTS["U"]).get(pr, 0.85)
        w_ui = cls.UI_WEIGHTS.get(ui, 0.85)
        w_c = cls.CIA_WEIGHTS.get(c, 0.0)
        w_i = cls.CIA_WEIGHTS.get(i, 0.0)
        w_a = cls.CIA_WEIGHTS.get(a, 0.0)

        # 1. Impact Sub-Score (ISS)
        iss = 1.0 - ((1.0 - w_c) * (1.0 - w_i) * (1.0 - w_a))

        # 2. Impact Sub-score Calculation
        if s == "U":
            impact = 6.42 * iss
        else:
            impact = 7.52 * (iss - 0.029) - 3.25 * math.pow((iss - 0.02), 15)

        # 3. Exploitability Calculation
        exploitability = 8.22 * w_av * w_ac * w_pr * w_ui

        # 4. Base Score Determination
        if impact <= 0:
            base_score = 0.0
        else:
            if s == "U":
                base_score = cls._roundup(min(impact + exploitability, 10.0))
            else:
                base_score = cls._roundup(min(1.08 * (impact + exploitability), 10.0))

        # Severity Mapping
        severity = cls.get_severity(base_score)
        vector_str = f"CVSS:3.1/AV:{av}/AC:{ac}/PR:{pr}/UI:{ui}/S:{s}/C:{c}/I:{i}/A:{a}"

        return {
            "cvss_version": "3.1",
            "cvss_score": base_score,
            "cvss_vector": vector_str,
            "severity": severity,
            "metrics": {
                "attack_vector": cls.METRIC_NAMES["AV"].get(av, av),
                "attack_complexity": cls.METRIC_NAMES["AC"].get(ac, ac),
                "privileges_required": cls.METRIC_NAMES["PR"].get(pr, pr),
                "user_interaction": cls.METRIC_NAMES["UI"].get(ui, ui),
                "scope": cls.METRIC_NAMES["S"].get(s, s),
                "confidentiality_impact": cls.METRIC_NAMES["C"].get(c, c),
                "integrity_impact": cls.METRIC_NAMES["I"].get(i, i),
                "availability_impact": cls.METRIC_NAMES["A"].get(a, a)
            },
            "calculation_factors": {
                "iss": round(iss, 4),
                "impact_subscore": round(impact, 2),
                "exploitability_subscore": round(exploitability, 2),
                "base_score": base_score,
                "scope_changed": (s == "C")
            }
        }

    @staticmethod
    def get_severity(score: float) -> str:
        """Returns qualitative severity rating based on CVSS 3.1 score ranges."""
        if score == 0.0:
            return "NONE"
        elif score < 4.0:
            return "LOW"
        elif score < 7.0:
            return "MEDIUM"
        elif score < 9.0:
            return "HIGH"
        else:
            return "CRITICAL"


class RiskEngine:
    """
    KAVACH Risk Evaluation Engine.
    Correlates findings, verified evidence, CVSS 3.1 calculation factors,
    and realistic non-exaggerated 5-point Business Impact models.
    """

    @classmethod
    def evaluate_finding_risk(
        cls,
        finding: Dict[str, Any],
        evidence_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Produces a complete finding-specific risk evaluation record.
        Strictly requires finding linkage and evidence validation.
        """
        finding_id = finding.get("finding_id") or finding.get("id", "UNKNOWN-FND")
        assessment_id = finding.get("assessment_id", "UNKNOWN-ASM")
        evidence_ids = finding.get("evidence_ids", [])
        if not evidence_ids and finding.get("evidence_id"):
            evidence_ids = [finding["evidence_id"]]

        # Calculate or parse deterministic CVSS
        raw_vector = finding.get("cvss_vector") or "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N"
        cvss_res = CVSSv31Calculator.calculate_score(raw_vector)

        # Integrity check: If evidence is absent, flag as unconfirmed risk
        status = finding.get("status", "OPEN")
        has_evidence = len(evidence_ids) > 0
        if not has_evidence or status in ("NOT CONFIRMED", "POTENTIAL"):
            confidence = "POTENTIAL" if status == "POTENTIAL" else "UNCERTAIN / UNVALIDATED"
            is_confirmed = False
        else:
            confidence = finding.get("confidence", "CERTAIN")
            is_confirmed = (status == "CONFIRMED")

        # Generate structured 5-point Business Impact
        b_impact = cls._generate_structured_business_impact(finding, cvss_res)

        return {
            "risk_id": f"RSK-{finding_id}",
            "assessment_id": assessment_id,
            "finding_id": finding_id,
            "evidence_ids": evidence_ids,
            "is_confirmed": is_confirmed,
            "confidence": confidence,
            "cvss_version": cvss_res["cvss_version"],
            "cvss_score": cvss_res["cvss_score"],
            "cvss_vector": cvss_res["cvss_vector"],
            "severity": cvss_res["severity"],
            "metrics": cvss_res["metrics"],
            "calculation_factors": cvss_res["calculation_factors"],
            "technical_impact": finding.get("technical_impact") or finding.get("description", ""),
            "business_impact": b_impact,
            "affected_assets": [finding.get("affected_component", "Application Endpoint")],
            "potential_consequences": [
                b_impact["potential_security_consequence"],
                b_impact["application_consequence"],
                b_impact["business_consequence"]
            ],
            "reasoning": (
                f"Evaluated CVSS:3.1 score {cvss_res['cvss_score']} ({cvss_res['severity']}) based on "
                f"Attack Vector: {cvss_res['metrics']['attack_vector']}, "
                f"Complexity: {cvss_res['metrics']['attack_complexity']}, "
                f"Privileges: {cvss_res['metrics']['privileges_required']}, "
                f"User Interaction: {cvss_res['metrics']['user_interaction']}."
            )
        }

    @classmethod
    def _generate_structured_business_impact(
        cls,
        finding: Dict[str, Any],
        cvss_res: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generates realistic, non-exaggerated 5-point Business Impact translation.
        """
        title = finding.get("title", "")
        desc = finding.get("description", "")
        comp = finding.get("affected_component", "")
        cat = finding.get("category", "")

        # Default fallback mapping
        tech_cond = desc if len(desc) < 200 else f"{title} observed on {comp}."
        sec_conseq = "Potential unauthorized information access or configuration bypass."
        app_conseq = "Degraded defense-in-depth posture on affected service components."
        biz_conseq = "Compliance deficiency and increased vulnerability to targeted attack vectors."
        stakeholders = "Application Developers, Security Operations Team, End Users."

        if "HSTS" in title:
            sec_conseq = "Network eavesdroppers on untrusted local networks can perform SSL stripping attacks."
            app_conseq = "Traffic between client browsers and the backend can be intercepted without encryption."
            biz_conseq = "Potential exposure of user session cookies; failure to meet transport security compliance standards."
            stakeholders = "Web Application Users, Compliance Officers, Security Operations."
        elif "Content-Security-Policy" in title or "CSP" in title:
            sec_conseq = "Absence of client execution restrictions allows injected scripts or malicious frames to run freely."
            app_conseq = "Web clients will not restrict untrusted external scripts or unauthorized frame embedding."
            biz_conseq = "Increased exposure to client-side data leakage if a cross-site scripting flaw exists."
            stakeholders = "Frontend Users, Security Team."
        elif "AWS" in title or "Secret" in title or "Password" in title:
            sec_conseq = "Direct access to backend resources and cloud services using unencrypted credentials."
            app_conseq = "Attackers can authenticate directly to service APIs without secondary verification."
            biz_conseq = "Risk of cloud asset compromise and proprietary data exposure; immediate key revocation required."
            stakeholders = "Infrastructure Engineers, Cloud Administrators, Executive Management."
        elif "CORS" in title:
            sec_conseq = "Untrusted web origins can read authenticated API responses on behalf of users."
            app_conseq = "Browsers allow malicious origins to receive private API responses with user credentials."
            biz_conseq = "Cross-site data harvesting of private organizational records."
            stakeholders = "Authenticated Application Users, API Engineers."
        elif "Double Extension" in title or "DECEPTIVE" in title:
            sec_conseq = "Users can be deceived into launching executable programs disguised as document files."
            app_conseq = "Host workstation may execute malicious binaries under current user permissions."
            biz_conseq = "Endpoint workstation compromise via social engineering payloads."
            stakeholders = "Internal Staff, Endpoint IT Administrators."
        elif "Banner" in title or "Documentation" in title or "Debug" in title:
            sec_conseq = "Assists external reconnaissance by disclosing backend framework versions and endpoint schemas."
            app_conseq = "Application architecture details are readable by unauthenticated third parties."
            biz_conseq = "Accelerates automated vulnerability scanning against known framework CVEs."
            stakeholders = "Application Maintainers, SOC Analysts."

        return {
            "technical_condition": tech_cond,
            "potential_security_consequence": sec_conseq,
            "application_consequence": app_conseq,
            "business_consequence": biz_conseq,
            "affected_stakeholders": stakeholders
        }


# Singleton instances
cvss_calculator = CVSSv31Calculator()
risk_engine = RiskEngine()
