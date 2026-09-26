import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.app.core.database import SessionLocal
from backend.app.services.report_service import ReportService
from backend.app.models.models import Assessment, Finding

def test_cb52_report():
    db = SessionLocal()
    svc = ReportService()
    
    # 1. Test CB52
    assessment_id = "KAVACH-WM-20260922-CB52"
    asm = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    assert asm is not None, f"Assessment {assessment_id} not found"
    
    data = svc.generate_report_data(db, assessment_id)
    html = svc.generate_html_report(db, assessment_id)
    
    exec_sum = data["executive_summary"]
    print("=== KAVACH-WM-20260922-CB52 EXECUTIVE SUMMARY ===")
    print(json.dumps(exec_sum, indent=2))
    
    assert exec_sum["total_findings"] == 1, f"Expected 1 finding, got {exec_sum['total_findings']}"
    assert exec_sum["confirmed_findings"] == 1, f"Expected 1 confirmed finding, got {exec_sum['confirmed_findings']}"
    assert exec_sum["confirmed_evidence"] == 1, f"Expected 1 confirmed evidence, got {exec_sum['confirmed_evidence']}"
    assert exec_sum["total_evidence_collected"] == 1, f"Expected 1 evidence proof, got {exec_sum['total_evidence_collected']}"
    assert exec_sum["retest_evidence_count"] == 17, f"Expected 17 retest evidence records, got {exec_sum['retest_evidence_count']}"
    assert exec_sum["total_retests_executed"] == 17, f"Expected 17 retests executed, got {exec_sum['total_retests_executed']}"
    
    # Check narrative
    summary = exec_sum["summary"]
    print("\n=== EXECUTIVE SUMMARY NARRATIVE ===")
    print(summary)
    assert "baseline security headers" not in summary, "Generic fallback narrative should be removed!"
    assert "publicly accessible interactive API schema and documentation" in summary
    assert "STILL_OPEN" in summary
    
    # Check findings
    findings = data["findings_detail"]
    assert len(findings) == 1
    f = findings[0]
    print("\n=== FINDING DETAIL ===")
    print(f"ID: {f['id']}")
    print(f"Title: {f['title']}")
    print(f"Status: {f['status']}")
    print(f"Baseline Evidence count: {len(f['evidence'])}")
    print(f"Retest Evidence count: {len(f['retest_evidence'])}")
    print(f"Re-Verifications count: {len(f['re_verifications'])}")
    print(f"Quick Fix: {f['remediation']['quick_fix']}")
    
    assert f["status"] == "STILL_OPEN"
    assert len(f["evidence"]) >= 1
    assert any(e["id"] == "EV-WM-API-DOCS-CB52" and e["validation_result"] == "CONFIRMED" for e in f["evidence"])
    assert "OpenAPI/Swagger documentation exposure" in f["remediation"]["quick_fix"]
    assert "strict schema validation on input parameters" not in f["remediation"]["quick_fix"]
    
    # Check HTML Report
    assert "Evidence Confirmed" in html
    assert f">{exec_sum['confirmed_evidence']}<" in html
    assert "Deterministic Re-Test &amp; Verification Lifecycle" in html or "Deterministic Re-Test & Verification Lifecycle" in html
    
    print("\n=== ZERO-FINDING ASSESSMENT TEST ===")
    # 2. Test an assessment with zero findings
    all_asms = db.query(Assessment).all()
    zero_asm = next((a for a in all_asms if db.query(Finding).filter(Finding.assessment_id == a.id).count() == 0), None)
    if zero_asm:
        zero_data = svc.generate_report_data(db, zero_asm.id)
        zero_exec = zero_data["executive_summary"]
        print(f"Testing Zero-Finding Assessment [{zero_asm.id}]:")
        print(json.dumps(zero_exec, indent=2))
        assert zero_exec["total_findings"] == 0
        assert zero_exec["confirmed_findings"] == 0
        assert zero_exec["confirmed_evidence"] == 0
        assert zero_exec["total_evidence_collected"] == 0
        assert len(zero_data["findings_detail"]) == 0
        print(f"Zero-finding assessment {zero_asm.id} verified clean!")
    else:
        print("No zero-finding assessment found in database to test.")
        
    print("\nALL REPORT VERIFICATIONS PASSED!")

if __name__ == "__main__":
    test_cb52_report()
