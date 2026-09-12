"""
Application constants and domain configuration.
Sanjesh (Konkur) Registration & Analytics System.
"""

from pathlib import Path

# ── Application Info ────────────────────────────────────────
APP_NAME = "سامانه جامع سنجش"
APP_NAME_EN = "Sanjesh System"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Sanjesh Engineering Team"

# ── Paths ───────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
BACKUP_DIR = APP_DIR / "backups"
ASSETS_DIR = APP_DIR / "app" / "assets"
LOGS_DIR = DATA_DIR / "logs"
EXPORTS_DIR = DATA_DIR / "exports"

# Ensure directories exist
for d in (DATA_DIR, BACKUP_DIR, LOGS_DIR, EXPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Database ────────────────────────────────────────────────
DATABASE_PATH = DATA_DIR / "sanjesh.db"

# ── Exam Capacities (from original project) ─────────────────
TOTAL_CAPACITY = 1_200_000
TAJRABI_CAPACITY = 700_000
RIAZI_CAPACITY = 500_000

# ── Subject Definitions ─────────────────────────────────────
TAJRABI_SUBJECTS = [
    "زیست", "شیمی", "فیزیک", "ریاضی", "زمین شناسی"
]
RIAZI_SUBJECTS = [
    "حسابان", "گسسته", "هندسه", "فیزیک", "شیمی", "زمین شناسی"
]

# ── Gender Options ──────────────────────────────────────────
GENDER_MALE = "مرد"
GENDER_FEMALE = "زن"
GENDER_OPTIONS = [GENDER_MALE, GENDER_FEMALE]

# ── Field (رشته) Options ───────────────────────────────────
FIELD_TAJRABI = "تجربی"
FIELD_RIAZI = "ریاضی"
FIELD_OPTIONS = [FIELD_TAJRABI, FIELD_RIAZI]

# ── Previous Exam ───────────────────────────────────────────
PREV_EXAM_YES = "بله"
PREV_EXAM_NO = "خیر"
PREV_EXAM_OPTIONS = [PREV_EXAM_YES, PREV_EXAM_NO]

# ── UI Constants ────────────────────────────────────────────
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 750
SIDEBAR_WIDTH = 240
SIDEBAR_COLLAPSED_WIDTH = 60

# ── Pagination ──────────────────────────────────────────────
DEFAULT_PAGE_SIZE = 50

# ── Application Settings Keys ───────────────────────────────
SETTING_THEME = "theme"
SETTING_THEME_DARK = "dark"
SETTING_THEME_LIGHT = "light"
SETTING_FONT_SIZE = "font_size"
SETTING_DB_PATH = "database_path"
SETTING_LANGUAGE = "language"

# ── Stats Card Colors ───────────────────────────────────────
COLOR_PRIMARY = "#1976D2"
COLOR_SECONDARY = "#26A69A"
COLOR_SUCCESS = "#43A047"
COLOR_WARNING = "#FFA000"
COLOR_DANGER = "#E53935"
COLOR_INFO = "#5C6BC0"
COLOR_PURPLE = "#8E24AA"
COLOR_TEAL = "#00897B"
COLOR_ORANGE = "#FB8C00"
COLOR_PINK = "#D81B60"

# ── Chart Colors ────────────────────────────────────────────
CHART_COLORS = [
    "#1976D2", "#26A69A", "#E53935", "#FFA000",
    "#8E24AA", "#5C6BC0", "#FB8C00", "#D81B60",
    "#00897B", "#43A047", "#5D4037", "#757575",
]

# ── File Extensions ─────────────────────────────────────────
EXT_CSV = ".csv"
EXT_EXCEL = ".xlsx"
EXT_JSON = ".json"
EXT_DB = ".db"
EXT_BACKUP = ".bak"
EXT_PDF = ".pdf"
