"""
SQLite3 database connection management with SQLAlchemy.

Handles connection lifecycle, schema creation, foreign-key enforcement,
and session factory.
"""

from __future__ import annotations

import logging
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import event, text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.settings import Config

logger = logging.getLogger(__name__)


# ── Base ────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Engine & Session Factory ────────────────────────────────

_engine = None
_SessionFactory = None


def _get_database_url() -> str:
    cfg = Config()
    path = Path(cfg.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def initialize_database() -> None:
    """Create engine, session factory, and tables."""
    global _engine, _SessionFactory

    # Tests and restore operations may initialize the database more than once.
    # Close the previous pool before replacing its global reference.
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionFactory = None

    url = _get_database_url()
    _engine = create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

    # Enable WAL mode and foreign keys for every connection
    @event.listens_for(_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)

    # Create tables
    Base.metadata.create_all(_engine)
    logger.info("Database initialized: %s", url)


def shutdown_database() -> None:
    """Dispose engine on application exit."""
    global _engine, _SessionFactory
    engine = _engine
    _engine = None
    _SessionFactory = None
    if engine is not None:
        engine.dispose()
        logger.info("Database connections closed.")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional ORM session scope."""
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_engine():
    """Return the current SQLAlchemy engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized.")
    return _engine


def execute_raw(sql: str, params: dict | None = None) -> list:
    """Execute raw SQL and return fetched results."""
    with get_session() as session:
        result = session.execute(text(sql), params or {})
        return result.fetchall()


def get_table_count(table_name: str) -> int:
    """Return row count for a given table."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("Invalid table name.")
    with get_session() as session:
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()


def backup_database(backup_path: Path) -> bool:
    """Copy the current database file to a backup path."""
    import shutil
    source = Path(Config().database_path)
    if not source.exists():
        logger.error("Source database does not exist: %s", source)
        return False
    try:
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup_path)
        logger.info("Database backed up to %s", backup_path)
        return True
    except OSError as exc:
        logger.error("Backup failed: %s", exc)
        return False


def restore_database(backup_path: Path) -> bool:
    """Restore database from a backup file."""
    import shutil
    if not backup_path.exists():
        logger.error("Backup file does not exist: %s", backup_path)
        return False
    target = Path(Config().database_path)
    try:
        shutdown_database()
        shutil.copy2(backup_path, target)
        initialize_database()
        logger.info("Database restored from %s", backup_path)
        return True
    except Exception as exc:
        logger.error("Restore failed: %s", exc)
        return False
