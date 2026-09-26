"""
KAVACH 6.0 Desktop - Home & Overview Page.
Displays real-time system posture, quick assessment triggers, and architecture summary.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from widgets.glass_card import GlassCard
from widgets.status_badge import StatusBadge

class HomePage(QWidget):
    navigate_requested = Signal(str)

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
        
        # Hero Banner
        hero_card = GlassCard(glow="cyan")
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(12)
        
        badge_row = QHBoxLayout()
        badge_row.addWidget(StatusBadge("SOVEREIGN DEFENSE ENGINE", "INFO"))
        badge_row.addWidget(StatusBadge("RULE-BASED + AI HYBRID", "READY"))
        badge_row.addStretch()
        hero_layout.addLayout(badge_row)
        
        h1 = QLabel("Autonomous Empirical Security Verification")
        h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;")
        hero_layout.addWidget(h1)
        
        p = QLabel(
            "KAVACH delivers sovereign, tamper-evident security assessments. "
            "Every finding is backed by empirical proof, SHA-256 integrity hashes, and reproducible PowerShell procedures."
        )
        p.setWordWrap(True)
        p.setStyleSheet("font-size: 13px; color: #a1a1aa; line-height: 1.4;")
        hero_layout.addWidget(p)
        
        # Action CTA buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        btn_scan = QPushButton("🌐 Check Target URL →")
        btn_scan.setObjectName("cyanBtn")
        btn_scan.clicked.connect(lambda: self.navigate_requested.emit("url_check"))
        btn_row.addWidget(btn_scan)
        
        btn_local = QPushButton("💻 Audit Local Posture")
        btn_local.clicked.connect(lambda: self.navigate_requested.emit("local_posture"))
        btn_row.addWidget(btn_local)
        
        btn_world = QPushButton("🌍 Open World Monitor")
        btn_world.clicked.connect(lambda: self.navigate_requested.emit("world_monitor"))
        btn_row.addWidget(btn_world)
        btn_row.addStretch()
        hero_layout.addLayout(btn_row)
        
        hero_card.add_layout(hero_layout)
        layout.addWidget(hero_card)
        
        # 3 Pillar Cards Grid
        grid = QGridLayout()
        grid.setSpacing(16)
        
        # Pillar 1
        card1 = GlassCard("Empirical Probing", "Zero-Assumption Verification", "🎯")
        c1_desc = QLabel("Automated non-destructive network and protocol probing against authorized web applications.")
        c1_desc.setWordWrap(True)
        c1_desc.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        card1.add_widget(c1_desc)
        grid.addWidget(card1, 0, 0)
        
        # Pillar 2
        card2 = GlassCard("Cryptographic Evidence", "Dual Verification Model", "🔐")
        c2_desc = QLabel("Every finding produces verbatim PowerShell commands with expected vs observed outputs and SHA-256 signatures.")
        c2_desc.setWordWrap(True)
        c2_desc.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        card2.add_widget(c2_desc)
        grid.addWidget(card2, 0, 1)
        
        # Pillar 3
        card3 = GlassCard("Deterministic Engine", "Reproducible Intelligence", "⚡")
        c3_desc = QLabel("Rule-based fallback guarantees zero-leak security analysis even in strictly air-gapped offline environments.")
        c3_desc.setWordWrap(True)
        c3_desc.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        card3.add_widget(card3)
        grid.addWidget(card3, 0, 2)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
