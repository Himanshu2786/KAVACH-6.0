"""
KAVACH 6.0 Desktop - Theme & Style System (Qt QSS).
Translucent glassmorphic aesthetic with dark void palette, hairline borders, and cyan/teal accents.
"""

# Color Palette Constants
BG_VOID = "#000000"
BG_SURFACE = "#000000"
BG_SUBTLE = "#080808"
BG_GLASS = "rgba(10, 10, 10, 0.65)"
BG_GLASS_HOVER = "rgba(18, 18, 18, 0.85)"
BG_GLASS_MODAL = "rgba(8, 8, 8, 0.95)"
BG_TERMINAL = "#000000"

BORDER_GLASS = "rgba(255, 255, 255, 0.08)"
BORDER_GLASS_HOVER = "rgba(255, 255, 255, 0.22)"
BORDER_GLASS_STRONG = "rgba(255, 255, 255, 0.35)"

TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a1a1aa"
TEXT_MUTED = "#52525b"

ACCENT_CYAN = "#06b6d4"
ACCENT_CYAN_GLOW = "rgba(6, 182, 212, 0.3)"
STATUS_DANGER = "#f43f5e"
STATUS_WARNING = "#fbbf24"
STATUS_SUCCESS = "#34d399"
STATUS_INFO = "#38bdf8"
STATUS_PURPLE = "#a855f7"

SELECTION_BG = "#263238"
SELECTION_TEXT = "#ffffff"

GLOBAL_QSS = f"""
/* Global Window & Base Styles - Pure Black #000000 Canvas with High-Contrast Text Selection */
* {{
    selection-background-color: {SELECTION_BG};
    selection-color: {SELECTION_TEXT};
}}

QMainWindow, QWidget#rootWidget, QStackedWidget {{
    background-color: {BG_VOID};
    background: {BG_VOID};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', 'Inter', sans-serif;
    font-size: 13px;
}}

/* Scroll Areas & Scrollbars */
QScrollArea, QScrollArea > QWidget > QWidget {{
    background: {BG_VOID};
    background-color: {BG_VOID};
    border: none;
}}

QScrollBar:vertical {{
    border: none;
    background: rgba(255, 255, 255, 0.02);
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.15);
    min-height: 25px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.30);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: rgba(255, 255, 255, 0.02);
    height: 6px;
    margin: 0px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: rgba(255, 255, 255, 0.15);
    min-width: 25px;
    border-radius: 3px;
}}

/* Labels */
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#subheading {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}

QLabel#mutedText {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

QLabel#codeText {{
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
}}

/* Buttons */
QPushButton {{
    background-color: rgba(255, 255, 255, 0.06);
    color: #e4e4e7;
    border: 1px solid {BORDER_GLASS};
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 12px;
}}

QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    border-color: {BORDER_GLASS_HOVER};
}}

QPushButton:pressed {{
    background-color: rgba(255, 255, 255, 0.04);
}}

QPushButton:disabled {{
    background-color: rgba(255, 255, 255, 0.02);
    color: {TEXT_MUTED};
    border-color: rgba(255, 255, 255, 0.03);
}}

/* Primary Buttons */
QPushButton#primaryBtn {{
    background-color: #ffffff;
    color: #000000;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.95);
}}

QPushButton#primaryBtn:hover {{
    background-color: #f4f4f5;
    border-color: #ffffff;
}}

QPushButton#primaryBtn:pressed {{
    background-color: #e4e4e7;
}}

QPushButton#primaryBtn:disabled {{
    background-color: rgba(255, 255, 255, 0.3);
    color: rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.2);
}}

/* Cyan Action Buttons */
QPushButton#cyanBtn {{
    background-color: {ACCENT_CYAN};
    color: #030305;
    font-weight: 700;
    border: 1px solid rgba(6, 182, 212, 0.8);
    border-radius: 6px;
    padding: 7px 16px;
}}

QPushButton#cyanBtn:hover {{
    background-color: #22d3ee;
}}

QPushButton#cyanBtn:disabled {{
    background-color: rgba(6, 182, 212, 0.3);
    color: rgba(0, 0, 0, 0.4);
}}

/* Danger Buttons */
QPushButton#dangerBtn {{
    background-color: rgba(244, 63, 94, 0.15);
    color: #fb7185;
    border: 1px solid rgba(244, 63, 94, 0.35);
}}

QPushButton#dangerBtn:hover {{
    background-color: rgba(244, 63, 94, 0.25);
    color: #f43f5e;
    border-color: rgba(244, 63, 94, 0.55);
}}

/* Line Edits & Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: rgba(10, 12, 18, 0.85);
    color: #f4f4f5;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    selection-background-color: {SELECTION_BG};
    selection-color: {SELECTION_TEXT};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT_CYAN};
    background-color: rgba(14, 18, 28, 0.95);
}}

/* ComboBoxes */
QComboBox {{
    background-color: rgba(10, 12, 18, 0.85);
    color: #f4f4f5;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}}

QComboBox:hover {{
    border-color: {BORDER_GLASS_HOVER};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: #000000;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    selection-background-color: {SELECTION_BG};
    selection-color: {SELECTION_TEXT};
    padding: 4px;
}}

/* Navigation Bar */
QFrame#navbar {{
    background-color: #000000;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}}

QPushButton#navBtn {{
    background-color: transparent;
    color: #a1a1aa;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton#navBtn:hover {{
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.06);
}}

QPushButton#navBtn[active="true"] {{
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
}}

/* Glass Cards & Panels (floating over pure black) */
QFrame#glassCard {{
    background-color: rgba(10, 10, 10, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}}

QFrame#glassCardHover:hover {{
    border: 1px solid rgba(255, 255, 255, 0.20);
    background-color: rgba(18, 18, 18, 0.75);
}}

QFrame#glassTerminal {{
    background-color: #000000;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
}}
"""

def apply_theme(app):
    """Applies the global KAVACH stylesheet to the QApplication."""
    app.setStyleSheet(GLOBAL_QSS)
