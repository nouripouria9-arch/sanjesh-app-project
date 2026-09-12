"""
Theme management — Light and Dark mode for PySide6.
"""

from __future__ import annotations

from app.constants import (
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
)

LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #f7f9fc;
    color: #333333;
}
QWidget {
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 12px;
    color: #333333;
}
QDialog {
    border: 1px solid #dbe5f0;
}
QLabel#dialogSubtitle {
    color: #607d8b;
    padding: 0 12px 6px;
}
QLineEdit#primaryInput {
    border: 2px solid #90caf9;
    background-color: #fbfdff;
}
QLineEdit#primaryInput:focus {
    border-color: #1976D2;
    background-color: white;
}
QLabel {
    background: transparent;
    color: #333333;
}
QPushButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #1565C0;
}
QPushButton:pressed {
    background-color: #0D47A1;
}
QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}
QPushButton#dangerBtn {
    background-color: #E53935;
}
QPushButton#dangerBtn:hover {
    background-color: #C62828;
}
QPushButton#successBtn {
    background-color: #43A047;
}
QPushButton#successBtn:hover {
    background-color: #2E7D32;
}
QPushButton#secondaryBtn {
    background-color: #78909C;
}
QPushButton#secondaryBtn:hover {
    background-color: #546E7A;
}
QPushButton#sidebarBtn {
    background-color: transparent;
    color: #555;
    text-align: right;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#sidebarBtn:hover {
    background-color: #e3f2fd;
    color: #1976D2;
}
QPushButton#sidebarBtn:checked {
    background-color: #1976D2;
    color: white;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
    background-color: white;
    border: 1.5px solid #ddd;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    min-height: 24px;
    selection-background-color: #1976D2;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #1976D2;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #e3f2fd;
    selection-color: #1976D2;
    border: 1px solid #ddd;
    border-radius: 4px;
}
QTableView, QTableWidget {
    background-color: white;
    alternate-background-color: #fafbfc;
    gridline-color: #e8eaed;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    selection-background-color: #e3f2fd;
    selection-color: #333;
    font-size: 12px;
    outline: none;
}
QTableView::item, QTableWidget::item {
    padding: 6px 8px;
}
QHeaderView::section {
    background-color: #f5f7fa;
    border: none;
    border-bottom: 2px solid #1976D2;
    padding: 8px 10px;
    font-weight: bold;
    color: #1976D2;
}
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #c0c0c0;
    border-radius: 4px;
    min-width: 30px;
}
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    background: white;
}
QTabBar::tab {
    background: #f0f0f0;
    border: 1px solid #e0e0e0;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: white;
    color: #1976D2;
    font-weight: bold;
    border-bottom: 2px solid #1976D2;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #1976D2;
}
QStatusBar {
    background-color: #f5f7fa;
    border-top: 1px solid #e0e0e0;
    color: #555;
}
QToolTip {
    background-color: #333;
    color: white;
    border: none;
    padding: 6px;
    border-radius: 4px;
    font-size: 11px;
}
QProgressBar {
    border: 1px solid #ddd;
    border-radius: 4px;
    text-align: center;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 3px;
}
"""

DARK_THEME = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QWidget {
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 12px;
    color: #cdd6f4;
    background-color: #1e1e2e;
}
QLabel {
    background: transparent;
    color: #cdd6f4;
}
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #585b70;
}
QPushButton:pressed {
    background-color: #313244;
}
QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
}
QPushButton#dangerBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
}
QPushButton#dangerBtn:hover {
    background-color: #eba0ac;
}
QPushButton#successBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
}
QPushButton#successBtn:hover {
    background-color: #94e2d5;
}
QPushButton#secondaryBtn {
    background-color: #6c7086;
    color: #cdd6f4;
}
QPushButton#sidebarBtn {
    background-color: transparent;
    color: #a6adc8;
    text-align: right;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#sidebarBtn:hover {
    background-color: #313244;
    color: #89b4fa;
}
QPushButton#sidebarBtn:checked {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
    background-color: #313244;
    border: 1.5px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #cdd6f4;
    min-height: 24px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #89b4fa;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border: 1px solid #45475a;
}
QTableView, QTableWidget {
    background-color: #1e1e2e;
    alternate-background-color: #181825;
    gridline-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
    color: #cdd6f4;
    font-size: 12px;
}
QHeaderView::section {
    background-color: #313244;
    border: none;
    border-bottom: 2px solid #89b4fa;
    padding: 8px 10px;
    font-weight: bold;
    color: #89b4fa;
}
QScrollBar:vertical {
    background: transparent;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 6px;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #313244;
    border: 1px solid #45475a;
    padding: 8px 20px;
    color: #a6adc8;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background: #1e1e2e;
    color: #89b4fa;
    font-weight: bold;
    border-bottom: 2px solid #89b4fa;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QStatusBar {
    background-color: #181825;
    border-top: 1px solid #45475a;
    color: #a6adc8;
}
QToolTip {
    background-color: #45475a;
    color: #cdd6f4;
    padding: 6px;
    border-radius: 4px;
}
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 4px;
    text-align: center;
    height: 20px;
    background-color: #313244;
    color: #cdd6f4;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 3px;
}
"""


def get_theme(theme_name: str) -> str:
    """Return the QSS stylesheet for the given theme name."""
    if theme_name == "dark":
        return DARK_THEME
    return LIGHT_THEME
