import sys
from unittest.mock import MagicMock, patch

# Mock httpx and pydantic_settings before importing worker.worker
sys.modules["httpx"] = MagicMock()
sys.modules["pydantic_settings"] = MagicMock()

import worker.worker as worker

def test_fetch_snapshot_bytes_success():
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = b"\xff\xd8fakejpeg"
    mock_response.headers = {"content-type": "image/jpeg"}
    mock_client_instance.get.return_value = mock_response

    with patch("worker.worker.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = worker.fetch_snapshot_bytes("http://example.com/snap.jpg")

        assert result == b"\xff\xd8fakejpeg"
        mock_client_instance.get.assert_called_once_with("http://example.com/snap.jpg", auth=None)

def test_fetch_snapshot_bytes_http_error():
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    # Mock raise_for_status to raise an exception
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_client_instance.get.return_value = mock_response

    with patch("worker.worker.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = worker.fetch_snapshot_bytes("http://example.com/snap.jpg")

        assert result is None

def test_fetch_snapshot_bytes_invalid_content():
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = b"not a jpeg"
    mock_response.headers = {"content-type": "text/plain"}
    mock_client_instance.get.return_value = mock_response

    with patch("worker.worker.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = worker.fetch_snapshot_bytes("http://example.com/snap.jpg")

        assert result is None

def test_fetch_snapshot_bytes_exception():
    with patch("worker.worker.httpx.Client") as mock_client:
        # Mocking __enter__ to raise an exception to simulate a connection error or similar
        mock_client.return_value.__enter__.side_effect = Exception("Connection refused")

        result = worker.fetch_snapshot_bytes("http://example.com/snap.jpg")

        assert result is None
