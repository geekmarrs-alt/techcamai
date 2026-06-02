import importlib.util
import subprocess
from pathlib import Path

import pytest


WORKER_PATH = Path(__file__).resolve().parents[1] / "worker" / "worker.py"


def load_worker(monkeypatch, tmp_path):
    monkeypatch.setenv("CLIPS_DIR", str(tmp_path / "clips"))
    monkeypatch.setenv("CLIP_DURATION_SEC", "2")
    spec = importlib.util.spec_from_file_location("techcamai_worker_under_test", WORKER_PATH)
    worker = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(worker)
    worker.S.CLIPS_DIR = str(tmp_path / "clips")
    worker.S.CLIP_DURATION_SEC = 2
    worker._PENDING_CLIP_FUTURES.clear()
    return worker


def test_capture_alert_clip_marks_ready_with_timeout(monkeypatch, tmp_path):
    worker = load_worker(monkeypatch, tmp_path)
    updates = []
    run_calls = []

    def fake_run(cmd, **kwargs):
        run_calls.append((cmd, kwargs))
        Path(cmd[2]).write_bytes(b"mp4")

    monkeypatch.setattr(worker, "_camera_rtsp_url", lambda cam: "rtsp://example/stream")
    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    worker.capture_alert_clip({"id": 7}, {"id": 42, "created_at": "2024-01-02T03:04:05+00:00"})

    assert run_calls[0][0] == ["/app/rtsp_clip.sh", "rtsp://example/stream", str(tmp_path / "clips" / "7/20240102T030405Z-alert-42.mp4"), "2"]
    assert run_calls[0][1]["timeout"] == 17
    assert updates == [(42, "ready", "7/20240102T030405Z-alert-42.mp4", None)]


def test_capture_alert_clip_timeout_marks_failed_and_removes_partial(monkeypatch, tmp_path):
    worker = load_worker(monkeypatch, tmp_path)
    updates = []
    partial = tmp_path / "clips" / "7/20240102T030405Z-alert-42.mp4"

    def fake_run(cmd, **kwargs):
        Path(cmd[2]).write_bytes(b"partial")
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr(worker, "_camera_rtsp_url", lambda cam: "rtsp://example/stream")
    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    worker.capture_alert_clip({"id": 7}, {"id": 42, "created_at": "2024-01-02T03:04:05+00:00"})

    assert not partial.exists()
    assert updates[0][0:3] == (42, "failed", None)
    assert "timed out" in updates[0][3]


def test_schedule_alert_clip_submits_without_running_inline(monkeypatch, tmp_path):
    worker = load_worker(monkeypatch, tmp_path)
    submitted = []

    class FakeFuture:
        def add_done_callback(self, callback):
            self.callback = callback

        def exception(self):
            return None

    class FakeExecutor:
        def submit(self, fn, *args):
            submitted.append((fn, args))
            return FakeFuture()

    monkeypatch.setattr(worker, "_CLIP_EXECUTOR", FakeExecutor())

    future = worker.schedule_alert_clip({"id": 1, "ip": "10.0.0.1"}, {"id": 99})

    assert future is not None
    assert len(submitted) == 1
    assert submitted[0][0] is worker.capture_alert_clip
    assert submitted[0][1] == ({"id": 1, "ip": "10.0.0.1"}, {"id": 99})


def test_main_schedules_triggered_alerts_instead_of_capturing_inline(monkeypatch, tmp_path):
    worker = load_worker(monkeypatch, tmp_path)
    scheduled = []

    monkeypatch.setattr(worker, "get_cameras", lambda: [{"id": 1, "ip": "10.0.0.1"}])
    monkeypatch.setattr(worker, "fetch_rtsp_frame", lambda rtsp: b"jpeg")
    monkeypatch.setattr(worker, "motion_detect", lambda prev, cur: ("motion", 0.9))
    monkeypatch.setattr(worker, "post_detection", lambda *args: {"triggered": [{"id": 123}]})
    monkeypatch.setattr(worker, "schedule_alert_clip", lambda cam, alert: scheduled.append((cam, alert)))
    monkeypatch.setattr(worker, "capture_alert_clip", lambda *args: pytest.fail("capture ran inline"))
    monkeypatch.setattr(worker, "_write_heartbeat", lambda: None)
    monkeypatch.setattr(worker.time, "sleep", lambda seconds: (_ for _ in ()).throw(StopIteration))

    with pytest.raises(StopIteration):
        worker.main()

    assert scheduled == [({"id": 1, "ip": "10.0.0.1"}, {"id": 123})]
