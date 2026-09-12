"""
Score entry dialog — percentages per subject for a candidate.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.constants import RIAZI_SUBJECTS, TAJRABI_SUBJECTS
from app.repositories.repositories import CandidateRepository, ScoreRepository
from app.services.candidate_service import ScoreService


class ScoreDialog(QDialog):
    """Enter or edit a candidate's subject scores."""

    def __init__(self, candidate_id: int, parent=None):
        super().__init__(parent)
        self.candidate_id = candidate_id
        self.candidate = CandidateRepository.get_by_id(candidate_id)
        if self.candidate is None:
            raise ValueError("Candidate not found")

        self.setWindowTitle(f"نمرات — {self.candidate.name}")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"ثبت نمرات: {self.candidate.name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subjects = TAJRABI_SUBJECTS if self.candidate.field == "تجربی" else RIAZI_SUBJECTS
        existing = ScoreRepository.get_scores(self.candidate_id)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.spinboxes: dict[str, QDoubleSpinBox] = {}
        for subject in subjects:
            spin = QDoubleSpinBox()
            spin.setRange(0, 100)
            spin.setDecimals(2)
            spin.setSuffix(" %")
            spin.setValue(existing.get(subject, 0.0))
            form.addRow(f"{subject}:", spin)
            self.spinboxes[subject] = spin

        layout.addLayout(form)

        buttons = QHBoxLayout()
        save_btn = QPushButton("ذخیره نمرات")
        save_btn.setObjectName("successBtn")
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _on_save(self) -> None:
        scores = {subject: spin.value() for subject, spin in self.spinboxes.items()}
        if ScoreService.set_scores(self.candidate_id, scores):
            QMessageBox.information(self, "موفق", "نمرات با موفقیت ذخیره شد.")
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", "ذخیره نمرات با خطا مواجه شد.")
