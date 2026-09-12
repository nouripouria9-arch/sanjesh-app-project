"""
Reusable stat card widget for dashboards.
Displays a metric with icon, label, and value.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class StatCard(QFrame):
    """A compact card showing a single KPI metric."""

    def __init__(
        self,
        title: str,
        value: str | int | float = "—",
        color: str = "#1976D2",
        icon_text: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumSize(200, 110)
        self.setMaximumHeight(130)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(14)

        # Icon area
        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setStyleSheet(f"""
                font-size: 28px;
                color: {color};
                background: transparent;
            """)
            icon_label.setFixedWidth(40)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)

        # Text area
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 12px; color: #757575; background: transparent; font-weight: normal;")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
            background: transparent;
        """)
        text_layout.addWidget(self.value_label)

        text_layout.addStretch()
        main_layout.addLayout(text_layout)

    def set_value(self, value: str | int | float) -> None:
        self.value_label.setText(str(value))

    def set_value_color(self, color: str) -> None:
        self.value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
            background: transparent;
        """)
