"""
KAVACH 6.0 Desktop - Operator Guide & Technical Documentation Page.
Comprehensive scrollable manual detailing File Scanning, Drag-and-Drop, Findings, Cryptographic Evidence, User Manual, and 16 High-Definition Demonstration Recordings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
)
from PySide6.QtCore import Qt
import os
import subprocess
from widgets.glass_card import GlassCard

class GuidePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # Header
        h1 = QLabel("📖 Operator Field Manual & Verification Guide")
        h1.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        layout.addWidget(h1)
        
        sub = QLabel("Standard operating procedures for defensive assessment, least-privilege verification, and 16 playable demonstration recordings.")
        sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
        layout.addWidget(sub)

        # User Manual & Demos Card
        c_manual = GlassCard("📘 KAVACH 6.0 Complete User Manual & Demos", "Full Operator Manual (INFO/USER_MANUAL.md)", "🎬", glow="cyan")
        t_manual = QLabel(
            "• End-to-End User Manual: 25 comprehensive chapters covering all buttons, workflows, and SIH PS 26163 evaluation criteria.\n"
            "• 16 Playable Demonstration Recordings: High-Definition video captures saved in docs/user_manual/demos/ and frontend/public/demos/.\n"
            "• Truth Hierarchy: 'AI Hypothesizes. Evidence Confirms. Ollama is NEVER the detector.'\n"
            "• Verification Standard: 100% Deterministic FIRST.org CVSS 3.1 & Merkle-style SHA-256 audit chaining."
        )
        t_manual.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.6;")
        c_manual.add_widget(t_manual)
        
        btn_open_manual = QPushButton("📄 Open INFO/USER_MANUAL.md")
        btn_open_manual.setStyleSheet("background: rgba(0, 240, 255, 0.15); color: #00f0ff; border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 11px;")
        btn_open_manual.clicked.connect(self._open_user_manual)
        c_manual.add_widget(btn_open_manual)
        layout.addWidget(c_manual)
        
        # Tutorial 1: Drag & Drop and Manual Path Entry
        c_tut1 = GlassCard("Tutorial 1: Drag & Drop or Path File Scanning", "Defensive Static Assessment Workflow", "📂")
        t_tut1 = QLabel(
            "1. Open the Findings page in KAVACH.\n"
            "2. Drag any file or folder from Windows Explorer directly onto the 'DROP FILE OR FOLDER HERE' area, OR enter a path manually (e.g. demo/training_samples/demo_api_keys.env).\n"
            "3. Review the 'Permission & Scope Verification' dialog confirming Read-Only access.\n"
            "4. Click 'START DEFENSIVE SCAN'.\n"
            "5. The background worker inspects file metadata, computes chunked SHA-256 hashes, and evaluates static detection rules without executing any code.\n"
            "6. Review the newly generated findings in the list."
        )
        t_tut1.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.6;")
        c_tut1.add_widget(t_tut1)
        layout.addWidget(c_tut1)

        # Tutorial 2: Cryptographic Evidence & PowerShell Verification
        c_tut2 = GlassCard("Tutorial 2: Cryptographic Evidence & PowerShell Reproduction", "8-Step Verifiable Proof Model", "💻")
        t_tut2 = QLabel(
            "1. In the Findings page, click '🔍 View Cryptographic Evidence' on any finding.\n"
            "2. The Evidence tab displays the 8-step investigative breakdown:\n"
            "   • 01 FINDING: Finding classification and severity\n"
            "   • 02 WHY: Technical security risk explanation\n"
            "   • 03 WHERE: Target file path\n"
            "   • 04 PROOF: Redacted observation snippet with line number\n"
            "   • 05 ANALYSIS: SHA-256 integrity hash verification\n"
            "   • 06 VERIFY: Verbatim PowerShell command\n"
            "   • 07 FIX: Remediation guidance\n"
            "   • 08 RE-VERIFY: Live differential re-scan button\n"
            "3. Click 'Copy' on step 06 and run the command in Windows PowerShell to verify the observation independently."
        )
        t_tut2.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.6;")
        c_tut2.add_widget(t_tut2)
        layout.addWidget(c_tut2)

        # Tutorial 3: Remediation & Differential Re-Verification
        c_tut3 = GlassCard("Tutorial 3: Remediation & On-Disk Re-Verification", "Confirming Fixes on Disk", "🔄")
        t_tut3 = QLabel(
            "1. Follow the remediation steps in Step 07 to remove the exposed secret or correct the file configuration on disk.\n"
            "2. In KAVACH Evidence tab, click '🔄 Re-Scan Target on Disk' (Step 08).\n"
            "3. KAVACH re-analyzes the live file:\n"
            "   • If fixed: Shows '✓ VERIFIED — FINDING RESOLVED' and updates finding status to RESOLVED.\n"
            "   • If still present: Shows '⚠ STILL DETECTED' and preserves the OPEN finding state.\n"
            "4. The resolution is cryptographically appended to the Audit Trail."
        )
        t_tut3.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.6;")
        c_tut3.add_widget(t_tut3)
        layout.addWidget(c_tut3)

        # Safe Demo Test Cases
        c_demo = GlassCard("Bundled Safe Demo Test Cases", "Pre-configured benign test samples in demo/training_samples/", "🧪")
        t_demo = QLabel(
            "• demo_api_keys.env: Tests regex detection of AWS keys and DB passwords with automatic redaction.\n"
            "• suspicious_invoice.pdf.exe: Harmless test file validating disguised double-extension detection.\n"
            "• demo_insecure_config.json: Tests configuration analysis for debug=true and permit_root_login=true.\n"
            "• clean_document.txt: Benchmark file proving that clean files produce exactly 0 findings."
        )
        t_demo.setStyleSheet("color: #d4d4d8; font-size: 12px; line-height: 1.6;")
        c_demo.add_widget(t_demo)
        layout.addWidget(c_demo)
        
        layout.addStretch()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _open_user_manual(self):
        manual_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "INFO", "USER_MANUAL.md"))
        if os.path.exists(manual_path):
            try:
                os.startfile(manual_path)
            except Exception:
                subprocess.Popen(["notepad.exe", manual_path])
