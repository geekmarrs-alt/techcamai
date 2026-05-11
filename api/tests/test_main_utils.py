import pytest
from app.main import _channel_hint_from_source_url

@pytest.mark.parametrize("url,expected", [
    # RTSP patterns
    ("rtsp://admin:pass@192.168.1.10/Streaming/Channels/1", 1),
    ("rtsp://admin:pass@192.168.1.10/Streaming/Channels/2", 2),
    ("rtsp://admin:pass@192.168.1.10/Streaming/Channels/101", 1),
    ("rtsp://admin:pass@192.168.1.10/Streaming/Channels/102", 1),
    ("rtsp://admin:pass@192.168.1.10/Streaming/Channels/201", 2),
    # Case insensitivity for RTSP
    ("rtsp://192.168.1.10/streaming/channels/1", 1),

    # HTTP patterns
    ("http://192.168.1.10/channels/1", 1),
    ("http://192.168.1.10/channels/2/", 2),
    ("http://192.168.1.10/channels/3/picture", 3),
    ("http://192.168.1.10/channels/101", 1),
    ("http://192.168.1.10/channels/402/snapshot", 4),
    # Case insensitivity for HTTP
    ("HTTP://192.168.1.10/CHANNELS/5", 5),

    # Non-matching cases
    ("rtsp://192.168.1.10/some/other/path", None),
    ("http://192.168.1.10/not-channels/1", None),
    ("just a string", None),
    ("", None),
    (None, None),
])
def test_channel_hint_from_source_url(url, expected):
    assert _channel_hint_from_source_url(url) == expected
