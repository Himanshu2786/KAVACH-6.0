"""
KAVACH 6.0 Desktop - Main Application Window.
Coordinates page switching via QStackedWidget, LandingScreen bootup, and global responsive layouts.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from app.navigation import NavigationBar
from ui.landing_screen import LandingScreen
from ui.home_page import HomePage
from ui.url_check_page import UrlCheckPage
from ui.world_monitor_page import WorldMonitorPage
from ui.local_posture_page import LocalPosturePage
from ui.findings_page import FindingsPage
from ui.evidence_page import EvidencePage
from ui.experience_db_page import ExperienceDbPage
from ui.audit_trail_page import AuditTrailPage
from ui.guide_page import GuidePage
from ui.history_page import HistoryPage
from ui.team_desk_page import TeamDeskPage
from ui.test_center_page import TestCenterPage
from ui.security_report_page import SecurityReportPage
from ui.system_status_page import SystemStatusPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAVACH 6.0 — Sovereign Security Intelligence Platform")
        self.resize(1280, 800)
        self.setMinimumSize(850, 600)
        
        self._init_ui()

    def _init_ui(self):
        self.root_widget = QWidget()
        self.root_widget.setObjectName("rootWidget")
        self.setCentralWidget(self.root_widget)
        
        self.main_layout = QVBoxLayout(self.root_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Navigation Bar (hidden during boot loading screen)
        self.navbar = NavigationBar(self)
        self.navbar.page_changed.connect(self._on_page_navigated)
        self.main_layout.addWidget(self.navbar)
        self.navbar.setVisible(False)
        
        # Stacked Pages
        self.stack = QStackedWidget(self)
        self.main_layout.addWidget(self.stack)
        
        # 1. Landing Screen (Index 0)
        self.landing = LandingScreen(self)
        self.landing.boot_completed.connect(self._on_boot_completed)
        self.landing.open_system_status.connect(lambda: self.navigate_to("system_status"))
        self.stack.addWidget(self.landing)
        
        # 2. Main Pages Map
        self.pages = {
            "home": HomePage(self),
            "url_check": UrlCheckPage(self),
            "world_monitor": WorldMonitorPage(self),
            "local_posture": LocalPosturePage(self),
            "findings": FindingsPage(self),
            "evidence": EvidencePage(self),
            "experience_db": ExperienceDbPage(self),
            "audit_trail": AuditTrailPage(self),
            "guide": GuidePage(self),
            "history": HistoryPage(self),
            "team_desk": TeamDeskPage(self),
            "test_center": TestCenterPage(self),
            "report": SecurityReportPage(self),
            "system_status": SystemStatusPage(self)
        }
        
        for pid, page in self.pages.items():
            self.stack.addWidget(page)
            # Connect page-specific navigation events
            if hasattr(page, "navigate_requested"):
                page.navigate_requested.connect(self.navigate_to)
            if hasattr(page, "assessment_done"):
                page.assessment_done.connect(self._on_assessment_done)
            if hasattr(page, "inspect_evidence_requested"):
                page.inspect_evidence_requested.connect(self._on_inspect_evidence)
            if hasattr(page, "open_assessment_findings_requested"):
                page.open_assessment_findings_requested.connect(self._on_open_assessment_findings)
            if hasattr(page, "open_assessment_evidence_requested"):
                page.open_assessment_evidence_requested.connect(self._on_open_assessment_evidence)

    def _on_boot_completed(self):
        self.navbar.setVisible(True)
        self.navigate_to("home")

    def _on_page_navigated(self, page_id: str):
        if page_id in self.pages:
            page = self.pages[page_id]
            self.stack.setCurrentWidget(page)
            if hasattr(page, "refresh_findings"):
                page.refresh_findings()
            elif hasattr(page, "refresh_evidence"):
                page.refresh_evidence()
            elif hasattr(page, "refresh_history"):
                page.refresh_history()
            elif hasattr(page, "refresh_desk"):
                page.refresh_desk()

    def navigate_to(self, page_id: str):
        self.navbar.set_active_page(page_id)

    def _on_assessment_done(self, asm_id: str):
        self._on_open_assessment_findings(asm_id)

    def _on_open_assessment_findings(self, assessment_id: str):
        findings_page = self.pages["findings"]
        findings_page.load_assessment(assessment_id)
        self.navigate_to("findings")

    def _on_open_assessment_evidence(self, assessment_id: str):
        evidence_page = self.pages["evidence"]
        evidence_page.load_assessment(assessment_id)
        self.navigate_to("evidence")

    def _on_inspect_evidence(self, evidence_id: str):
        ev_page = self.pages["evidence"]
        ev_page.load_specific_evidence(evidence_id)
        self.navigate_to("evidence")
