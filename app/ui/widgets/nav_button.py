"""
Custom reusable sidebar navigation button.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QStyle


class SidebarButton(QPushButton):
    """Navigation button for the sidebar."""

    clicked_nav = Signal(str)

    def __init__(self, text: str, nav_id: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.nav_id = nav_id
        self.setCheckable(True)
        self.setObjectName("sidebarBtn")

        self.setText(text)
        icon_types = {
            "dashboard": QStyle.StandardPixmap.SP_ComputerIcon,
            "registration": QStyle.StandardPixmap.SP_FileDialogNewFolder,
            "candidates": QStyle.StandardPixmap.SP_DirHomeIcon,
            "analytics": QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "years": QStyle.StandardPixmap.SP_FileDialogContentsView,
            "reports": QStyle.StandardPixmap.SP_FileIcon,
            "import_export": QStyle.StandardPixmap.SP_ArrowUp,
            "database": QStyle.StandardPixmap.SP_DriveHDIcon,
            "settings": QStyle.StandardPixmap.SP_FileDialogListView,
        }
        if nav_id in icon_types:
            self.setIcon(self.style().standardIcon(icon_types[nav_id]))
        self.setIconSize(self.sizeHint())
        self.setToolTip(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setMinimumHeight(44)
        self.setStyleSheet("""
            QPushButton {
                text-align: right;
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 8px;
                font-size: 13px;
            }
        """)

        self.clicked.connect(lambda: self.clicked_nav.emit(self.nav_id))
