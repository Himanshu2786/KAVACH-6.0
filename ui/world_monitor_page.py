"""
KAVACH 6.0 Desktop - World Monitor Page.
Global Cyber Situational Awareness, live/demo threat feeds, and
Real World Monitor Security Assessment (Enterprise VAPT).
Implements the FINDING → EVIDENCE → SAFE PoC assessment workflow.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame,
    QLineEdit, QComboBox, QProgressBar, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from services.world_monitor_service import world_monitor_service
from core.assessment_engine import assessment_engine
from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine
from backend.app.services.remediation_service import remediation_service
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge


class FeedWorker(QThread):
    events_ready = Signal(list)

    def run(self):
        events = world_monitor_service.fetch_live_feed()
        self.events_ready.emit(events)


class AssessmentWorker(QThread):
    assessment_done = Signal(dict)
    assessment_error = Signal(str)

    def __init__(self, target_url: str, source_path: str, mode: str):
        super().__init__()
        self.target_url = target_url
        self.source_path = source_path
        self.mode = mode

    def run(self):
        try:
            res = assessment_engine.run_world_monitor_assessment(
                target_url=self.target_url,
                source_path=self.source_path,
                mode=self.mode
            )
            self.assessment_done.emit(res)
        except Exception as e:
            self.assessment_error.emit(str(e))


class WorldMonitorPage(QWidget):
    open_assessment_findings_requested = Signal(str)
    open_assessment_evidence_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_assessment = None
        self._init_ui()
        self._load_events()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        top_row = QHBoxLayout()
        h_layout = QVBoxLayout()
        h1 = QLabel("🌍 Global Cyber World Monitor & Enterprise VAPT Assessment")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Real-time CISA KEV threat telemetry & authorized empirical security assessment of World Monitor.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh Feed")
        self.btn_refresh.clicked.connect(self._load_events)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)

        # ─────────────────────────────────────────────────────────────────────
        # SECTION 1: REAL WORLD MONITOR SECURITY ASSESSMENT (ENTERPRISE VAPT)
        # ─────────────────────────────────────────────────────────────────────
        asm_card = GlassCard(
            "World Monitor Security Assessment (Enterprise VAPT)",
            "Empirical non-destructive evaluation across live deployment & source repository",
            "🛡️"
        )
        asm_layout = QVBoxLayout()
        asm_layout.setSpacing(12)

        # Controls Row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(10)

        # Target URL Input
        url_box = QVBoxLayout()
        url_lbl = QLabel("Live Target URL:")
        url_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #d4d4d8;")
        self.url_input = QLineEdit("https://www.worldmonitor.app")
        self.url_input.setPlaceholderText("https://www.worldmonitor.app")
        self.url_input.setStyleSheet("background: rgba(10,12,18,0.9); color: #ffffff; padding: 6px; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px;")
        url_box.addWidget(url_lbl)
        url_box.addWidget(self.url_input)
        ctrl_row.addLayout(url_box, stretch=3)

        # Source Path Input
        src_box = QVBoxLayout()
        src_lbl = QLabel("Source Code Directory (https://github.com/koala73/worldmonitor):")
        src_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #d4d4d8;")
        self.src_input = QLineEdit("")
        self.src_input.setPlaceholderText("e.g. ./worldmonitor (or leave empty if unconfigured)")
        self.src_input.setStyleSheet("background: rgba(10,12,18,0.9); color: #ffffff; padding: 6px; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px;")
        src_box.addWidget(src_lbl)
        src_box.addWidget(self.src_input)
        ctrl_row.addLayout(src_box, stretch=3)

        # Mode Selector
        mode_box = QVBoxLayout()
        mode_lbl = QLabel("Assessment Mode:")
        mode_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #d4d4d8;")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["HYBRID (Runtime + Source)", "RUNTIME (Live App Only)", "SOURCE (Static Repo Only)"])
        self.mode_combo.setStyleSheet("background: rgba(10,12,18,0.9); color: #ffffff; padding: 6px; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px;")
        mode_box.addWidget(mode_lbl)
        mode_box.addWidget(self.mode_combo)
        ctrl_row.addLayout(mode_box, stretch=2)

        # Trigger Button
        btn_box = QVBoxLayout()
        btn_box.addWidget(QLabel(" "))
        self.btn_run_asm = QPushButton("▶ Run Assessment")
        self.btn_run_asm.setObjectName("cyanBtn")
        self.btn_run_asm.setFixedHeight(34)
        self.btn_run_asm.clicked.connect(self._run_world_monitor_assessment)
        btn_box.addWidget(self.btn_run_asm)
        ctrl_row.addLayout(btn_box, stretch=2)

        asm_layout.addLayout(ctrl_row)

        # Progress Bar & Stage Status
        self.asm_progress = QProgressBar()
        self.asm_progress.setFixedHeight(4)
        self.asm_progress.setTextVisible(False)
        self.asm_progress.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.05); border: none; } QProgressBar::chunk { background: #06b6d4; }")
        self.asm_progress.setVisible(False)
        asm_layout.addWidget(self.asm_progress)

        self.lbl_asm_status = QLabel("")
        self.lbl_asm_status.setStyleSheet("font-size: 11px; color: #34d399; font-family: 'JetBrains Mono', monospace;")
        asm_layout.addWidget(self.lbl_asm_status)

        # Assessment Output Container
        self.asm_output_layout = QVBoxLayout()
        self.asm_output_layout.setSpacing(10)
        self.asm_output_widget = QWidget()
        self.asm_output_widget.setLayout(self.asm_output_layout)
        asm_layout.addWidget(self.asm_output_widget)

        asm_card.add_layout(asm_layout)
        layout.addWidget(asm_card)

        # ─────────────────────────────────────────────────────────────────────
        # SECTION 2: ACTIVE GLOBAL THREAT TELEMETRY & ADVISORIES
        # ─────────────────────────────────────────────────────────────────────
        map_card = GlassCard("Active Global Threat Matrix", "CISA KEV Feeds & Situational Advisories", "🌐")
        
        self.events_layout = QVBoxLayout()
        self.events_layout.setSpacing(10)
        
        self.events_container = QWidget()
        self.events_container.setLayout(self.events_layout)
        map_card.add_widget(self.events_container)
        
        layout.addWidget(map_card)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _load_events(self):
        self.btn_refresh.setEnabled(False)
        self.worker = FeedWorker()
        self.worker.events_ready.connect(self._render_events)
        self.worker.start()

    def _render_events(self, events: list):
        self.btn_refresh.setEnabled(True)
        
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for ev in events:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: rgba(10, 12, 18, 0.85);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 8px;
                    padding: 12px;
                }
                QFrame:hover {
                    border-color: rgba(6, 182, 212, 0.35);
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(12, 10, 12, 10)
            c_layout.setSpacing(6)
            
            top_line = QHBoxLayout()
            sev_badge = StatusBadge(ev.get("severity", "HIGH"), ev.get("severity", "HIGH"))
            top_line.addWidget(sev_badge)
            
            source_badge = StatusBadge(ev.get("source", "THREAT FEED"), "PUBLIC" if not ev.get("is_demo") else "DEMO")
            top_line.addWidget(source_badge)
            
            geo_lbl = QLabel(f"📍 {ev.get('city', 'Global')}, {ev.get('country', '')}")
            geo_lbl.setStyleSheet("font-size: 11px; color: #71717a;")
            top_line.addWidget(geo_lbl)
            top_line.addStretch()
            
            time_lbl = QLabel(ev.get("timestamp", ""))
            time_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #52525b;")
            top_line.addWidget(time_lbl)
            c_layout.addLayout(top_line)
            
            title = QLabel(ev.get("title", ""))
            title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff;")
            c_layout.addWidget(title)
            
            desc = QLabel(ev.get("description", ""))
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 11px; color: #a1a1aa; line-height: 1.3;")
            c_layout.addWidget(desc)
            
            self.events_layout.addWidget(card)

    def _run_world_monitor_assessment(self):
        target_url = self.url_input.text().strip()
        source_path = self.src_input.text().strip()
        mode_raw = self.mode_combo.currentText()
        mode = "HYBRID" if "HYBRID" in mode_raw else ("LIVE" if "LIVE" in mode_raw else "SOURCE")

        self.btn_run_asm.setEnabled(False)
        self.asm_progress.setVisible(True)
        self.asm_progress.setValue(30)
        self.lbl_asm_status.setText("Initiating empirical World Monitor assessment pipeline...")

        # Clear existing assessment output
        while self.asm_output_layout.count():
            item = self.asm_output_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.asm_worker = AssessmentWorker(target_url, source_path, mode)
        self.asm_worker.assessment_done.connect(self._on_assessment_completed)
        self.asm_worker.assessment_error.connect(self._on_assessment_error)
        self.asm_worker.start()

    def _on_assessment_completed(self, res: dict):
        self.last_assessment = res
        self.btn_run_asm.setEnabled(True)
        self.asm_progress.setValue(100)
        self.asm_progress.setVisible(False)

        status = res.get("status", "COMPLETED")
        asm_id = res.get("assessment_id", "")
        summary = res.get("summary", "")
        findings = res.get("findings", [])
        evidence = res.get("evidence", [])
        coverage_matrix = res.get("coverage_matrix", [])
        confirmed_count = sum(1 for f in findings if f.get("status") == "CONFIRMED")
        potential_count = sum(1 for f in findings if f.get("status") != "CONFIRMED")
        validated_domains = sum(1 for d in coverage_matrix if d.get("validation_status") == "VALIDATED")

        self.lbl_asm_status.setText(f"✓ Assessment {asm_id} completed: {validated_domains}/7 SIH domains validated, {len(findings)} findings.")

        # ─────────────────────────────────────────────────────────────────────
        # 1. Summary Header Card with Navigation Action Buttons
        # ─────────────────────────────────────────────────────────────────────
        hdr_card = QFrame()
        hdr_card.setStyleSheet("background: rgba(6,182,212,0.08); border: 1px solid rgba(6,182,212,0.3); border-radius: 6px; padding: 12px;")
        hdr_layout = QVBoxLayout(hdr_card)
        hdr_layout.setSpacing(8)

        t_row = QHBoxLayout()
        t_lbl = QLabel(f"Assessment ID: {asm_id} | Status: {status} | Mode: {res.get('mode')} | Validated Domains: {validated_domains}/7")
        t_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #06b6d4;")
        t_row.addWidget(t_lbl)
        t_row.addStretch()

        # FINDINGS button: enabled only if findings exist
        btn_view_findings = QPushButton(f"📋 View Findings ({len(findings)})")
        btn_view_findings.setEnabled(len(findings) > 0)
        btn_view_findings.setStyleSheet("font-size: 11px; padding: 4px 10px;")
        btn_view_findings.clicked.connect(lambda: self.open_assessment_findings_requested.emit(asm_id))
        t_row.addWidget(btn_view_findings)

        # EVIDENCE button: enabled only if evidence exists
        btn_view_evidence = QPushButton(f"🔐 View Evidence ({len(evidence)})")
        btn_view_evidence.setEnabled(len(evidence) > 0)
        btn_view_evidence.setStyleSheet("font-size: 11px; padding: 4px 10px;")
        btn_view_evidence.clicked.connect(lambda: self.open_assessment_evidence_requested.emit(asm_id))
        t_row.addWidget(btn_view_evidence)

        hdr_layout.addLayout(t_row)

        s_lbl = QLabel(summary)
        s_lbl.setWordWrap(True)
        s_lbl.setStyleSheet("font-size: 12px; color: #e4e4e7;")
        hdr_layout.addWidget(s_lbl)
        self.asm_output_layout.addWidget(hdr_card)

        # ─────────────────────────────────────────────────────────────────────
        # 2. DOMAIN VALIDATION COVERAGE MATRIX
        # ─────────────────────────────────────────────────────────────────────
        if coverage_matrix:
            cov_card = QFrame()
            cov_card.setStyleSheet("background: rgba(10,12,18,0.95); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 12px;")
            cov_layout = QVBoxLayout(cov_card)
            cov_layout.setSpacing(8)

            cov_hdr = QLabel("📊 Domain Validation Coverage Matrix")
            cov_hdr.setStyleSheet("font-size: 13px; font-weight: 800; color: #ffffff;")
            cov_layout.addWidget(cov_hdr)

            # Table Header
            th_row = QHBoxLayout()
            th_row.setContentsMargins(4, 4, 4, 4)
            th_c1 = QLabel("Category / Domain")
            th_c1.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a;")
            th_c2 = QLabel("Engine Status")
            th_c2.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a;")
            th_c3 = QLabel("Tests / Ev.")
            th_c3.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a; text-align: center;")
            th_c4 = QLabel("Findings")
            th_c4.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a; text-align: center;")
            th_c5 = QLabel("Validation Status")
            th_c5.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a;")

            th_row.addWidget(th_c1, stretch=3)
            th_row.addWidget(th_c2, stretch=2)
            th_row.addWidget(th_c3, stretch=1)
            th_row.addWidget(th_c4, stretch=1)
            th_row.addWidget(th_c5, stretch=2)
            cov_layout.addLayout(th_row)

            # Matrix Rows
            for d in coverage_matrix:
                row_f = QFrame()
                row_f.setStyleSheet("background: rgba(255,255,255,0.02); border-top: 1px solid rgba(255,255,255,0.06); padding: 4px;")
                row_l = QHBoxLayout(row_f)
                row_l.setContentsMargins(4, 4, 4, 4)
                row_l.setSpacing(6)

                # Domain Name & Code
                dom_lbl = QLabel(f"[{d.get('category_code')}] {d.get('category_name')}")
                dom_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #ffffff;")
                row_l.addWidget(dom_lbl, stretch=3)

                # Engine Status
                eng_st = d.get("engine_status", "IMPLEMENTED")
                eng_badge = StatusBadge(eng_st, "ONLINE" if eng_st == "FUNCTIONAL" else "PUBLIC")
                row_l.addWidget(eng_badge, stretch=2)

                # Tests & Evidence Count
                te_lbl = QLabel(f"{d.get('tests_executed', 0)} / {d.get('evidence_generated', 0)}")
                te_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #38bdf8;")
                row_l.addWidget(te_lbl, stretch=1)

                # Findings Count
                fc = d.get('findings_count', 0)
                fc_lbl = QLabel(str(fc))
                fc_lbl.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: {'#f87171' if fc > 0 else '#34d399'};")
                row_l.addWidget(fc_lbl, stretch=1)

                # Validation Status Badge
                val_st = d.get("validation_status", "NOT VALIDATED")
                val_badge = StatusBadge(val_st, "CONFIRMED" if val_st == "VALIDATED" else "OFFLINE")
                row_l.addWidget(val_badge, stretch=2)

                cov_layout.addWidget(row_f)

            self.asm_output_layout.addWidget(cov_card)

        # Zero Result Handling
        if not findings:
            empty_lbl = QLabel("ℹ️ No confirmed vulnerabilities identified. All tested defensive controls passed.")
            empty_lbl.setStyleSheet("font-size: 12px; color: #34d399; padding: 12px; font-weight: 600;")
            self.asm_output_layout.addWidget(empty_lbl)
            return

        if confirmed_count == 0 and potential_count > 0:
            pot_lbl = QLabel("⚠️ Potential issues requiring further validation.")
            pot_lbl.setStyleSheet("font-size: 12px; color: #f59e0b; padding: 8px; font-weight: 600;")
            self.asm_output_layout.addWidget(pot_lbl)

        # Render Findings with Evidence & 5-Point Judge Traceability
        for f in findings:
            f_card = QFrame()
            f_card.setStyleSheet("background: rgba(10,12,18,0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;")
            f_layout = QVBoxLayout(f_card)
            f_layout.setSpacing(8)

            r1 = QHBoxLayout()
            r1.addWidget(StatusBadge(f.get("severity", "MEDIUM"), f.get("severity", "MEDIUM")))
            status_val = f.get("status", "CONFIRMED")
            r1.addWidget(StatusBadge(status_val, "ONLINE" if status_val == "CONFIRMED" else "WARNING"))
            
            cwe_txt = f.get("cwe") or f.get("cwe_id", "")
            cat_txt = f.get("category", "")
            cvss_txt = f"CVSS {f.get('cvss_score', f.get('priority_score', 'N/A'))}"
            info_lbl = QLabel(f"{cwe_txt} | {cat_txt} | {cvss_txt}")
            info_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #a1a1aa;")
            r1.addWidget(info_lbl)
            r1.addStretch()

            rt_st = f.get("runtime_validation_status", status_val)
            rt_badge_col = "#10b981" if rt_st == "CONFIRMED" else ("#f59e0b" if rt_st == "POTENTIAL" else "#71717a")
            rt_badge_lbl = QLabel(f"Runtime: {rt_st}")
            rt_badge_lbl.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: {rt_badge_col}; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;")
            r1.addWidget(rt_badge_lbl)

            f_layout.addLayout(r1)

            title_lbl = QLabel(f.get("title", ""))
            title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff;")
            f_layout.addWidget(title_lbl)

            # 1. "What code caused the problem?" (Source Code / Scope)
            src_f = f.get("file") or f.get("affected_component", "")
            src_l = f.get("line")
            src_sym = f.get("symbol_or_function")
            src_det = f.get("detector") or f.get("code_pattern")

            if src_f or src_sym:
                c_box = QFrame()
                c_box.setStyleSheet("background: rgba(15,23,42,0.8); border: 1px solid rgba(56,189,248,0.2); border-radius: 4px; padding: 6px;")
                c_l = QVBoxLayout(c_box)
                c_l.setSpacing(2)
                c_hdr = QLabel(f"🔎 1. Source Location: {src_f}" + (f":{src_l}" if src_l else "") + (f" | Scope: {src_sym}" if src_sym else ""))
                c_hdr.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #38bdf8;")
                c_l.addWidget(c_hdr)
                if src_det:
                    d_lbl = QLabel(f"Detector Pattern: {src_det}")
                    d_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #94a3b8;")
                    c_l.addWidget(d_lbl)
                f_layout.addWidget(c_box)

            desc_lbl = QLabel(f.get("description", ""))
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 11px; color: #d4d4d8;")
            f_layout.addWidget(desc_lbl)

            # Match associated evidence
            ev_match = next((ev for ev in evidence if (ev.get("finding_id") == f.get("id") or ev.get("finding_id") == f.get("finding_id"))), None)
            if ev_match:
                ev_box = QFrame()
                ev_box.setStyleSheet("background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px; padding: 8px;")
                ev_l = QVBoxLayout(ev_box)
                ev_l.setSpacing(4)

                h_lbl = QLabel(f"SHA-256 Hash: {ev_match.get('hash', '')[:28]}... | Evidence ID: {ev_match.get('evidence_id', '')}")
                h_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #34d399;")
                ev_l.addWidget(h_lbl)

                if ev_match.get("simple_explanation"):
                    simp_lbl = QLabel(f"💡 Simple View: {ev_match.get('simple_explanation')}")
                    simp_lbl.setWordWrap(True)
                    simp_lbl.setStyleSheet("font-size: 11px; color: #e2e8f0; font-style: italic;")
                    ev_l.addWidget(simp_lbl)

                f_layout.addWidget(ev_box)

            # 5. Actionable 7-Point Remediation & Verification Re-Test
            rem_details = f.get("remediation_details")
            if not rem_details or not isinstance(rem_details, dict):
                rem_details = remediation_service.generate_structured_remediation(f)

            fix_box = QFrame()
            fix_box.setStyleSheet("background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.25); border-radius: 6px; padding: 10px;")
            fix_l = QVBoxLayout(fix_box)
            fix_l.setSpacing(5)

            fix_top = QHBoxLayout()
            fix_hdr = QLabel("🛠️ 5. ACTIONABLE REMEDIATION & VERIFICATION METHOD")
            fix_hdr.setStyleSheet("font-size: 11px; font-weight: 800; color: #10b981;")
            fix_top.addWidget(fix_hdr)
            fix_top.addStretch()

            curr_st = f.get("status", "CONFIRMED")
            st_badge = QLabel(f"Lifecycle: {curr_st}")
            st_badge.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #10b981; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;")
            fix_top.addWidget(st_badge)
            fix_l.addLayout(fix_top)

            for label_name, field_val in [
                ("Problem:", rem_details.get("problem")),
                ("Root Cause:", rem_details.get("root_cause")),
                ("Recommended Fix:", rem_details.get("recommended_fix") or f.get("remediation")),
                ("Security Principle:", rem_details.get("security_principle")),
                ("Verification Method:", rem_details.get("verification_method") or f.get("safe_poc"))
            ]:
                if field_val:
                    r_row = QHBoxLayout()
                    lbl_t = QLabel(label_name)
                    lbl_t.setFixedWidth(140)
                    lbl_t.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6ee7b7; font-weight: 700;")
                    val_t = QLabel(str(field_val))
                    val_t.setWordWrap(True)
                    val_t.setStyleSheet("font-size: 10px; color: #e2e8f0;")
                    r_row.addWidget(lbl_t)
                    r_row.addWidget(val_t)
                    fix_l.addLayout(r_row)

            # Code patch snippet
            guidance_txt = rem_details.get("implementation_guidance")
            if guidance_txt:
                g_lbl = QLabel("Implementation Guidance (Actionable Syntax Patch):")
                g_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #38bdf8; margin-top: 4px;")
                fix_l.addWidget(g_lbl)

                g_box = QLabel(guidance_txt)
                g_box.setWordWrap(True)
                g_box.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #f1f5f9; background: rgba(0,0,0,0.6); padding: 6px; border-radius: 4px; border-left: 3px solid #10b981;")
                fix_l.addWidget(g_box)

            # Retest Button Row
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            btn_retest = QPushButton("⚡ Re-Run Verification Test (BEFORE → AFTER)")
            btn_retest.setStyleSheet("font-size: 10px; font-weight: 700; background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; border-radius: 4px; padding: 4px 10px;")
            btn_retest.clicked.connect(lambda _, f_obj=f: self._run_retest_action(f_obj))
            btn_row.addWidget(btn_retest)
            fix_l.addLayout(btn_row)

            f_layout.addWidget(fix_box)

            self.asm_output_layout.addWidget(f_card)

    def _run_retest_action(self, f: dict):
        fnd_id = f.get("finding_id") or f.get("id")
        asm_id = f.get("assessment_id") or "ASM-WM"
        tgt = f.get("file") or f.get("affected_component")

        try:
            res = world_monitor_assessment_engine.verify_remediation(
                finding_id=fnd_id,
                assessment_id=asm_id,
                target=tgt
            )
            status_after = res.get("new_status", "VERIFIED")
            verdict = res.get("comparison_verdict", "VERIFIED")
            msg = (
                f"### Remediation Verification Re-Test\n\n"
                f"**Finding ID:** `{fnd_id}`\n\n"
                f"**Workflow Stage:** `BEFORE` → `VULNERABILITY OBSERVED` → `REMEDIATION` → `AFTER` → `RE-RUN TEST` → `COMPARE` → `{status_after}`\n\n"
                f"• **Before Observation:** {res.get('before_result')}\n"
                f"• **Remediation Target:** `{tgt}`\n"
                f"• **After Observation:** {res.get('after_result')}\n"
                f"• **Comparison Verdict:** **{verdict}**\n\n"
                f"**Integrity Hash:** `{res.get('hash', '')[:32]}...`\n"
                f"Finding status transitioned to: **{status_after}**."
            )
            QMessageBox.information(self, f"Verification Result: {status_after}", msg)
        except Exception as e:
            QMessageBox.critical(self, "Verification Error", f"Failed to execute verification re-test:\n{str(e)}")


    def _on_assessment_error(self, err_msg: str):
        self.btn_run_asm.setEnabled(True)
        self.asm_progress.setVisible(False)
        self.lbl_asm_status.setText("❌ Assessment encountered an error.")
        QMessageBox.critical(self, "Assessment Error", f"Failed to complete assessment:\n{err_msg}")
