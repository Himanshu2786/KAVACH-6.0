"""
KAVACH 6.0 Desktop - Assessment History Page.
Chronological log of past target scans and historical posture snapshots.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from services.storage_service import storage
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class HistoryPage(QWidget):
    view_findings_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.refresh_history()

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
        h1 = QLabel("🕒 Assessment History & Historical Trends")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Review past assessment executions, target endpoints, and posture summaries.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_history)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        self.history_layout = QVBoxLayout()
        self.history_layout.setSpacing(10)
        
        self.history_container = QWidget()
        self.history_container.setLayout(self.history_layout)
        layout.addWidget(self.history_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh_history(self):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        runs = storage.get_all_assessments()
        if not runs:
            empty = QLabel("No historical assessment runs found. Execute a URL check to record an assessment.")
            empty.setStyleSheet("color: #71717a; font-size: 12px; padding: 16px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_layout.addWidget(empty)
            return

        for run in runs:
            card = GlassCard()
            c_l = QVBoxLayout()
            c_l.setSpacing(6)
            
            top_line = QHBoxLayout()
            top_line.addWidget(StatusBadge(run.get("status", "COMPLETED"), "READY"))
            top_line.addWidget(StatusBadge(run.get("mode", "AUTOMATED"), "INFO"))
            top_line.addStretch()
            
            time_lbl = QLabel(run.get("created_at", ""))
            time_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a;")
            top_line.addWidget(time_lbl)
            c_l.addLayout(top_line)
            
            target = QLabel(f"Target: {run.get('target_url', '')}")
            target.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff;")
            c_l.addWidget(target)
            
            summary = QLabel(run.get("summary", ""))
            summary.setStyleSheet("font-size: 11px; color: #a1a1aa;")
            c_l.addWidget(summary)
            
            card.add_layout(c_l)
            self.history_layout.addWidget(card)
