"""
Database management page — integrity check, stats, raw tools.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.repositories.repositories import CandidateRepository, ScoreRepository


class DatabasePage(QWidget):
    """Database information and management tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_info()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("مدیریت پایگاه داده")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)

        # Actions
        actions = QHBoxLayout()
        refresh_btn = QPushButton("بروزرسانی اطلاعات")
        refresh_btn.clicked.connect(self.refresh_info)
        actions.addWidget(refresh_btn)

        check_btn = QPushButton("بررسی یکپارچگی")
        check_btn.setObjectName("secondaryBtn")
        check_btn.clicked.connect(self._check_integrity)
        actions.addWidget(check_btn)

        actions.addStretch()
        layout.addLayout(actions)

        # Info display
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px;")
        layout.addWidget(self.info_text, stretch=1)

    def refresh_info(self) -> None:
        from app.config.settings import Config
        from app.database.engine import get_table_count
        from app.models.entities import Candidate, Score, ExamYear, ActivityLog
        from pathlib import Path

        db_path = Path(Config().database_path)
        db_size = db_path.stat().st_size if db_path.exists() else 0
        size_str = f"{db_size / 1024:.1f} KB" if db_size < 1024 * 1024 else f"{db_size / (1024*1024):.2f} MB"

        lines = [
            "=" * 50,
            "        اطلاعات پایگاه داده",
            "=" * 50,
            f"  مسیر:         {db_path}",
            f"  حجم:          {size_str}",
            f"  وضعیت:        {'موجود ✅' if db_path.exists() else 'یافت نشد ❌'}",
            "",
            "── جداول ──",
            f"  candidates:   {CandidateRepository.count()} رکورد",
            f"  scores:       {ScoreRepository.count()} رکورد",
            f"  exam_years:   {get_table_count('exam_years')} رکورد",
            f"  activity_logs:{get_table_count('activity_logs')} رکورد",
            "",
            "── یکپارچگی ──",
            f"  داوطلبان با نمره:  {ScoreRepository.count_candidates_with_scores()}",
            f"  داوطلبان بدون نمره:{CandidateRepository.count() - ScoreRepository.count_candidates_with_scores()}",
            "",
            "── فهرست‌ها ──",
            f"  آزمون‌ها:     {CandidateRepository.distinct_years()}",
            f"  توزیع رشته:   {CandidateRepository.count_by_field()}",
            f"  توزیع جنسیت:  {CandidateRepository.count_by_gender()}",
        ]
        self.info_text.setPlainText("\n".join(lines))

    def _check_integrity(self) -> None:
        from app.database.engine import execute_raw
        try:
            results = execute_raw("PRAGMA integrity_check")
            status = results[0][0] if results else "unknown"
            if status == "ok":
                QMessageBox.information(self, "نتیجه بررسی", "یکپارچگی دیتابیس: ✅ سالم")
            else:
                QMessageBox.warning(self, "نتیجه بررسی", f"یکپارچگی دیتابیس: {status}")
        except Exception as exc:
            QMessageBox.critical(self, "خطا", f"بررسی یکپارچگی با خطا مواجه شد:\n{exc}")
