"""
KAVACH 6.0 Desktop - Responsive Button Group.
Dynamically handles button wrapping or column stacking based on container width.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize

class ResponsiveButtonGroup(QWidget):
    """
    A container that automatically shifts buttons between horizontal row
    and vertical column depending on available width, preventing overflow.
    """
    def __init__(self, breakpoint_width: int = 500, parent=None):
        super().__init__(parent)
        self.breakpoint_width = breakpoint_width
        self.buttons = []
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)
        self.is_vertical = False

    def add_button(self, btn: QPushButton):
        self.buttons.append(btn)
        self.main_layout.addWidget(btn)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.width()
        
        if width < self.breakpoint_width and not self.is_vertical:
            self._switch_to_vertical()
        elif width >= self.breakpoint_width and self.is_vertical:
            self._switch_to_horizontal()

    def _switch_to_vertical(self):
        self.is_vertical = True
        # Re-parent items into QVBoxLayout
        QWidget().setLayout(self.main_layout)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)
        for btn in self.buttons:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.main_layout.addWidget(btn)

    def _switch_to_horizontal(self):
        self.is_vertical = False
        QWidget().setLayout(self.main_layout)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)
        for btn in self.buttons:
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.main_layout.addWidget(btn)
