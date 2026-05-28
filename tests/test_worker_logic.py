import sys
import os

# Add worker directory to path so we can import worker
sys.path.append(os.path.join(os.getcwd(), "worker"))

from worker import motion_detect, parse_urls, jpeg_b64

def test_motion_detect_none():
    label, conf = motion_detect(None, None)
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_no_prev():
    label, conf = motion_detect(None, b"fake_jpeg")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_no_cur():
    label, conf = motion_detect(b"fake_jpeg", None)
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_identical():
    data = b"identical_data"
    label, conf = motion_detect(data, data)
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_empty_prev():
    label, conf = motion_detect(b"", b"something")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_change_size():
    # Large size difference should give high confidence
    prev = b"a" * 10
    cur = b"a" * 100
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0.0
    assert conf <= 0.99

def test_motion_detect_change_content_same_size():
    prev = b"a" * 100
    cur = b"b" * 100
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0.0
    assert conf <= 0.99

def test_motion_detect_clamping():
    # Extremely different data
    prev = b"\x00" * 1000
    cur = b"\xff" * 10000
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf == 0.99

def test_parse_urls():
    assert parse_urls("") == []
    assert parse_urls(None) == []
    assert parse_urls("http://url1") == ["http://url1"]
    assert parse_urls("http://url1, http://url2 ") == ["http://url1", "http://url2"]
    assert parse_urls(" , ,, ") == []

def test_jpeg_b64():
    assert jpeg_b64(None) is None
    assert jpeg_b64(b"hello") == "aGVsbG8="
