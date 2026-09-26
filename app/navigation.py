"""
KAVACH 6.0 Desktop - Top Navigation Bar.
Provides tab navigation, active page pill indicators, and quick action CTA.
"""

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal
from widgets.status_badge import StatusBadge

class NavigationBar(QFrame):
    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(54)
        self.nav_buttons = {}
        self.active_id = "home"
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(6)
        
        # Brand
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(8)
        
        logo = QLabel("🛡️")
        logo.setStyleSheet("font-size: 16px;")
        brand_layout.addWidget(logo)
        
        brand = QLabel("KAVACH")
        brand.setStyleSheet("font-size: 14px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;")
        brand_layout.addWidget(brand)
        
        ver = QLabel("5.0")
        ver.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.08);
            color: #a1a1aa;
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 4px;
            padding: 1px 5px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
        """)
        brand_layout.addWidget(ver)
        layout.addLayout(brand_layout)
        
        layout.addSpacing(16)
        
        # Nav Items
        self.tabs = [
            ("home", "Overview"),
            ("url_check", "URL Check"),
            ("world_monitor", "World Monitor"),
            ("local_posture", "Local Posture"),
            ("findings", "Findings"),
            ("evidence", "Evidence"),
            ("experience_db", "Experience DB"),
            ("audit_trail", "Audit Trail"),
            ("guide", "Guide"),
            ("history", "History"),
            ("team_desk", "Team Desk"),
            ("test_center", "Test Center"),
            ("report", "Report"),
            ("system_status", "Status")
        ]
        
        for page_id, label in self.tabs:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, pid=page_id: self.set_active_page(pid))
            self.nav_buttons[page_id] = btn
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Action CTA
        self.btn_assess = QPushButton("Assess Target →")
        self.btn_assess.setObjectName("primaryBtn")
        self.btn_assess.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_assess.setStyleSheet("padding: 5px 12px; font-size: 11px;")
        self.btn_assess.clicked.connect(lambda: self.set_active_page("url_check"))
        layout.addWidget(self.btn_assess)
        
        self.set_active_page("home")

    def set_active_page(self, page_id: str):
        self.active_id = page_id
        for pid, btn in self.nav_buttons.items():
            is_active = (pid == page_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.page_changed.emit(page_id)
