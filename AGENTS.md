# AGENTS.md

## Cursor Cloud specific instructions

### Architecture overview

TECHCAMAI is an edge-first AI camera monitoring platform with two services:

- **API** (`api/`): FastAPI app serving the operator dashboard (Jinja2 templates) + REST API. Uses SQLite at `/data/techcamai.db` and serves clips from `/data/clips`.
- **Worker** (`worker/`): Polling daemon that fetches camera snapshots, runs motion detection, posts detections to the API, and captures RTSP clips via ffmpeg.

### Running the API (dev)

```bash
cd /workspace/api
DB_PATH=/data/techcamai.db CLIPS_DIR=/data/clips python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `/data` directory must exist and be writable. On first start, the API auto-creates the SQLite DB and seeds a demo camera + rule.

### Running tests

```bash
# API smoke tests (26 tests, uses temp DB — no /data needed)
cd /workspace/api && python3 -m pytest tests/test_smoke.py -v

# Playback coherence integration tests (3 tests)
cd /workspace/api && python3 -m pytest /workspace/tests/test_playback_coherence.py -v
```

### Key caveats

- There is no `requirements.txt` or `pyproject.toml`. Dependencies are listed inline in `api/Dockerfile` and `worker/Dockerfile`. The pip install line for the API is: `pip install fastapi 'uvicorn[standard]' sqlmodel httpx pydantic-settings jinja2 python-multipart pytest`.
- The worker requires `ffmpeg` for RTSP clip capture, but the worker is not needed for API dev/testing.
- Tests use `python3 -m pytest` (not bare `pytest`) because pytest is installed as a user package.
- The integration test at `tests/test_playback_coherence.py` has a hardcoded REPO_ROOT path that doesn't match the workspace, but it still works when run from `api/` because `app.main` resolves via the Python path.
- No auth/login exists — the operator console is fully open.
- The `web/` directory is an empty placeholder.
