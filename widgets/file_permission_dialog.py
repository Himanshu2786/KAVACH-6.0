"""
KAVACH 6.0 Desktop - File & Folder Permission Dialog.
Performs pre-flight permission checks and collects explicit operator scope consent.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt

class FilePermissionDialog(QDialog):
    def __init__(self, target_path: str, parent=None):
        super().__init__(parent)
        self.target_path = os.path.abspath(target_path)
        self.is_dir = os.path.isdir(self.target_path)
        self.setWindowTitle("Pre-Scan Permission & Scope Check — KAVACH 6.0")
        self.setFixedSize(540, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 12, 18, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
        
        # Header
        h_box = QHBoxLayout()
        icon = QLabel("🛡️")
        icon.setStyleSheet("font-size: 18px;")
        h_box.addWidget(icon)
        
        h_text = QVBoxLayout()
        title = QLabel("PERMISSION & SCOPE VERIFICATION")
        title.setStyleSheet("font-size: 14px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;")
        h_text.addWidget(title)
        
        sub = QLabel("Least-Privilege Pre-Flight Inspection")
        sub.setStyleSheet("font-size: 11px; color: #a1a1aa;")
        h_text.addWidget(sub)
        h_box.addLayout(h_text)
        h_box.addStretch()
        layout.addLayout(h_box)
        
        # Target Box
        t_box = QFrame()
        t_box.setStyleSheet("background-color: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.22); border-radius: 6px; padding: 6px;")
        t_layout = QVBoxLayout(t_box)
        t_layout.setContentsMargins(8, 6, 8, 6)
        
        t_type = "DIRECTORY / FOLDER" if self.is_dir else "SINGLE FILE"
        type_lbl = QLabel(f"TARGET TYPE: {t_type}")
        type_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #22d3ee; font-weight: 700;")
        t_layout.addWidget(type_lbl)
        
        path_lbl = QLabel(self.target_path)
        path_lbl.setWordWrap(True)
        path_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ffffff;")
        t_layout.addWidget(path_lbl)
        layout.addWidget(t_box)
        
        # Access Verification status
        has_read = os.access(self.target_path, os.R_OK)
        status_lbl = QLabel(f"✓ READ PERMISSION: {'AVAILABLE' if has_read else 'DENIED'}")
        status_color = "#34d399" if has_read else "#f43f5e"
        status_lbl.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {status_color}; font-weight: 700;")
        layout.addWidget(status_lbl)
        
        # Guarantees Box
        g_box = QFrame()
        g_box.setStyleSheet("background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; padding: 6px;")
        g_layout = QVBoxLayout(g_box)
        g_layout.setContentsMargins(8, 6, 8, 6)
        
        g_text = QLabel(
            "KAVACH Non-Destructive Scanning Guarantees:\n"
            "• Static analysis only — files and scripts will NOT be executed.\n"
            "• Files will NOT be modified, encrypted, or deleted.\n"
            "• Scanned contents remain strictly local on your machine."
        )
        g_text.setStyleSheet("font-size: 11px; color: #a1a1aa; line-height: 1.4;")
        g_layout.addWidget(g_text)
        layout.addWidget(g_box)
        
        # Options if directory
        self.cb_symlinks = QCheckBox("Follow Symbolic Links (Default: NO — Prevents loop escalation)")
        self.cb_symlinks.setChecked(False)
        self.cb_symlinks.setStyleSheet("color: #d4d4d8; font-size: 11px;")
        if self.is_dir:
            layout.addWidget(self.cb_symlinks)
            
        layout.addStretch()
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()
        
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        
        self.btn_confirm = QPushButton("START DEFENSIVE SCAN →")
        self.btn_confirm.setObjectName("cyanBtn")
        self.btn_confirm.setEnabled(has_read)
        self.btn_confirm.clicked.connect(self.accept)
        btn_row.addWidget(self.btn_confirm)
        
        layout.addLayout(btn_row)
        outer_layout.addWidget(frame)

    def should_follow_symlinks(self) -> bool:
        return self.cb_symlinks.isChecked() if self.is_dir else False
