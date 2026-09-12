"""Analytics page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.analytics.analytics_engine import AnalyticsService
from app.repositories.repositories import CandidateRepository
from app.ui.widgets.mpl_canvas import MplCanvas
from app.ui.widgets.stat_card import StatCard


class AnalyticsPage(QWidget):
    """Statistics page with independent chart widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_analysis()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)
        title = QLabel("Analytics")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        layout.addWidget(title)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Exam year:"))
        self.year_filter = QComboBox()
        self.year_filter.addItem("All years", 0)
        for year in CandidateRepository.distinct_years():
            self.year_filter.addItem(str(year), year)
        self.year_filter.currentIndexChanged.connect(self.refresh_analysis)
        controls.addWidget(self.year_filter)
        reset = QPushButton("Reset")
        reset.clicked.connect(self._reset_filters)
        controls.addWidget(reset)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_analysis)
        controls.addWidget(refresh)
        controls.addStretch()
        layout.addLayout(controls)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def _reset_filters(self) -> None:
        self.year_filter.blockSignals(True)
        self.year_filter.setCurrentIndex(0)
        self.year_filter.blockSignals(False)
        self.refresh_analysis()

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_analysis(self) -> None:
        """Recalculate analytics and rebuild the dynamic content."""
        self._clear_content()
        year = self.year_filter.currentData() or None
        candidate_stats = AnalyticsService.get_candidate_analytics()
        score_stats = AnalyticsService.get_score_analytics(exam_year=year)

        cards = QHBoxLayout()
        cards.setSpacing(10)
        cards.addWidget(StatCard("Candidates", candidate_stats.total, "#1976D2", "C"))
        cards.addWidget(StatCard("Scores", score_stats.total_score_records, "#00897B", "S"))
        cards.addWidget(StatCard("With scores", score_stats.candidates_with_scores, "#8E24AA", "W"))
        cards.addWidget(StatCard("Average", f"{score_stats.overall_avg:.1f}", "#43A047", "A"))
        self.content_layout.addLayout(cards)

        histogram = MplCanvas(width=10, height=3.2)
        histogram.draw_histogram("Score distribution", self._score_values(year), bins=10, xlabel="Percent", ylabel="Count")
        self.content_layout.addWidget(histogram)

        pie = MplCanvas(width=10, height=3.2)
        pie.draw_pie("Score ranges", list(score_stats.score_distribution), list(score_stats.score_distribution.values()))
        self.content_layout.addWidget(pie)

        if score_stats.subject_averages:
            bar = MplCanvas(width=10, height=3.2)
            bar.draw_bar("Subject averages", list(score_stats.subject_averages), list(score_stats.subject_averages.values()), "Percent")
            self.content_layout.addWidget(bar)
        self.content_layout.addStretch()

    def refresh_data(self) -> None:
        """Refresh analytics after candidate or score data changes."""
        self.refresh_analysis()

    @staticmethod
    def _score_values(year: int | None) -> list[float]:
        from sqlalchemy import select
        from app.database.engine import get_session
        from app.models.entities import Candidate, Score

        statement = select(Score.percent)
        if year:
            statement = statement.join(Candidate, Score.candidate_id == Candidate.id).where(Candidate.exam_year == year)
        with get_session() as session:
            return [float(value) for value in session.execute(statement).scalars().all()]
