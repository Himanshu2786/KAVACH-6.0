"""
KAVACH 6.0 Desktop - Audit Trail Page.
Displays the immutable cryptographic event log, SHA-256 event chains, and operational audit trail.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from services.storage_service import storage
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class AuditTrailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.refresh_audit_events()

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
        h1 = QLabel("📜 Tamper-Evident Audit Trail")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_layout.addWidget(h1)
        
        sub = QLabel("Cryptographically linked operational log verifying every assessment, decision, and verification probe.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        h_layout.addWidget(sub)
        top_row.addLayout(h_layout)
        top_row.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_audit_events)
        top_row.addWidget(self.btn_refresh)
        layout.addLayout(top_row)
        
        # Events Container
        self.events_layout = QVBoxLayout()
        self.events_layout.setSpacing(10)
        
        self.events_container = QWidget()
        self.events_container.setLayout(self.events_layout)
        layout.addWidget(self.events_container)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh_audit_events(self):
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        events = storage.get_audit_events(limit=50)
        if not events:
            empty = QLabel("No audit events recorded.")
            empty.setStyleSheet("color: #71717a; font-size: 12px; padding: 16px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_layout.addWidget(empty)
            return

        for ev in events:
            card = GlassCard()
            c_l = QVBoxLayout()
            c_l.setSpacing(6)
            
            top_line = QHBoxLayout()
            top_line.addWidget(StatusBadge(ev.get("event_type", "AUDIT"), "INFO"))
            top_line.addWidget(StatusBadge(ev.get("actor", "OPERATOR"), "READY"))
            if ev.get("result"):
                res_status = "SUCCESS" if ev.get("result") in ("SUCCESS", "CONFIRMED", "VERIFIED") else "WARNING"
                top_line.addWidget(StatusBadge(str(ev.get("result")), res_status))
            top_line.addStretch()
            
            time_lbl = QLabel(ev.get("timestamp", ""))
            time_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #71717a;")
            top_line.addWidget(time_lbl)
            c_l.addLayout(top_line)
            
            act = QLabel(ev.get("action", ""))
            act.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
            c_l.addWidget(act)

            # Metadata details line
            meta_parts = []
            if ev.get("assessment_id"):
                meta_parts.append(f"Assessment: {ev.get('assessment_id')}")
            if ev.get("object"):
                meta_parts.append(f"Object: {ev.get('object')}")
            if ev.get("evidence_ref"):
                meta_parts.append(f"Evidence Ref: {ev.get('evidence_ref')}")
            if meta_parts:
                meta_lbl = QLabel(" | ".join(meta_parts))
                meta_lbl.setStyleSheet("font-size: 11px; color: #a1a1aa;")
                c_l.addWidget(meta_lbl)
            
            # Cryptographic Chaining info
            chain_box = QLabel(f"⛓️ SHA-256: {ev.get('event_hash', '')[:24]}... | PREV: {ev.get('prev_hash', 'GENESIS')[:24]}...")
            chain_box.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #06b6d4;")
            c_l.addWidget(chain_box)
            
            card.add_layout(c_l)
            self.events_layout.addWidget(card)
