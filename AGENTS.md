# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

TECHCAMAI is an edge-first IP camera monitoring stack with one source tree:

- Docker/Pi deployment: FastAPI operator console plus polling worker.
- Windows desktop package: PyInstaller wraps the FastAPI console in `TECHCAMAI.exe`.

The repo is proprietary. Do not publish installers, source bundles, Docker images, or desktop artifacts outside approved release channels.

### Architecture

- **API** (`api/`): FastAPI backend + Jinja2 operator dashboard. SQLite DB at `data/techcamai.db`, clips at `data/clips/`.
- **Worker** (`worker/`): Polling daemon for camera snapshots + motion detection + RTSP clip capture. Runs separately in Docker on Pi deployments; not bundled in the desktop `.exe`.
- **Desktop entry point** (`techcamai_app.py`): Tkinter GUI that starts uvicorn, opens the browser, and shows a status window. This is the PyInstaller entry point.
- **Build spec** (`techcamai.spec`): PyInstaller config producing `dist/TECHCAMAI.exe`.

### Building the Windows .exe

The `.exe` is built by GitHub Actions on `windows-latest`. Trigger:
- Push a version tag: `git tag v0.1.0 && git push --tags`
- Or trigger manually: Actions → `build-windows-exe` → Run workflow

You cannot build a Windows `.exe` from this Linux cloud agent VM (PyInstaller is platform-specific).

### Running tests

```bash
PYTHONPATH=/workspace/api python3 -m pytest tests api/tests
```

Use `python3 -m pytest`, not bare `pytest`.

### Running the API locally (for development/testing only)

```bash
sudo mkdir -p /data/clips && sudo chown -R $(whoami):$(whoami) /data
cd /workspace/api
DB_PATH=/data/techcamai.db CLIPS_DIR=/data/clips python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Key caveats

- Dependencies are listed in root `requirements.txt`, `api/requirements.txt`, and `worker/requirements.txt`. There is no `pyproject.toml`.
- LAN scanning uses `psutil` for cross-platform network detection, with a Linux `ip -j addr` fallback for Docker/Pi.
- `SECRET_KEY` enables worker/API bearer-token protection. Blank keeps legacy local-MVP behavior.
- UI login/user accounts are not built yet.
