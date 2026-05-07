import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

# Setup sys.path to import worker
REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_ROOT = REPO_ROOT / 'worker'
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

from worker import _alert_clip_relpath

def test_alert_clip_relpath_with_created_at():
    cam = {"id": 1}
    alert_id = 123
    created_at = "2024-05-20T15:30:00Z"

    rel_path = _alert_clip_relpath(cam, alert_id, created_at)

    # Expected: "1/20240520T153000Z-alert-123.mp4"
    assert rel_path == "1/20240520T153000Z-alert-123.mp4"

def test_alert_clip_relpath_without_created_at():
    cam = {"id": 2}
    alert_id = 456

    # Mock datetime.now to have a deterministic result
    mock_now = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

    with patch('worker.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now
        # We also need to make sure strftime works if called on the return value
        # But wait, worker.py does: ts = datetime.now(timezone.utc)
        # then ts.strftime(...)

        rel_path = _alert_clip_relpath(cam, alert_id)

    assert rel_path == "2/20240601T120000Z-alert-456.mp4"

def test_alert_clip_relpath_invalid_created_at():
    cam = {"id": 3}
    alert_id = 789
    created_at = "invalid-date"

    # When invalid, it should fall back to datetime.now()
    mock_now = datetime(2024, 7, 1, 10, 0, 0, tzinfo=timezone.utc)

    with patch('worker.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat.side_effect = Exception("invalid")

        rel_path = _alert_clip_relpath(cam, alert_id, created_at)

    assert rel_path == "3/20240701T100000Z-alert-789.mp4"

def test_alert_clip_relpath_missing_cam_id():
    cam = {}
    alert_id = 999
    created_at = "2024-08-01T08:00:00Z"

    rel_path = _alert_clip_relpath(cam, alert_id, created_at)

    # cam.get("id") or 0 => 0
    assert rel_path == "0/20240801T080000Z-alert-999.mp4"

def test_alert_clip_relpath_string_cam_id():
    cam = {"id": "5"}
    alert_id = 111
    created_at = "2024-09-01T09:00:00Z"

    rel_path = _alert_clip_relpath(cam, alert_id, created_at)

    assert rel_path == "5/20240901T090000Z-alert-111.mp4"
