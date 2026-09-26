import hashlib
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import EvidenceRecord, Finding
from backend.app.core.audit import log_audit_event
from backend.app.core.time import ist_isoformat

class EvidenceService:
    @staticmethod
    def calculate_integrity_hash(raw_data: str, timestamp: str, evidence_type: str) -> str:
        """Calculates cryptographic SHA-256 integrity hash for evidence record."""
        payload = f"{evidence_type}|{timestamp}|{raw_data}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def create_evidence(
        self,
        db: Session,
        finding_id: str,
        evidence_type: str,
        description: str,
        raw_data: str,
        validation_result: str,
        source: str = "Local Probe",
        is_demo: bool = False,
        what_found: str = "",
        why_matters: str = "",
        where_found: str = "",
        confidence_level: str = "HIGH",
        verification_command: str = "",
        expected_output: str = "",
        observed_output: str = "",
        evidence_nature: str = "REAL EVIDENCE"
    ) -> EvidenceRecord:
        timestamp = ist_isoformat()
        evidence_id = f"EVD-{uuid.uuid4().hex[:8].upper()}"
        integrity_hash = self.calculate_integrity_hash(raw_data, timestamp, evidence_type)

        record = EvidenceRecord(
            id=evidence_id,
            finding_id=finding_id,
            evidence_type=evidence_type,
            source=source,
            timestamp=timestamp,
            description=description,
            raw_data=raw_data,
            validation_result=validation_result,
            integrity_hash=integrity_hash,
            is_demo=is_demo,
            what_found=what_found,
            why_matters=why_matters,
            where_found=where_found,
            confidence_level=confidence_level,
            verification_command=verification_command,
            expected_output=expected_output,
            observed_output=observed_output,
            evidence_nature=evidence_nature
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if finding:
            finding.evidence_status = "AVAILABLE"
            db.commit()

            log_audit_event(
                db=db,
                event_type="EVIDENCE_RECORDED",
                description=f"Evidence {evidence_id} ({evidence_type}) attached to finding {finding_id} with result: {validation_result}",
                assessment_id=finding.assessment_id,
                finding_id=finding.id,
                metadata={"evidence_id": evidence_id, "integrity_hash": integrity_hash, "validation_result": validation_result}
            )

        return record

    def get_by_finding(self, db: Session, finding_id: str) -> List[EvidenceRecord]:
        return db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id).all()

    def get_all(self, db: Session) -> List[EvidenceRecord]:
        return db.query(EvidenceRecord).all()

evidence_service = EvidenceService()
