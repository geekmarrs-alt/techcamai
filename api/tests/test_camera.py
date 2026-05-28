import os
import tempfile
import pytest
import base64
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# Setup environment before importing app
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test.db")
_tmp_clips = os.path.join(_tmp_dir, "clips")
os.makedirs(_tmp_clips, exist_ok=True)
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = _tmp_clips

from app.main import app

@pytest.fixture(scope="module")
def client():
    # Use with statement to trigger startup/shutdown events
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

@patch("app.main.httpx.AsyncClient")
def test_camera_test_happy_path(mock_client_class, client):
    mock_client = mock_client_class.return_value
    # Mocking the async context manager
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake-jpeg-content"
    mock_client.get = AsyncMock(return_value=mock_response)

    payload = {
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "channel": 1
    }

    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "jpeg_b64" in data
    assert data["jpeg_b64"] == base64.b64encode(b"fake-jpeg-content").decode("ascii")
    assert "url" in data

@patch("app.main.httpx.AsyncClient")
def test_camera_test_all_404(mock_client_class, client):
    mock_client = mock_client_class.return_value
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    payload = {
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "channel": 1
    }

    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "Snapshot test failed" in detail
    assert "HTTP 404" in detail

@patch("app.main.httpx.AsyncClient")
def test_camera_test_empty_body(mock_client_class, client):
    mock_client = mock_client_class.return_value
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b""
    mock_client.get = AsyncMock(return_value=mock_response)

    payload = {
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "channel": 1
    }

    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "Snapshot test failed" in detail
    assert "empty body" in detail

@patch("app.main.httpx.AsyncClient")
def test_camera_test_exception(mock_client_class, client):
    mock_client = mock_client_class.return_value
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

    payload = {
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "channel": 1
    }

    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "Snapshot test failed" in detail
    assert "Connection refused" in detail

@patch("app.main.httpx.AsyncClient")
def test_camera_test_first_fails_second_works(mock_client_class, client):
    mock_client = mock_client_class.return_value
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)

    fail_response = MagicMock()
    fail_response.status_code = 404

    success_response = MagicMock()
    success_response.status_code = 200
    success_response.content = b"success-jpeg"

    mock_client.get = AsyncMock(side_effect=[fail_response, success_response])

    payload = {
        "ip": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "channel": 1
    }

    r = client.post("/cameras/test", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["jpeg_b64"] == base64.b64encode(b"success-jpeg").decode("ascii")
