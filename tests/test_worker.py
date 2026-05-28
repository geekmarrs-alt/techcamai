import base64
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from worker import worker

# Mock Settings for tests
worker.S.API_BASE_URL = "http://testserver"
worker.S.CLIPS_DIR = "/tmp/techcamai_test_clips"
worker.S.CLIP_CAPTURE_ENABLED = 1


def test_parse_urls():
    assert worker.parse_urls("") == []
    assert worker.parse_urls("http://a.com , http://b.com") == ["http://a.com", "http://b.com"]
    assert worker.parse_urls(None) == []

def test_jpeg_b64():
    data = b"\xff\xd8\xff\xe0"
    encoded = base64.b64encode(data).decode("ascii")
    assert worker.jpeg_b64(data) == encoded
    assert worker.jpeg_b64(None) is None

def test_fake_detect():
    label, conf = worker.fake_detect()
    assert label in ["person", "vehicle"]
    assert 0.3 <= conf <= 0.99

def test_alert_clip_relpath():
    cam = {"id": 5}
    alert_id = 123
    created_at = "2024-01-01T12:00:00Z"
    path = worker._alert_clip_relpath(cam, alert_id, created_at)
    assert path == "5/20240101T120000Z-alert-123.mp4"

    # Test without created_at (should not crash)
    path2 = worker._alert_clip_relpath(cam, alert_id)
    assert "5/" in path2
    assert "-alert-123.mp4" in path2

def test_camera_snapshot_url():
    cam = {"ip": "1.2.3.4", "scheme": "http", "channel": 2}
    url = worker._camera_snapshot_url(cam)
    assert url == "http://1.2.3.4/ISAPI/Streaming/channels/2/picture"

    # Default scheme/channel
    cam2 = {"ip": "1.2.3.4"}
    url2 = worker._camera_snapshot_url(cam2)
    assert url2 == "https://1.2.3.4/ISAPI/Streaming/channels/1/picture"

def test_camera_rtsp_url():
    cam = {"ip": "1.2.3.4", "username": "u", "password": "p", "channel": 1}
    url = worker._camera_rtsp_url(cam)
    assert url == "rtsp://u:p@1.2.3.4:554/Streaming/Channels/101"

    cam2 = {"ip": "1.2.3.4", "username": "u", "password": "p", "channel": 102}
    url2 = worker._camera_rtsp_url(cam2)
    assert url2 == "rtsp://u:p@1.2.3.4:554/Streaming/Channels/102"

def test_camera_auth():
    cam_basic = {"username": "u", "password": "p", "auth": "basic"}
    auth = worker._camera_auth(cam_basic)
    assert isinstance(auth, httpx.BasicAuth)

    cam_digest = {"username": "u", "password": "p", "auth": "digest"}
    auth2 = worker._camera_auth(cam_digest)
    assert isinstance(auth2, httpx.DigestAuth)

    cam_none = {"ip": "1.2.3.4"}
    assert worker._camera_auth(cam_none) is None

def test_motion_detect():
    # No current frame
    assert worker.motion_detect(b"prev", None) == ("motion", 0.0)

    # No previous frame
    assert worker.motion_detect(None, b"cur") == ("motion", 0.0)

    # Identical frames
    assert worker.motion_detect(b"same", b"same") == ("motion", 0.0)

    # Different frames (minor change)
    prev = b"a" * 1000
    cur = b"a" * 1001 # Small size change
    label, conf = worker.motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0

    # Large difference
    prev = b"\x00" * 1000
    cur = b"\xff" * 2000
    label2, conf2 = worker.motion_detect(prev, cur)
    assert label2 == "motion"
    assert conf2 > conf

def test_get_cameras_success():
    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = [{"id": 1, "ip": "1.1.1.1"}]

        cams = worker.get_cameras()
        assert len(cams) == 1
        assert cams[0]["id"] == 1

def test_post_detection():
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"ok": True, "triggered": []}

        res = worker.post_detection("http://snap", "motion", 0.5, "base64", 1)
        assert res["ok"] is True

def test_update_alert_clip():
    with patch("httpx.Client.put") as mock_put:
        mock_put.return_value = MagicMock(status_code=200)
        mock_put.return_value.json.return_value = {"ok": True}

        res = worker.update_alert_clip(123, "ready", "path/to/clip")
        assert res["ok"] is True

def test_fetch_snapshot_bytes_success():
    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.headers = {"content-type": "image/jpeg"}
        mock_get.return_value.content = b"\xff\xd8snapshotdata"

        data = worker.fetch_snapshot_bytes("http://camera/snap")
        assert data == b"\xff\xd8snapshotdata"

def test_fetch_snapshot_bytes_fail():
    with patch("httpx.Client.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        data = worker.fetch_snapshot_bytes("http://camera/snap")
        assert data is None

def test_write_heartbeat():
    with patch("pathlib.Path.write_text") as mock_write:
        worker._write_heartbeat()
        mock_write.assert_called_once()
        args, _ = mock_write.call_args
        data = json.loads(args[0])
        assert "ts" in data
        assert "unix_ts" in data

from unittest.mock import mock_open

def test_fetch_rtsp_frame_success():
    mock_file_content = b"\xff\xd8frame"
    with patch("subprocess.run") as mock_run, \
         patch("builtins.open", mock_open(read_data=mock_file_content)):

        data = worker.fetch_rtsp_frame("rtsp://url")
        assert data == mock_file_content
        mock_run.assert_called_once()

def test_capture_alert_clip_success():
    cam = {"id": 1, "ip": "1.1.1.1"}
    alert = {"id": 123, "created_at": "2024-01-01T12:00:00Z"}

    with patch("subprocess.run") as mock_run, \
         patch("pathlib.Path.mkdir"), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.stat") as mock_stat, \
         patch("worker.worker.update_alert_clip") as mock_update:

        mock_stat.return_value.st_size = 1000
        worker.capture_alert_clip(cam, alert)

        mock_run.assert_called_once()
        mock_update.assert_called_once_with(123, "ready", "1/20240101T120000Z-alert-123.mp4", None)
