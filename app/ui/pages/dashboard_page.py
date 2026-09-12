"""Dashboard page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.analytics.analytics_engine import AnalyticsService
from app.repositories.repositories import ActivityLogRepository
from app.ui.widgets.mpl_canvas import MplCanvas
from app.ui.widgets.stat_card import StatCard


class DashboardPage(QWidget):
    """Main dashboard with summary cards and charts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_data(self) -> None:
        """Reload dashboard data and replace all dynamic widgets safely."""
        self._clear_content()
        candidate_stats = AnalyticsService.get_candidate_analytics()
        score_stats = AnalyticsService.get_score_analytics()

        cards = QHBoxLayout()
        cards.setSpacing(10)
        cards.addWidget(StatCard("Candidates", candidate_stats.total, "#1976D2", "C"))
        cards.addWidget(StatCard("Tajrobi", candidate_stats.total_tajrobi, "#26A69A", "T"))
        cards.addWidget(StatCard("Riazi", candidate_stats.total_riazi, "#8E24AA", "R"))
        cards.addWidget(StatCard("Score records", score_stats.total_score_records, "#00897B", "S"))
        self.content_layout.addLayout(cards)

        charts = QHBoxLayout()
        charts.setSpacing(10)
        gender = MplCanvas(width=5, height=3.2)
        gender.draw_pie("Gender distribution", list(candidate_stats.gender_distribution), list(candidate_stats.gender_distribution.values()))
        charts.addWidget(gender, 1)
        fields = MplCanvas(width=5, height=3.2)
        fields.draw_bar("Field distribution", list(candidate_stats.field_distribution), list(candidate_stats.field_distribution.values()), "Count")
        charts.addWidget(fields, 1)
        self.content_layout.addLayout(charts)

        if score_stats.subject_averages:
            subjects = MplCanvas(width=10, height=3.2)
            subjects.draw_bar("Subject averages", list(score_stats.subject_averages), list(score_stats.subject_averages.values()), "Percent")
            self.content_layout.addWidget(subjects)

        activity = QLabel("Recent activity")
        activity.setAlignment(Qt.AlignmentFlag.AlignRight)
        activity.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; background: transparent;")
        self.content_layout.addWidget(activity)
        for entry in ActivityLogRepository.recent(limit=10):
            item = QLabel(f"{entry.timestamp} - {entry.action} {entry.detail or ''}")
            item.setStyleSheet("background: white; border: 1px solid #e0e0e0; padding: 6px;")
            self.content_layout.addWidget(item)
        self.content_layout.addStretch()
