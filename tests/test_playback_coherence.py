import importlib
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path('/data/.openclaw/workspace/recovered/techcamai')
API_ROOT = REPO_ROOT / 'api'
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


class PlaybackCoherenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = Path(tempfile.mkdtemp(prefix='techcamai-test-'))
        os.environ['DB_PATH'] = str(cls.tempdir / 'techcamai.db')
        os.environ['CLIPS_DIR'] = str(cls.tempdir / 'clips')
        cls.main = importlib.import_module('app.main')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(self.tempdir / 'clips', ignore_errors=True)

        self.client_cm = TestClient(self.main.app)
        self.client = self.client_cm.__enter__()

        with sqlite3.connect(self.tempdir / 'techcamai.db') as conn:
            conn.execute('DELETE FROM alert')
            conn.execute('DELETE FROM rule')
            conn.execute('DELETE FROM camera')
            conn.commit()

    def tearDown(self):
        self.client_cm.__exit__(None, None, None)

    def _create_camera(self, name: str, ip: str, channel: int):
        res = self.client.post(
            '/cameras',
            json={
                'name': name,
                'ip': ip,
                'username': 'admin',
                'password': 'secret',
                'channel': channel,
                'scheme': 'https',
                'auth': 'digest',
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()

    def _create_rule(self, camera_id: int, name: str = 'Motion'):
        res = self.client.post(
            '/rules',
            json={
                'name': name,
                'camera_id': camera_id,
                'label': 'motion',
                'min_conf': 0.05,
                'cooldown_sec': 0,
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()

    def test_ingest_prefers_explicit_camera_id(self):
        cam1 = self._create_camera('Yard ch1', '10.0.0.50', 1)
        cam2 = self._create_camera('Yard ch2', '10.0.0.50', 2)
        self._create_rule(cam1['id'])
        self._create_rule(cam2['id'])

        res = self.client.post(
            '/ingest/detection',
            json={
                'camera_snapshot_url': 'rtsp://admin:secret@10.0.0.50:554/Streaming/Channels/101',
                'camera_id': cam2['id'],
                'label': 'motion',
                'conf': 0.91,
                'snapshot_b64': None,
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(len(body['triggered']), 1)
        self.assertEqual(body['triggered'][0]['camera_id'], cam2['id'])

    def test_ingest_falls_back_to_channel_hint_when_ip_is_shared(self):
        cam1 = self._create_camera('Shared ch1', '10.0.0.60', 1)
        cam2 = self._create_camera('Shared ch2', '10.0.0.60', 2)
        self._create_rule(cam1['id'])
        self._create_rule(cam2['id'])

        res = self.client.post(
            '/ingest/detection',
            json={
                'camera_snapshot_url': 'rtsp://admin:secret@10.0.0.60:554/Streaming/Channels/201',
                'label': 'motion',
                'conf': 0.88,
                'snapshot_b64': None,
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(len(body['triggered']), 1)
        self.assertEqual(body['triggered'][0]['camera_id'], cam2['id'])

    def test_clip_updates_validate_and_render_cleanly(self):
        cam = self._create_camera('Playback cam', '10.0.0.70', 1)
        self._create_rule(cam['id'])
        created = self.client.post(
            '/ingest/detection',
            json={
                'camera_snapshot_url': 'rtsp://admin:secret@10.0.0.70:554/Streaming/Channels/101',
                'camera_id': cam['id'],
                'label': 'motion',
                'conf': 0.77,
                'snapshot_b64': None,
            },
        ).json()['triggered'][0]
        alert_id = created['id']

        bad = self.client.put(
            f'/alerts/{alert_id}/clip',
            json={'clip_status': 'ready', 'clip_path': '../escape.mp4', 'clip_error': None},
        )
        self.assertEqual(bad.status_code, 400)

        ok = self.client.put(
            f'/alerts/{alert_id}/clip',
            json={'clip_status': 'ready', 'clip_path': '1/test-alert.mp4', 'clip_error': None},
        )
        self.assertEqual(ok.status_code, 200, ok.text)
        self.assertEqual(ok.json()['clip_path'], '1/test-alert.mp4')

        alerts_page = self.client.get('/alerts')
        self.assertEqual(alerts_page.status_code, 200)
        self.assertIn('/clips/1/test-alert.mp4', alerts_page.text)

        failed = self.client.put(
            f'/alerts/{alert_id}/clip',
            json={'clip_status': 'failed', 'clip_path': '1/should-clear.mp4', 'clip_error': 'rtsp failed'},
        )
        self.assertEqual(failed.status_code, 200, failed.text)
        self.assertIsNone(failed.json()['clip_path'])


if __name__ == '__main__':
    unittest.main()
