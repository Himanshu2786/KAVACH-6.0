"""
KAVACH 6.0 Desktop - Authorization Verification Modal Dialog.
Ensures legal compliance and explicit authorization confirmation before target assessments.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt

class AuthorizationDialog(QDialog):
    def __init__(self, target_url: str, parent=None):
        super().__init__(parent)
        self.target_url = target_url
        self.setWindowTitle("Authorization Required — KAVACH 6.0")
        self.setFixedSize(500, 360)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Glass frame container
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 12, 18, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Header
        header = QLabel("🔒 AUTHORIZATION REQUIRED")
        header.setStyleSheet("font-size: 15px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;")
        layout.addWidget(header)
        
        sub = QLabel("Legal Compliance & Scope Verification")
        sub.setStyleSheet("font-size: 11px; color: #a1a1aa;")
        layout.addWidget(sub)
        
        # Target pill
        target_label = QLabel(f"Target: {self.target_url}")
        target_label.setStyleSheet("""
            background-color: rgba(6, 182, 212, 0.10);
            color: #22d3ee;
            border: 1px solid rgba(6, 182, 212, 0.25);
            border-radius: 6px;
            padding: 6px 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
        """)
        layout.addWidget(target_label)
        
        desc = QLabel(
            "KAVACH performs authorized technical security assessments using non-destructive empirical probing. "
            "To adhere to cybersecurity legal frameworks, confirm your testing authority below:"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11px; color: #d4d4d8; line-height: 1.4;")
        layout.addWidget(desc)
        
        # Checkboxes
        self.cb_owner = QCheckBox("I own this application OR have explicit authorization from its owner.")
        self.cb_owner.setStyleSheet("color: #e4e4e7; font-size: 11px;")
        self.cb_owner.stateChanged.connect(self._check_validity)
        layout.addWidget(self.cb_owner)
        
        self.cb_scope = QCheckBox("I agree to assess only authorized assets within agreed boundaries.")
        self.cb_scope.setStyleSheet("color: #e4e4e7; font-size: 11px;")
        self.cb_scope.stateChanged.connect(self._check_validity)
        layout.addWidget(self.cb_scope)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_confirm = QPushButton("CONFIRM & SCAN →")
        self.btn_confirm.setObjectName("primaryBtn")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_confirm)
        
        layout.addLayout(btn_layout)
        outer_layout.addWidget(frame)

    def _check_validity(self):
        can_proceed = self.cb_owner.isChecked() and self.cb_scope.isChecked()
        self.btn_confirm.setEnabled(can_proceed)
