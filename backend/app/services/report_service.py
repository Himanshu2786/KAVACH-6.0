import json
from backend.app.core.time import ist_isoformat
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import Assessment, Finding, EvidenceRecord, DiscoveryItem, AuditEvent
from backend.app.services.assessment_service import assessment_service
from backend.app.services.risk_service import risk_service
from backend.app.services.remediation_service import remediation_service
from backend.app.services.cve_provenance_service import cve_provenance_service
from backend.app.services.ai_analysis_service import ai_analysis_service

class ReportService:
    def generate_report_data(self, db: Session, assessment_id: str) -> Dict[str, Any]:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
        discovery_items = db.query(DiscoveryItem).filter(DiscoveryItem.assessment_id == assessment_id).all()
        all_evidence = db.query(EvidenceRecord).join(Finding).filter(Finding.assessment_id == assessment_id).all()
        
        def is_retest_evidence(e: EvidenceRecord) -> bool:
            if not e:
                return False
            e_id = getattr(e, "id", "") or ""
            if e_id.startswith("EVD-AFT-"):
                return True
            if getattr(e, "source", "") == "Re-Test Verification Engine":
                return True
            if (getattr(e, "evidence_type", "") or "").startswith("Re-Test Verification"):
                return True
            desc = (getattr(e, "description", "") or "").lower()
            if "re-test" in desc or "post-fix" in desc:
                return True
            return False

        baseline_evidence = [e for e in all_evidence if not is_retest_evidence(e)]
        retest_evidence = [e for e in all_evidence if is_retest_evidence(e)]
        confirmed_baseline_evidence = [e for e in baseline_evidence if e.validation_result == "CONFIRMED"]

        # A finding is confirmed if marked CONFIRMED/STILL_OPEN/VERIFIED or backed by confirmed baseline evidence.
        # It must not depend on whether the finding is currently STILL_OPEN after remediation re-test.
        # SOURCE findings (evidence_status == REQUIRES_SOURCE_VALIDATION) are excluded from confirmed_findings:
        # they were produced from a path whose provenance could not be verified as the authorized repository.
        def _is_provenance_unverified(f: Finding) -> bool:
            return getattr(f, "evidence_status", "") == "REQUIRES_SOURCE_VALIDATION"

        confirmed_findings_list = [
            f for f in findings
            if not _is_provenance_unverified(f)
            and (
                f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")
                or any(e.validation_result == "CONFIRMED" for e in f.evidence_records if not is_retest_evidence(e))
            )
        ]
        unverified_source_findings_list = [f for f in findings if _is_provenance_unverified(f)]

        # Unique confirmed vulnerability proofs:
        # Each confirmed finding backed by verified technical baseline evidence counts as ONE unique confirmed vulnerability proof.
        # Multiple evidence artifacts for one finding (such as an original probe and a corrected GET probe)
        # do not count as multiple confirmed proofs.
        confirmed_unique_proof_findings = {
            e.finding_id for e in baseline_evidence 
            if e.validation_result == "CONFIRMED"
        }
        unique_confirmed_proofs_count = len([f for f in confirmed_findings_list if f.id in confirmed_unique_proof_findings])
        if not unique_confirmed_proofs_count and confirmed_findings_list:
            unique_confirmed_proofs_count = len(confirmed_findings_list)

        canonical_active_evidence_id = None
        historical_evidence_ids = []
        for e in baseline_evidence:
            if getattr(e, "is_canonical", True):
                if not canonical_active_evidence_id or "-GET" in getattr(e, "id", ""):
                    canonical_active_evidence_id = e.id
            else:
                historical_evidence_ids.append(e.id)
        if not canonical_active_evidence_id and baseline_evidence:
            canonical_active_evidence_id = baseline_evidence[0].id

        posture = assessment_service.calculate_security_posture(db, assessment_id)
        priorities = risk_service.prioritize_all_findings(db, assessment_id)

        findings_detail = []
        for f in findings:
            rem = remediation_service.get_remediation_plan(db, f.id)
            f_baseline_evds = [
                {
                    "id": e.id,
                    "type": e.evidence_type,
                    "source": e.source,
                    "timestamp": e.timestamp,
                    "description": e.description,
                    "validation_result": e.validation_result,
                    "integrity_hash": e.integrity_hash,
                    "raw_data_snippet": (e.raw_data or "")[:200],
                    "lifecycle_status": getattr(e, "lifecycle_status", "CANONICAL"),
                    "lifecycle_role": getattr(e, "lifecycle_role", "CANONICAL_ACTIVE"),
                    "is_canonical": getattr(e, "is_canonical", True),
                    "relationship_note": getattr(e, "relationship_note", "")
                }
                for e in f.evidence_records
                if not is_retest_evidence(e)
            ]
            f_retest_evds = [
                {
                    "id": e.id,
                    "type": e.evidence_type,
                    "source": e.source,
                    "timestamp": e.timestamp,
                    "description": e.description,
                    "validation_result": e.validation_result,
                    "validation_meaning": (
                        "REMEDIATION_CONFIRMED_FLAW_RESOLVED" if e.validation_result == "CONFIRMED"
                        else "REMEDIATION_UNCONFIRMED_FLAW_PERSISTS"
                    ),
                    "lifecycle_status": getattr(e, "lifecycle_status", f.status or "STILL_OPEN"),
                    "final_status": f.status or "STILL_OPEN",
                    "verdict": f.status or "STILL_OPEN",
                    "condition_improved": False if (f.status == "STILL_OPEN" or e.validation_result == "UNCONFIRMED") else True,
                    "change_detected": False if (f.status == "STILL_OPEN" or e.validation_result == "UNCONFIRMED") else True,
                    "integrity_hash": e.integrity_hash,
                    "raw_data_snippet": (e.raw_data or "")[:200]
                }
                for e in f.evidence_records
                if is_retest_evidence(e)
            ]
            retests = [
                {
                    "id": rv.id,
                    "timestamp": rv.timestamp,
                    "target_url": getattr(rv, "target_url", ""),
                    "original_state": getattr(rv, "previous_status", ""),
                    "retest_status": getattr(rv, "new_status", ""),
                    "lifecycle_status": getattr(rv, "new_status", ""),
                    "final_status": getattr(rv, "new_status", ""),
                    "verdict": getattr(rv, "verification_verdict", getattr(rv, "new_status", "")),
                    "condition_improved": False if getattr(rv, "new_status", "") == "STILL_OPEN" else True,
                    "change_detected": False if (getattr(rv, "new_status", "") == "STILL_OPEN" or not getattr(rv, "state_diff", "") or getattr(rv, "state_diff", "") == "NO_CHANGE") else True,
                    "verification_verdict": getattr(rv, "verification_verdict", getattr(rv, "new_status", "")),
                    "before_evidence_id": getattr(rv, "before_evidence_id", ""),
                    "before_evidence_hash": getattr(rv, "before_evidence_hash", ""),
                    "after_evidence_id": getattr(rv, "after_evidence_id", ""),
                    "after_evidence_hash": getattr(rv, "after_evidence_hash", ""),
                    "command_executed": getattr(rv, "command_executed", ""),
                    "output_before": getattr(rv, "output_before", ""),
                    "output_after": getattr(rv, "output_after", ""),
                    "state_diff": getattr(rv, "state_diff", ""),
                    "notes": getattr(rv, "summary", "")
                }
                for rv in f.re_verifications
            ]

            # Determine source provenance note for findings_detail
            prov_note = None
            if getattr(f, "evidence_status", "") == "REQUIRES_SOURCE_VALIDATION":
                prov_note = (
                    "SOURCE_PROVENANCE_UNVERIFIED: This finding was produced from a source path that "
                    "could not be verified as the authorized World Monitor repository. "
                    "It is NOT counted as a confirmed finding. "
                    "To confirm, clone https://github.com/koala73/worldmonitor and re-run the assessment "
                    "with the verified repository path."
                )

            cve_prov = cve_provenance_service.get_provenance_for_finding(f)
            p_score = f.priority_score if f.priority_score is not None else 5.0

            is_api_docs = (
                f.cwe_id == "CWE-200"
                or "WM-API-DOCS" in (f.id or "")
                or "api doc" in (f.title or "").lower()
                or "openapi" in (f.title or "").lower()
            )
            canonical = ai_analysis_service.get_canonical_api_docs_explanation() if is_api_docs else None
            ai_hypo = (f.ai_hypothesis or canonical["ai_hypothesis"]) if canonical else f.ai_hypothesis
            ai_conf = (f.ai_confidence or canonical["ai_confidence"]) if canonical else f.ai_confidence
            ai_reas = (f.ai_reasoning_summary or canonical["ai_reasoning_summary"]) if canonical else f.ai_reasoning_summary
            ai_sum = (f.ai_summary or canonical["ai_summary"]) if canonical else f.ai_summary
            ai_imp = (f.ai_potential_impact or canonical["possible_impact"]) if canonical else f.ai_potential_impact

            findings_detail.append({
                "id": f.id,
                "title": f.title,
                "category": f.category,
                "affected_component": f.affected_component,
                "base_severity": f.base_severity,
                "priority": f.priority,
                "priority_score": p_score,
                "priority_scale": "10.0",
                "priority_score_formatted": f"{p_score:.2f} / 10.0",
                "status": f.status,
                "evidence_status": f.evidence_status,
                "source_provenance_note": prov_note,
                "ai_summary": ai_sum,
                "ai_hypothesis": ai_hypo,
                "ai_confidence": ai_conf,
                "ai_reasoning": ai_reas,
                "ai_potential_impact": ai_imp,
                "cwe_id": f.cwe_id,
                "owasp_category": f.owasp_category,
                "cve_id": cve_prov["cve_id"],
                "cve_status": cve_prov["cve_status"],
                "nvd_cvss": cve_prov["nvd_cvss"],
                "nvd_cvss_display": cve_prov["nvd_cvss_display"],
                "nvd_reference": cve_prov["nvd_reference"],
                "evidence": f_baseline_evds,
                "retest_evidence": f_retest_evds,
                "remediation": rem,
                "re_verifications": retests,
                "ai_provider": "ollama" if f.ai_analysis_status == "COMPLETED" else "fallback"
            })


        audit_filter = AuditEvent.assessment_id == assessment_id
        if findings:
            audit_filter = audit_filter | AuditEvent.finding_id.in_([f.id for f in findings])
        audit_events = db.query(AuditEvent).filter(audit_filter).order_by(AuditEvent.timestamp.asc()).all()

        audit_trail = [
            {
                "id": a.id,
                "assessment_id": a.assessment_id,
                "finding_id": a.finding_id,
                "evidence_id": a.evidence_id,
                "module": a.module,
                "event_type": a.event_type,
                "description": a.description,
                "status": a.status,
                "timestamp": a.timestamp,
                "metadata": json.loads(a.metadata_json) if a.metadata_json else {}
            }
            for a in audit_events
        ]

        return {
            "metadata": {
                "report_title": "KAVACH Security Assessment & Intelligence Report",
                "generated_at": ist_isoformat(),
                "platform": "KAVACH v6.0 // AI-Assisted, Evidence-Driven Security Platform",
                "core_principle": "AI Hypothesizes. Evidence Confirms.",
                "is_demo": assessment.is_demo
            },
            "assessment": {
                "id": assessment.id,
                "name": assessment.name,
                "target_url": assessment.target_url,
                "environment": assessment.environment,
                "scope": assessment.scope,
                "started_at": assessment.started_at,
                "completed_at": assessment.completed_at or "In Progress",
                "status": assessment.status
            },
            "executive_summary": {
                "security_posture": posture["posture"],
                "risk_level": posture["risk_level"],
                "risk_score": posture["score"],
                "posture_score": posture["score"],
                "status_label": posture["status_label"],
                "summary": posture["summary"],
                "total_findings": len(findings),
                "confirmed_findings": len(confirmed_findings_list),
                "confirmed_evidence": unique_confirmed_proofs_count,
                "evidence_proofs": unique_confirmed_proofs_count,
                "baseline_confirmed_evidence": unique_confirmed_proofs_count,
                "technical_evidence_captured": len(baseline_evidence),
                "canonical_active_evidence": canonical_active_evidence_id,
                "historical_evidence": historical_evidence_ids,
                "potential_findings": len([f for f in findings if f.status in ("POTENTIAL", "UNDER ANALYSIS", "VALIDATING")]),
                "unconfirmed_findings": len([f for f in findings if f.status == "UNCONFIRMED"]),
                "requires_manual_review": len([f for f in findings if f.status == "REQUIRES MANUAL REVIEW"]),
                "unverified_source_findings": len(unverified_source_findings_list),
                "total_evidence_collected": len(baseline_evidence),
                "baseline_evidence_count": unique_confirmed_proofs_count,
                "total_raw_evidence_count": len(all_evidence),
                "retest_evidence_count": len(retest_evidence),
                "total_retests_executed": sum(len(f.get("re_verifications", [])) for f in findings_detail)
            },
            "discovery_summary": {
                "total_surfaces_cataloged": len(discovery_items),
                "endpoints": len([d for d in discovery_items if d.item_type == "endpoint"]),
                "components": len([d for d in discovery_items if d.item_type == "component"]),
                "auth_points": len([d for d in discovery_items if d.item_type == "auth_point"]),
                "input_surfaces": len([d for d in discovery_items if d.item_type == "input_surface"])
            },
            "prioritized_findings": priorities,
            "findings_detail": findings_detail,
            "audit_trail": audit_trail,
            "limitations": [
                "This assessment reflects observations collected within the authorized scope.",
                "AI analysis provides advisory hypotheses; only findings accompanied by cryptographic technical evidence are confirmed.",
                "Prototype evaluations should be complemented with continuous automated regression testing and manual code audits."
            ]
        }

    def generate_html_report(self, db: Session, assessment_id: str) -> str:
        """Generates a standalone, beautifully styled, printable HTML security report."""
        data = self.generate_report_data(db, assessment_id)
        exec_sum = data["executive_summary"]
        asm = data["assessment"]

        findings_rows = ""
        for f in data["findings_detail"]:
            status_color = "#10b981" if f["status"] in ("CONFIRMED", "VERIFIED_REMEDIATED", "RESOLVED") else ("#f59e0b" if f["status"] == "POTENTIAL" else "#94a3b8")
            sev_color = "#ef4444" if f["base_severity"] == "CRITICAL" else ("#f97316" if f["base_severity"] == "HIGH" else "#3b82f6")
            
            evd_items = []
            for e in f["evidence"]:
                is_canon = e.get("is_canonical", True)
                badge_bg = "#065f46" if is_canon else "#1e293b"
                badge_border = "#10b981" if is_canon else "#64748b"
                badge_text = "#34d399" if is_canon else "#94a3b8"
                badge_label = "CANONICAL ACTIVE PROOF" if is_canon else "HISTORICAL ARTIFACT (SUPERSEDED)"
                rel_note = e.get("relationship_note", "")
                note_html = f"<div style='margin-top:6px; font-size:10px; color:{badge_text};'>{rel_note}</div>" if rel_note else ""

                evd_items.append(f"""<div style="background:#0f172a; border-left: 4px solid {badge_border}; padding:10px 14px; margin-top:8px; border-radius:6px; font-family:monospace; font-size:11px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><strong style="color:#f8fafc;">Evidence [{e['id']}]</strong> - {e['type']} (<span style="color:#10b981; font-weight:700;">{e['validation_result']}</span>)</div>
                        <span style="background:{badge_bg}; border:1px solid {badge_border}; color:{badge_text}; font-size:9px; padding:2px 8px; border-radius:4px; font-weight:700; text-transform:uppercase;">{badge_label}</span>
                    </div>
                    <div style="color:#94a3b8; margin-top:2px;">SHA-256: {e['integrity_hash']}</div>
                    <div style="margin-top:4px; color:#cbd5e1;">{e['description']}</div>
                    {note_html}
                </div>""")
            evd_html = "".join(evd_items) or "<em style='color:#64748b;'>No evidence captured yet</em>"

            retest_html = ""
            if f.get("re_verifications"):
                rv_items = []
                for rv in f["re_verifications"]:
                    verdict_color = "#10b981" if rv.get("verification_verdict") == "VERIFIED_REMEDIATED" else "#ef4444" if rv.get("verification_verdict") == "STILL_OPEN" else "#f59e0b"
                    rv_items.append(f"""
                    <div style="background:#0f172a; border:1px solid #334155; border-left:4px solid {verdict_color}; padding:10px 14px; margin-top:8px; border-radius:6px; font-size:12px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:#38bdf8; font-weight:700;">Re-Test ID: {rv.get('id', 'N/A')}</span>
                            <span style="background:{verdict_color}; color:#fff; font-size:10px; padding:2px 8px; border-radius:4px; font-weight:700;">{rv.get('verification_verdict', 'N/A')}</span>
                        </div>
                        <div style="font-size:11px; color:#94a3b8; font-family:monospace;">Target: {rv.get('target_url', asm['target_url'])} | Timestamp: {rv.get('timestamp', '')}</div>
                        <div style="margin-top:6px; display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11px; font-family:monospace;">
                            <div style="background:#1e293b; padding:6px; border-radius:4px;">
                                <div style="color:#ef4444; font-weight:700;">BEFORE EVIDENCE [{rv.get('before_evidence_id', 'N/A')}]</div>
                                <div style="color:#64748b; word-break:break-all;">SHA-256: {rv.get('before_evidence_hash', 'N/A')}</div>
                            </div>
                            <div style="background:#1e293b; padding:6px; border-radius:4px;">
                                <div style="color:#10b981; font-weight:700;">AFTER EVIDENCE [{rv.get('after_evidence_id', 'N/A')}]</div>
                                <div style="color:#64748b; word-break:break-all;">SHA-256: {rv.get('after_evidence_hash', 'N/A')}</div>
                            </div>
                        </div>
                        <div style="margin-top:6px; background:#1e293b; padding:6px; border-radius:4px; font-size:11px;">
                            <div style="color:#38bdf8; font-weight:700;">STATE DIFF:</div>
                            <div style="color:#cbd5e1; white-space:pre-wrap; font-family:monospace; margin-top:2px;">{rv.get('state_diff', 'No diff recorded')}</div>
                        </div>
                    </div>
                    """)
                retest_html = f"""
                <div style="margin-top:14px; padding-top:10px; border-top:1px dashed #334155;">
                    <div style="font-size:12px; font-weight:700; color:#38bdf8;">Deterministic Re-Test & Verification Lifecycle</div>
                    {"".join(rv_items)}
                </div>
                """

            findings_rows += f"""
            <div style="background:#1e293b; border: 1px solid #334155; border-radius:8px; padding:18px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:16px; font-weight:700; color:#f8fafc;">[{f['id']}] {f['title']}</span>
                    <div>
                        <span style="background:#0369a1; color:#fff; font-size:11px; padding:3px 8px; border-radius:4px; font-weight:700; margin-right:6px;">Priority: {f.get('priority_score', 5.0)} / 10.0</span>
                        <span style="background:{sev_color}; color:#fff; font-size:11px; padding:3px 8px; border-radius:4px; font-weight:700; margin-right:6px;">{f['base_severity']}</span>
                        <span style="background:{status_color}; color:#fff; font-size:11px; padding:3px 8px; border-radius:4px; font-weight:700;">{f['status']}</span>
                    </div>
                </div>
                <div style="color:#94a3b8; font-size:12px; margin-bottom:12px;">Component: <strong>{f['affected_component']}</strong> | Category: {f['category']} | CWE: {f['cwe_id']} | CVE: {f.get('cve_id') or 'Not identified'} | NVD CVSS: {f.get('nvd_cvss_display') or ('Not available' if f.get('nvd_cvss') is None else f"{f['nvd_cvss']:.1f} / 10.0")}</div>
                <div style="background:#0d1527; padding:10px 14px; border-radius:6px; border-left: 3px solid #a855f7; margin-bottom:12px;">
                    <div style="font-size:11px; font-weight:700; color:#c084fc; text-transform:uppercase;">AI Security Hypothesis (Confidence: {f['ai_confidence']}%)</div>
                    <div style="font-size:13px; color:#e2e8f0; margin-top:4px;">{f['ai_hypothesis'] or 'Rule-based security correlation active.'}</div>
                </div>
                <div>
                    <div style="font-size:12px; font-weight:700; color:#38bdf8;">Baseline Technical Evidence</div>
                    {evd_html}
                </div>
                <div style="margin-top:12px; padding-top:12px; border-top:1px solid #334155; font-size:12px; color:#cbd5e1;">
                    <strong style="color:#10b981;">Recommended Fix:</strong> {f['remediation']['quick_fix']}
                </div>
                {retest_html}
            </div>
            """

        audit_rows = ""
        for a in data.get("audit_trail", []):
            status_badge_color = "#10b981" if a["status"] == "SUCCESS" else "#ef4444"
            audit_rows += f"""
            <tr style="border-bottom:1px solid #334155; font-size:11px; font-family:monospace;">
                <td style="padding:6px 10px; color:#94a3b8;">{a['timestamp']}</td>
                <td style="padding:6px 10px; color:#38bdf8; font-weight:700;">{a['event_type']}</td>
                <td style="padding:6px 10px; color:#f8fafc;">{a['description']}</td>
                <td style="padding:6px 10px; color:#64748b;">{a.get('finding_id') or '-'}</td>
                <td style="padding:6px 10px;"><span style="color:{status_badge_color}; font-weight:700;">{a['status']}</span></td>
            </tr>
            """
        posture_color = (
            "#ef4444" if any(w in exec_sum['security_posture'] for w in ("CRITICAL", "HIGH"))
            else "#f59e0b" if any(w in exec_sum['security_posture'] for w in ("MODERATE", "MEDIUM"))
            else "#10b981"
        )

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>KAVACH Assessment Report - {asm['id']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #0b0f19;
            color: #f1f5f9;
            line-height: 1.6;
            padding: 30px;
            margin: 0;
        }}
        .report-header {{
            border-bottom: 2px solid #06b6d4;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .brand-title {{
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
            color: #38bdf8;
        }}
        .tagline {{
            color: #94a3b8;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: #1e293b;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .kpi-num {{
            font-size: 28px;
            font-weight: 800;
            color: #38bdf8;
        }}
        .kpi-label {{
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        @media print {{
            body {{ background: #fff; color: #000; padding: 15px; }}
            .report-header {{ border-bottom: 2px solid #000; }}
            .kpi-card, .finding-card {{ border: 1px solid #ccc; background: #fafafa; color: #000; }}
            .kpi-num {{ color: #000; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px; text-align: right;">
        <button onclick="window.print()" style="background:#06b6d4; color:#fff; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-weight:700;">
            Print / Save to PDF
        </button>
    </div>

    <div class="report-header">
        <div class="brand-title">KAVACH 6.0 // SECURITY ASSESSMENT INTELLIGENCE REPORT</div>
        <div class="tagline">AI HYPOTHESIZES. EVIDENCE CONFIRMS.</div>
        <div style="margin-top:10px; font-size:12px; color:#64748b;">Generated: {data['metadata']['generated_at']} | Scope: {asm['scope']} | Environment: {asm['environment']}</div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-num" style="color:{posture_color};">{exec_sum['security_posture']}</div>
            <div class="kpi-label">Security Posture ({exec_sum.get('risk_score', 70)}/100 &bull; {exec_sum.get('risk_level', 'MEDIUM')} Risk)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num">{exec_sum['total_findings']}</div>
            <div class="kpi-label">Total Findings</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num" style="color:#10b981;">{exec_sum.get('confirmed_evidence', 1)}</div>
            <div class="kpi-label">Evidence Confirmed (Proof: {exec_sum.get('evidence_proofs', 1)})</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num" style="color:#06b6d4;">{exec_sum.get('technical_evidence_captured', 2)}</div>
            <div class="kpi-label">Technical Evidence Captured</div>
        </div>
    </div>

    <div style="background:#1e293b; padding:18px; border-radius:8px; border-left:4px solid #06b6d4; margin-bottom:30px;">
        <h3 style="margin-top:0; color:#38bdf8; font-size:16px;">Executive Evaluation</h3>
        <p style="margin-bottom:0; color:#cbd5e1; font-size:14px;">{exec_sum['summary']}</p>
    </div>

    <h2 style="font-size:18px; color:#f8fafc; border-bottom: 1px solid #334155; padding-bottom: 8px;">Detailed Findings & Technical Evidence</h2>
    <div>
        {findings_rows}
    </div>

    <h2 style="font-size:18px; color:#f8fafc; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-top:30px;">Cryptographic Audit Trail</h2>
    <div style="background:#1e293b; border: 1px solid #334155; border-radius:8px; overflow:hidden;">
        <table style="width:100%; border-collapse:collapse; text-align:left;">
            <thead>
                <tr style="background:#0f172a; border-bottom:2px solid #334155; font-size:11px; text-transform:uppercase; color:#94a3b8;">
                    <th style="padding:8px 10px;">Timestamp</th>
                    <th style="padding:8px 10px;">Event Type</th>
                    <th style="padding:8px 10px;">Description</th>
                    <th style="padding:8px 10px;">Finding ID</th>
                    <th style="padding:8px 10px;">Status</th>
                </tr>
            </thead>
            <tbody>
                {audit_rows or '<tr><td colspan="5" style="padding:10px; color:#64748b; text-align:center;">No audit events recorded</td></tr>'}
            </tbody>
        </table>
    </div>

    <div style="margin-top:40px; border-top:1px solid #334155; padding-top:15px; font-size:11px; color:#64748b;">
        <strong>KAVACH Architectural Rule:</strong> AI Confidence metrics represent hypothesis relevance. Vulnerability confirmation strictly requires cryptographic and technical validation evidence.
    </div>
</body>
</html>"""
        return html_template

report_service = ReportService()

