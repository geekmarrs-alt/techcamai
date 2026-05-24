import importlib.util
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = REPO_ROOT / "worker" / "worker.py"

spec = importlib.util.spec_from_file_location("techcamai_worker", WORKER_PATH)
worker = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(worker)


def test_clip_capture_timeout_marks_alert_failed_and_cleans_partial_file(monkeypatch, tmp_path):
    worker.S.CLIPS_DIR = str(tmp_path)
    worker.S.CLIP_CAPTURE_ENABLED = 1
    worker.S.CLIP_DURATION_SEC = 12
    worker.S.CLIP_CAPTURE_TIMEOUT_SEC = 30

    calls = []
    updates = []

    def fake_run(cmd, check, stdout, stderr, timeout=None):
        calls.append({"cmd": cmd, "timeout": timeout})
        Path(cmd[2]).write_bytes(b"partial mp4")
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

    def fake_update(alert_id, clip_status, clip_path=None, clip_error=None):
        updates.append(
            {
                "alert_id": alert_id,
                "clip_status": clip_status,
                "clip_path": clip_path,
                "clip_error": clip_error,
            }
        )

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", fake_update)

    worker.capture_alert_clip(
        {"id": 7, "ip": "192.0.2.10", "username": "admin", "password": "secret", "channel": 1},
        {"id": 42, "created_at": "2026-05-24T11:00:00Z"},
    )

    assert calls[0]["timeout"] == 30
    out_path = Path(calls[0]["cmd"][2])
    assert not out_path.exists()
    assert updates[0]["alert_id"] == 42
    assert updates[0]["clip_status"] == "failed"
    assert updates[0]["clip_path"] is None
    assert "timed out after 30 seconds" in updates[0]["clip_error"]


def test_clip_capture_timeout_allows_longer_configured_durations():
    worker.S.CLIP_DURATION_SEC = 60
    worker.S.CLIP_CAPTURE_TIMEOUT_SEC = 30

    assert worker._clip_capture_timeout() == 75
