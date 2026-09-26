"""
KAVACH 6.0 Desktop - Findings & Secure Scanner Page.
Features drag-and-drop, path manual entry, permission verification, background scanning,
assessment isolation filtering, deterministic CVSS 3.1 calculation factors, and structured 5-point business impact.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame,
    QComboBox, QFileDialog, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from services.storage_service import storage
from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine
from backend.app.services.remediation_service import remediation_service
from core.scanner.filesystem_scanner import FilesystemScanner
from core.scanner.scan_result import ScanResult
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge
from widgets.drop_zone import DropZone
from widgets.file_permission_dialog import FilePermissionDialog


class BackgroundScanWorker(QThread):
    progress_update = Signal(int, str, int) # (scanned_count, current_file, findings_count)
    scan_completed = Signal(object) # ScanResult
    scan_failed = Signal(str)

    def __init__(self, target_path: str, follow_symlinks: bool = False):
        super().__init__()
        self.target_path = target_path
        self.follow_symlinks = follow_symlinks
        self.scanner = FilesystemScanner(on_progress=self._on_progress)

    def _on_progress(self, count: int, current_file: str, findings: int):
        self.progress_update.emit(count, current_file, findings)

    def cancel(self):
        self.scanner.cancel()

    def run(self):
        try:
            res = self.scanner.scan_target(self.target_path, self.follow_symlinks)
            self.scan_completed.emit(res)
        except Exception as e:
            self.scan_failed.emit(str(e))


class FindingsPage(QWidget):
    inspect_evidence_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_findings = []
        self.selected_assessment_id = None
        self.worker = None
        self._init_ui()
        self.refresh_findings()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        top_row = QHBoxLayout()
        h_layout = QVBoxLayout()
        h1 = QLabel("🛡️ Defensive File & Target Findings")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Drag & drop a file/folder or enter a path below to run a safe static security scan.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()

        self.lbl_asm_filter = QLabel("")
        self.lbl_asm_filter.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #38bdf8; background: rgba(56,189,248,0.1); padding: 4px 8px; border-radius: 4px;")
        self.lbl_asm_filter.setVisible(False)
        top_row.addWidget(self.lbl_asm_filter)

        self.btn_clear_filter = QPushButton("✕ Clear Scope")
        self.btn_clear_filter.setVisible(False)
        self.btn_clear_filter.clicked.connect(self._clear_assessment_scope)
        top_row.addWidget(self.btn_clear_filter)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_findings)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # 1. Drag & Drop Zone
        self.drop_zone = DropZone(self)
        self.drop_zone.file_dropped.connect(self._on_path_selected)
        layout.addWidget(self.drop_zone)
        
        # 2. Path Manual Entry & Browser Bar
        scan_bar = GlassCard()
        bar_l = QVBoxLayout()
        bar_l.setSpacing(10)
        
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Enter or paste file / directory path (e.g. C:\\Project or demo\\training_samples)...")
        self.input_path.setFixedHeight(36)
        input_row.addWidget(self.input_path)
        
        btn_file = QPushButton("📄 Browse File")
        btn_file.clicked.connect(self._browse_file)
        input_row.addWidget(btn_file)
        
        btn_dir = QPushButton("📁 Browse Folder")
        btn_dir.clicked.connect(self._browse_dir)
        input_row.addWidget(btn_dir)
        
        self.btn_scan = QPushButton("⚡ Scan Target")
        self.btn_scan.setObjectName("cyanBtn")
        self.btn_scan.setFixedHeight(36)
        self.btn_scan.clicked.connect(lambda: self._on_path_selected(self.input_path.text().strip()))
        input_row.addWidget(self.btn_scan)
        bar_l.addLayout(input_row)
        
        # Quick Presets Row
        preset_row = QHBoxLayout()
        p_lbl = QLabel("Training Fixtures:")
        p_lbl.setStyleSheet("color: #71717a; font-size: 11px;")
        preset_row.addWidget(p_lbl)
        
        for name, path in [
            ("Demo Secrets (.env)", "demo/training_samples/demo_api_keys.env"),
            ("Suspicious Extension (.pdf.exe)", "demo/training_samples/suspicious_invoice.pdf.exe"),
            ("Insecure Config (.json)", "demo/training_samples/demo_insecure_config.json"),
            ("Clean Baseline (.txt)", "demo/training_samples/clean_document.txt")
        ]:
            b = QPushButton(name)
            b.setStyleSheet("font-size: 11px; padding: 3px 8px;")
            b.clicked.connect(lambda _, p=path: self._on_path_selected(p))
            preset_row.addWidget(b)
        preset_row.addStretch()
        bar_l.addLayout(preset_row)
        
        # 3. Live Progress Panel (Hidden by default)
        self.prog_panel = QFrame()
        self.prog_panel.setStyleSheet("background-color: rgba(6, 8, 14, 0.9); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 8px; padding: 8px;")
        prog_l = QVBoxLayout(self.prog_panel)
        prog_l.setSpacing(6)
        
        prog_top = QHBoxLayout()
        self.lbl_prog_status = QLabel("Scanning files in target directory...")
        self.lbl_prog_status.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #22d3ee; font-weight: 700;")
        prog_top.addWidget(self.lbl_prog_status)
        prog_top.addStretch()
        
        self.btn_cancel = QPushButton("🛑 Cancel Scan")
        self.btn_cancel.setObjectName("dangerBtn")
        self.btn_cancel.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.btn_cancel.clicked.connect(self._cancel_scan)
        prog_top.addWidget(self.btn_cancel)
        prog_l.addLayout(prog_top)
        
        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(4)
        self.prog_bar.setRange(0, 0)
        self.prog_bar.setTextVisible(False)
        prog_l.addWidget(self.prog_bar)
        
        self.lbl_current_file = QLabel("")
        self.lbl_current_file.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a;")
        prog_l.addWidget(self.lbl_current_file)
        
        self.prog_panel.setVisible(False)
        bar_l.addWidget(self.prog_panel)
        
        scan_bar.add_layout(bar_l)
        layout.addWidget(scan_bar)
        
        # 4. Filters & Search Bar for existing findings
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter findings by title, category, or file path...")
        self.search_input.textChanged.connect(self._apply_filter)
        filter_bar.addWidget(self.search_input)
        
        self.sev_filter = QComboBox()
        self.sev_filter.addItems(["All Severities", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.sev_filter.currentTextChanged.connect(self._apply_filter)
        filter_bar.addWidget(self.sev_filter)
        layout.addLayout(filter_bar)
        
        # 5. Findings Catalog List
        self.findings_layout = QVBoxLayout()
        self.findings_layout.setSpacing(14)
        
        self.findings_container = QWidget()
        self.findings_container.setLayout(self.findings_layout)
        layout.addWidget(self.findings_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_assessment(self, assessment_id: str):
        """Loads findings scoped strictly to a specific assessment ID."""
        self.selected_assessment_id = assessment_id
        self.lbl_asm_filter.setText(f"Scope: {assessment_id}")
        self.lbl_asm_filter.setVisible(True)
        self.btn_clear_filter.setVisible(True)
        self.refresh_findings()

    def _clear_assessment_scope(self):
        self.selected_assessment_id = None
        self.lbl_asm_filter.setVisible(False)
        self.btn_clear_filter.setVisible(False)
        self.refresh_findings()

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Scan")
        if path:
            self._on_path_selected(path)

    def _browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if path:
            self._on_path_selected(path)

    def _on_path_selected(self, target_path: str):
        if not target_path:
            QMessageBox.warning(self, "Missing Path", "Please enter or select a valid file or folder path.")
            return

        if not os.path.exists(target_path):
            QMessageBox.warning(self, "Target Not Found", f"The path '{target_path}' does not exist on this machine.")
            return

        self.input_path.setText(target_path)
        
        # Open Least-Privilege Permission & Scope Confirmation Dialog
        dlg = FilePermissionDialog(target_path, self)
        if dlg.exec() != FilePermissionDialog.DialogCode.Accepted:
            return

        follow_symlinks = dlg.should_follow_symlinks()
        
        # Start Background Scanner Worker
        self.btn_scan.setEnabled(False)
        self.prog_panel.setVisible(True)
        self.lbl_prog_status.setText(f"Scanning: {os.path.basename(target_path)}")
        
        self.worker = BackgroundScanWorker(target_path, follow_symlinks)
        self.worker.progress_update.connect(self._on_scan_progress)
        self.worker.scan_completed.connect(self._on_scan_done)
        self.worker.scan_failed.connect(self._on_scan_failed)
        self.worker.start()

    def _on_scan_progress(self, count: int, current_file: str, findings: int):
        self.lbl_prog_status.setText(f"Scanning... Files inspected: {count} | Findings generated: {findings}")
        self.lbl_current_file.setText(f"Inspecting: {current_file}")

    def _cancel_scan(self):
        if self.worker:
            self.worker.cancel()
            self.lbl_prog_status.setText("Cancelling scan gracefully...")

    def _on_scan_done(self, res: ScanResult):
        self.btn_scan.setEnabled(True)
        self.prog_panel.setVisible(False)
        self.refresh_findings()
        
        count = len(res.observations)
        if count == 0:
            QMessageBox.information(
                self,
                "Scan Completed — Clean Target",
                f"Defensive scan finished in {res.duration_seconds}s.\nInspected {res.total_files_scanned} files.\n\nNo confirmed vulnerabilities identified."
            )
        else:
            QMessageBox.information(
                self,
                "Scan Completed",
                f"Defensive scan finished in {res.duration_seconds}s.\nInspected {res.total_files_scanned} files.\nIdentified {count} findings."
            )

    def _on_scan_failed(self, err: str):
        self.btn_scan.setEnabled(True)
        self.prog_panel.setVisible(False)
        QMessageBox.critical(self, "Scan Failed", f"An error occurred during scanning: {err}")

    def refresh_findings(self):
        self.all_findings = storage.get_all_findings(assessment_id=self.selected_assessment_id)
        self._apply_filter()

    def _apply_filter(self):
        while self.findings_layout.count():
            item = self.findings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        query = self.search_input.text().strip().lower()
        sev = self.sev_filter.currentText()
        
        matched = []
        for f in self.all_findings:
            if sev != "All Severities" and f.get("severity") != sev:
                continue
            if query and (
                query not in f.get("title", "").lower()
                and query not in f.get("category", "").lower()
                and query not in f.get("affected_component", "").lower()
            ):
                continue
            matched.append(f)

        if not matched:
            empty_msg = "No confirmed vulnerabilities identified." if not self.selected_assessment_id else f"No findings recorded for assessment {self.selected_assessment_id}."
            empty_lbl = QLabel(empty_msg)
            empty_lbl.setStyleSheet("color: #71717a; font-size: 13px; padding: 24px;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.findings_layout.addWidget(empty_lbl)
            return

        for f in matched:
            card = GlassCard()
            c_layout = QVBoxLayout()
            c_layout.setSpacing(10)
            
            top_line = QHBoxLayout()
            top_line.addWidget(StatusBadge(f.get("severity", "MEDIUM"), f.get("severity", "MEDIUM")))
            status_tag = f.get("status", "OPEN")
            top_line.addWidget(StatusBadge(status_tag, "ONLINE" if status_tag == "CONFIRMED" else "INFO"))
            
            cwe_str = f.get("cwe_id", "")
            if cwe_str:
                top_line.addWidget(StatusBadge(cwe_str, "INFO"))
            
            cvss_s = f.get("cvss_score")
            if cvss_s:
                cvss_lbl = QLabel(f"CVSS v3.1: {cvss_s}")
                cvss_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 800; color: #f59e0b;")
                top_line.addWidget(cvss_lbl)

            top_line.addStretch()
            
            comp = QLabel(f"Target: {os.path.basename(f.get('affected_component', ''))}")
            comp.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #71717a;")
            top_line.addWidget(comp)
            c_layout.addLayout(top_line)
            
            title = QLabel(f.get("title", ""))
            title.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
            c_layout.addWidget(title)
            
            desc = QLabel(f.get("description", ""))
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 12px; color: #a1a1aa; line-height: 1.3;")
            c_layout.addWidget(desc)

            # ─────────────────────────────────────────────────────────────────
            # 1. "What code caused the problem?" (Source Code & Symbol Context)
            # ─────────────────────────────────────────────────────────────────
            src_file = f.get("file") or f.get("source_reference", "")
            src_line = f.get("line")
            src_symbol = f.get("symbol_or_function")
            src_pattern = f.get("code_pattern") or f.get("detector")
            src_code_snippet = f.get("what_code_caused_problem", {}).get("snippet") if isinstance(f.get("what_code_caused_problem"), dict) else None

            if src_file or src_symbol:
                code_box = QFrame()
                code_box.setStyleSheet("background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 6px; padding: 8px;")
                code_l = QVBoxLayout(code_box)
                code_l.setSpacing(4)

                c_head = QHBoxLayout()
                c_tag = QLabel("🔎 1. WHAT CODE CAUSED THE PROBLEM?")
                c_tag.setStyleSheet("font-size: 10px; font-weight: 800; color: #38bdf8;")
                c_head.addWidget(c_tag)
                c_head.addStretch()

                if src_file:
                    loc_lbl = QLabel(f"File: {src_file}" + (f":{src_line}" if src_line else ""))
                    loc_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #38bdf8; font-weight: 700;")
                    c_head.addWidget(loc_lbl)
                code_l.addLayout(c_head)

                if src_symbol:
                    sym_row = QHBoxLayout()
                    sym_tag = QLabel("Scope / Function:")
                    sym_tag.setFixedWidth(120)
                    sym_tag.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94a3b8;")
                    sym_val = QLabel(src_symbol)
                    sym_val.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #a78bfa; font-weight: 700;")
                    sym_row.addWidget(sym_tag)
                    sym_row.addWidget(sym_val)
                    sym_row.addStretch()
                    code_l.addLayout(sym_row)

                if src_pattern:
                    pat_row = QHBoxLayout()
                    pat_tag = QLabel("Detector Pattern:")
                    pat_tag.setFixedWidth(120)
                    pat_tag.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94a3b8;")
                    pat_val = QLabel(str(src_pattern))
                    pat_val.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #34d399;")
                    pat_row.addWidget(pat_tag)
                    pat_row.addWidget(pat_val)
                    pat_row.addStretch()
                    code_l.addLayout(pat_row)

                if src_code_snippet:
                    snip_lbl = QLabel(src_code_snippet)
                    snip_lbl.setWordWrap(True)
                    snip_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #f1f5f9; background: rgba(0,0,0,0.5); padding: 6px; border-radius: 4px; border-left: 3px solid #38bdf8;")
                    code_l.addWidget(snip_lbl)

                c_layout.addWidget(code_box)

            # ─────────────────────────────────────────────────────────────────
            # 2. "What happened at runtime?" (Runtime Observation & Status)
            # ─────────────────────────────────────────────────────────────────
            rt_status = f.get("runtime_validation_status", f.get("status", "POTENTIAL"))
            rt_obs = f.get("what_happened_at_runtime", {}).get("observation") if isinstance(f.get("what_happened_at_runtime"), dict) else None
            
            rt_box = QFrame()
            rt_box.setStyleSheet("background: rgba(10, 12, 18, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 8px;")
            rt_l = QVBoxLayout(rt_box)
            rt_l.setSpacing(4)

            rt_head = QHBoxLayout()
            rt_tag = QLabel("⚡ 2. WHAT HAPPENED AT RUNTIME?")
            rt_tag.setStyleSheet("font-size: 10px; font-weight: 800; color: #f59e0b;")
            rt_head.addWidget(rt_tag)
            rt_head.addStretch()

            rt_badge_color = "#10b981" if rt_status == "CONFIRMED" else ("#f59e0b" if rt_status == "POTENTIAL" else "#71717a")
            rt_badge = QLabel(f"Status: {rt_status}")
            rt_badge.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 800; color: {rt_badge_color}; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;")
            rt_head.addWidget(rt_badge)
            rt_l.addLayout(rt_head)

            if rt_obs:
                obs_lbl = QLabel(rt_obs)
                obs_lbl.setWordWrap(True)
                obs_lbl.setStyleSheet("font-size: 11px; color: #cbd5e1;")
                rt_l.addWidget(obs_lbl)
            else:
                obs_lbl = QLabel(f.get("description", "Observation captured during authorized assessment."))
                obs_lbl.setWordWrap(True)
                obs_lbl.setStyleSheet("font-size: 11px; color: #cbd5e1;")
                rt_l.addWidget(obs_lbl)

            c_layout.addWidget(rt_box)

            # ─────────────────────────────────────────────────────────────────
            # 3. "What evidence proves it?" & CVSS 3.1 / Business Impact
            # ─────────────────────────────────────────────────────────────────
            calc_factors = f.get("calculation_factors", {})
            vec_str = f.get("cvss_vector")
            if vec_str:
                cvss_box = QFrame()
                cvss_box.setStyleSheet("background: rgba(10,12,18,0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px;")
                cvss_l = QVBoxLayout(cvss_box)
                cvss_l.setSpacing(4)

                v_row = QHBoxLayout()
                v_tag = QLabel("📊 4. WHAT IS THE IMPACT? (CVSS 3.1 Vector):")
                v_tag.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #38bdf8;")
                v_row.addWidget(v_tag)
                v_val = QLabel(vec_str)
                v_val.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #34d399;")
                v_row.addWidget(v_val)
                v_row.addStretch()

                if calc_factors:
                    sub_info = QLabel(f"Impact: {calc_factors.get('impact_subscore', 'N/A')} | Exploitability: {calc_factors.get('exploitability_subscore', 'N/A')} | ISS: {calc_factors.get('iss', 'N/A')}")
                    sub_info.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #94a3b8;")
                    v_row.addWidget(sub_info)

                cvss_l.addLayout(v_row)
                c_layout.addWidget(cvss_box)

            # Structured 5-Point Business Impact Panel
            b_details = f.get("business_impact_details", {})
            if b_details and isinstance(b_details, dict) and b_details.get("business_consequence"):
                biz_box = QFrame()
                biz_box.setStyleSheet("background: rgba(245,158,11,0.05); border: 1px solid rgba(245,158,11,0.25); border-radius: 6px; padding: 8px;")
                biz_l = QVBoxLayout(biz_box)
                biz_l.setSpacing(4)

                b_head = QLabel("💼 BUSINESS IMPACT & OPERATIONAL RISK")
                b_head.setStyleSheet("font-size: 10px; font-weight: 800; color: #f59e0b;")
                biz_l.addWidget(b_head)

                for tag_lbl, key_name in [
                    ("Security Consequence:", "potential_security_consequence"),
                    ("Application Impact:", "application_consequence"),
                    ("Business Consequence:", "business_consequence"),
                    ("Affected Stakeholders:", "affected_stakeholders")
                ]:
                    if key_name in b_details and b_details[key_name]:
                        r_l = QHBoxLayout()
                        t_lbl = QLabel(tag_lbl)
                        t_lbl.setFixedWidth(145)
                        t_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #d4d4d8; font-weight: 700;")
                        val_lbl = QLabel(str(b_details[key_name]))
                        val_lbl.setWordWrap(True)
                        val_lbl.setStyleSheet("font-size: 11px; color: #fef08a;")
                        r_l.addWidget(t_lbl)
                        r_l.addWidget(val_lbl)
                        biz_l.addLayout(r_l)
                c_layout.addWidget(biz_box)

            # ─────────────────────────────────────────────────────────────────
            # 5. "How should it be fixed?" (Actionable 7-Field Remediation & Verification)
            # ─────────────────────────────────────────────────────────────────
            rem_details = f.get("remediation_details")
            if not rem_details or not isinstance(rem_details, dict):
                rem_details = remediation_service.generate_structured_remediation(f)

            rem_box = QFrame()
            rem_box.setStyleSheet("background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 10px;")
            rem_l = QVBoxLayout(rem_box)
            rem_l.setSpacing(6)

            rem_top = QHBoxLayout()
            rem_head = QLabel("🛠️ 5. ACTIONABLE REMEDIATION & EMPIRICAL VERIFICATION")
            rem_head.setStyleSheet("font-size: 11px; font-weight: 800; color: #10b981;")
            rem_top.addWidget(rem_head)
            rem_top.addStretch()

            curr_status = f.get("status", "OPEN")
            status_color = "#10b981" if curr_status == "VERIFIED" else ("#ef4444" if curr_status == "NOT_VERIFIED" else "#f59e0b")
            st_badge = QLabel(f"Lifecycle: {curr_status}")
            st_badge.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 800; color: {status_color}; background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 4px;")
            rem_top.addWidget(st_badge)
            rem_l.addLayout(rem_top)

            for label_name, field_val in [
                ("Problem:", rem_details.get("problem")),
                ("Root Cause:", rem_details.get("root_cause")),
                ("Recommended Fix:", rem_details.get("recommended_fix") or f.get("remediation")),
                ("Affected Component:", rem_details.get("affected_component") or f.get("affected_component")),
                ("Security Principle:", rem_details.get("security_principle")),
                ("Verification Method:", rem_details.get("verification_method") or f.get("safe_poc"))
            ]:
                if field_val:
                    r_row = QHBoxLayout()
                    lbl_t = QLabel(label_name)
                    lbl_t.setFixedWidth(145)
                    lbl_t.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6ee7b7; font-weight: 700;")
                    val_t = QLabel(str(field_val))
                    val_t.setWordWrap(True)
                    val_t.setStyleSheet("font-size: 11px; color: #e2e8f0;")
                    r_row.addWidget(lbl_t)
                    r_row.addWidget(val_t)
                    rem_l.addLayout(r_row)

            # Implementation Guidance (Code Patch / Syntax)
            guidance_txt = rem_details.get("implementation_guidance")
            if guidance_txt:
                g_lbl = QLabel("Implementation Guidance (Actionable Syntax Patch):")
                g_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #38bdf8; margin-top: 4px;")
                rem_l.addWidget(g_lbl)

                g_box = QLabel(guidance_txt)
                g_box.setWordWrap(True)
                g_box.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #f1f5f9; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 4px; border-left: 3px solid #10b981;")
                rem_l.addWidget(g_box)

            c_layout.addWidget(rem_box)

            # Action Row (Re-Test Verification & Evidence buttons)
            act_row = QHBoxLayout()
            act_row.addStretch()

            btn_verify = QPushButton("⚡ Run Verification Test (BEFORE → AFTER)")
            btn_verify.setStyleSheet("font-size: 11px; font-weight: 700; background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; border-radius: 4px; padding: 5px 12px;")
            btn_verify.clicked.connect(lambda _, finding_dict=f: self._verify_finding_action(finding_dict))
            act_row.addWidget(btn_verify)
            
            ev_id = f.get("evidence_id")
            if not ev_id and f.get("evidence_ids"):
                ev_id = f["evidence_ids"][0]

            if ev_id:
                btn_ev = QPushButton("🔍 View Cryptographic Evidence →")
                btn_ev.setObjectName("cyanBtn")
                btn_ev.setStyleSheet("font-size: 11px; padding: 5px 12px;")
                btn_ev.clicked.connect(lambda _, eid=ev_id: self.inspect_evidence_requested.emit(eid))
                act_row.addWidget(btn_ev)
                
            c_layout.addLayout(act_row)
            card.add_layout(c_layout)
            self.findings_layout.addWidget(card)

    def _verify_finding_action(self, f: dict):
        fnd_id = f.get("finding_id") or f.get("id")
        asm_id = f.get("assessment_id") or "ASM-LOCAL"
        tgt = f.get("file") or f.get("affected_component")

        try:
            res = world_monitor_assessment_engine.verify_remediation(
                finding_id=fnd_id,
                assessment_id=asm_id,
                target=tgt
            )
            verdict = res.get("comparison_verdict", "VERIFIED")
            status_after = res.get("new_status", "VERIFIED")
            msg = (
                f"### Remediation Verification Re-Test\n\n"
                f"**Finding ID:** `{fnd_id}`\n\n"
                f"**Workflow Stage:** `BEFORE` → `VULNERABILITY OBSERVED` → `REMEDIATION` → `AFTER` → `RE-RUN TEST` → `COMPARE` → `{status_after}`\n\n"
                f"• **Before Observation:** {res.get('before_result')}\n"
                f"• **Remediation Target:** `{tgt}`\n"
                f"• **After Observation:** {res.get('after_result')}\n"
                f"• **Comparison Verdict:** **{verdict}**\n\n"
                f"**Integrity Hash:** `{res.get('hash', '')[:32]}...`\n"
                f"Finding lifecycle status transitioned to: **{status_after}**."
            )
            QMessageBox.information(self, f"Verification Result: {status_after}", msg)
            self.load_findings()
        except Exception as e:
            QMessageBox.critical(self, "Verification Error", f"Failed to execute verification re-test:\n{str(e)}")

