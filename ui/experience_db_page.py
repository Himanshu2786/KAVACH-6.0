"""
KAVACH 6.0 Desktop - Experience DB Page.
False positive lessons memory ledger & suppression signature manager.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from services.storage_service import storage
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class ExperienceDbPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.refresh_items()

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
        h1 = QLabel("🧠 Experience DB — False Positive Memory")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Institutional memory for verified false positives, boundary exclusions, and custom suppression rules.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_items)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # Add new entry card
        add_card = GlassCard(title="Commit False-Positive Lesson", subtitle="Document boundary justifications to suppress repeat alerts", glow="purple")
        form_l = QVBoxLayout()
        form_l.setSpacing(8)
        
        self.input_fnd = QLineEdit()
        self.input_fnd.setPlaceholderText("Target Finding ID (e.g. FND-HSTS-001)...")
        form_l.addWidget(self.input_fnd)
        
        self.input_rationale = QTextEdit()
        self.input_rationale.setPlaceholderText("Explain technical disproof rationale & boundary justification...")
        self.input_rationale.setFixedHeight(70)
        form_l.addWidget(self.input_rationale)
        
        btn_commit = QPushButton("💾 Commit to Experience Memory")
        btn_commit.setObjectName("primaryBtn")
        btn_commit.clicked.connect(self._handle_commit)
        form_l.addWidget(btn_commit)
        
        add_card.add_layout(form_l)
        layout.addWidget(add_card)
        
        # List of items
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(10)
        
        self.items_container = QWidget()
        self.items_container.setLayout(self.items_layout)
        layout.addWidget(self.items_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh_items(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        items = storage.get_experience_items()
        if not items:
            empty = QLabel("No false positive suppressions recorded in Experience DB.")
            empty.setStyleSheet("color: #71717a; font-size: 12px; padding: 16px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_layout.addWidget(empty)
            return

        for exp in items:
            card = GlassCard()
            c_l = QVBoxLayout()
            c_l.setSpacing(6)
            
            top_line = QHBoxLayout()
            top_line.addWidget(StatusBadge(exp.get("status", "ACTIVE"), "ONLINE"))
            top_line.addWidget(StatusBadge(exp.get("finding_id", "FINDING"), "INFO"))
            top_line.addStretch()
            
            time_lbl = QLabel(exp.get("created_at", ""))
            time_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #52525b;")
            top_line.addWidget(time_lbl)
            c_l.addLayout(top_line)
            
            rat = QLabel(exp.get("rationale", ""))
            rat.setWordWrap(True)
            rat.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.3;")
            c_l.addWidget(rat)
            
            card.add_layout(c_l)
            self.items_layout.addWidget(card)

    def _handle_commit(self):
        fnd_id = self.input_fnd.text().strip()
        rat = self.input_rationale.toPlainText().strip()
        if not fnd_id or not rat:
            QMessageBox.warning(self, "Incomplete Entry", "Please provide both Finding ID and Rationale.")
            return
            
        storage.add_experience_item(fnd_id, rat)
        self.input_fnd.clear()
        self.input_rationale.clear()
        self.refresh_items()
        QMessageBox.information(self, "Committed", f"Lesson recorded for {fnd_id}.")
