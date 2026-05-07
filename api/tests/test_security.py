import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Point DB and clips at safe temp locations before importing app.
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test.db")
_tmp_clips = os.path.join(_tmp_dir, "clips")
os.makedirs(_tmp_clips, exist_ok=True)
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_clips

from app.main import app

@pytest.fixture
def client():
    # Use context manager to trigger startup events (db creation)
    with TestClient(app) as c:
        yield c

def test_test_camera_ssrf_loopback(client):
    payload = {"ip": "127.0.0.1", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "Invalid IP address" in r.text
    # "127.0.0.1" is blocked by the explicit list first
    assert "not allowed" in r.text.lower()

def test_test_camera_ssrf_loopback_v6(client):
    payload = {"ip": "::1", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "Invalid IP address" in r.text

def test_test_camera_ssrf_link_local(client):
    # AWS metadata etc.
    payload = {"ip": "169.254.169.254", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "Invalid IP address" in r.text
    assert "link-local" in r.text.lower()

def test_create_camera_ssrf_loopback(client):
    payload = {"name": "Bad Cam", "ip": "127.0.0.1", "username": "admin", "password": "password"}
    r = client.post("/cameras", json=payload)
    assert r.status_code == 400
    assert "Invalid IP address" in r.text

def test_update_camera_ssrf_loopback(client):
    # Create valid first
    r_init = client.post("/cameras", json={"name": "Good Cam", "ip": "192.168.1.10", "username": "u", "password": "p"})
    assert r_init.status_code == 200
    cam_id = r_init.json()["id"]

    # Try update to bad
    r = client.put(f"/cameras/{cam_id}", json={"ip": "127.0.0.1"})
    assert r.status_code == 400
    assert "Invalid IP address" in r.text

def test_test_camera_valid_private_ip(client):
    # This should be allowed by the security logic but fail to connect
    payload = {"ip": "192.168.1.254", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "Snapshot test failed" in r.text
