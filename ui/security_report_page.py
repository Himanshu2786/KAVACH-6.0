"""
KAVACH 6.0 Desktop - Executive Security Report Page.
Compiles executive audit dossier, exportable JSON, and formatted printable summary.
"""

import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from services.storage_service import storage
from widgets.glass_card import GlassCard

class SecurityReportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.generate_report()

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
        h1 = QLabel("📄 Executive Security Intelligence Report")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Formal assessment audit dossier with cryptographic technical evidence and prioritized remediation.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_export_forensic = QPushButton("📦 Forensic Package (JSON)")
        self.btn_export_forensic.clicked.connect(self._export_forensic_package)
        top_row.addWidget(self.btn_export_forensic)

        self.btn_export_html = QPushButton("📄 HTML Forensic Dossier")
        self.btn_export_html.clicked.connect(self._export_html_dossier)
        top_row.addWidget(self.btn_export_html)
        
        self.btn_refresh = QPushButton("🔄 Refresh Report")
        self.btn_refresh.setObjectName("cyanBtn")
        self.btn_refresh.clicked.connect(self.generate_report)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # Report Document Card
        report_card = GlassCard(title="KAVACH Posture Audit Dossier", subtitle="Sovereign Tamper-Evident Report", glow="cyan")
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setStyleSheet("font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; background: rgba(6,8,14,0.9); color: #e4e4e7; line-height: 1.4;")
        self.report_text.setFixedHeight(450)
        report_card.add_widget(self.report_text)
        
        layout.addWidget(report_card)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def generate_report(self):
        findings = storage.get_all_findings()
        assessments = storage.get_all_assessments()
        events = storage.get_audit_events(limit=10)
        
        doc = [
            "================================================================================",
            "                        KAVACH 6.0 SECURITY AUDIT REPORT                        ",
            "                  Sovereign Empirical Assessment Intelligence                   ",
            "================================================================================",
            f"Generated: {assessments[0].get('created_at', 'N/A') if assessments else 'N/A'}",
            f"Total Assessments Run: {len(assessments)}",
            f"Active Findings Count: {len(findings)}",
            "--------------------------------------------------------------------------------",
            "\n[1. EXECUTIVE SUMMARY]",
            f"KAVACH completed technical security analysis across target assets.",
            f"Identified {len(findings)} empirical findings requiring remediation.",
            "\n[2. DETAILED FINDINGS CATALOG]"
        ]
        
        for i, f in enumerate(findings, 1):
            doc.append(f"\n[{i}] {f.get('title')}")
            doc.append(f"    Severity:   {f.get('severity')}")
            doc.append(f"    Component:  {f.get('affected_component')}")
            doc.append(f"    CWE / OWASP:{f.get('cwe_id', 'N/A')} | {f.get('owasp_id', 'N/A')}")
            doc.append(f"    Description:{f.get('description')}")
            doc.append(f"    Remediation:{f.get('remediation')}")
            doc.append(f"    Evidence ID:{f.get('evidence_id', 'N/A')}")
            
        doc.append("\n--------------------------------------------------------------------------------")
        doc.append("[3. TAMPER-EVIDENT AUDIT TRAIL HEAD]")
        for ev in events[:5]:
            doc.append(f"  • {ev.get('timestamp')} | {ev.get('event_type')} | {ev.get('action')}")
            
        doc.append("\n================================================================================")
        doc.append("                             END OF DOSSIER                                     ")
        doc.append("================================================================================")
        
        self.report_text.setText("\n".join(doc))

    def _export_forensic_package(self):
        from backend.app.services.forensic_export_service import forensic_export_service
        assessments = storage.get_all_assessments()
        asm_id = assessments[0]["id"] if assessments else "GLOBAL"

        path, _ = QFileDialog.getSaveFileName(self, "Export Forensic Reproducibility Package", f"kavach_forensic_package_{asm_id}.json", "JSON Files (*.json)")
        if path:
            try:
                forensic_export_service.export_json(assessment_id=asm_id, output_path=path, actor="Desktop Operator")
                QMessageBox.information(self, "Export Successful", f"Tamper-evident forensic package saved with SHA-256 manifest to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def _export_html_dossier(self):
        from backend.app.services.forensic_export_service import forensic_export_service
        assessments = storage.get_all_assessments()
        asm_id = assessments[0]["id"] if assessments else "GLOBAL"

        path, _ = QFileDialog.getSaveFileName(self, "Export HTML Forensic Dossier", f"kavach_forensic_dossier_{asm_id}.html", "HTML Files (*.html)")
        if path:
            try:
                forensic_export_service.export_html(assessment_id=asm_id, output_path=path, actor="Desktop Operator")
                QMessageBox.information(self, "Export Successful", f"Printable HTML forensic dossier generated successfully at:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))
