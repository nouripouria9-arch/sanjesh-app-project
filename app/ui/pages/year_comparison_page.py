"""
Exam-year comparison page — compare metrics across exam years.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.analytics.analytics_engine import AnalyticsService
from app.repositories.repositories import CandidateRepository
from app.ui.widgets.mpl_canvas import MplCanvas


class YearComparisonPage(QWidget):
    """Compare candidate and score metrics across exam years."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        title = QLabel("مقایسه سال‌های آزمون")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def refresh_data(self) -> None:
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        comp = AnalyticsService.get_year_comparison()
        years = sorted(comp.keys())

        if not years:
            empty = QLabel("هنوز داده‌ای برای مقایسه سال‌ها وجود ندارد.\nابتدا داوطلبانی با سال‌های آزمون مختلف ثبت کنید.")
            empty.setStyleSheet("color: #999; font-size: 14px; background: transparent; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty)
            return

        # ── Summary table ───────────────────────────────────
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        headers = ["سال", "تعداد داوطلب", "میانگین سن", "مرد", "زن", "میانگین نمره", "میانه نمره", "انحراف معیار"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(years))
        for row, year in enumerate(years):
            d = comp[year]
            table.setItem(row, 0, QTableWidgetItem(str(year)))
            table.setItem(row, 1, QTableWidgetItem(str(d["candidate_count"])))
            table.setItem(row, 2, QTableWidgetItem(str(d["avg_age"])))
            table.setItem(row, 3, QTableWidgetItem(str(d["male_count"])))
            table.setItem(row, 4, QTableWidgetItem(str(d["female_count"])))
            table.setItem(row, 5, QTableWidgetItem(f"{d['overall_avg']:.1f}%"))
            table.setItem(row, 6, QTableWidgetItem(f"{d['overall_median']:.1f}%"))
            table.setItem(row, 7, QTableWidgetItem(f"{d['overall_std']:.1f}"))
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setMaximumHeight(220)
        self.content_layout.addWidget(table)

        # ── Candidate count chart ───────────────────────────
        if len(years) >= 2:
            chart = MplCanvas(width=10, height=3.5)
            chart.draw_line(
                "تعداد داوطلبان بر اساس سال",
                [str(y) for y in years],
                [float(comp[y]["candidate_count"]) for y in years],
                "تعداد",
            )
            self.content_layout.addWidget(chart)

            # Average score comparison
            score_chart = MplCanvas(width=10, height=3.5)
            score_chart.draw_line(
                "میانگین نمرات بر اساس سال",
                [str(y) for y in years],
                [float(comp[y]["overall_avg"]) for y in years],
                "درصد",
            )
            self.content_layout.addWidget(score_chart)

            # Subject comparison across years (grouped bar)
            all_subjects = sorted({s for y in years for s in comp[y]["subject_averages"]})
            if all_subjects:
                grouped = MplCanvas(width=10, height=4)
                series = {}
                for year in years:
                    series[str(year)] = [comp[year]["subject_averages"].get(s, 0) for s in all_subjects]
                grouped.draw_grouped_bar("مقایسه نمرات دروس بین سال‌ها", all_subjects, series, "درصد")
                self.content_layout.addWidget(grouped)

        self.content_layout.addStretch()
