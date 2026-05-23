import sys
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parents[1] / "worker"
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

import worker  # noqa: E402


def test_camera_rtsp_url_encodes_reserved_credential_characters():
    url = worker._camera_rtsp_url({
        "ip": "192.168.1.50",
        "channel": 1,
        "username": "admin@example",
        "password": "p@ss:word#1/2",
    })

    assert url == (
        "rtsp://admin%40example:p%40ss%3Aword%231%2F2"
        "@192.168.1.50:554/Streaming/Channels/101"
    )
