import json
import traceback
from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord, DiscoveryItem, AuditEvent
from services.storage_service import storage

db = SessionLocal()
asm = storage.get_all_assessments()
asm_2fc1 = next((a for a in asm if a['id'] == 'KAVACH-WM-20260922-2FC1'), None)
findings = storage.get_all_findings('KAVACH-WM-20260922-2FC1')
evidence = storage.get_all_evidence('KAVACH-WM-20260922-2FC1')

print('Testing insertion with exact fields...')
try:
    for ev in evidence:
        ev_id = ev.get("evidence_id") or ev["id"]
        finding_id = ev["finding_id"]
        test_name = ev.get("test_name") or ev.get("type") or "Probe"
        raw_obs = ev.get("raw_observation") or ev.get("observed_output") or ""
        print(f"Checking ev {ev_id}: test_name={test_name!r}")
        
        # Check if ev already in db
        existing = db.query(EvidenceRecord).filter(EvidenceRecord.id == ev_id).first()
        if existing:
            print(f"Already exists in DB: {ev_id}")
            continue

        ev_obj = EvidenceRecord(
            id=ev_id,
            finding_id=finding_id,
            evidence_type=test_name,
            source=ev.get("source", ev.get("provenance", "LIVE_PROBE")),
            timestamp=ev.get("timestamp") or ev.get("created_at") or "",
            description=raw_obs,
            raw_data=json.dumps(ev.get("technical_explanation", ev.get("response", {}))),
            validation_result=ev.get("verification_result", ev.get("result", "CONFIRMED")),
            integrity_hash=ev.get("hash", ev.get("integrity_hash", "")),
            is_demo=False,
            what_found=raw_obs,
            why_matters=f"Category: {ev.get('test_category', 'General Security')}",
            where_found=ev.get("target") or ev.get("f_target") or "",
            verification_command=ev.get("verification_command", ev.get("command", "")),
            expected_output=ev.get("expected_output", ""),
            observed_output=ev.get("observed_output", "")
        )
        db.add(ev_obj)
        db.flush()
        print(f"Flushed {ev_id} successfully")
    db.commit()
    print("ALL COMMITTED!")
except Exception as e:
    print("FAILED with exception:", e)
    traceback.print_exc()
    db.rollback()
