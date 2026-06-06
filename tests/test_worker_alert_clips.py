import subprocess
import sys
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def _cam() -> dict:
    return {
        "id": 7,
        "ip": "10.0.0.7",
        "username": "admin",
        "password": "secret",
        "channel": 1,
    }


def _alert() -> dict:
    return {"id": 42, "created_at": "2026-06-06T11:00:00Z"}


def test_capture_alert_clip_keeps_file_when_ready_update_fails(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))
    monkeypatch.setattr(worker.S, "CLIP_DURATION_SEC", 12)

    rel_path = worker._alert_clip_relpath(_cam(), 42, _alert()["created_at"])
    out_path = tmp_path / rel_path
    updates = []

    def fake_run(cmd, **kwargs):
        assert kwargs["timeout"] == 12 + worker.CLIP_CONNECT_TIMEOUT_SEC
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"valid mp4 bytes")

    def fake_update(alert_id, clip_status, clip_path=None, clip_error=None):
        updates.append((alert_id, clip_status, clip_path, clip_error))
        if clip_status == "ready":
            raise RuntimeError("api temporarily down")
        raise AssertionError("successful clips must not be marked failed")

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", fake_update)

    worker.capture_alert_clip(_cam(), _alert())

    assert out_path.read_bytes() == b"valid mp4 bytes"
    assert updates == [(42, "ready", rel_path, None)]
    assert "metadata update failed" in capsys.readouterr().out


def test_capture_alert_clip_cleans_partial_file_on_capture_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))

    rel_path = worker._alert_clip_relpath(_cam(), 42, _alert()["created_at"])
    out_path = tmp_path / rel_path
    updates = []

    def fake_run(cmd, **kwargs):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"partial")
        raise subprocess.CalledProcessError(1, cmd)

    def fake_update(alert_id, clip_status, clip_path=None, clip_error=None):
        updates.append((alert_id, clip_status, clip_path, clip_error))

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", fake_update)

    worker.capture_alert_clip(_cam(), _alert())

    assert not out_path.exists()
    assert updates[0][0] == 42
    assert updates[0][1] == "failed"
    assert updates[0][2] is None
    assert "returned non-zero exit status" in updates[0][3]


def test_fetch_rtsp_frame_uses_bounded_subprocess_timeout(monkeypatch, tmp_path):
    frame_path = None

    def fake_run(cmd, **kwargs):
        nonlocal frame_path
        assert kwargs["timeout"] == worker.RTSP_GRAB_TIMEOUT_SEC
        frame_path = Path(cmd[2])
        frame_path.write_bytes(b"\xff\xd8jpeg")

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    try:
        assert worker.fetch_rtsp_frame("rtsp://example.test/stream") == b"\xff\xd8jpeg"
    finally:
        if frame_path and frame_path.exists():
            frame_path.unlink()


def test_camera_rtsp_url_escapes_credentials():
    cam = {
        "ip": "10.0.0.7",
        "username": "admin@example.com",
        "password": "p@ss:word/space #",
        "channel": 2,
    }

    assert worker._camera_rtsp_url(cam) == (
        "rtsp://admin%40example.com:p%40ss%3Aword%2Fspace%20%23"
        "@10.0.0.7:554/Streaming/Channels/201"
    )
