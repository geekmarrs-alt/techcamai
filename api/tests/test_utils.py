import os
import tempfile
import pytest

# Set up environment variables before importing app.main to avoid side effects.
_tmp_dir = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(_tmp_dir, "test_utils.db")
os.environ["CLIPS_DIR"] = os.path.join(_tmp_dir, "clips")

from app.main import _channel_hint_from_source_url

def test_channel_hint_rtsp_basic():
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Channels/1") == 1
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Channels/2") == 2

def test_channel_hint_rtsp_hikvision_style():
    # Hikvision uses 101 for channel 1 main stream, 102 for substream, 201 for channel 2, etc.
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Channels/101") == 1
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Channels/102") == 1
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Channels/201") == 2

def test_channel_hint_http_basic():
    assert _channel_hint_from_source_url("http://1.2.3.4/channels/1/picture") == 1
    assert _channel_hint_from_source_url("http://1.2.3.4/channels/2") == 2
    assert _channel_hint_from_source_url("http://1.2.3.4/channels/101/") == 1

def test_channel_hint_case_insensitive():
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/streaming/channels/1") == 1
    assert _channel_hint_from_source_url("HTTP://1.2.3.4/CHANNELS/1") == 1

def test_channel_hint_none_or_empty():
    # The function signature says value: str, but it handles None via `value or ""`
    assert _channel_hint_from_source_url(None) is None
    assert _channel_hint_from_source_url("") is None

def test_channel_hint_no_match():
    assert _channel_hint_from_source_url("http://1.2.3.4/some/other/path") is None
    assert _channel_hint_from_source_url("rtsp://1.2.3.4/Streaming/Other/1") is None

def test_channel_hint_boundary():
    # raw >= 100 -> raw // 100
    assert _channel_hint_from_source_url("/channels/99") == 99
    assert _channel_hint_from_source_url("/channels/100") == 1
    assert _channel_hint_from_source_url("/channels/1000") == 10

def test_channel_hint_rtsp_with_params():
    url = "rtsp://user:pass@1.2.3.4:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"
    assert _channel_hint_from_source_url(url) == 1

def test_channel_hint_http_with_params():
    url = "http://1.2.3.4/channels/2/picture?resolution=high"
    assert _channel_hint_from_source_url(url) == 2

def test_channel_hint_malformed_number():
    # \d+ matches digits, but if it's too large for int? Python handles large ints.
    # What if it's not a number? regex won't match.
    assert _channel_hint_from_source_url("/channels/abc/") is None
