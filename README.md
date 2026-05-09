# TECHCAMAI

Single-repo, operator-focused camera monitoring application.

This repository contains one application with three runtime components:
- `api/` - FastAPI backend + operator UI templates
- `worker/` - polling and detection worker
- `web/` - placeholder for future marketing site (not required to run the app)

## Repository cleanup policy (single active branch workflow)

If your remote has many old branches, use this workflow to keep one active delivery branch:

1. Keep `master` as the source-of-truth stable branch.
2. Create one short-lived feature branch per change.
3. Merge to `master` quickly, then delete the feature branch.
4. Regularly prune merged local/remote branches.

Commands:

```bash
# Remove local branches already merged into master (except master)
git checkout master
git pull origin master
git branch --merged | rg -v "^\*|master$" | xargs -r git branch -d

# Remove stale remote-tracking refs
git fetch --prune
```

To delete merged branches on GitHub UI:
- GitHub -> repository -> Branches -> delete merged branches

## Quick start (Windows-first)

Use Docker Desktop on Windows and run the helper script:

1. Install:
   - Docker Desktop
   - Git for Windows
2. Download this repo (see "Direct download for Windows" below).
3. Open PowerShell in the project root and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start-techcamai.ps1
```

Then open:
- App dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs

Detailed guide: `docs/WINDOWS_SETUP.md`

## Direct download for Windows

For this repository (`geekmarrs-alt/techcamai`), a direct source ZIP download is:

`https://github.com/geekmarrs-alt/techcamai/archive/refs/heads/master.zip`

You can also run the one-step download/start script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\download-and-start.ps1
```

This downloads `master.zip`, extracts it, copies `.env.example` to `.env`, starts Docker Compose, and opens the dashboard.

## Standard developer quick start (all platforms)

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs

## Raspberry Pi deployment

See:
- `pi/README_PI.md`
- `pi/UPDATE_STRATEGY.md`

## Current operator surfaces

### UI routes
- `/` (dashboard)
- `/ui/scan`
- `/ui/add`
- `/cameras/manage`
- `/live`
- `/alerts`
- `/timeline`

### API routes
- `/health`
- `/discover`
- `/cameras`
- `/cameras/test`
- `/worker/cameras`
- `/rules`
- `/ingest/detection`
- `/api/alerts/latest`
- `/alerts/{id}/clip`
- `/alerts/{id}/ack`
