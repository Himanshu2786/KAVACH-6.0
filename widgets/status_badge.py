"""
KAVACH 6.0 Desktop - StatusBadge Widget.
Pill badge with colored background, border, and monospace typography.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class StatusBadge(QLabel):
    def __init__(self, text: str = "INFO", variant: str = "INFO", parent=None):
        text_str = str(text) if text is not None else "INFO"
        variant_str = str(variant) if variant is not None else "INFO"
        if parent is not None:
            super().__init__(text_str, parent)
        else:
            super().__init__(text_str)
        self.variant = variant_str.upper()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(22)
        self._apply_style()

    def _apply_style(self):
        styles = {
            "CRITICAL": "background-color: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.40);",
            "HIGH": "background-color: rgba(249, 115, 22, 0.18); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.40);",
            "MEDIUM": "background-color: rgba(251, 191, 36, 0.18); color: #fde047; border: 1px solid rgba(251, 191, 36, 0.40);",
            "LOW": "background-color: rgba(56, 189, 248, 0.18); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.40);",
            "INFO": "background-color: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.30);",
            "ONLINE": "background-color: rgba(52, 211, 153, 0.18); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.40);",
            "READY": "background-color: rgba(52, 211, 153, 0.18); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.40);",
            "OFFLINE": "background-color: rgba(251, 191, 36, 0.18); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.40);",
            "DEMO": "background-color: rgba(168, 85, 247, 0.18); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.40);",
            "LIVE": "background-color: rgba(52, 211, 153, 0.18); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.40);",
            "PUBLIC": "background-color: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.40);",
            "RESOLVED": "background-color: rgba(52, 211, 153, 0.18); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.40);",
            "UNRESOLVED": "background-color: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.40);",
        }
        style = styles.get(self.variant, styles["INFO"])
        self.setStyleSheet(f"""
            QLabel {{
                {style}
                border-radius: 11px;
                padding: 2px 10px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)
