"""
KAVACH 6.0 Desktop - Local Posture Assessment Page.
Audit endpoint configuration, detect hardcoded secret keys in training samples, and generate PowerShell proofs.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from core.assessment_engine import assessment_engine
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class LocalScanWorker(QThread):
    finished = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            res = assessment_engine.run_local_posture_scan()
            self.finished.emit(res)
        except Exception as e:
            self.failed.emit(str(e))

class LocalPosturePage(QWidget):
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
        h1 = QLabel("💻 Local Host Posture Audit")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Scan local endpoint for exposed plaintext credentials, configuration flaws, and security fixtures.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        layout.addLayout(h_layout)
        
        # Trigger Card
        card = GlassCard(title="Endpoint Inspection Engine", subtitle="Deterministic credential & permission analyzer", glow="cyan")
        
        c_layout = QVBoxLayout()
        c_layout.setSpacing(12)
        
        info = QLabel(
            "The Local Posture scanner inspects bundled training samples and configuration files for unencrypted secrets, "
            "evaluating exposure against OWASP Top 10 A07 (Identification & Authentication Failures)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #a1a1aa; font-size: 12px; line-height: 1.4;")
        c_layout.addWidget(info)
        
        self.btn_run = QPushButton("⚡ Execute Local Posture Audit")
        self.btn_run.setObjectName("cyanBtn")
        self.btn_run.setFixedHeight(38)
        self.btn_run.clicked.connect(self._run_audit)
        c_layout.addWidget(self.btn_run)
        
        self.prog = QProgressBar()
        self.prog.setFixedHeight(4)
        self.prog.setRange(0, 0)
        self.prog.setTextVisible(False)
        self.prog.setVisible(False)
        c_layout.addWidget(self.prog)
        
        card.add_layout(c_layout)
        layout.addWidget(card)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _run_audit(self):
        self.btn_run.setEnabled(False)
        self.prog.setVisible(True)
        
        self.worker = LocalScanWorker()
        self.worker.finished.connect(self._on_success)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_success(self, res: dict):
        self.btn_run.setEnabled(True)
        self.prog.setVisible(False)
        findings_count = len(res.get("findings", []))
        QMessageBox.information(
            self,
            "Audit Complete",
            f"Local posture audit complete. Identified {findings_count} findings.\nNavigate to Findings or Evidence tab to inspect."
        )
        self.assessment_done.emit(res.get("assessment", {}).get("id", ""))

    def _on_failed(self, err: str):
        self.btn_run.setEnabled(True)
        self.prog.setVisible(False)
        QMessageBox.critical(self, "Audit Failed", f"Local scan failed: {err}")
