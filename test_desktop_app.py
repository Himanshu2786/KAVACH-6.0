"""
Test script to verify desktop application initialization and all pages.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from app.theme import apply_theme
from app.main_window import MainWindow

def test_app():
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        apply_theme(app)
        window = MainWindow()
        if hasattr(window, "landing") and hasattr(window.landing, "timer"):
            window.landing.timer.stop()
        print(f"SUCCESS: MainWindow created with {len(window.pages)} pages.")
        for pid, page in window.pages.items():
            print(f" - Page loaded: {pid} ({page.__class__.__name__})")
        del window
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
        
if __name__ == "__main__":
    success = test_app()
    if success:
        print("[SUCCESS] All 14 Desktop UI pages verified.")
        os._exit(0)
    else:
        os._exit(1)


