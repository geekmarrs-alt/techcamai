import importlib
import sys
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

worker = importlib.import_module("worker")


def test_camera_rtsp_url_percent_encodes_reserved_userinfo_characters():
    url = worker._camera_rtsp_url(
        {
            "ip": "10.0.0.9",
            "channel": 1,
            "username": "admin@example.com",
            "password": "p@ss:word#1/2",
        }
    )

    assert (
        url
        == "rtsp://admin%40example.com:p%40ss%3Aword%231%2F2@10.0.0.9:554/Streaming/Channels/101"
    )


def test_camera_rtsp_url_preserves_hikvision_channel_mapping():
    url = worker._camera_rtsp_url(
        {
            "ip": "10.0.0.10",
            "channel": 2,
            "username": "admin",
            "password": "plain-pass",
        }
    )

    assert url == "rtsp://admin:plain-pass@10.0.0.10:554/Streaming/Channels/201"
