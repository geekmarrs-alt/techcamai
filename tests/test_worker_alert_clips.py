import importlib.util
from pathlib import Path


def _load_worker_module():
    worker_path = Path(__file__).resolve().parents[1] / "worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("techcamai_worker_under_test", worker_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_camera_rtsp_url_escapes_reserved_credential_chars():
    worker = _load_worker_module()

    url = worker._camera_rtsp_url(
        {
            "ip": "10.0.0.5",
            "channel": 2,
            "username": "admin@example.com",
            "password": "pa:ss@word#1%",
        }
    )

    assert url == (
        "rtsp://admin%40example.com:pa%3Ass%40word%231%25"
        "@10.0.0.5:554/Streaming/Channels/201"
    )


def test_schedule_alert_clip_submits_without_running_capture_inline(monkeypatch):
    worker = _load_worker_module()
    submitted = []

    class RecordingExecutor:
        def submit(self, fn, cam, alert):
            submitted.append((fn, cam, alert))
            return "queued"

    def capture_should_not_run_inline(cam, alert):
        raise AssertionError("clip capture ran synchronously")

    monkeypatch.setattr(worker, "_CLIP_EXECUTOR", RecordingExecutor())
    monkeypatch.setattr(worker, "capture_alert_clip", capture_should_not_run_inline)
    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_ENABLED", 1)

    cam = {"id": 7, "ip": "10.0.0.7"}
    alert = {"id": 42, "created_at": "2026-05-31T11:00:00+00:00"}

    result = worker.schedule_alert_clip(cam, alert)

    assert result == "queued"
    assert len(submitted) == 1
    assert submitted[0][0] is capture_should_not_run_inline
    assert submitted[0][1] == cam
    assert submitted[0][1] is not cam
    assert submitted[0][2] == alert
    assert submitted[0][2] is not alert


def test_schedule_alert_clip_respects_disabled_capture(monkeypatch):
    worker = _load_worker_module()

    class FailingExecutor:
        def submit(self, fn, cam, alert):
            raise AssertionError("disabled clip capture should not submit work")

    monkeypatch.setattr(worker, "_CLIP_EXECUTOR", FailingExecutor())
    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_ENABLED", 0)

    assert worker.schedule_alert_clip({"id": 1}, {"id": 2}) is None
