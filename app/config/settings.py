"""
Persistent application configuration.
Stores user preferences in a JSON file inside the data directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.constants import (
    DATA_DIR,
    DATABASE_PATH,
    SETTING_THEME,
    SETTING_THEME_LIGHT,
    SETTING_FONT_SIZE,
)

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS: dict[str, Any] = {
    SETTING_THEME: SETTING_THEME_LIGHT,
    SETTING_FONT_SIZE: 12,
    "database_path": str(DATABASE_PATH),
    "export_directory": str(DATA_DIR / "exports"),
    "backup_directory": str(DATA_DIR.parent / "backups"),
    "show_dashboard_on_startup": True,
    "auto_backup": False,
    "window_width": 1366,
    "window_height": 768,
    "max_recent_candidates": 20,
}

_CONFIG_PATH = DATA_DIR / "settings.json"


class Config:
    """Thread-safe, file-backed configuration singleton."""

    _instance: Config | None = None
    _data: dict[str, Any]

    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
            cls._instance._load()
        return cls._instance

    # ── Load / Save ─────────────────────────────────────────

    def _load(self) -> None:
        if _CONFIG_PATH.exists():
            try:
                with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
                    self._data = json.load(fh)
                logger.info("Configuration loaded from %s", _CONFIG_PATH)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load config: %s — using defaults", exc)
                self._data = {}
        # Apply defaults for missing keys
        for key, default in DEFAULT_SETTINGS.items():
            if key not in self._data:
                self._data[key] = default
        self.save()

    def save(self) -> None:
        """Persist current settings to disk."""
        try:
            _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_CONFIG_PATH, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, ensure_ascii=False, indent=2)
        except OSError as exc:
            logger.error("Failed to save config: %s", exc)

    # ── Accessors ────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def get_int(self, key: str, default: int = 0) -> int:
        return int(self._data.get(key, default))

    def get_bool(self, key: str, default: bool = False) -> bool:
        return bool(self._data.get(key, default))

    def get_str(self, key: str, default: str = "") -> str:
        return str(self._data.get(key, default))

    # ── Convenience ──────────────────────────────────────────

    @property
    def theme(self) -> str:
        return self.get_str(SETTING_THEME, SETTING_THEME_LIGHT)

    @theme.setter
    def theme(self, value: str) -> None:
        self.set(SETTING_THEME, value)

    @property
    def database_path(self) -> str:
        return self.get_str("database_path", str(DATABASE_PATH))

    @property
    def font_size(self) -> int:
        return self.get_int(SETTING_FONT_SIZE, 12)

    @property
    def window_width(self) -> int:
        return self.get_int("window_width", 1366)

    @property
    def window_height(self) -> int:
        return self.get_int("window_height", 768)
