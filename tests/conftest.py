"""
Tests for the Sanjesh application.
Run with: pytest tests/ -v
"""

import os
import sys
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Use a temporary database for tests
TEST_DB = PROJECT_ROOT / "data" / "test_sanjesh.db"

_original_db_path = None


def pytest_configure(config):
    """Override database path before any test runs, saving original for restoration."""
    global _original_db_path
    from app.config.settings import Config
    cfg = Config()
    _original_db_path = cfg.database_path
    cfg.set("database_path", str(TEST_DB))


def pytest_sessionfinish(session, exitstatus):
    """Clean up test database and restore original settings."""
    global _original_db_path
    # Clean up test database files
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(TEST_DB) + suffix)
        if p.exists():
            p.unlink()
    # Restore original database path in settings
    if _original_db_path:
        from app.config.settings import Config
        cfg = Config()
        cfg._data["database_path"] = _original_db_path
        cfg.save()
