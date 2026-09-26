"""
KAVACH 6.0 Desktop - Team Desk Collaboration & Triage Page.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QTextEdit, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from services.storage_service import storage
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class TeamDeskPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.refresh_desk()

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
        h1 = QLabel("👥 Team Desk — Collaboration & SecOps Triage")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Air-gapped on-premise collaboration notes, finding triage status, and audit log integration.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_desk)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # Add Note Card
        add_card = GlassCard("Append SecOps Audit Note", "Log triage actions and team reproduction notes", "📝")
        f_l = QVBoxLayout()
        f_l.setSpacing(8)
        
        self.input_fnd = QLineEdit()
        self.input_fnd.setPlaceholderText("Finding ID or Component Reference...")
        f_l.addWidget(self.input_fnd)
        
        self.input_note = QTextEdit()
        self.input_note.setPlaceholderText("Enter investigation notes, reproduction timestamps, or patch review notes...")
        self.input_note.setFixedHeight(70)
        f_l.addWidget(self.input_note)
        
        btn_save = QPushButton("💾 Log Investigation Note")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_note)
        f_l.addWidget(btn_save)
        
        add_card.add_layout(f_l)
        layout.addWidget(add_card)
        
        # Notes List
        self.notes_layout = QVBoxLayout()
        self.notes_layout.setSpacing(10)
        
        self.notes_container = QWidget()
        self.notes_container.setLayout(self.notes_layout)
        layout.addWidget(self.notes_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh_desk(self):
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        events = [e for e in storage.get_audit_events(limit=20) if e.get("event_type") == "TEAM_NOTE"]
        if not events:
            empty = QLabel("No team triage notes logged yet.")
            empty.setStyleSheet("color: #71717a; font-size: 12px; padding: 16px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notes_layout.addWidget(empty)
            return

        for ev in events:
            card = GlassCard()
            c_l = QVBoxLayout()
            c_l.setSpacing(6)
            
            top_line = QHBoxLayout()
            top_line.addWidget(StatusBadge("SECOPS NOTE", "INFO"))
            top_line.addWidget(StatusBadge(ev.get("actor", "OPERATOR"), "READY"))
            top_line.addStretch()
            
            time_lbl = QLabel(ev.get("timestamp", ""))
            time_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a;")
            top_line.addWidget(time_lbl)
            c_l.addLayout(top_line)
            
            act = QLabel(ev.get("action", ""))
            act.setWordWrap(True)
            act.setStyleSheet("font-size: 12px; color: #d4d4d8;")
            c_l.addWidget(act)
            
            card.add_layout(c_l)
            self.notes_layout.addWidget(card)

    def _save_note(self):
        fnd = self.input_fnd.text().strip()
        note = self.input_note.toPlainText().strip()
        if not fnd or not note:
            QMessageBox.warning(self, "Incomplete", "Please specify Finding ID and Note content.")
            return
            
        storage.log_audit_event("TEAM_NOTE", f"[{fnd}] {note}", actor="Operator", details={"finding_id": fnd, "note": note})
        self.input_fnd.clear()
        self.input_note.clear()
        self.refresh_desk()
        QMessageBox.information(self, "Saved", "Investigation note logged in audit trail.")
