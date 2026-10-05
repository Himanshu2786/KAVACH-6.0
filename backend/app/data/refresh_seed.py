from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord
from backend.app.data.seed_data import seed_database

def refresh():
    db = SessionLocal()
    try:
        # Remove old demo findings and evidence to populate with new 7 security categories
        demo_asm = db.query(Assessment).filter(Assessment.id == "ASM-DEMO-001").first()
        if demo_asm:
            print("Refreshing demo assessment findings and evidence...")
            db.query(EvidenceRecord).filter(EvidenceRecord.finding_id.like("KAV-2026-%")).delete(synchronize_session=False)
            db.query(Finding).filter(Finding.assessment_id == "ASM-DEMO-001").delete(synchronize_session=False)
            db.delete(demo_asm)
            db.commit()
        
        seed_database(db)
        print("Fresh seed applied successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    refresh()
