"""
Sanjesh — University Entrance Exam Management System.
Professional PySide6 + SQLite3 desktop application.

Entry point: initializes database, logging, services, and launches the GUI.
"""

import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt

# Ensure the project root is on sys.path so `app.*` imports resolve.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def main() -> int:
    from PySide6.QtWidgets import QApplication

    # ── 1. Initialize configuration ────────────────────────
    from app.config.logger import setup_logging
    setup_logging()

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Sanjesh application starting...")

    # ── 2. Create Qt application ───────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName("Sanjesh")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Sanjesh Engineering")
    # Persian is the primary application language; keep every view RTL.
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # Set high-DPI support
    app.setStyle("Fusion")

    # ── 3. Initialize database ─────────────────────────────
    from app.database.engine import initialize_database, shutdown_database
    from app.models.entities import Candidate, Score, ExamYear, ActivityLog  # noqa: ensure models registered

    initialize_database()
    logger.info("Database initialized successfully.")

    # ── 4. Seed default exam year if empty ──────────────────
    from app.repositories.repositories import ExamYearRepository, CandidateRepository
    from datetime import datetime
    current_year = datetime.now().year
    existing_years = ExamYearRepository.years()
    if not existing_years:
        ExamYearRepository.get_or_create(current_year)
        logger.info("Seeded default exam year: %d", current_year)

    # ── 5. Create and show main window ─────────────────────
    from app.ui.main_window import MainWindow
    from app.ui.theme import get_theme
    from app.config.settings import Config

    window = MainWindow()
    window.setStyleSheet(get_theme(Config().theme))
    window.show()
    logger.info("Main window shown.")

    # ── 6. Run event loop ──────────────────────────────────
    exit_code = app.exec()

    # ── 7. Shutdown ────────────────────────────────────────
    shutdown_database()
    logger.info("Sanjesh application exited with code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
