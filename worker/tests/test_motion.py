import sys
from pathlib import Path

# Add worker directory to sys.path
WORKER_ROOT = Path(__file__).parent.parent
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))

from worker import motion_detect

def test_motion_detect_no_current():
    label, conf = motion_detect(b"data", None)
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_no_previous():
    label, conf = motion_detect(None, b"data")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_identical():
    label, conf = motion_detect(b"same", b"same")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_empty_bytes():
    label, conf = motion_detect(b"", b"data")
    assert label == "motion"
    assert conf == 0.0

    label, conf = motion_detect(b"data", b"")
    assert label == "motion"
    assert conf == 0.0

def test_motion_detect_different_size():
    # Significant size difference should trigger higher confidence
    prev = b"small"
    cur = b"something much larger than small"
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0.0
    assert conf <= 0.99

def test_motion_detect_same_size_different_content():
    # Same size but different content (different hash)
    prev = b"data1"
    cur = b"data2"
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf > 0.0
    assert conf <= 0.99

def test_motion_detect_clamp_max():
    # Trigger maximum confidence
    prev = b"a"
    cur = b"z" * 1000 # Very different size
    label, conf = motion_detect(prev, cur)
    assert label == "motion"
    assert conf == 0.99 # Clamped at 0.99
