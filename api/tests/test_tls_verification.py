
import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Add api and worker directories to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "worker")))

# Mocking modules that might be missing in the environment
mock_fastapi = MagicMock()
def mock_decorator(func):
    return func
mock_fastapi.post.return_value = mock_decorator
mock_fastapi.get.return_value = mock_decorator
mock_fastapi.put.return_value = mock_decorator
mock_fastapi.on_event.return_value = mock_decorator

sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi"].FastAPI = MagicMock(return_value=mock_fastapi)
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.templating"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["pydantic_settings"] = MagicMock()
sys.modules["sqlmodel"] = MagicMock()
sys.modules["httpx"] = MagicMock()
sys.modules["app.discover"] = MagicMock()

# Directly import the module and use a more robust way to handle top-level effects
with patch("sqlmodel.create_engine"), \
     patch("sqlmodel.SQLModel"), \
     patch("pydantic_settings.BaseSettings", new=MagicMock()):

    import app.main as main
    import worker as worker_mod

def test_fetch_camera_snapshot_respects_verify_ssl():
    mock_cam = MagicMock()
    mock_cam.ip = "1.2.3.4"
    mock_cam.channel = 1
    mock_cam.scheme = "https"
    mock_cam.auth = "digest"
    mock_cam.username = "user"
    mock_cam.password = "pass"
    mock_cam.verify_ssl = True

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client_instance

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-jpeg-data"
        mock_client_instance.get.return_value = mock_response

        asyncio.run(main._fetch_camera_snapshot(mock_cam))

        # Verify that AsyncClient was called with verify=True
        MockClient.assert_called_once()
        args, kwargs = MockClient.call_args
        assert kwargs["verify"] is True

def test_fetch_camera_snapshot_disables_verify_ssl():
    mock_cam = MagicMock()
    mock_cam.ip = "1.2.3.4"
    mock_cam.channel = 1
    mock_cam.scheme = "https"
    mock_cam.auth = "digest"
    mock_cam.username = "user"
    mock_cam.password = "pass"
    mock_cam.verify_ssl = False

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client_instance

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-jpeg-data"
        mock_client_instance.get.return_value = mock_response

        asyncio.run(main._fetch_camera_snapshot(mock_cam))

        # Verify that AsyncClient was called with verify=False
        MockClient.assert_called_once()
        args, kwargs = MockClient.call_args
        assert kwargs["verify"] is False

def test_test_camera_respects_verify_ssl():
    mock_req = MagicMock()
    mock_req.ip = "1.2.3.4"
    mock_req.username = "user"
    mock_req.password = "pass"
    mock_req.channel = 1
    mock_req.verify_ssl = True

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client_instance

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-jpeg-data"
        mock_client_instance.get.return_value = mock_response

        asyncio.run(main.test_camera(mock_req))

        # Verify that AsyncClient was called with verify=True
        MockClient.assert_called_once()
        args, kwargs = MockClient.call_args
        assert kwargs["verify"] is True

def test_worker_fetch_snapshot_bytes_respects_verify_ssl():
    url = "https://example.com/snap"

    with patch("httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\xff\xd8fake-jpeg-data"
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_client_instance.get.return_value = mock_response

        worker_mod.fetch_snapshot_bytes(url, verify=True)

        # Verify that Client was called with verify=True
        MockClient.assert_called()
        found = False
        for call in MockClient.call_args_list:
            if call.kwargs.get("verify") is True:
                found = True
                break
        assert found

def test_worker_fetch_snapshot_bytes_disables_verify_ssl():
    url = "https://example.com/snap"

    with patch("httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\xff\xd8fake-jpeg-data"
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_client_instance.get.return_value = mock_response

        worker_mod.fetch_snapshot_bytes(url, verify=False)

        # Verify that Client was called with verify=False
        MockClient.assert_called()
        found = False
        for call in MockClient.call_args_list:
            if call.kwargs.get("verify") is False:
                found = True
                break
        assert found
