import subprocess
import sys
from concurrent.futures import Future
from pathlib import Path

import pytest

WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def test_main_schedules_alert_clips_without_running_capture_inline(monkeypatch):
    cam = {"id": 7, "ip": "10.0.0.7", "username": "admin", "password": "pw", "channel": 1}
    alert = {"id": 42, "created_at": "2026-06-07T11:00:00+00:00"}
    scheduled = []

    monkeypatch.setattr(worker, "get_cameras", lambda: [cam])
    monkeypatch.setattr(worker, "fetch_rtsp_frame", lambda _url: b"\xff\xd8frame")
    monkeypatch.setattr(worker, "motion_detect", lambda _prev, _cur: ("motion", 0.9))
    monkeypatch.setattr(worker, "jpeg_b64", lambda _jpeg: "snapshot")
    monkeypatch.setattr(worker, "post_detection", lambda *_args: {"triggered": [alert]})
    monkeypatch.setattr(worker, "schedule_alert_clip", lambda c, a: scheduled.append((c, a)))
    monkeypatch.setattr(worker, "_write_heartbeat", lambda: None)

    def stop_after_one_loop(_seconds):
        raise RuntimeError("stop")

    monkeypatch.setattr(worker.time, "sleep", stop_after_one_loop)

    with pytest.raises(RuntimeError, match="stop"):
        worker.main()

    assert scheduled == [(cam, alert)]


def test_schedule_alert_clip_submits_copies_to_executor(monkeypatch):
    submitted = []

    class RecordingExecutor:
        def submit(self, fn, *args):
            fut = Future()
            submitted.append((fn, args))
            fut.set_result(None)
            return fut

    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_ENABLED", 1)
    monkeypatch.setattr(worker, "_clip_executor", RecordingExecutor())

    cam = {"id": 1, "ip": "10.0.0.1"}
    alert = {"id": 99}
    fut = worker.schedule_alert_clip(cam, alert)
    cam["id"] = 2
    alert["id"] = 100

    assert fut is not None
    assert submitted[0][0] is worker.capture_alert_clip
    assert submitted[0][1] == ({"id": 1, "ip": "10.0.0.1"}, {"id": 99})


def test_capture_alert_clip_times_out_and_marks_failed(tmp_path, monkeypatch):
    calls = []
    updates = []

    monkeypatch.setattr(worker.S, "CLIPS_DIR", str(tmp_path))
    monkeypatch.setattr(worker.S, "CLIP_DURATION_SEC", 12)
    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_TIMEOUT_SEC", 3)
    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_ENABLED", 1)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        Path(cmd[2]).write_bytes(b"partial")
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    worker.capture_alert_clip(
        {"id": 5, "ip": "10.0.0.5", "username": "admin", "password": "secret", "channel": 1},
        {"id": 123, "created_at": "2026-06-07T11:00:00+00:00"},
    )

    cmd, kwargs = calls[0]
    assert cmd[:2] == ["/app/rtsp_clip.sh", "rtsp://admin:secret@10.0.0.5:554/Streaming/Channels/101"]
    assert cmd[3] == "12"
    assert kwargs["timeout"] == 17
    assert not Path(cmd[2]).exists()
    assert updates
    assert updates[0][0] == 123
    assert updates[0][1] == "failed"
    assert updates[0][2] is None
    assert "timed out" in updates[0][3]


def test_camera_rtsp_url_quotes_reserved_credential_characters():
    url = worker._camera_rtsp_url(
        {
            "ip": "192.168.1.10",
            "username": "admin@example",
            "password": "p:a#ss%",
            "channel": 2,
        }
    )

    assert url == "rtsp://admin%40example:p%3Aa%23ss%25@192.168.1.10:554/Streaming/Channels/201"
