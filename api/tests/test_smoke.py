"""
Lightweight smoke tests for TECHCAMAI operator API.

Run from the repo root with:
    pytest api/tests/test_smoke.py -v

Tests use an in-memory SQLite database (DB_PATH=:memory:) and a temp clips dir
so they never touch /data.  No cameras, workers, or real RTSP streams needed.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Point DB and clips at safe temp locations before importing app.
# Use a real temp file, not :memory:, because SQLAlchemy opens multiple
# connections and each :memory: connection is an isolated empty database.
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test.db")
_tmp_clips = os.path.join(_tmp_dir, "clips")
os.makedirs(_tmp_clips, exist_ok=True)
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_clips

from app.main import app  # noqa: E402 — must be after env setup


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ── HTML pages ────────────────────────────────────────────────────────────────

def test_dashboard_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "TECHCAMAI" in r.text


def test_dashboard_root_poll(client):
    r = client.get("/?poll=1")
    assert r.status_code == 200


def test_live_wall(client):
    r = client.get("/live")
    assert r.status_code == 200
    assert "Snapshot wall" in r.text


def test_alerts_page(client):
    r = client.get("/alerts")
    assert r.status_code == 200
    assert "Alert inbox" in r.text


def test_alerts_page_show_all(client):
    r = client.get("/alerts?show=all")
    assert r.status_code == 200


def test_timeline_page(client):
    r = client.get("/timeline")
    assert r.status_code == 200
    assert "Daily activity strip" in r.text


def test_cameras_manage(client):
    r = client.get("/cameras/manage")
    assert r.status_code == 200
    assert "Camera inventory" in r.text


def test_add_camera_get(client):
    r = client.get("/ui/add")
    assert r.status_code == 200


# ── API / health ──────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "db" in body
    assert "worker_stale" in body


def test_list_cameras(client):
    r = client.get("/cameras")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_list_rules(client):
    r = client.get("/rules")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_api_alerts_latest(client):
    r = client.get("/api/alerts/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "alerts" in body
    assert isinstance(body["alerts"], list)


def test_api_alerts_latest_since(client):
    r = client.get("/api/alerts/latest?since=0&unacked_only=0")
    assert r.status_code == 200


# ── Camera CRUD ───────────────────────────────────────────────────────────────

def test_create_camera(client):
    payload = {"name": "Test Cam", "ip": "192.168.1.100", "username": "admin", "password": "pass"}
    r = client.post("/cameras", json=payload)
    assert r.status_code == 200
    cam = r.json()
    assert cam["ip"] == "192.168.1.100"
    assert cam["name"] == "Test Cam"
    assert cam["channel"] == 1

def test_list_cameras_no_passwords(client):
    """GET /cameras (public list) must never include passwords."""
    r = client.get("/cameras")
    assert r.status_code == 200
    for cam in r.json():
        assert "password" not in cam


def test_update_camera(client):
    r = client.post("/cameras", json={"name": "ToUpdate", "ip": "10.0.0.2", "username": "u", "password": "p"})
    cam_id = r.json()["id"]
    r2 = client.put(f"/cameras/{cam_id}", json={"name": "Updated"})
    assert r2.status_code == 200
    assert r2.json()["ok"] is True


def test_update_nonexistent_camera(client):
    r = client.put("/cameras/99999", json={"name": "Ghost"})
    assert r.status_code == 404


# ── Rule CRUD ─────────────────────────────────────────────────────────────────

def test_create_rule(client):
    cam_r = client.post("/cameras", json={"name": "RuleCam", "ip": "10.0.0.3", "username": "u", "password": "p"})
    cam_id = cam_r.json()["id"]
    r = client.post("/rules", json={"name": "Motion rule", "camera_id": cam_id})
    assert r.status_code == 200
    rule = r.json()
    assert rule["camera_id"] == cam_id


def test_create_rule_missing_camera(client):
    r = client.post("/rules", json={"name": "Bad rule", "camera_id": 99999})
    assert r.status_code == 404


# ── Ingest / detection ────────────────────────────────────────────────────────

def test_ingest_unknown_camera(client):
    """Detection for an unknown camera should return ok with empty triggered list."""
    r = client.post("/ingest/detection", json={
        "camera_snapshot_url": "http://999.999.999.999/snapshot.jpg",
        "label": "motion",
        "conf": 0.9,
    })
    assert r.status_code == 200
    assert r.json()["triggered"] == []


def test_ingest_triggers_alert(client):
    """End-to-end: create camera + rule → post detection → expect alert triggered."""
    cam_r = client.post("/cameras", json={"name": "IngestCam", "ip": "192.168.2.1", "username": "u", "password": "p"})
    cam_id = cam_r.json()["id"]
    client.post("/rules", json={"name": "Ingest motion", "camera_id": cam_id, "min_conf": 0.1, "cooldown_sec": 0})

    r = client.post("/ingest/detection", json={
        "camera_snapshot_url": "http://192.168.2.1/snapshot",
        "camera_id": cam_id,
        "label": "motion",
        "conf": 0.8,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert len(body["triggered"]) == 1


# ── Alert clip updates ────────────────────────────────────────────────────────

def test_clip_update_ready(client):
    cam_r = client.post("/cameras", json={"name": "ClipCam", "ip": "10.1.1.1", "username": "u", "password": "p"})
    cam_id = cam_r.json()["id"]
    client.post("/rules", json={"name": "Clip rule", "camera_id": cam_id, "min_conf": 0.1, "cooldown_sec": 0})
    det_r = client.post("/ingest/detection", json={
        "camera_id": cam_id,
        "camera_snapshot_url": "http://10.1.1.1/snap",
        "label": "motion",
        "conf": 0.9,
    })
    alert_id = det_r.json()["triggered"][0]["id"]

    r = client.put(f"/alerts/{alert_id}/clip", json={
        "clip_status": "ready",
        "clip_path": f"{cam_id}/20240101T120000Z-alert-{alert_id}.mp4",
    })
    assert r.status_code == 200
    assert r.json()["clip_status"] == "ready"


def test_clip_update_failed(client):
    cam_r = client.post("/cameras", json={"name": "FailCam", "ip": "10.1.1.2", "username": "u", "password": "p"})
    cam_id = cam_r.json()["id"]
    client.post("/rules", json={"name": "Fail rule", "camera_id": cam_id, "min_conf": 0.1, "cooldown_sec": 0})
    det_r = client.post("/ingest/detection", json={
        "camera_id": cam_id,
        "camera_snapshot_url": "http://10.1.1.2/snap",
        "label": "motion",
        "conf": 0.9,
    })
    alert_id = det_r.json()["triggered"][0]["id"]

    r = client.put(f"/alerts/{alert_id}/clip", json={
        "clip_status": "failed",
        "clip_error": "ffmpeg returned non-zero exit",
    })
    assert r.status_code == 200
    assert r.json()["clip_status"] == "failed"


def test_clip_update_bad_status(client):
    r = client.put("/alerts/1/clip", json={"clip_status": "bogus"})
    assert r.status_code == 400


def test_clip_ready_requires_path(client):
    r = client.put("/alerts/1/clip", json={"clip_status": "ready"})
    assert r.status_code == 400


def test_clip_path_traversal_rejected(client):
    r = client.put("/alerts/1/clip", json={"clip_status": "ready", "clip_path": "../../etc/passwd"})
    assert r.status_code == 400
