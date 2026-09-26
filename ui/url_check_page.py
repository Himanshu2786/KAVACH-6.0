"""
KAVACH 6.0 Desktop - URL Security Check Page.
Target configuration, authorization guard modal, and live empirical scan runner.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from core.assessment_engine import assessment_engine
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge
from widgets.authorization_dialog import AuthorizationDialog

class ScanWorker(QThread):
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, target_url: str):
        super().__init__()
        self.target_url = target_url

    def run(self):
        try:
            res = assessment_engine.run_url_assessment(self.target_url)
            self.finished.emit(res)
        except Exception as e:
            self.failed.emit(str(e))

class UrlCheckPage(QWidget):
    assessment_done = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        h_layout = QVBoxLayout()
        h1 = QLabel("🌐 URL Security Assessment")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Perform non-destructive empirical analysis on authorized web endpoints.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        layout.addLayout(h_layout)
        
        # Target Input Card
        input_card = GlassCard(title="Target Configuration", subtitle="Enter target domain or fully qualified URL", glow="cyan")
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        
        url_row = QHBoxLayout()
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://example.com or target domain...")
        self.input_url.setText("https://example.com")
        self.input_url.setFixedHeight(38)
        url_row.addWidget(self.input_url)
        
        self.btn_scan = QPushButton("🚀 Run Assessment")
        self.btn_scan.setObjectName("cyanBtn")
        self.btn_scan.setFixedHeight(38)
        self.btn_scan.clicked.connect(self._on_start_scan)
        url_row.addWidget(self.btn_scan)
        form_layout.addLayout(url_row)
        
        # Presets Row
        preset_row = QHBoxLayout()
        preset_lbl = QLabel("Quick Presets:")
        preset_lbl.setStyleSheet("color: #71717a; font-size: 11px;")
        preset_row.addWidget(preset_lbl)
        
        for preset in ["https://example.com", "https://httpbin.org", "https://owasp.org"]:
            btn_p = QPushButton(preset)
            btn_p.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_p.clicked.connect(lambda _, p=preset: self.input_url.setText(p))
            preset_row.addWidget(btn_p)
        preset_row.addStretch()
        form_layout.addLayout(preset_row)
        
        # Progress indicator
        self.prog = QProgressBar()
        self.prog.setFixedHeight(4)
        self.prog.setRange(0, 0)
        self.prog.setTextVisible(False)
        self.prog.setVisible(False)
        form_layout.addWidget(self.prog)
        
        input_card.add_layout(form_layout)
        layout.addWidget(input_card)
        
        # Scope Notice
        scope_card = GlassCard("Assessment Scope & Guardrails", "Non-Destructive Empirical Probes", "🛡️")
        s_text = QLabel(
            "• HTTP Headers & Cryptographic Transport Check (HSTS, TLS version)\n"
            "• Content-Security-Policy & Client-Side Defense Analysis\n"
            "• Anti-Clickjacking & MIME-sniffing Protection Verifications\n"
            "• SHA-256 Verifiable Evidence & PowerShell Reproducible Procedure Generation"
        )
        s_text.setStyleSheet("font-size: 12px; color: #a1a1aa; line-height: 1.6;")
        scope_card.add_widget(s_text)
        layout.addWidget(scope_card)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_start_scan(self):
        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please provide a valid target URL.")
            return

        # Show Authorization confirmation dialog
        auth_dlg = AuthorizationDialog(url, self)
        if auth_dlg.exec() != AuthorizationDialog.DialogCode.Accepted:
            return

        self.btn_scan.setEnabled(False)
        self.prog.setVisible(True)
        
        self.worker = ScanWorker(url)
        self.worker.finished.connect(self._on_scan_success)
        self.worker.failed.connect(self._on_scan_failed)
        self.worker.start()

    def _on_scan_success(self, res: dict):
        self.btn_scan.setEnabled(True)
        self.prog.setVisible(False)
        asm = res.get("assessment", {})
        findings_count = len(res.get("findings", []))
        QMessageBox.information(
            self,
            "Assessment Completed",
            f"Successfully assessed {asm.get('target_url')}.\nIdentified {findings_count} findings."
        )
        self.assessment_done.emit(asm.get("id", ""))

    def _on_scan_failed(self, err: str):
        self.btn_scan.setEnabled(True)
        self.prog.setVisible(False)
        QMessageBox.critical(self, "Assessment Failed", f"Error during assessment: {err}")
