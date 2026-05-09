import sys
import os
from pathlib import Path
import pytest
import httpx
import base64
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# Add worker directory to sys.path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'worker'))

import worker

def test_parse_urls():
    assert worker.parse_urls("http://a.com, http://b.com") == ["http://a.com", "http://b.com"]
    assert worker.parse_urls("") == []
    assert worker.parse_urls(None) == []
    assert worker.parse_urls("  ") == []

def test_jpeg_b64():
    data = b"\xff\xd8\xff\xe0"
    expected = base64.b64encode(data).decode("ascii")
    assert worker.jpeg_b64(data) == expected
    assert worker.jpeg_b64(None) is None

def test_motion_detect_no_cur():
    label, conf = worker.motion_detect(b"prev", None)
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_no_prev():
    label, conf = worker.motion_detect(None, b"cur")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_identical():
    label, conf = worker.motion_detect(b"same", b"same")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_different():
    # Different JPEGs should produce some confidence
    prev = b"\xff\xd8" + b"A" * 100
    cur = b"\xff\xd8" + b"B" * 200
    label, conf = worker.motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0.0

def test_camera_snapshot_url():
    cam = {"ip": "1.2.3.4", "scheme": "http", "channel": 2}
    url = worker._camera_snapshot_url(cam)
    assert url == "http://1.2.3.4/ISAPI/Streaming/channels/2/picture"

    cam_default = {"ip": "1.2.3.4"}
    assert worker._camera_snapshot_url(cam_default) == "https://1.2.3.4/ISAPI/Streaming/channels/1/picture"

def test_camera_rtsp_url():
    cam = {"ip": "1.2.3.4", "username": "user", "password": "pass", "channel": 1}
    url = worker._camera_rtsp_url(cam)
    assert url == "rtsp://user:pass@1.2.3.4:554/Streaming/Channels/101"

    cam_ch2 = {"ip": "1.2.3.4", "username": "user", "password": "pass", "channel": 2}
    assert worker._camera_rtsp_url(cam_ch2) == "rtsp://user:pass@1.2.3.4:554/Streaming/Channels/201"

    cam_ch102 = {"ip": "1.2.3.4", "username": "user", "password": "pass", "channel": 102}
    assert worker._camera_rtsp_url(cam_ch102) == "rtsp://user:pass@1.2.3.4:554/Streaming/Channels/102"

def test_camera_auth_basic():
    cam = {"username": "u", "password": "p", "auth": "basic"}
    auth = worker._camera_auth(cam)
    assert isinstance(auth, httpx.BasicAuth)

def test_camera_auth_digest():
    cam = {"username": "u", "password": "p", "auth": "digest"}
    auth = worker._camera_auth(cam)
    assert isinstance(auth, httpx.DigestAuth)

def test_camera_auth_none():
    cam = {"ip": "1.2.3.4"}
    assert worker._camera_auth(cam) is None

def test_alert_clip_relpath():
    cam = {"id": 123}
    created_at = "2024-05-01T12:00:00Z"
    path = worker._alert_clip_relpath(cam, 456, created_at)
    assert path == "123/20240501T120000Z-alert-456.mp4"

    # Test fallback to now
    path_now = worker._alert_clip_relpath(cam, 456, "invalid")
    assert "123/" in path_now
    assert "-alert-456.mp4" in path_now

def test_fetch_snapshot_bytes_success(mocker):
    mock_response = mocker.Mock()
    mock_response.content = b"\xff\xd8 image data"
    mock_response.headers = {"content-type": "image/jpeg"}
    mock_response.raise_for_status = mocker.Mock()

    mock_client = mocker.patch("httpx.Client")
    mock_client.return_value.__enter__.return_value.get.return_value = mock_response

    res = worker.fetch_snapshot_bytes("http://test.com")
    assert res == b"\xff\xd8 image data"

def test_fetch_snapshot_bytes_fail(mocker):
    mock_client = mocker.patch("httpx.Client")
    mock_client.return_value.__enter__.return_value.get.side_effect = Exception("fail")

    res = worker.fetch_snapshot_bytes("http://test.com")
    assert res is None

def test_fetch_rtsp_frame_success(mocker):
    mocker.patch("subprocess.run")
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"\xff\xd8 frame"))

    res = worker.fetch_rtsp_frame("rtsp://test")
    assert res == b"\xff\xd8 frame"

def test_fetch_rtsp_frame_fail(mocker):
    mocker.patch("subprocess.run", side_effect=Exception("fail"))

    res = worker.fetch_rtsp_frame("rtsp://test")
    assert res is None

def test_post_detection(mocker):
    mock_client = mocker.patch("httpx.Client")
    mock_client.return_value.__enter__.return_value.post.return_value.json.return_value = {"ok": True}

    res = worker.post_detection("url", "label", 0.9, "snap", 1)
    assert res == {"ok": True}

    # Check that it was called with correct payload
    args, kwargs = mock_client.return_value.__enter__.return_value.post.call_args
    assert kwargs["json"]["label"] == "label"
    assert kwargs["json"]["camera_id"] == 1

def test_update_alert_clip(mocker):
    mock_client = mocker.patch("httpx.Client")
    mock_client.return_value.__enter__.return_value.put.return_value.json.return_value = {"ok": True}

    res = worker.update_alert_clip(1, "ready", "path")
    assert res == {"ok": True}

    args, kwargs = mock_client.return_value.__enter__.return_value.put.call_args
    assert kwargs["json"]["clip_status"] == "ready"
    assert kwargs["json"]["clip_path"] == "path"

def test_capture_alert_clip_success(mocker):
    # Setup mocks
    mocker.patch("worker.S.CLIP_CAPTURE_ENABLED", 1)
    mocker.patch("worker.S.CLIPS_DIR", "/tmp/clips")
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("subprocess.run")
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.stat", return_value=mocker.Mock(st_size=100))
    mock_update = mocker.patch("worker.update_alert_clip")

    cam = {"id": 1, "ip": "1.1.1.1"}
    alert = {"id": 10, "created_at": "2024-01-01T00:00:00Z"}

    worker.capture_alert_clip(cam, alert)

    mock_update.assert_called_with(10, "ready", mocker.ANY, None)

def test_write_heartbeat(mocker):
    mock_path = mocker.patch("pathlib.Path.write_text")
    worker._write_heartbeat()
    mock_path.assert_called_once()
    args, _ = mock_path.call_args
    data = json.loads(args[0])
    assert "ts" in data
    assert "unix_ts" in data
