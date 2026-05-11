# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

TECHCAMAI is a **native Windows desktop application** for edge-first IP camera monitoring. The end-user experience is: download `TECHCAMAI.exe`, double-click, dashboard opens in the browser. No Python, no terminal, no installers.

Under the hood it is a FastAPI app bundled via PyInstaller into a single `.exe`. The source code lives in this repo and the build runs on GitHub Actions (Windows runner).

### Architecture

- **API** (`api/`): FastAPI backend + Jinja2 operator dashboard. SQLite DB at `data/techcamai.db`, clips at `data/clips/`.
- **Worker** (`worker/`): Polling daemon source for camera snapshots, motion detection, and clip capture.
- **Desktop entry point** (`techcamai_app.py`): Tkinter GUI that starts uvicorn, opens the browser, and shows a status window. This is the PyInstaller entry point.
- **Build spec** (`techcamai.spec`): PyInstaller config producing `dist/TECHCAMAI.exe`.

### Building the Windows .exe

The `.exe` is built by GitHub Actions on `windows-latest`. Trigger:
- Push a version tag: `git tag v0.1.0 && git push --tags`
- Or trigger manually: Actions → `build-windows-exe` → Run workflow

You cannot build a Windows `.exe` from this Linux cloud agent VM (PyInstaller is platform-specific).

### Running tests

```bash
# API smoke tests (26 tests)
cd /workspace/api && python3 -m pytest tests/test_smoke.py -v

# Playback coherence integration tests (3 tests)
cd /workspace/api && python3 -m pytest /workspace/tests/test_playback_coherence.py -v
```

The two test suites must be run separately (they each set up their own DB environment at import time).

### Running the API locally (for development/testing only)

```bash
sudo mkdir -p /data/clips && sudo chown -R $(whoami):$(whoami) /data
cd /workspace/api
DB_PATH=/data/techcamai.db CLIPS_DIR=/data/clips python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Key caveats

- Dependencies are listed in `requirements.txt` for the Windows build workflow. There is no `pyproject.toml`.
- Use `python3 -m pytest` (not bare `pytest`) — pytest is installed as a user package.
- LAN scanning uses `psutil` for Windows-friendly network detection.
- The `web/` directory is an empty placeholder.
- No auth/login exists — the operator console is fully open.
- AI assist and voice control panels in the dashboard are UI placeholders marked "planned" — no backend ML or speech code exists yet.
