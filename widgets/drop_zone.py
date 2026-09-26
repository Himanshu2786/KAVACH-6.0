"""
KAVACH 6.0 Desktop - Drag & Drop Target Zone.
Accepts file or folder drag-and-drop from Windows Explorer with visual feedback.
"""

import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setFixedHeight(120)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        
        self.icon_lbl = QLabel("📂")
        self.icon_lbl.setStyleSheet("font-size: 28px;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)
        
        self.text_lbl = QLabel("DROP FILE OR FOLDER HERE FOR DEFENSIVE SCAN")
        self.text_lbl.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #ffffff;")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_lbl)
        
        self.sub_lbl = QLabel("or enter a path manually / browse below")
        self.sub_lbl.setStyleSheet("font-size: 11px; color: #71717a;")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_lbl)
        
        self._set_normal_style()

    def _set_normal_style(self):
        self.setStyleSheet("""
            QFrame#dropZone {
                background-color: rgba(13, 15, 23, 0.55);
                border: 2px dashed rgba(255, 255, 255, 0.14);
                border-radius: 12px;
            }
            QFrame#dropZone:hover {
                border-color: rgba(6, 182, 212, 0.40);
                background-color: rgba(18, 22, 34, 0.65);
            }
        """)

    def _set_hover_style(self):
        self.setStyleSheet("""
            QFrame#dropZone {
                background-color: rgba(6, 182, 212, 0.15);
                border: 2px dashed #06b6d4;
                border-radius: 12px;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_hover_style()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._set_normal_style()

    def dropEvent(self, event: QDropEvent):
        self._set_normal_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path and os.path.exists(path):
                self.file_dropped.emit(path)
