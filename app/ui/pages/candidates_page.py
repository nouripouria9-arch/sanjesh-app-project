"""
Candidate management page — table, search, filters, CRUD actions.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.constants import FIELD_OPTIONS, GENDER_OPTIONS, PREV_EXAM_OPTIONS
from app.repositories.repositories import CandidateRepository, ScoreRepository
from app.services.candidate_service import CandidateService


class CandidatePage(QWidget):
    """Candidate management with table, search, and CRUD."""

    request_edit = Signal(int)  # candidate_id
    request_score_edit = Signal(int)  # candidate_id
    request_add = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("مدیریت داوطلبان")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("ثبت نام جدید")
        add_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        add_btn.setObjectName("successBtn")
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self.request_add.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Search & Filter bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet("QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px; }")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس نام، کد ملی یا کد رهگیری...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_input)

        self.field_filter = QComboBox()
        self.field_filter.addItem("همه رشته‌ها", "")
        for f in FIELD_OPTIONS:
            self.field_filter.addItem(f, f)
        self.field_filter.currentIndexChanged.connect(self._on_search)
        filter_layout.addWidget(self.field_filter)

        self.gender_filter = QComboBox()
        self.gender_filter.addItem("همه جنسیت‌ها", "")
        for g in GENDER_OPTIONS:
            self.gender_filter.addItem(g, g)
        self.gender_filter.currentIndexChanged.connect(self._on_search)
        filter_layout.addWidget(self.gender_filter)

        self.year_filter = QComboBox()
        self.year_filter.addItem("همه سال‌ها", 0)
        self._refresh_years()
        self.year_filter.currentIndexChanged.connect(self._on_search)
        filter_layout.addWidget(self.year_filter)

        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)

        layout.addWidget(filter_frame)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        self.table.doubleClicked.connect(self._on_double_click)
        self._setup_table_headers()
        layout.addWidget(self.table, stretch=1)

        # Action buttons
        actions = QHBoxLayout()
        self.edit_btn = QPushButton("ویرایش")
        self.edit_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.edit_btn.clicked.connect(self._on_edit)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("حذف")
        self.delete_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.edit_btn.setObjectName("secondaryBtn")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setEnabled(False)
        self.scores_btn = QPushButton("نمرات")
        self.scores_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.scores_btn.setObjectName("secondaryBtn")
        self.scores_btn.clicked.connect(self._on_scores)
        self.scores_btn.setEnabled(False)
        self.detail_btn = QPushButton("جزئیات")
        self.detail_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.detail_btn.setObjectName("secondaryBtn")
        self.detail_btn.clicked.connect(self._on_detail)
        self.detail_btn.setEnabled(False)

        actions.addWidget(self.detail_btn)
        actions.addWidget(self.scores_btn)
        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        actions.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #757575; background: transparent;")
        actions.addWidget(self.count_label)
        layout.addLayout(actions)

        self.table.selectionModel().selectionChanged.connect(self._on_selection)

    def _setup_table_headers(self) -> None:
        headers = ["ردیف", "نام", "کد ملی", "سن", "جنسیت", "رشته", "شرکت مجدد", "سال آزمون", "کد رهگیری", "زمان ثبت", "ID"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnHidden(10, True)  # Hide ID column
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in [0, 3, 4, 5, 6, 7]:
            header_view.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

    def _refresh_years(self) -> None:
        self.year_filter.blockSignals(True)
        current = self.year_filter.currentData()
        self.year_filter.clear()
        self.year_filter.addItem("همه سال‌ها", 0)
        for y in CandidateRepository.distinct_years():
            self.year_filter.addItem(str(y), y)
        # Restore selection
        for i in range(self.year_filter.count()):
            if self.year_filter.itemData(i) == current:
                self.year_filter.setCurrentIndex(i)
                break
        self.year_filter.blockSignals(False)

    def refresh_data(self) -> None:
        """Refresh the table while preserving the active filters."""
        self._refresh_years()
        self._on_search()

    def _load_data(self, candidates) -> None:
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
            self.table.setRowCount(0)
            self.table.setRowCount(len(candidates))
            for row, c in enumerate(candidates):
                values = (
                    row + 1,
                    c.name,
                    c.national_id,
                    c.age,
                    c.gender,
                    c.field,
                    c.previous_exam,
                    c.exam_year,
                    c.tracking_code,
                    c.register_time,
                    c.id,
                )
                for column, value in enumerate(values):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))
        finally:
            self.table.blockSignals(False)
        self.count_label.setText(f"تعداد: {len(candidates)}")
        self._clear_selection()

    def _on_search(self) -> None:
        query = self.search_input.text().strip()
        field = self.field_filter.currentData() or None
        gender = self.gender_filter.currentData() or None
        year = self.year_filter.currentData() or None
        if year == 0:
            year = None
        results = CandidateRepository.search(query, field, gender, year)
        self._load_data(results)

    def _get_selected_id(self) -> int | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        item = self.table.item(row, 10)
        return int(item.text()) if item else None

    def _clear_selection(self) -> None:
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.scores_btn.setEnabled(False)
        self.detail_btn.setEnabled(False)

    def _on_selection(self) -> None:
        has = self._get_selected_id() is not None
        self.edit_btn.setEnabled(has)
        self.delete_btn.setEnabled(has)
        self.scores_btn.setEnabled(has)
        self.detail_btn.setEnabled(has)

    def _on_edit(self) -> None:
        cid = self._get_selected_id()
        if cid:
            self.request_edit.emit(cid)

    def _on_delete(self) -> None:
        cid = self._get_selected_id()
        if not cid:
            return
        candidate = CandidateRepository.get_by_id(cid)
        if not candidate:
            return
        reply = QMessageBox.question(
            self,
            "تایید حذف",
            f"آیا از حذف داوطلب «{candidate.name}» (کد ملی: {candidate.national_id}) اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if CandidateService.delete(cid):
                QMessageBox.information(self, "موفق", "داوطلب با موفقیت حذف شد.")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "خطا", "حذف داوطلب با خطا مواجه شد.")

    def _on_scores(self) -> None:
        cid = self._get_selected_id()
        if cid:
            self.request_score_edit.emit(cid)

    def _on_detail(self) -> None:
        cid = self._get_selected_id()
        if not cid:
            return
        candidate = CandidateRepository.get_by_id(cid)
        if not candidate:
            return
        scores = ScoreRepository.get_scores(cid)
        score_text = "\n".join(f"  {s}: {p}%" for s, p in scores.items()) or "  نمره‌ای ثبت نشده"
        avg = sum(scores.values()) / len(scores) if scores else 0

        QMessageBox.information(
            self,
            f"جزئیات — {candidate.name}",
            f"نام: {candidate.name}\n"
            f"کد ملی: {candidate.national_id}\n"
            f"سن: {candidate.age}\n"
            f"جنسیت: {candidate.gender}\n"
            f"رشته: {candidate.field}\n"
            f"شرکت مجدد: {candidate.previous_exam}\n"
            f"سال آزمون: {candidate.exam_year}\n"
            f"کد رهگیری: {candidate.tracking_code}\n"
            f"زمان ثبت: {candidate.register_time}\n\n"
            f"نمرات:\n{score_text}\n\n"
            f"میانگین نمرات: {avg:.1f}%",
        )

    def _on_double_click(self, index) -> None:
        self._on_detail()

    def _context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu
        cid = self._get_selected_id()
        if not cid:
            return
        menu = QMenu(self)
        menu.addAction("جزئیات", self._on_detail)
        menu.addAction("ویرایش", self._on_edit)
        menu.addAction("نمرات", self._on_scores)
        menu.addSeparator()
        menu.addAction("حذف", self._on_delete)
        menu.exec(self.table.viewport().mapToGlobal(pos))
