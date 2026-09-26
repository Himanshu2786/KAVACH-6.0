"""
KAVACH 6.0 Desktop - GlassCard Widget.
Translucent container card with title header, subtitle, and content layout.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt

class GlassCard(QFrame):
    def __init__(self, title: str = "", subtitle: str = "", icon_text: str = "", glow: str = "none", parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self._glow = glow
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(10)
        
        # Header area if title provided
        if title or icon_text:
            self.header_layout = QHBoxLayout()
            self.header_layout.setSpacing(8)
            
            if icon_text:
                self.icon_label = QLabel(icon_text)
                self.icon_label.setStyleSheet("font-size: 14px;")
                self.header_layout.addWidget(self.icon_label)
                
            self.title_layout = QVBoxLayout()
            self.title_layout.setSpacing(2)
            
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff;")
            self.title_layout.addWidget(self.title_label)
            
            if subtitle:
                self.sub_label = QLabel(subtitle)
                self.sub_label.setStyleSheet("font-size: 11px; color: #a1a1aa;")
                self.title_layout.addWidget(self.sub_label)
                
            self.header_layout.addLayout(self.title_layout)
            self.header_layout.addStretch()
            self.main_layout.addLayout(self.header_layout)
            
        self._apply_glass_style()
        
    def add_widget(self, widget: QWidget):
        """Adds a child widget to the card's main content area."""
        self.main_layout.addWidget(widget)
        
    def add_layout(self, layout):
        """Adds a child layout to the card."""
        self.main_layout.addLayout(layout)

    def _apply_glass_style(self):
        border_color = "rgba(255, 255, 255, 0.08)"
        if self._glow == "cyan":
            border_color = "rgba(6, 182, 212, 0.25)"
        elif self._glow == "purple":
            border_color = "rgba(168, 85, 247, 0.25)"
            
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background-color: rgba(13, 15, 23, 0.72);
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
        """)
