"""
KAVACH 6.0 Desktop - Technical Terminal Verification Dialog.
Displays reproducible PowerShell commands, expected vs observed results, and SHA-256 hash.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QScrollArea, QApplication
)
from PySide6.QtCore import Qt
from typing import Dict, Any

class TerminalViewerDialog(QDialog):
    def __init__(self, evidence_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.evidence_data = evidence_data
        self.setWindowTitle(f"Technical Verification — {evidence_data.get('id', 'Evidence')}")
        self.resize(750, 560)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        # Header
        header_layout = QHBoxLayout()
        icon = QLabel("💻")
        icon.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(icon)
        
        title_box = QVBoxLayout()
        title = QLabel(f"TECHNICAL VERIFICATION — {self.evidence_data.get('id', '')}")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff;")
        title_box.addWidget(title)
        
        sub = QLabel("Direct empirical verification & reproducible PowerShell procedure")
        sub.setStyleSheet("font-size: 11px; color: #a1a1aa;")
        title_box.addWidget(sub)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Command box with Copy Button
        cmd_frame = QFrame()
        cmd_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(6, 8, 14, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
            }
        """)
        cmd_layout = QVBoxLayout(cmd_frame)
        cmd_layout.setContentsMargins(12, 10, 12, 10)
        
        cmd_top = QHBoxLayout()
        cmd_label = QLabel("POWERSHELL VERIFICATION COMMAND")
        cmd_label.setStyleSheet("font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #a1a1aa; font-weight: 700;")
        cmd_top.addWidget(cmd_label)
        cmd_top.addStretch()
        
        self.btn_copy = QPushButton("📋 COPY COMMAND")
        self.btn_copy.setObjectName("cyanBtn")
        self.btn_copy.setStyleSheet("font-size: 10px; padding: 4px 10px;")
        self.btn_copy.clicked.connect(self._copy_command)
        cmd_top.addWidget(self.btn_copy)
        cmd_layout.addLayout(cmd_top)
        
        command_str = self.evidence_data.get("command", "# No command available")
        cmd_text = QLabel(command_str)
        cmd_text.setWordWrap(True)
        cmd_text.setStyleSheet("font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; color: #34d399; padding: 4px 0;")
        cmd_layout.addWidget(cmd_text)
        layout.addWidget(cmd_frame)
        
        # Comparison: Expected vs Observed
        comp_layout = QHBoxLayout()
        comp_layout.setSpacing(12)
        
        # Expected
        exp_box = QFrame()
        exp_box.setStyleSheet("background-color: rgba(13, 15, 23, 0.6); border: 1px solid rgba(52, 211, 153, 0.25); border-radius: 8px;")
        exp_layout = QVBoxLayout(exp_box)
        exp_layout.addWidget(QLabel("EXPECTED RESULT (BASELINE)"))
        exp_val = QLabel(self.evidence_data.get("expected_output", "N/A"))
        exp_val.setWordWrap(True)
        exp_val.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #cbd5e1;")
        exp_layout.addWidget(exp_val)
        comp_layout.addWidget(exp_box)
        
        # Observed
        obs_box = QFrame()
        obs_box.setStyleSheet("background-color: rgba(13, 15, 23, 0.6); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 8px;")
        obs_layout = QVBoxLayout(obs_box)
        obs_layout.addWidget(QLabel("OBSERVED RESULT (KAVACH PROBE)"))
        obs_val = QLabel(self.evidence_data.get("observed_output", "N/A"))
        obs_val.setWordWrap(True)
        obs_val.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #fca5a5;")
        obs_layout.addWidget(obs_val)
        comp_layout.addWidget(obs_box)
        
        layout.addLayout(comp_layout)
        
        # SHA-256 Footer
        hash_val = self.evidence_data.get("integrity_hash", "UNVERIFIED")
        hash_label = QLabel(f"SHA-256 INTEGRITY HASH: {hash_val}")
        hash_label.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a; padding: 4px;")
        layout.addWidget(hash_label)
        
        # Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

    def _copy_command(self):
        cmd = self.evidence_data.get("command", "")
        if cmd:
            clipboard = QApplication.clipboard()
            clipboard.setText(cmd)
            self.btn_copy.setText("✓ COPIED!")
