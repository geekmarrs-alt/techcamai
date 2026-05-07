"""
Tests for ingest_detection coverage, specifically fallback paths.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Setup temp environment
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test_coverage.db")
_tmp_clips = os.path.join(_tmp_dir, "clips_coverage")
os.makedirs(_tmp_clips, exist_ok=True)
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_clips

from app.main import app # noqa: E402

@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

def test_ingest_detection_malformed_url(client):
    """
    Test that a malformed URL in camera_snapshot_url is handled gracefully
    (hits the except block in ingest_detection).
    """
    # Malformed IPv6 URL that causes urlparse().hostname to raise ValueError
    malformed_url = "http://[::1"

    payload = {
        "camera_snapshot_url": malformed_url,
        "label": "motion",
        "conf": 0.9,
    }

    r = client.post("/ingest/detection", json=payload)
    assert r.status_code == 200
    assert r.json() == {"ok": True, "triggered": []}

def test_ingest_detection_fallback_match(client):
    """
    Test the fallback matching by hostname and channel hint.
    """
    # Create a camera with a specific IP and channel
    cam_payload = {
        "name": "FallbackCam",
        "ip": "10.0.0.50",
        "username": "admin",
        "password": "password",
        "channel": 2
    }
    r_cam = client.post("/cameras", json=cam_payload)
    cam_id = r_cam.json()["id"]

    # Create a rule for this camera
    rule_payload = {
        "name": "Motion Rule",
        "camera_id": cam_id,
        "label": "motion",
        "min_conf": 0.5,
        "cooldown_sec": 0
    }
    client.post("/rules", json=rule_payload)

    # Send a detection with a different snapshot_url but same host and channel hint
    # /Streaming/Channels/201 implies channel 2
    snapshot_url = "http://10.0.0.50/Streaming/Channels/201/picture"

    det_payload = {
        "camera_snapshot_url": snapshot_url,
        "label": "motion",
        "conf": 0.8
    }

    r = client.post("/ingest/detection", json=det_payload)
    assert r.status_code == 200
    triggered = r.json()["triggered"]
    assert len(triggered) == 1
    assert triggered[0]["camera_id"] == cam_id

def test_ingest_detection_fallback_match_host_only(client):
    """
    Test the fallback matching by hostname only when channel hint is missing or doesn't match.
    """
    # Create a camera with a specific IP
    cam_payload = {
        "name": "HostOnlyCam",
        "ip": "10.0.0.60",
        "username": "admin",
        "password": "password",
        "channel": 1
    }
    r_cam = client.post("/cameras", json=cam_payload)
    cam_id = r_cam.json()["id"]

    # Create a rule for this camera
    rule_payload = {
        "name": "Motion Rule",
        "camera_id": cam_id,
        "label": "motion",
        "min_conf": 0.5,
        "cooldown_sec": 0
    }
    client.post("/rules", json=rule_payload)

    # URL with no channel hint
    snapshot_url = "http://10.0.0.60/some/other/path"

    det_payload = {
        "camera_snapshot_url": snapshot_url,
        "label": "motion",
        "conf": 0.8
    }

    r = client.post("/ingest/detection", json=det_payload)
    assert r.status_code == 200
    triggered = r.json()["triggered"]
    assert len(triggered) == 1
    assert triggered[0]["camera_id"] == cam_id
