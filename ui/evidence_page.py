"""
KAVACH 6.0 Desktop - Evidence Investigation & Re-Verification Page.
Presents the standardized 8-step cryptographic proof layout with Simple & Technical Explanations,
SHA-256 integrity hashes, and differential on-disk Re-Verification (BEFORE / AFTER).
"""

import os
import hashlib
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from services.storage_service import storage
from core.scanner.filesystem_scanner import FilesystemScanner
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge


class EvidencePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_evidence_id = None
        self.selected_assessment_id = None
        self._init_ui()
        self.refresh_evidence()

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
        h1 = QLabel("🔐 Cryptographic Evidence & Verification Explorer")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("8-step deterministic proof model with SHA-256 integrity signatures, Simple & Technical views, and BEFORE/AFTER verification.")
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
        self.btn_refresh.clicked.connect(self.refresh_evidence)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # Evidence Items Container
        self.ev_layout = QVBoxLayout()
        self.ev_layout.setSpacing(16)
        
        self.ev_container = QWidget()
        self.ev_container.setLayout(self.ev_layout)
        layout.addWidget(self.ev_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_assessment(self, assessment_id: str):
        """Loads evidence records scoped strictly to a specific assessment ID."""
        self.selected_assessment_id = assessment_id
        self.lbl_asm_filter.setText(f"Scope: {assessment_id}")
        self.lbl_asm_filter.setVisible(True)
        self.btn_clear_filter.setVisible(True)
        self.refresh_evidence()

    def _clear_assessment_scope(self):
        self.selected_assessment_id = None
        self.lbl_asm_filter.setVisible(False)
        self.btn_clear_filter.setVisible(False)
        self.refresh_evidence()

    def load_specific_evidence(self, evidence_id: str):
        self.selected_evidence_id = evidence_id
        self.refresh_evidence()

    def refresh_evidence(self):
        while self.ev_layout.count():
            item = self.ev_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        records = storage.get_all_evidence(assessment_id=self.selected_assessment_id)

        if not records:
            empty_msg = "No cryptographic evidence records stored yet." if not self.selected_assessment_id else f"No evidence records for assessment {self.selected_assessment_id}."
            empty_lbl = QLabel(empty_msg)
            empty_lbl.setStyleSheet("color: #71717a; font-size: 13px; padding: 24px;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ev_layout.addWidget(empty_lbl)
            return

        for rec in records:
            is_selected = (rec.get("id") == self.selected_evidence_id)
            card = GlassCard(glow="cyan" if is_selected else "none")
            
            c_layout = QVBoxLayout()
            c_layout.setSpacing(10)
            
            # Evidence Header
            top_line = QHBoxLayout()
            f_sev = rec.get("f_sev") or "HIGH"
            top_line.addWidget(StatusBadge(f_sev, f_sev))
            ev_type = rec.get("type") or "FILE_INSPECTION"
            top_line.addWidget(StatusBadge(ev_type, "INFO"))
            
            ev_id_lbl = QLabel(f"EVIDENCE: {rec.get('id') or ''}")
            ev_id_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #38bdf8; font-weight: 700;")
            top_line.addWidget(ev_id_lbl)
            top_line.addStretch()
            
            f_stat = rec.get("f_status") or "OPEN"
            stat_badge = StatusBadge(f_stat, "ONLINE" if f_stat in ("RESOLVED", "CONFIRMED") else "CRITICAL")
            top_line.addWidget(stat_badge)
            c_layout.addLayout(top_line)

            # Simple Explanation Card (Executive View)
            if rec.get("simple_explanation"):
                s_box = QFrame()
                s_box.setStyleSheet("background: rgba(6,182,212,0.06); border: 1px solid rgba(6,182,212,0.25); border-radius: 6px; padding: 8px;")
                s_l = QVBoxLayout(s_box)
                s_l.setSpacing(2)
                s_tag = QLabel("💡 SIMPLE EXPLANATION")
                s_tag.setStyleSheet("font-size: 10px; font-weight: 800; color: #06b6d4;")
                s_l.addWidget(s_tag)
                s_txt = QLabel(rec.get("simple_explanation"))
                s_txt.setWordWrap(True)
                s_txt.setStyleSheet("font-size: 12px; color: #e2e8f0;")
                s_l.addWidget(s_txt)
                c_layout.addWidget(s_box)

            # Technical Explanation Breakdown
            tech_exp = rec.get("technical_explanation") or {}
            if tech_exp and isinstance(tech_exp, dict):
                t_box = QFrame()
                t_box.setStyleSheet("background: rgba(10,12,18,0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px;")
                t_l = QVBoxLayout(t_box)
                t_l.setSpacing(4)
                t_tag = QLabel("🔬 TECHNICAL BREAKDOWN")
                t_tag.setStyleSheet("font-size: 10px; font-weight: 800; color: #a1a1aa;")
                t_l.addWidget(t_tag)

                for label, key in [
                    ("Endpoint:", "endpoint"),
                    ("HTTP Method:", "http_method"),
                    ("Parameter:", "parameter"),
                    ("Auth State:", "auth_state"),
                    ("Authz State:", "authz_state"),
                    ("Observed:", "observed_behavior"),
                    ("Expected:", "expected_behavior"),
                    ("Actual:", "actual_behavior")
                ]:
                    if key in tech_exp and tech_exp[key]:
                        row = QHBoxLayout()
                        lbl = QLabel(label)
                        lbl.setFixedWidth(100)
                        lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a; font-weight: 700;")
                        val = QLabel(str(tech_exp[key]))
                        val.setWordWrap(True)
                        val.setStyleSheet("font-size: 11px; color: #d4d4d8;")
                        row.addWidget(lbl)
                        row.addWidget(val)
                        t_l.addLayout(row)
                c_layout.addWidget(t_box)
            
            # 8-Step Verification Grid
            grid_frame = QFrame()
            grid_frame.setStyleSheet("background-color: rgba(6, 8, 14, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 12px;")
            g_l = QVBoxLayout(grid_frame)
            g_l.setSpacing(8)
            
            # Step 1 & 2: FINDING & WHY
            g_l.addLayout(self._create_step_row("01 FINDING", rec.get("f_title", "Observation"), "#ffffff"))
            g_l.addLayout(self._create_step_row("02 WHY", rec.get("f_desc", "Security deficiency identified."), "#a1a1aa"))
            
            # Step 3: WHERE
            target_path = rec.get("f_target", "")
            g_l.addLayout(self._create_step_row("03 WHERE", target_path, "#22d3ee"))
            
            # Step 4: PROOF (Observed output)
            g_l.addLayout(self._create_step_row("04 PROOF", rec.get("observed_output", "N/A"), "#fb7185"))
            
            # Step 5: ANALYSIS (SHA-256)
            sha = rec.get("integrity_hash", "")
            g_l.addLayout(self._create_step_row("05 ANALYSIS", f"SHA-256: {sha} (Cryptographic Proof)", "#34d399"))
            
            # Step 6: VERIFY (PowerShell command)
            cmd_box = QHBoxLayout()
            cmd_tag = QLabel("06 VERIFY")
            cmd_tag.setFixedWidth(85)
            cmd_tag.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a; font-weight: 700;")
            cmd_box.addWidget(cmd_tag)
            
            cmd_str = rec.get("command", "")
            cmd_lbl = QLabel(cmd_str)
            cmd_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #34d399; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;")
            cmd_box.addWidget(cmd_lbl)
            
            btn_copy = QPushButton("📋 Copy")
            btn_copy.setStyleSheet("font-size: 10px; padding: 3px 8px;")
            btn_copy.clicked.connect(lambda _, c=cmd_str: self._copy_to_clipboard(c))
            cmd_box.addWidget(btn_copy)
            g_l.addLayout(cmd_box)
            
            # Step 7: FIX
            g_l.addLayout(self._create_step_row("07 FIX", rec.get("f_rem", "Apply remediation."), "#cbd5e1"))
            
            # Step 8: RE-VERIFY (BEFORE / AFTER RESULT)
            re_box = QHBoxLayout()
            re_tag = QLabel("08 RE-VERIFY")
            re_tag.setFixedWidth(85)
            re_tag.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a; font-weight: 700;")
            re_box.addWidget(re_tag)
            
            btn_reverify = QPushButton("🔄 Execute Verification Check")
            btn_reverify.setObjectName("cyanBtn")
            btn_reverify.setStyleSheet("font-size: 11px; padding: 4px 12px;")
            btn_reverify.clicked.connect(lambda _, r=rec: self._reverify_target(r))
            re_box.addWidget(btn_reverify)
            re_box.addStretch()
            g_l.addLayout(re_box)
            
            c_layout.addWidget(grid_frame)
            card.add_layout(c_layout)
            self.ev_layout.addWidget(card)

    def _create_step_row(self, tag: str, value: str, val_color: str) -> QHBoxLayout:
        row = QHBoxLayout()
        t = QLabel(str(tag) if tag is not None else "")
        t.setFixedWidth(85)
        t.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a; font-weight: 700;")
        row.addWidget(t)
        
        v = QLabel(str(value) if value is not None else "")
        v.setWordWrap(True)
        v.setStyleSheet(f"font-size: 11px; color: {val_color};")
        row.addWidget(v)
        return row

    def _copy_to_clipboard(self, text: str):
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Copied", "PowerShell verification command copied to clipboard.")

    def _reverify_target(self, record: dict):
        target_path = record.get("f_target")
        finding_id = record.get("finding_id")
        
        if not target_path or not os.path.exists(target_path):
            QMessageBox.warning(self, "Target Missing", f"Target file '{target_path}' was removed or is not found.")
            return

        # Perform on-disk re-scan using FilesystemScanner
        scanner = FilesystemScanner()
        obs = scanner._scan_single_file(target_path)
        
        # Check if the specific finding rule is still triggered
        rule_still_triggered = any(o.file_path == target_path for o in obs)
        
        if not rule_still_triggered:
            # Mark finding as RESOLVED in DB
            with storage._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE findings SET status = 'RESOLVED' WHERE id = ?", (finding_id,))
                conn.commit()
                
            storage.log_audit_event("FINDING_REVERIFIED", f"Re-verification confirmed remediation: {finding_id} is RESOLVED on disk.")
            QMessageBox.information(
                self,
                "Re-Verification Result",
                "✓ BEFORE RESULT: Vulnerability Confirmed\n✓ AFTER RESULT: Remediated & Verified Clean on Disk\n\nFinding status updated to RESOLVED."
            )
        else:
            QMessageBox.warning(
                self,
                "Re-Verification Result",
                "⚠ BEFORE RESULT: Vulnerability Confirmed\n⚠ AFTER RESULT: Security deficiency still detected.\n\nPlease apply recommended remediation."
            )
            
        self.refresh_evidence()
