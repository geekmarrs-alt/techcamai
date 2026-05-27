import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_ROOT = REPO_ROOT / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def test_camera_rtsp_url_quotes_credentials():
    url = worker._camera_rtsp_url({
        "ip": "10.0.0.5",
        "channel": 2,
        "username": "admin@example.com",
        "password": "p@ss:word/100%",
    })

    assert url == "rtsp://admin%40example.com:p%40ss%3Aword%2F100%25@10.0.0.5:554/Streaming/Channels/201"


def test_worker_headers_include_token(monkeypatch):
    monkeypatch.setattr(worker.S, "WORKER_TOKEN", "secret-token")

    assert worker._worker_headers() == {"X-Worker-Token": "secret-token"}


def test_fetch_rtsp_frame_uses_bounded_subprocess_timeout(monkeypatch):
    calls = {}

    def fake_run(cmd, check, stdout, stderr, timeout):
        calls["cmd"] = cmd
        calls["timeout"] = timeout
        Path(cmd[2]).write_bytes(b"\xff\xd8jpeg")

    monkeypatch.setattr(worker.S, "RTSP_CONNECT_TIMEOUT_SEC", 3)
    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    assert worker.fetch_rtsp_frame("rtsp://u:p@10.0.0.5/stream") == b"\xff\xd8jpeg"
    assert calls["cmd"][:2] == ["/app/rtsp_grab.sh", "rtsp://u:p@10.0.0.5/stream"]
    assert calls["timeout"] == 18


def test_capture_alert_clip_uses_bounded_subprocess_timeout(monkeypatch, tmp_path):
    calls = {}
    updates = []

    def fake_run(cmd, check, stdout, stderr, timeout):
        calls["cmd"] = cmd
        calls["timeout"] = timeout
        Path(cmd[2]).write_bytes(b"mp4")

    def fake_update(alert_id, clip_status, clip_path=None, clip_error=None):
        updates.append((alert_id, clip_status, clip_path, clip_error))

    monkeypatch.setattr(worker.S, "RTSP_CONNECT_TIMEOUT_SEC", 5)
    monkeypatch.setattr(worker.S, "CLIP_DURATION_SEC", 12)
    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))
    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", fake_update)

    worker.capture_alert_clip(
        {"id": 4, "ip": "10.0.0.6", "channel": 1, "username": "u", "password": "p"},
        {"id": 7, "created_at": "2024-01-01T12:00:00+00:00"},
    )

    assert calls["cmd"][0] == "/app/rtsp_clip.sh"
    assert calls["cmd"][3] == "12"
    assert calls["timeout"] == 32
    assert updates == [(7, "ready", "4/20240101T120000Z-alert-7.mp4", None)]
