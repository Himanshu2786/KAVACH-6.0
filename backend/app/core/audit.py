from backend.app.core.time import ist_isoformat
import json
from sqlalchemy.orm import Session
from backend.app.models.models import AuditEvent

def log_audit_event(
    db: Session,
    event_type: str,
    description: str,
    assessment_id: str = None,
    finding_id: str = None,
    module: str = "CORE",
    evidence_id: str = None,
    status: str = "SUCCESS",
    metadata: dict = None
) -> AuditEvent:
    event = AuditEvent(
        assessment_id=assessment_id,
        finding_id=finding_id,
        module=module,
        evidence_id=evidence_id,
        status=status,
        event_type=event_type,
        description=description,
        timestamp=ist_isoformat(),
        metadata_json=json.dumps(metadata or {})
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
