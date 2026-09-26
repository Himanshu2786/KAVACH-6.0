"""
KAVACH 6.0 Desktop - Landing & Loading Screen.
Simulates module boot sequence, checks local Ollama engine, and presents the responsive Ollama Offline Dialog.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal
from services.ollama_service import ollama_service
from widgets.glass_card import GlassCard

class LandingScreen(QWidget):
    # Signals to parent MainWindow
    boot_completed = Signal()
    open_system_status = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.step = 0
        self.modules = [
            ("Interface Engine", "READY"),
            ("Assessment Engine", "READY"),
            ("Knowledge Engine", "READY"),
            ("Evidence Engine", "READY"),
            ("AI Engine", "INITIALIZING"),
            ("Ollama Connection", "CHECKING")
        ]
        self._init_ui()
        self._start_boot_sequence()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Center container
        self.card = QFrame(self)
        self.card.setFixedWidth(460)
        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 12, 18, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)
        
        # Brand Header
        header_layout = QHBoxLayout()
        logo = QLabel("🛡️")
        logo.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(logo)
        
        brand = QLabel("KAVACH")
        brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        header_layout.addWidget(brand)
        
        ver_badge = QLabel("5.0")
        ver_badge.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.08);
            color: #a1a1aa;
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 4px;
            padding: 2px 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
        """)
        header_layout.addWidget(ver_badge)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Title
        sub_title = QLabel("Sovereign Security Intelligence Platform")
        sub_title.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        card_layout.addWidget(sub_title)
        
        # Module checklist
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)
        self.module_labels = {}
        
        for name, _ in self.modules:
            row = QHBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 12px; color: #d4d4d8;")
            row.addWidget(lbl_name)
            row.addStretch()
            
            lbl_status = QLabel("PENDING")
            lbl_status.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a;")
            row.addWidget(lbl_status)
            self.module_labels[name] = lbl_status
            self.list_layout.addLayout(row)
            
        card_layout.addLayout(self.list_layout)
        
        # Progress Bar
        self.prog = QProgressBar()
        self.prog.setFixedHeight(4)
        self.prog.setTextVisible(False)
        self.prog.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #06b6d4;
                border-radius: 2px;
            }
        """)
        card_layout.addWidget(self.prog)
        
        # Failsafe Panel (Ollama Offline Dialog)
        self.failsafe_panel = QFrame()
        self.failsafe_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(251, 191, 36, 0.05);
                border: 1px solid rgba(251, 191, 36, 0.25);
                border-radius: 8px;
            }
        """)
        self.failsafe_layout = QVBoxLayout(self.failsafe_panel)
        self.failsafe_layout.setContentsMargins(14, 14, 14, 14)
        self.failsafe_layout.setSpacing(10)
        
        warn_header = QLabel("⚠️ OLLAMA OFFLINE — RULE-BASED ENGINE ACTIVE")
        warn_header.setStyleSheet("color: #fbbf24; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700;")
        self.failsafe_layout.addWidget(warn_header)
        
        warn_desc = QLabel("Local Ollama service was not detected at port 11434. KAVACH will operate using deterministic rule-based security intelligence.")
        warn_desc.setWordWrap(True)
        warn_desc.setStyleSheet("color: #d4d4d8; font-size: 11px; line-height: 1.3;")
        self.failsafe_layout.addWidget(warn_desc)
        
        # Action Buttons: [ Continue — Demo Mode ] [ System Status ] [ Retry ]
        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(8)
        
        self.btn_continue = QPushButton("▶ Continue — Demo Mode")
        self.btn_continue.setObjectName("primaryBtn")
        self.btn_continue.clicked.connect(self._handle_continue)
        self.btn_row.addWidget(self.btn_continue)
        
        self.btn_status = QPushButton("📊 System Status")
        self.btn_status.clicked.connect(self._handle_status)
        self.btn_row.addWidget(self.btn_status)
        
        self.btn_retry = QPushButton("🔄 Retry")
        self.btn_retry.clicked.connect(self._handle_retry)
        self.btn_row.addWidget(self.btn_retry)
        
        self.failsafe_layout.addLayout(self.btn_row)
        self.failsafe_panel.setVisible(False)
        card_layout.addWidget(self.failsafe_panel)
        
        main_layout.addWidget(self.card)

    def _start_boot_sequence(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_boot_step)
        self.timer.start(350)

    def _on_boot_step(self):
        self.step += 1
        pct = min(100, int((self.step / 6) * 100))
        self.prog.setValue(pct)
        
        if self.step <= len(self.modules) - 1:
            name, _ = self.modules[self.step - 1]
            lbl = self.module_labels.get(name)
            if lbl:
                lbl.setText("READY")
                lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #34d399; font-weight: 700;")
        elif self.step >= len(self.modules):
            self.timer.stop()
            # Check Ollama
            status = ollama_service.check_status()
            lbl = self.module_labels.get("Ollama Connection")
            if status["status"] == "online":
                if lbl:
                    lbl.setText("ONLINE")
                    lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #34d399; font-weight: 700;")
                QTimer.singleShot(600, self.boot_completed.emit)
            else:
                if lbl:
                    lbl.setText("OFFLINE")
                    lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #fbbf24; font-weight: 700;")
                self.failsafe_panel.setVisible(True)

    def _handle_continue(self):
        self.boot_completed.emit()

    def _handle_status(self):
        self.boot_completed.emit()
        self.open_system_status.emit()

    def _handle_retry(self):
        self.failsafe_panel.setVisible(False)
        self.step = 0
        self._start_boot_sequence()
