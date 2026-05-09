import os
import tempfile
from datetime import datetime, timezone, timedelta

# Mocking env before imports
_tmp_dir = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(_tmp_dir, "test_utils.db")
os.environ["CLIPS_DIR"] = os.path.join(_tmp_dir, "clips")

from app.main import _fmt_dt_compact, _fmt_dt_full

def test_fmt_dt_compact_none():
    assert _fmt_dt_compact(None) == "—"

def test_fmt_dt_compact_naive():
    # Naive should be treated as UTC
    dt = datetime(2026, 3, 14, 12, 0, 0)
    assert _fmt_dt_compact(dt) == "14 Mar 12:00 UTC"

def test_fmt_dt_compact_utc():
    dt = datetime(2026, 3, 14, 12, 0, 0, tzinfo=timezone.utc)
    assert _fmt_dt_compact(dt) == "14 Mar 12:00 UTC"

def test_fmt_dt_compact_timezone_conversion():
    # US/Eastern is UTC-5 (or UTC-4 during DST)
    # Let's use a fixed offset to be sure
    est = timezone(timedelta(hours=-5))
    dt = datetime(2026, 3, 14, 7, 0, 0, tzinfo=est)
    # 07:00 EST should be 12:00 UTC
    assert _fmt_dt_compact(dt) == "14 Mar 12:00 UTC"

def test_fmt_dt_full_none():
    assert _fmt_dt_full(None) == "—"

def test_fmt_dt_full_utc():
    dt = datetime(2026, 3, 14, 12, 0, 0, tzinfo=timezone.utc)
    assert _fmt_dt_full(dt) == "2026-03-14 12:00:00 UTC"

def test_fmt_dt_full_naive():
    dt = datetime(2026, 3, 14, 12, 0, 0)
    assert _fmt_dt_full(dt) == "2026-03-14 12:00:00 UTC"
