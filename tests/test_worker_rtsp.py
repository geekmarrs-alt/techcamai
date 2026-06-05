import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_ROOT = REPO_ROOT / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def _rtsp_frame_path(rtsp_url: str) -> Path:
    digest = hashlib.sha256(rtsp_url.encode("utf-8")).hexdigest()
    return Path(f"/tmp/techcamai_rtsp_{digest}.jpg")


def test_fetch_rtsp_frame_removes_stale_output_before_each_grab(monkeypatch):
    rtsp_url = "rtsp://admin:secret@10.0.0.10:554/Streaming/Channels/101"
    out_path = _rtsp_frame_path(rtsp_url)
    out_path.write_bytes(b"stale-frame")
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        assert kwargs["timeout"] == worker.S.RTSP_FRAME_TIMEOUT_SEC
        output = Path(cmd[2])
        assert output == out_path
        assert not output.exists()
        output.write_bytes(b"\xff\xd8fresh-frame-" + str(len(calls)).encode("ascii"))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    assert worker.fetch_rtsp_frame(rtsp_url) == b"\xff\xd8fresh-frame-1"
    assert not out_path.exists()
    assert worker.fetch_rtsp_frame(rtsp_url) == b"\xff\xd8fresh-frame-2"
    assert not out_path.exists()
    assert len(calls) == 2


def test_fetch_rtsp_frame_timeout_returns_none_and_cleans_output(monkeypatch):
    rtsp_url = "rtsp://admin:secret@10.0.0.20:554/Streaming/Channels/101"
    out_path = _rtsp_frame_path(rtsp_url)

    def fake_run(cmd, **kwargs):
        Path(cmd[2]).write_bytes(b"partial")
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    assert worker.fetch_rtsp_frame(rtsp_url) is None
    assert not out_path.exists()


def test_camera_rtsp_url_percent_encodes_userinfo():
    url = worker._camera_rtsp_url(
        {
            "ip": "10.0.0.30",
            "channel": 2,
            "username": "admin@example.com",
            "password": "p@ss:word/one#x?",
        }
    )

    assert url == (
        "rtsp://admin%40example.com:p%40ss%3Aword%2Fone%23x%3F"
        "@10.0.0.30:554/Streaming/Channels/201"
    )


def test_capture_alert_clip_times_out_and_marks_alert_failed(monkeypatch, tmp_path):
    updates = []

    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))
    monkeypatch.setattr(worker.S, "CLIP_DURATION_SEC", 2)
    monkeypatch.setattr(worker.S, "RTSP_CLIP_TIMEOUT_EXTRA_SEC", 3)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    def fake_run(cmd, **kwargs):
        assert kwargs["timeout"] == 5
        Path(cmd[2]).write_bytes(b"partial-clip")
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    worker.capture_alert_clip(
        {"id": 7, "ip": "10.0.0.40", "channel": 1, "username": "admin", "password": "secret"},
        {"id": 99, "created_at": "2026-06-05T11:00:00+00:00"},
    )

    assert len(updates) == 1
    alert_id, status, clip_path, clip_error = updates[0]
    assert alert_id == 99
    assert status == "failed"
    assert clip_path is None
    assert "timed out" in clip_error
    assert not any(tmp_path.rglob("*.mp4"))
