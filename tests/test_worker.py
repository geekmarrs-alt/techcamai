import os
import subprocess
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add worker directory to sys.path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "worker"))

import worker

class TestWorker(unittest.TestCase):
    @patch("worker.subprocess.run")
    def test_fetch_rtsp_frame_success(self, mock_run):
        """Test fetch_rtsp_frame successful path."""
        rtsp_url = "rtsp://example.com/stream"

        def side_effect(args, **kwargs):
            out_path = args[2]
            with open(out_path, "wb") as f:
                f.write(b"\xff\xd8 some data")
            return MagicMock(returncode=0)

        mock_run.side_effect = side_effect

        try:
            result = worker.fetch_rtsp_frame(rtsp_url)
            self.assertEqual(result, b"\xff\xd8 some data")

            # Verify subprocess call
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0][0], "/app/rtsp_grab.sh")
            self.assertEqual(args[0][1], rtsp_url)
            self.assertTrue(args[0][2].startswith("/tmp/techcamai_rtsp_"))
            self.assertTrue(args[0][2].endswith(".jpg"))

            out_path = args[0][2]
        finally:
            if 'out_path' in locals() and os.path.exists(out_path):
                os.remove(out_path)

    @patch("worker.subprocess.run")
    def test_fetch_rtsp_frame_invalid_jpeg(self, mock_run):
        """Test fetch_rtsp_frame with invalid JPEG data."""
        rtsp_url = "rtsp://example.com/stream_invalid"

        def side_effect(args, **kwargs):
            out_path = args[2]
            with open(out_path, "wb") as f:
                f.write(b"not a jpeg")
            return MagicMock(returncode=0)

        mock_run.side_effect = side_effect

        try:
            result = worker.fetch_rtsp_frame(rtsp_url)
            self.assertIsNone(result)

            args, kwargs = mock_run.call_args
            out_path = args[0][2]
        finally:
            if 'out_path' in locals() and os.path.exists(out_path):
                os.remove(out_path)

    @patch("worker.subprocess.run")
    def test_fetch_rtsp_frame_subprocess_error(self, mock_run):
        """Test fetch_rtsp_frame when subprocess fails."""
        rtsp_url = "rtsp://example.com/stream_error"
        # Simulate subprocess failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")

        result = worker.fetch_rtsp_frame(rtsp_url)

        self.assertIsNone(result)

    @patch("worker.subprocess.run")
    def test_fetch_rtsp_frame_file_not_found(self, mock_run):
        """Test fetch_rtsp_frame when the output file is not created."""
        rtsp_url = "rtsp://example.com/stream_missing"
        mock_run.return_value = MagicMock(returncode=0)

        # Don't create the file in mock_run

        result = worker.fetch_rtsp_frame(rtsp_url)

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
