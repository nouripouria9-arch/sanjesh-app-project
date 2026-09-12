"""
Main application window — sidebar navigation + stacked pages.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.constants import APP_NAME, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from app.config.settings import Config
from app.ui.theme import get_theme
from app.ui.widgets.nav_button import SidebarButton
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.candidates_page import CandidatePage
from app.ui.pages.analytics_page import AnalyticsPage
from app.ui.pages.year_comparison_page import YearComparisonPage
from app.ui.pages.reports_page import ReportsPage
from app.ui.pages.import_export_page import ImportExportPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.database_page import DatabasePage
from app.ui.dialogs.candidate_dialog import CandidateDialog
from app.ui.dialogs.score_dialog import ScoreDialog


class MainWindow(QMainWindow):
    """Professional multi-view desktop application shell."""

    NAV_ITEMS = [
        ("داشبورد", "dashboard", "📊"),
        ("ثبت نام کنکور", "registration", "✍"),
        ("داوطلبان", "candidates", "👤"),
        ("تحلیل آماری", "analytics", "📈"),
        ("مقایسه سال‌ها", "years", "📅"),
        ("گزارش‌ها", "reports", "📄"),
        ("ورود / خروج", "import_export", "🔄"),
        ("پایگاه داده", "database", "🗄"),
        ("تنظیمات", "settings", "⚙"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        cfg = Config()
        self.resize(cfg.window_width, cfg.window_height)

        self._build_ui()
        self._apply_theme()
        self._navigate_to("dashboard")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ─────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("QFrame { background: #f5f7fa; border-right: 1px solid #e0e0e0; }")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 16, 8, 16)
        sb_layout.setSpacing(2)

        # App logo / title
        from PySide6.QtWidgets import QLabel
        logo = QLabel(f"  📋  {APP_NAME}")
        logo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; padding: 8px; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignRight)
        sb_layout.addWidget(logo)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #e0e0e0;")
        sb_layout.addWidget(separator)

        self.nav_buttons: dict[str, SidebarButton] = {}
        for text, nav_id, icon in self.NAV_ITEMS:
            btn = SidebarButton(text, nav_id, icon)
            btn.clicked_nav.connect(self._navigate_to)
            sb_layout.addWidget(btn)
            self.nav_buttons[nav_id] = btn

        sb_layout.addStretch()

        # Version label
        from app.constants import APP_VERSION
        ver_label = QLabel(f"  نسخه {APP_VERSION}")
        ver_label.setStyleSheet("font-size: 10px; color: #aaa; background: transparent;")
        sb_layout.addWidget(ver_label)

        main_layout.addWidget(sidebar)

        # ── Content area ────────────────────────────────────
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background: #f5f7fa; }")
        cl = QVBoxLayout(content_frame)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #f5f7fa;")
        cl.addWidget(self.stack)

        main_layout.addWidget(content_frame, stretch=1)

        # ── Create pages ────────────────────────────────────
        self.pages: dict[str, QWidget] = {}
        self._create_pages()

        # Status bar
        self.statusBar().showMessage("آماده")

    def _create_pages(self) -> None:
        # Dashboard
        self.pages["dashboard"] = DashboardPage()
        self.stack.addWidget(self.pages["dashboard"])

        # Candidates
        candidates_page = CandidatePage()
        candidates_page.request_add.connect(self._on_add_candidate)
        candidates_page.request_edit.connect(self._on_edit_candidate)
        candidates_page.request_score_edit.connect(self._on_edit_scores)
        self.pages["candidates"] = candidates_page
        self.stack.addWidget(candidates_page)

        # Analytics
        self.pages["analytics"] = AnalyticsPage()
        self.stack.addWidget(self.pages["analytics"])

        # Year comparison
        self.pages["years"] = YearComparisonPage()
        self.stack.addWidget(self.pages["years"])

        # Reports
        self.pages["reports"] = ReportsPage()
        self.stack.addWidget(self.pages["reports"])

        # Import/Export
        self.pages["import_export"] = ImportExportPage()
        self.stack.addWidget(self.pages["import_export"])

        # Database
        self.pages["database"] = DatabasePage()
        self.stack.addWidget(self.pages["database"])

        # Settings
        settings_page = SettingsPage()
        settings_page.theme_changed.connect(self._apply_theme)
        self.pages["settings"] = settings_page
        self.stack.addWidget(settings_page)

    def _navigate_to(self, nav_id: str) -> None:
        if nav_id == "registration":
            self._on_add_candidate()
            self._navigate_to("candidates")
            return
        if nav_id in self.pages:
            self.stack.setCurrentWidget(self.pages[nav_id])
            # Update button states
            for bid, btn in self.nav_buttons.items():
                btn.setChecked(bid == nav_id)
            self.statusBar().showMessage(
                next((t for t, nid, _ in self.NAV_ITEMS if nid == nav_id), "")
            )

    def _apply_theme(self) -> None:
        theme = Config().theme
        self.setStyleSheet(get_theme(theme))

    def _on_add_candidate(self) -> None:
        dlg = CandidateDialog(self)
        if dlg.exec() == CandidateDialog.DialogCode.Accepted:
            self.pages["candidates"].refresh_data()
            self.pages["dashboard"].refresh_data()
            self.statusBar().showMessage("داوطلب جدید ثبت نام شد")

    def _on_edit_candidate(self, candidate_id: int) -> None:
        from app.repositories.repositories import CandidateRepository
        candidate = CandidateRepository.get_by_id(candidate_id)
        if candidate:
            dlg = CandidateDialog(self, candidate)
            if dlg.exec() == CandidateDialog.DialogCode.Accepted:
                self.pages["candidates"].refresh_data()
                self.pages["dashboard"].refresh_data()

    def _on_edit_scores(self, candidate_id: int) -> None:
        try:
            dlg = ScoreDialog(candidate_id, self)
            if dlg.exec() == ScoreDialog.DialogCode.Accepted:
                self.pages["dashboard"].refresh_data()
                self.pages["analytics"].refresh_data()
        except Exception as exc:
            import logging
            from PySide6.QtWidgets import QMessageBox
            logging.getLogger(__name__).exception("Failed to edit candidate scores")
            QMessageBox.critical(self, "خطا", f"باز کردن فرم نمرات با خطا مواجه شد:\n{exc}")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        Config().set("window_width", event.size().width())
        Config().set("window_height", event.size().height())
