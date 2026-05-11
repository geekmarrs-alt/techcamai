import sqlite3
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Mock environment before importing app.main to avoid side effects on real files
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test_migration.db")
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_dir

from app.main import _ensure_alert_columns

@pytest.fixture
def temp_db_path():
    fd, path_str = tempfile.mkstemp()
    os.close(fd)
    path = Path(path_str)
    yield path
    if path.exists():
        path.unlink()

def test_ensure_alert_columns_no_table(temp_db_path):
    """Verifies that the function returns early if the alert table does not exist."""
    # Ensure database exists but has no alert table
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute("CREATE TABLE other (id INTEGER)")

    with patch("app.main.db_path", temp_db_path):
        _ensure_alert_columns()

        with sqlite3.connect(temp_db_path) as conn:
            cur = conn.cursor()
            tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alert'").fetchall()
            assert len(tables) == 0

def test_ensure_alert_columns_migration(temp_db_path):
    """Verifies that the function correctly adds the missing columns to an existing alert table."""
    # Create alert table without the new columns
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute("CREATE TABLE alert (id INTEGER PRIMARY KEY, created_at TEXT)")

    with patch("app.main.db_path", temp_db_path):
        _ensure_alert_columns()

        with sqlite3.connect(temp_db_path) as conn:
            cur = conn.cursor()
            cols = {row[1] for row in cur.execute("PRAGMA table_info(alert)").fetchall()}
            assert "clip_path" in cols
            assert "clip_status" in cols
            assert "clip_error" in cols

            # Verify specific DDL for one column
            clip_status_info = [row for row in cur.execute("PRAGMA table_info(alert)").fetchall() if row[1] == "clip_status"][0]
            # row[4] is dflt_value, row[3] is notnull
            assert clip_status_info[3] == 1  # NOT NULL
            assert clip_status_info[4] == "'pending'"

def test_ensure_alert_columns_idempotent(temp_db_path):
    """Verifies that the function does not cause errors if the columns already exist."""
    # Create alert table with all columns
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute("""
            CREATE TABLE alert (
                id INTEGER PRIMARY KEY,
                clip_path TEXT,
                clip_status TEXT NOT NULL DEFAULT 'pending',
                clip_error TEXT
            )
        """)

    with patch("app.main.db_path", temp_db_path):
        # Should not raise any error
        _ensure_alert_columns()

        with sqlite3.connect(temp_db_path) as conn:
            cur = conn.cursor()
            cols = {row[1] for row in cur.execute("PRAGMA table_info(alert)").fetchall()}
            assert "clip_path" in cols
            assert "clip_status" in cols
            assert "clip_error" in cols
