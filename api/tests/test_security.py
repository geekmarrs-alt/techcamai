import os
import sys
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select

# Point DB and clips at safe temp locations before importing app.
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test.db")
_tmp_clips = os.path.join(_tmp_dir, "clips")
os.makedirs(_tmp_clips, exist_ok=True)
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_clips
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import app.main as main_module
from app.main import app, Camera, startup
from app.crypto import encrypt_password, decrypt_password, is_encrypted

@pytest.fixture
def client():
    # Use context manager to trigger startup events (db creation)
    with TestClient(app) as c:
        c.cookies.set("tcai_session", "admin-session-demo")
        yield c

def test_test_camera_ssrf_loopback(client):
    payload = {"ip": "127.0.0.1", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "camera ip" in r.text
    # "127.0.0.1" is blocked by the explicit list first
    assert "not allowed" in r.text.lower()

def test_test_camera_ssrf_loopback_v6(client):
    payload = {"ip": "::1", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "camera ip" in r.text

def test_test_camera_ssrf_link_local(client):
    # AWS metadata etc.
    payload = {"ip": "169.254.169.254", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "camera ip" in r.text
    assert "link-local" in r.text.lower()

def test_create_camera_ssrf_loopback(client):
    payload = {"name": "Bad Cam", "ip": "127.0.0.1", "username": "admin", "password": "password"}
    r = client.post("/cameras", json=payload)
    assert r.status_code == 400
    assert "camera ip" in r.text

def test_update_camera_ssrf_loopback(client):
    # Create valid first
    r_init = client.post("/cameras", json={"name": "Good Cam", "ip": "192.168.1.10", "username": "u", "password": "p"})
    assert r_init.status_code == 200
    cam_id = r_init.json()["id"]

    # Try update to bad
    r = client.put(f"/cameras/{cam_id}", json={"ip": "127.0.0.1"})
    assert r.status_code == 400
    assert "camera ip" in r.text

def test_test_camera_valid_private_ip(client):
    # This should be allowed by the security logic but fail to connect
    payload = {"ip": "192.168.1.254", "username": "admin", "password": "password", "channel": 1}
    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    assert "Snapshot test failed" in r.text


def test_encryption_decryption():
    pw = "secret_password"
    encrypted = encrypt_password(pw)
    assert encrypted != pw
    assert is_encrypted(encrypted)
    assert decrypt_password(encrypted) == pw


def test_migration(tmp_path):
    db_file = tmp_path / "test_migration.db"
    test_engine = create_engine(f"sqlite:///{db_file}")
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        cam = Camera(name="Test Cam", ip="1.2.3.4", password="plaintext_pw")
        session.add(cam)
        session.commit()

    original_engine = main_module.engine
    main_module.engine = test_engine
    try:
        startup()
        with Session(test_engine) as session:
            cam = session.exec(select(Camera).where(Camera.ip == "1.2.3.4")).one()
            assert cam.password != "plaintext_pw"
            assert is_encrypted(cam.password)
            assert decrypt_password(cam.password) == "plaintext_pw"
    finally:
        main_module.engine = original_engine


def test_worker_decryption():
    pw = "worker_secret"
    encrypted = encrypt_password(pw)
    from worker.crypto import decrypt_password as worker_decrypt
    assert worker_decrypt(encrypted) == pw
