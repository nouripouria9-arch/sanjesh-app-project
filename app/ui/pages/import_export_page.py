"""
Import / Export page — graphical data exchange.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.constants import EXPORTS_DIR
from app.repositories.repositories import CandidateRepository
from app.services.candidate_service import CandidateService
from app.services.import_export_service import ExportService, ImportService


class ImportExportPage(QWidget):
    """Import from file and export to file."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._preview_data: list[dict] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("ورود / خروج داده")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)

        # ── Import Section ──────────────────────────────────
        import_frame = QFrame()
        import_frame.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; }")
        il = QVBoxLayout(import_frame)

        import_title = QLabel("ورود داده (Import)")
        import_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; background: transparent;")
        il.addWidget(import_title)

        import_row = QHBoxLayout()
        self.import_type = QComboBox()
        self.import_type.addItems(["CSV", "Excel (.xlsx)", "JSON"])
        import_row.addWidget(self.import_type)

        select_btn = QPushButton("انتخاب فایل")
        select_btn.clicked.connect(self._select_import_file)
        import_row.addWidget(select_btn)

        self.preview_btn = QPushButton("پیش‌نمایش")
        self.preview_btn.setObjectName("secondaryBtn")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._preview_import)
        import_row.addWidget(self.preview_btn)

        self.import_btn = QPushButton("وارد کردن داده")
        self.import_btn.setObjectName("successBtn")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._do_import)
        import_row.addWidget(self.import_btn)

        import_row.addStretch()
        il.addLayout(import_row)

        # Import preview table
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setMaximumHeight(200)
        il.addWidget(self.preview_table)

        self.import_status = QLabel("")
        self.import_status.setStyleSheet("background: transparent; font-size: 12px;")
        il.addWidget(self.import_status)

        layout.addWidget(import_frame)

        # ── Export Section ──────────────────────────────────
        export_frame = QFrame()
        export_frame.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; }")
        el = QVBoxLayout(export_frame)

        export_title = QLabel("خروج داده (Export)")
        export_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #26A69A; background: transparent;")
        el.addWidget(export_title)

        export_row = QHBoxLayout()
        self.export_type = QComboBox()
        self.export_type.addItems(["CSV", "Excel (.xlsx)", "JSON"])
        export_row.addWidget(self.export_type)

        export_btn = QPushButton("صادر کردن داده")
        export_btn.setObjectName("successBtn")
        export_btn.clicked.connect(self._do_export)
        export_row.addWidget(export_btn)

        export_row.addStretch()
        el.addLayout(export_row)

        self.export_status = QLabel(f"تعداد داوطلبان قابل صدور: {CandidateRepository.count()}")
        self.export_status.setStyleSheet("background: transparent; font-size: 12px;")
        el.addWidget(self.export_status)

        layout.addWidget(export_frame)
        layout.addStretch()

    def _select_import_file(self) -> None:
        ext_map = {
            0: "CSV Files (*.csv)",
            1: "Excel Files (*.xlsx)",
            2: "JSON Files (*.json)",
        }
        ext = ext_map[self.import_type.currentIndex()]
        filepath, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل ورودی", "", ext)
        if filepath:
            self._import_path = Path(filepath)
            self.preview_btn.setEnabled(True)
            self.import_btn.setEnabled(True)
            self.import_status.setText(f"فایل انتخاب شده: {filepath}")

    def _preview_import(self) -> None:
        if not hasattr(self, "_import_path"):
            return
        ext = self._import_path.suffix.lower()
        if ext == ".csv":
            self._preview_data, errors = ImportService.import_csv(self._import_path)
        elif ext == ".xlsx":
            self._preview_data, errors = ImportService.import_excel(self._import_path)
        elif ext == ".json":
            self._preview_data, errors = ImportService.import_json(self._import_path)
        else:
            QMessageBox.warning(self, "خطا", "فرمت فایل پشتیبانی نمی‌شود.")
            return

        if errors:
            self.import_status.setText(f"خطاها: {'; '.join(errors[:5])}")

        self._fill_preview_table(self._preview_data)

    def _fill_preview_table(self, data: list[dict]) -> None:
        if not data:
            self.preview_table.setRowCount(0)
            return
        cols = ["national_id", "name", "age", "gender", "field"]
        headers = ["کد ملی", "نام", "سن", "جنسیت", "رشته"]
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)
        self.preview_table.setRowCount(min(len(data), 20))
        for row in range(min(len(data), 20)):
            for col, key in enumerate(cols):
                val = str(data[row].get(key, ""))
                self.preview_table.setItem(row, col, QTableWidgetItem(val))
        self.import_status.setText(f"پیش‌نمایش: {min(len(data), 20)} سطر از {len(data)} سطر کل")

    def _do_import(self) -> None:
        if not self._preview_data:
            QMessageBox.information(self, "اعلام", "ابتدا فایل را انتخاب و پیش‌نمایش کنید.")
            return

        confirm = QMessageBox.question(
            self,
            "تایید ورود داده",
            f"آیا از وارد کردن {len(self._preview_data)} رکورد اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        imported, skipped, errors = CandidateService.import_bulk(self._preview_data)
        msg = f"ورود موفق: {imported}\nرد شده: {skipped}"
        if errors:
            msg += "\n\nخطاها:\n" + "\n".join(errors[:10])
        QMessageBox.information(self, "نتیجه ورود داده", msg)
        self._preview_data = []

    def _do_export(self) -> None:
        ext = self.export_type.currentIndex()
        ext_map = {0: (".csv", "CSV Files (*.csv)"), 1: (".xlsx", "Excel Files (*.xlsx)"), 2: (".json", "JSON Files (*.json)")}
        suffix, filter_str = ext_map[ext]
        filepath, _ = QFileDialog.getSaveFileName(
            self, "ذخیره فایل خروجی", str(EXPORTS_DIR / f"export{suffix}"), filter_str
        )
        if not filepath:
            return

        if ext == 0:
            ok = ExportService.export_csv(Path(filepath))
        elif ext == 1:
            ok = ExportService.export_excel(Path(filepath))
        else:
            ok = ExportService.export_json(Path(filepath))

        if ok:
            self.export_status.setText(f"صادر شد: {filepath}")
            QMessageBox.information(self, "موفق", f"داده‌ها با موفقیت صادر شدند:\n{filepath}")
        else:
            QMessageBox.warning(self, "خطا", "صادر کردن داده‌ها با خطا مواجه شد.")
