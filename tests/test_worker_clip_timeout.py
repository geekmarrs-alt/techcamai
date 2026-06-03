import subprocess
import sys
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def test_fetch_rtsp_frame_uses_bounded_subprocess_timeout(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr(worker.S, "RTSP_CONNECT_TIMEOUT_SEC", 7)
    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    assert worker.fetch_rtsp_frame("rtsp://user:pass@10.0.0.5:554/Streaming/Channels/101") is None
    assert calls[0][1]["timeout"] == 7


def test_capture_alert_clip_timeout_marks_alert_failed_and_cleans_partial_file(tmp_path, monkeypatch):
    calls = []
    updates = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        Path(cmd[2]).write_bytes(b"partial mp4")
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    def fake_update_alert_clip(alert_id, clip_status, clip_path=None, clip_error=None):
        updates.append(
            {
                "alert_id": alert_id,
                "clip_status": clip_status,
                "clip_path": clip_path,
                "clip_error": clip_error,
            }
        )

    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))
    monkeypatch.setattr(worker.S, "CLIP_DURATION_SEC", 12)
    monkeypatch.setattr(worker.S, "RTSP_CONNECT_TIMEOUT_SEC", 3)
    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", fake_update_alert_clip)

    worker.capture_alert_clip(
        {"id": 5, "ip": "10.0.0.5", "username": "admin", "password": "secret", "channel": 1},
        {"id": 42, "created_at": "2024-01-01T12:00:00+00:00"},
    )

    assert calls[0][1]["timeout"] == 15
    assert len(updates) == 1
    assert updates[0]["alert_id"] == 42
    assert updates[0]["clip_status"] == "failed"
    assert updates[0]["clip_path"] is None
    assert "timed out" in updates[0]["clip_error"]
    assert list(tmp_path.rglob("*.mp4")) == []
