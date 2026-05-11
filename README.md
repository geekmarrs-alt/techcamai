# TECHCAMAI

Edge-local camera monitoring for Windows workstations and Raspberry Pi deployments.

## Proprietary notice

TECHCAMAI is proprietary software. Copyright (c) 2026 TECHCAMAI. All rights reserved.

This repository, source code, documentation, UI designs, brand assets, Docker images, Pi bundles, desktop builds, archives, and generated binaries are not open source and are not licensed for copying, redistribution, publication, resale, or production use without written permission from the owner.

Access to the repository or a build artifact does not grant a licence to fork, clone for reuse, rebrand, package, sell, or deploy TECHCAMAI as another product. See `LICENSE`.

## What is in this repo

- `api/` - FastAPI operator console, templates, REST endpoints, SQLite models, assistant search.
- `worker/` - Camera polling, motion detection, ingest posting, RTSP clip capture.
- `windows/` - controlled Windows install/launcher scripts.
- `pi/` - Raspberry Pi compose, installer, and update strategy.
- `web/` - static marketing/download placeholders; not the live product website.
- `docs/` - product specs, demo checklist, Windows structure, archived historical notes.

## Current product state

Works today:
- LAN camera discovery/onboarding.
- Add/manage cameras and NVR recorder channels.
- Snapshot polling and rule-based motion alerts.
- Alert inbox, timeline, live wall, dashboard preview.
- Clip capture/playback when RTSP capture succeeds.
- Local assistant search across indexed alerts/clips.
- Camera credential encryption at rest.
- Optional worker/API bearer-token protection via `SECRET_KEY`.
- GHCR image publishing from `master`.
- Windows `.exe` build workflow for approved desktop artifacts.

Not finished yet:
- User login/roles.
- Customer billing portal.
- Multi-tenant hosted control plane.
- Fleet management UI.
- Public website/download flow.

## Quick start: local Docker stack

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs

Useful checks:
```bash
docker compose ps
curl -s http://127.0.0.1:8000/health
```

## Windows desktop build

The source of truth is still this repo. The Windows desktop package wraps the API console in `TECHCAMAI.exe` with PyInstaller.

Approved build paths:
1. Run the private GitHub Actions workflow `build-windows-exe`.
2. Or build on a Windows machine:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller techcamai.spec
```

Output: `dist\TECHCAMAI.exe`.

Do not publish the `.exe`, `dist/`, installer scripts, or source archives publicly. Use `windows/README.md` for the controlled install flow.

## Raspberry Pi deployment

For a Pi, use registry images and Watchtower:

```bash
cp .env.example .env
docker compose -f pi/docker-compose.pi.yml up -d
```

Read:
- `pi/README_PI.md`
- `pi/UPDATE_STRATEGY.md`

Keep GHCR images private unless a written release decision approves public distribution.

## Environment settings

Start from `.env.example`.

Important values:
- `SECRET_KEY` - enables bearer-token protection between worker and API when set.
- `TECHCAMAI_LICENSE_KEY` - optional Pro/Enterprise feature key.
- `TCAI_ENCRYPTION_KEY` / `TCAI_KEY_PATH` - camera credential encryption key source.
- `DB_PATH` - SQLite database path.
- `CLIPS_DIR` - clip storage path.
- `PREFER_RTSP` - worker prefers RTSP frame grabs when set to `1`.
- `CLIP_CAPTURE_ENABLED` - enables/disables post-alert clip capture.

## Operator flow

1. Start the stack.
2. Open `/ui/scan` to discover LAN devices.
3. Open `/ui/add` to test and save a camera or bulk-add NVR channels.
4. Open `/cameras/manage` to edit cameras and confirm each enabled camera has rules.
5. Watch `/alerts`, `/timeline`, and `/live`.
6. Use the assistant panel or `POST /api/assistant/query` to search indexed alert history.

## Tests

Install local dependencies if needed:

```bash
python3 -m pip install -r requirements.txt
```

Run the focused suite:

```bash
PYTHONPATH=/workspace/api python3 -m pytest tests api/tests
```

## Branch policy

Use `master` as the single source-of-truth branch after this consolidation merges. Old feature, test, security, cleanup, and experiment branches should be closed or deleted once their useful work is represented here.

This consolidation branch intentionally integrates current security, licensing, Windows, assistant, dependency, and documentation work while leaving stale large experiments out of the default path.

## More docs

- `docs/README.md` - documentation map.
- `docs/DEMO_WALKTHROUGH_CHECKLIST.md` - demo/run-through checklist.
- `docs/BRANCH_CONSOLIDATION.md` - branch cleanup notes.
- `docs/archive/2026-03-13/` - historical recovery and playback notes.
