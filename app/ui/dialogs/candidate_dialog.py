"""
Candidate registration dialog — full form with validation.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.constants import (
    FIELD_OPTIONS,
    GENDER_OPTIONS,
    PREV_EXAM_OPTIONS,
)
from app.services.candidate_service import CandidateService


class CandidateDialog(QDialog):
    """Register or edit a candidate."""

    def __init__(self, parent=None, candidate=None):
        super().__init__(parent)
        self.candidate = candidate
        self.setWindowTitle("ثبت نام داوطلب" if candidate is None else "ویرایش داوطلب")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if candidate:
            self._load_candidate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("ثبت نام داوطلب جدید" if self.candidate is None else "ویرایش اطلاعات داوطلب")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "اطلاعات داوطلب را وارد کنید تا ثبت‌نام آزمون با کد رهگیری اختصاصی انجام شود."
            if self.candidate is None else
            "اطلاعات ثبت‌شده‌ی داوطلب را بررسی و ویرایش کنید."
        )
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("primaryInput")
        self.name_input.setPlaceholderText("نام و نام خانوادگی")
        form.addRow("نام:", self.name_input)

        self.nid_input = QLineEdit()
        self.nid_input.setObjectName("primaryInput")
        self.nid_input.setPlaceholderText("۱۰ رقم")
        self.nid_input.setMaxLength(10)
        form.addRow("کد ملی:", self.nid_input)

        self.age_input = QSpinBox()
        self.age_input.setRange(14, 100)
        self.age_input.setValue(18)
        form.addRow("سن:", self.age_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(GENDER_OPTIONS)
        form.addRow("جنسیت:", self.gender_input)

        self.field_input = QComboBox()
        self.field_input.addItems(FIELD_OPTIONS)
        form.addRow("رشته:", self.field_input)

        self.prev_input = QComboBox()
        self.prev_input.addItems(PREV_EXAM_OPTIONS)
        form.addRow("شرکت مجدد:", self.prev_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1380, 1500)
        from datetime import datetime
        self.year_input.setValue(datetime.now().year)
        form.addRow("سال آزمون:", self.year_input)

        layout.addLayout(form)

        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("successBtn")
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _load_candidate(self) -> None:
        c = self.candidate
        self.name_input.setText(c.name)
        self.nid_input.setText(c.national_id)
        self.age_input.setValue(c.age)
        self.gender_input.setCurrentText(c.gender)
        self.field_input.setCurrentText(c.field)
        self.prev_input.setCurrentText(c.previous_exam)
        self.year_input.setValue(c.exam_year)

    def _on_save(self) -> None:
        if self.candidate is None:
            result = CandidateService.register(
                national_id=self.nid_input.text(),
                name=self.name_input.text(),
                age=self.age_input.value(),
                gender=self.gender_input.currentText(),
                field=self.field_input.currentText(),
                previous_exam=self.prev_input.currentText(),
                exam_year=self.year_input.value(),
            )
            if result.success:
                QMessageBox.information(
                    self, "موفق",
                    f"ثبت نام با موفقیت انجام شد.\nکد رهگیری: {result.candidate.tracking_code}"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "خطای اعتبارسنجی", result.message)
        else:
            ok = CandidateService.update(
                self.candidate.id,
                name=self.name_input.text(),
                national_id=self.nid_input.text(),
                age=self.age_input.value(),
                gender=self.gender_input.currentText(),
                field=self.field_input.currentText(),
                previous_exam=self.prev_input.currentText(),
                exam_year=self.year_input.value(),
            )
            if ok:
                QMessageBox.information(self, "موفق", "اطلاعات داوطلب با موفقیت ویرایش شد.")
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "ویرایش با خطا مواجه شد.")
