import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import KnowledgeRecord

class KnowledgeService:
    def get_all(self, db: Session) -> List[KnowledgeRecord]:
        return db.query(KnowledgeRecord).all()

    def get_by_id(self, db: Session, knowledge_id: str) -> Optional[KnowledgeRecord]:
        return db.query(KnowledgeRecord).filter(KnowledgeRecord.id == knowledge_id).first()

    def get_knowledge(self, knowledge_id: str, db: Optional[Session] = None) -> Optional[KnowledgeRecord]:
        """Convenience method to retrieve KnowledgeRecord with automatic session handling."""
        if db:
            return self.get_by_id(db, knowledge_id)
        from backend.app.core.database import SessionLocal
        local_db = SessionLocal()
        try:
            return local_db.query(KnowledgeRecord).filter(KnowledgeRecord.id == knowledge_id).first()
        finally:
            local_db.close()

    def correlate(self, db: Optional[Session] = None, category: str = "", title: str = "", cwe_id: str = "") -> Dict[str, Any]:
        """Correlate finding category/title/CWE with canonical CWE and OWASP knowledge."""
        if db is None:
            from backend.app.core.database import SessionLocal
            local_db = SessionLocal()
            try:
                return self.correlate(local_db, category=category, title=title, cwe_id=cwe_id)
            finally:
                local_db.close()

        records = db.query(KnowledgeRecord).all()
        cat_lower = (category or "").lower()
        title_lower = (title or "").lower()
        cwe_upper = (cwe_id or "").strip().upper()

        matched_cwe: Optional[KnowledgeRecord] = None
        matched_owasp: Optional[KnowledgeRecord] = None

        # 1. Direct CWE-ID match if provided
        if cwe_upper:
            matched_cwe = next((r for r in records if r.id.upper() == cwe_upper), None)
            if matched_cwe and matched_cwe.related_owasp:
                matched_owasp = next(
                    (r for r in records if r.type == "OWASP" and (r.id in matched_cwe.related_owasp or r.title in matched_cwe.related_owasp)),
                    None
                )

        # 2. Rule-based correlation if not directly resolved
        if not matched_cwe:
            # Rule: Exposed API Documentation / Schema / Information Exposure (CWE-200)
            if (
                "cwe-200" in title_lower
                or "cwe-200" in cat_lower
                or any(k in title_lower for k in ("openapi", "swagger", "api schema", "api doc", "interactive api"))
                or ("api" in cat_lower and any(k in title_lower for k in ("doc", "schema", "expose", "public", "endpoint")))
                or "information exposure" in cat_lower
                or "information disclosure" in title_lower
                or "sensitive information" in title_lower
            ):
                matched_cwe = next((r for r in records if r.id == "CWE-200"), None)
                matched_owasp = next((r for r in records if "A05" in r.id), None)
            elif "access control" in cat_lower or "idor" in title_lower or "authorization" in cat_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-284" or r.id == "CWE-639"), None)
                matched_owasp = next((r for r in records if "A01" in r.id), None)
            elif "injection" in cat_lower or "sql" in title_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-89"), None)
                matched_owasp = next((r for r in records if "A03" in r.id), None)
            elif "xss" in cat_lower or "cross-site scripting" in title_lower or "script" in cat_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-79"), None)
                matched_owasp = next((r for r in records if "A03" in r.id), None)
            elif "header" in cat_lower or "cors" in cat_lower or "csp" in title_lower or "security header" in cat_lower or "clickjacking" in title_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-16" or r.id == "CWE-1021"), None)
                matched_owasp = next((r for r in records if "A05" in r.id), None)
            elif "authentication" in cat_lower or "jwt" in title_lower or "token" in title_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-306" or r.id == "CWE-287"), None)
                matched_owasp = next((r for r in records if "A07" in r.id), None)
            elif "configuration" in cat_lower or "misconfiguration" in cat_lower:
                matched_cwe = next((r for r in records if r.id == "CWE-16"), None)
                matched_owasp = next((r for r in records if "A05" in r.id), None)

        # 3. Resolve OWASP from matched CWE if OWASP not yet matched
        if matched_cwe and not matched_owasp and matched_cwe.related_owasp:
            matched_owasp = next(
                (r for r in records if r.type == "OWASP" and (r.id in matched_cwe.related_owasp or r.title in matched_cwe.related_owasp)),
                None
            )

        # Note: Do NOT blindly fallback to records[0]. Unmatched findings must return None
        # rather than fabricating an unrelated taxonomy linkage (e.g. IDOR/A01).
        return {
            "cwe": matched_cwe,
            "owasp": matched_owasp
        }

    def resolve_canonical_taxonomy(
        self,
        db: Optional[Session] = None,
        cwe_id: Optional[str] = None,
        owasp_category: Optional[str] = None,
        category: str = "",
        title: str = ""
    ) -> Dict[str, str]:
        """Resolves single authoritative canonical CWE and OWASP taxonomy strings for a finding."""
        if db is None:
            from backend.app.core.database import SessionLocal
            local_db = SessionLocal()
            try:
                return self.resolve_canonical_taxonomy(
                    local_db, cwe_id=cwe_id, owasp_category=owasp_category, category=category, title=title
                )
            finally:
                local_db.close()

        cwe_out = (cwe_id or "").strip()
        owasp_out = (owasp_category or "").strip()

        # If either is missing, query the correlation engine
        if not cwe_out or not owasp_out:
            corr = self.correlate(db, category=category, title=title, cwe_id=cwe_out)
            if not cwe_out and corr.get("cwe"):
                cwe_out = corr["cwe"].id
            if not owasp_out and corr.get("cwe") and corr["cwe"].related_owasp:
                owasp_out = corr["cwe"].related_owasp
            elif not owasp_out and corr.get("owasp"):
                owasp_out = f"{corr['owasp'].id}:2021 - {corr['owasp'].title}" if "OWASP-" not in corr["owasp"].title else corr["owasp"].title

        # Special canonical normalization for CWE-200 in KAVACH
        if cwe_out.upper() == "CWE-200":
            cwe_out = "CWE-200"
            if not owasp_out or "A01" in owasp_out:
                # Disallow erroneous A01 fallback for CWE-200
                owasp_out = "OWASP-A05:2021 - Security Misconfiguration"

        return {
            "cwe_id": cwe_out,
            "owasp_category": owasp_out
        }

knowledge_service = KnowledgeService()
