# TECHCAMAI

Edge-first camera monitoring MVP.

This repo is **not** the finished product website yet. It is the current operator-facing stack: scan cameras, save cameras, run worker polling, create alerts, and review alert playback when clip capture succeeds.

## What this repo is good for right now
- Local/LAN camera onboarding
- Snapshot polling via worker
- Rule-based motion alert creation
- Alert inbox + timeline
- Post-trigger clip capture/playback MVP
- Raspberry Pi deployment path via Docker/GHCR
- Dashboard direction work for the operator UI

## What it is not yet
- Public customer-facing product site
- Login / auth / roles
- Licence or billing system
- Multi-tenant backend
- Hardened production fleet management

If anyone says this is launch-ready as a commercial SaaS today, they are chatting shit.

## Current surfaces
### Operator UI
- `/` — dashboard v2 preview (current default)
- `/preview/dashboard-v1` — simpler fallback overview
- `/preview/dashboard-v2` — explicit preview route
- `/ui/scan` — LAN scan
- `/ui/add` — test/save camera
- `/cameras/manage` — camera inventory and editing
- `/live` — live wall
- `/alerts` — alert inbox
- `/timeline` — event flow

### API / integration endpoints
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

## Beta-readiness snapshot
### Near enough for a real beta walkthrough
- Recovered FastAPI app boots
- Dashboard is no longer the broken/truncated template from the earlier recovery state
- Alert playback fields exist in the API model
- Worker has clip capture path using `ffmpeg`
- Docker Compose mounts shared `/data` volume for API + worker
- GitHub Actions workflow exists to publish multi-arch images to GHCR on `master`

### Still needs beta validation in a live environment
- Real RTSP clip capture against live camera streams
- Browser playback on the actual Pi deployment
- End-to-end ingest on the real camera/rule set
- Clear proof that every enabled camera has a valid rule
- Failure visibility for bad creds / unreachable cameras / slow snapshots
- Fresh image publish + pull on Pi from the real source-of-truth repo

For the blunt version, read `BETA_READINESS_2026-03-13.md`.

## Quick start — run on your own machine (no Docker needed)

### Prerequisites
- **Python 3.10+** — download from https://www.python.org/downloads/
  - Windows: tick **"Add Python to PATH"** during installation

### Windows
1. Download this repo: **[Download ZIP](../../archive/refs/heads/master.zip)**
2. Unzip the folder
3. Double-click **`run.bat`**

That's it. A browser window will open automatically at http://localhost:8000/.

### Mac / Linux
```bash
git clone https://github.com/geekmarrs-alt/techcamai.git
cd techcamai
./run.sh
```

### What the scripts do
1. Create a Python virtual environment (`venv/`)
2. Install dependencies from `requirements.txt`
3. Create a local `data/` folder for the SQLite database and clips
4. Start the API server on http://localhost:8000/
5. Open the dashboard in your browser

Press **Ctrl+C** to stop the server. Run the script again to restart — it skips setup if already done.

### Quick start — Docker (alternative)
```bash
cp .env.example .env
docker compose up --build
```

Then open:
- Dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs

## Raspberry Pi path
Read:
- `pi/README_PI.md`
- `pi/UPDATE_STRATEGY.md`

Short version:
1. Push code to the real GitHub-backed repo
2. Let GitHub Actions publish fresh GHCR images
3. On the Pi, pull and restart the compose stack

## Recommended demo order
Use `TOMORROW_WALKTHROUGH_CHECKLIST.md`.

## Known product truth
TECHCAMAI currently looks like a serious operator MVP, not a finished commercial control plane. That is still useful. Just present it honestly.
