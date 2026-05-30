import importlib.util
import subprocess
from pathlib import Path


def _load_worker_module():
    module_path = Path(__file__).resolve().parents[1] / "worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("techcamai_worker_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_schedule_alert_clip_submits_background_job(monkeypatch):
    worker = _load_worker_module()
    submitted = []

    class FakeExecutor:
        def submit(self, fn, *args):
            submitted.append((fn, args))
            return "future"

    monkeypatch.setattr(worker, "_CLIP_EXECUTOR", FakeExecutor())

    result = worker.schedule_alert_clip({"id": 7, "ip": "10.0.0.7"}, {"id": 123})

    assert result == "future"
    assert len(submitted) == 1
    fn, args = submitted[0]
    assert fn is worker.capture_alert_clip
    assert args == ({"id": 7, "ip": "10.0.0.7"}, {"id": 123})


def test_fetch_rtsp_frame_uses_process_timeout(monkeypatch, tmp_path):
    worker = _load_worker_module()
    captured = {}

    worker.S.RTSP_FRAME_TIMEOUT_SEC = 17

    def fake_run(args, **kwargs):
        captured["timeout"] = kwargs["timeout"]
        Path(args[2]).write_bytes(b"\xff\xd8jpeg")

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "open", lambda path, mode: Path(path).open(mode), raising=False)

    assert worker.fetch_rtsp_frame("rtsp://camera/stream") == b"\xff\xd8jpeg"
    assert captured["timeout"] == 17


def test_capture_alert_clip_uses_process_timeout_and_marks_ready(monkeypatch, tmp_path):
    worker = _load_worker_module()
    updates = []

    worker.S.CLIPS_DIR = str(tmp_path)
    worker.S.CLIP_DURATION_SEC = 12
    worker.S.CLIP_CAPTURE_TIMEOUT_SEC = 33

    def fake_run(args, **kwargs):
        assert kwargs["timeout"] == 33
        Path(args[2]).parent.mkdir(parents=True, exist_ok=True)
        Path(args[2]).write_bytes(b"mp4")

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    worker.capture_alert_clip(
        {"id": 4, "ip": "10.0.0.4", "username": "u", "password": "p", "channel": 1},
        {"id": 99, "created_at": "2026-05-30T11:00:00+00:00"},
    )

    assert updates == [(99, "ready", "4/20260530T110000Z-alert-99.mp4", None)]


def test_capture_alert_clip_timeout_marks_failed(monkeypatch, tmp_path):
    worker = _load_worker_module()
    updates = []

    worker.S.CLIPS_DIR = str(tmp_path)
    worker.S.CLIP_CAPTURE_TIMEOUT_SEC = 1

    def fake_run(args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "update_alert_clip", lambda *args: updates.append(args))

    worker.capture_alert_clip(
        {"id": 5, "ip": "10.0.0.5", "username": "u", "password": "p", "channel": 1},
        {"id": 100, "created_at": "2026-05-30T11:00:00+00:00"},
    )

    assert len(updates) == 1
    assert updates[0][0:3] == (100, "failed", None)
    assert "timed out" in updates[0][3]
