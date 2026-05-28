from __future__ import annotations

import sys
import threading
from concurrent.futures import Future
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))


def test_schedule_alert_clip_submits_capture_without_running_inline(monkeypatch):
    import worker

    submitted = []

    def capture_alert_clip(cam, alert):
        raise AssertionError("clip capture must not run inline")

    class RecordingExecutor:
        def submit(self, fn, *args):
            submitted.append((fn, args))
            future = Future()
            future.set_result(None)
            return future

    monkeypatch.setattr(worker.S, "CLIP_CAPTURE_ENABLED", 1)
    monkeypatch.setattr(worker, "_CLIP_EXECUTOR", RecordingExecutor())
    monkeypatch.setattr(worker, "_CLIP_CAPTURE_SLOTS", threading.BoundedSemaphore(1))
    monkeypatch.setattr(worker, "capture_alert_clip", capture_alert_clip)

    assert worker.schedule_alert_clip({"id": 7}, {"id": 42}) is True
    assert submitted == [(capture_alert_clip, ({"id": 7}, {"id": 42}))]
