"""
KAVACH 6.0 — Sovereign Security Intelligence Platform (Desktop Application).
Direct desktop entry point. Initializes PySide6 QApplication, applies dark glassmorphic styling, and launches MainWindow.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.theme import apply_theme
from app.main_window import MainWindow

def main():
    # High DPI Scaling attributes
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("KAVACH")
    app.setApplicationDisplayName("KAVACH 6.0")
    app.setOrganizationName("KAVACH Security")
    
    # Apply signature dark glassmorphic styling
    apply_theme(app)
    
    # Launch main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
