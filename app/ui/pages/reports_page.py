"""
Reports page — generate, preview, and export statistical reports.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.constants import EXPORTS_DIR
from app.reports.report_generator import ReportGenerator


class ReportsPage(QWidget):
    """Report generation and export page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("گزارش‌گیری")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Report selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("نوع گزارش:"))
        self.report_type = QComboBox()
        self.report_type.addItems([
            "گزارش خلاصه آماری",
            "گزارش مقایسه دروس",
            "گزارش مقایسه سال‌ها",
        ])
        self.report_type.setMinimumWidth(250)
        selector_layout.addWidget(self.report_type)

        gen_btn = QPushButton("تولید گزارش")
        gen_btn.clicked.connect(self._generate_report)
        selector_layout.addWidget(gen_btn)

        save_btn = QPushButton("ذخیره گزارش")
        save_btn.setObjectName("successBtn")
        save_btn.clicked.connect(self._save_report)
        selector_layout.addWidget(save_btn)

        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Report preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.preview, stretch=1)

        self.current_report = ""

    def _generate_report(self) -> None:
        report_type = self.report_type.currentIndex()
        try:
            if report_type == 0:
                self.current_report = ReportGenerator.generate_summary_report()
            elif report_type == 1:
                self.current_report = ReportGenerator.generate_subject_report()
            elif report_type == 2:
                self.current_report = ReportGenerator.generate_year_comparison_report()
            else:
                self.current_report = "گزارش نامعتبر"

            if not self.current_report.strip():
                self.current_report = "داده‌ای برای تولید گزارش وجود ندارد."
                QMessageBox.information(self, "اعلام", "هنوز داده‌ای در پایگاه داده ثبت نشده است.")
            else:
                self.preview.setPlainText(self.current_report)
        except Exception as exc:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش:\n{exc}")

    def _save_report(self) -> None:
        if not self.current_report.strip():
            QMessageBox.information(self, "اعلام", "ابتدا گزارش را تولید کنید.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "ذخیره گزارش", str(EXPORTS_DIR / "report.txt"),
            "Text Files (*.txt);;All Files (*)"
        )
        if filepath:
            if ReportGenerator.save_report(self.current_report, Path(filepath)):
                QMessageBox.information(self, "موفق", f"گزارش در:\n{filepath}\nذخیره شد.")
            else:
                QMessageBox.warning(self, "خطا", "ذخیره گزارش با خطا مواجه شد.")
