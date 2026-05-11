import unittest
from unittest.mock import MagicMock, patch
import httpx
import sys
import os

# Add api to path
sys.path.append(os.path.abspath('api'))

from app.main import _fetch_camera_snapshot, Camera, CameraTestRequest, test_camera, CameraUpdate, ui_camera_update, ui_add_post
from fastapi import Request

class TestTLSLogic(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_camera_snapshot_respects_verify_ssl(self):
        cam = Camera(name="Test", ip="1.2.3.4", verify_ssl=True)
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = MagicMock(status_code=200, content=b"fake-jpeg")

            await _fetch_camera_snapshot(cam)

            mock_client.assert_called_once()
            kwargs = mock_client.call_args.kwargs
            self.assertEqual(kwargs.get("verify"), True)

        cam.verify_ssl = False
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = MagicMock(status_code=200, content=b"fake-jpeg")

            await _fetch_camera_snapshot(cam)

            mock_client.assert_called_once()
            kwargs = mock_client.call_args.kwargs
            self.assertEqual(kwargs.get("verify"), False)

    async def test_test_camera_respects_verify_ssl(self):
        req = CameraTestRequest(ip="1.2.3.4", username="u", password="p", verify_ssl=True)
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = MagicMock(status_code=200, content=b"fake-jpeg")

            await test_camera(req)

            mock_client.assert_called_once()
            kwargs = mock_client.call_args.kwargs
            self.assertEqual(kwargs.get("verify"), True)

        req.verify_ssl = False
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = MagicMock(status_code=200, content=b"fake-jpeg")

            await test_camera(req)

            mock_client.assert_called_once()
            kwargs = mock_client.call_args.kwargs
            self.assertEqual(kwargs.get("verify"), False)

    def test_worker_fetch_snapshot_bytes_respects_verify(self):
        # We need to import worker here because it might have side effects on import
        # or we might need to mock things before importing.
        # But for now let's just patch httpx.Client which it uses.

        with patch("sys.path", sys.path + ["worker"]):
            import worker as worker_mod

            with patch("httpx.Client") as mock_client:
                mock_instance = mock_client.return_value.__enter__.return_value
                mock_instance.get.return_value = MagicMock()
                mock_instance.get.return_value.headers = {"content-type": "image/jpeg"}
                mock_instance.get.return_value.content = b"\xff\xd8fake"

                worker_mod.fetch_snapshot_bytes("http://test", verify=True)
                kwargs = mock_client.call_args.kwargs
                self.assertEqual(kwargs.get("verify"), True)

                worker_mod.fetch_snapshot_bytes("http://test", verify=False)
                kwargs = mock_client.call_args.kwargs
                self.assertEqual(kwargs.get("verify"), False)

if __name__ == "__main__":
    unittest.main()
