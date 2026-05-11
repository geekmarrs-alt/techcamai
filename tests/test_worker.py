import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "worker"))

import worker  # noqa: E402


def test_parse_urls():
    assert worker.parse_urls("http://a, http://b") == ["http://a", "http://b"]
    assert worker.parse_urls("") == []


def test_camera_rtsp_url_channel_mapping():
    cam = {"ip": "1.2.3.4", "username": "u", "password": "p", "channel": 2}
    with patch("worker.decrypt_password", return_value="p"):
        assert worker._camera_rtsp_url(cam) == "rtsp://u:p@1.2.3.4:554/Streaming/Channels/201"


@patch("worker.subprocess.run")
@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.read_bytes", return_value=b"\xff\xd8\xff\xe0abc")
def test_fetch_rtsp_frame_success(mock_read, mock_exists, mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    result = worker.fetch_rtsp_frame("rtsp://camera/stream")
    assert result == b"\xff\xd8\xff\xe0abc"
    args = mock_run.call_args[0][0]
    assert args[0] == "ffmpeg"

