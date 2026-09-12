"""
Settings page — application configuration.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import Config


class SettingsPage(QWidget):
    """Application settings with theme switching and configuration."""

    theme_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("تنظیمات")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)

        # ── Appearance Section ──────────────────────────────
        self._add_section(layout, "ظاهر", [
            ("تم برنامه:", self._create_theme_combo()),
        ])

        # ── Database Section ────────────────────────────────
        db_row = QHBoxLayout()
        self.db_path = QLineEdit()
        self.db_path.setReadOnly(True)
        db_row.addWidget(self.db_path, stretch=1)
        browse_btn = QPushButton("انتخاب مسیر")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.clicked.connect(self._browse_db)
        db_row.addWidget(browse_btn)
        self._add_section(layout, "پایگاه داده", [
            ("مسیر دیتابیس:", db_row),
        ])

        # ── Backup Section ──────────────────────────────────
        backup_row = QHBoxLayout()
        backup_btn = QPushButton("پشتیبان‌گیری")
        backup_btn.clicked.connect(self._do_backup)
        backup_row.addWidget(backup_btn)
        restore_btn = QPushButton("بازیابی از پشتیبان")
        restore_btn.setObjectName("secondaryBtn")
        restore_btn.clicked.connect(self._do_restore)
        backup_row.addWidget(restore_btn)
        backup_row.addStretch()
        self._add_section(layout, "پشتیبان‌گیری", [
            ("عملیات:", backup_row),
        ])

        # ── About Section ───────────────────────────────────
        from app.constants import APP_NAME, APP_VERSION, APP_AUTHOR
        self._add_section(layout, "درباره برنامه", [
            (f"نام: {APP_NAME}", QLabel("")),
            (f"نسخه: {APP_VERSION}", QLabel("")),
            (f"توسعه‌دهنده: {APP_AUTHOR}", QLabel("")),
        ])

        layout.addStretch()

    def _add_section(self, layout, title: str, rows: list) -> None:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; }")
        fl = QVBoxLayout(frame)
        label = QLabel(title)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; background: transparent;")
        fl.addWidget(label)
        for row_label, widget in rows:
            rl = QHBoxLayout()
            rl.addWidget(QLabel(row_label))
            if isinstance(widget, QWidget):
                rl.addWidget(widget)
            else:
                rl.addStretch()
            fl.addLayout(rl)
        layout.addWidget(frame)

    def _create_theme_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(["روشن", "تاریک"])
        cfg = Config()
        combo.setCurrentIndex(0 if cfg.theme == "light" else 1)
        combo.currentIndexChanged.connect(self._on_theme_change)
        return combo

    def _on_theme_change(self, index: int) -> None:
        theme = "light" if index == 0 else "dark"
        Config().theme = theme
        self.theme_changed.emit()

    def _browse_db(self) -> None:
        from app.constants import DATA_DIR
        filepath, _ = QFileDialog.getSaveFileName(
            self, "انتخاب مسیر دیتابیس", str(DATA_DIR / "sanjesh.db"),
            "SQLite DB (*.db)"
        )
        if filepath:
            Config().set("database_path", filepath)
            self.db_path.setText(filepath)

    def _do_backup(self) -> None:
        from datetime import datetime
        from app.constants import BACKUP_DIR
        from app.database.engine import backup_database

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"sanjesh_backup_{timestamp}.db"

        if backup_database(backup_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "موفق", f"پشتیبان با موفقیت ایجاد شد:\n{backup_path}")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "خطا", "ایجاد پشتیبان با خطا مواجه شد.")

    def _do_restore(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل پشتیبان", "", "SQLite DB (*.db)"
        )
        if not filepath:
            return
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "تایید بازیابی",
            "آیا از بازیابی اطلاعات از این فایل اطمینان دارید؟\n"
            "اطلاعات فعلی بازنویسی خواهد شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from app.database.engine import restore_database
            from pathlib import Path
            if restore_database(Path(filepath)):
                QMessageBox.information(self, "موفق", "بازیابی با موفقیت انجام شد.\n برنامه را مجدداً راه‌اندازی کنید.")
            else:
                QMessageBox.warning(self, "خطا", "بازیابی با خطا مواجه شد.")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.db_path.setText(Config().database_path)
