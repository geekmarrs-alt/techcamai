# CLAUDE.md — AI Assistant Guide for techcamai

This file provides context for AI assistants (Claude Code, etc.) working in this repository.

---

## Project Overview

**techcamai** is an edge-first CCTV event ingestion system designed to run on Raspberry Pi (and any Docker host). It continuously polls IP cameras, performs lightweight motion detection, and stores alerts with snapshots in a local SQLite database. A built-in web dashboard provides live views, alert management, and camera configuration.

Target use case: low-cost, local-first security camera monitoring without cloud dependencies.

---

## Repository Structure

```
techcamai/
├── api/                        # FastAPI backend + web UI
│   ├── Dockerfile
│   └── app/
│       ├── main.py             # App entry point: DB models, API routes, Jinja2 views
│       ├── discover.py         # LAN camera auto-discovery (async TCP scan)
│       ├── static/             # Frontend assets (JS, SVG logos)
│       │   └── poll.js         # Client-side polling for live alert updates
│       └── templates/          # Jinja2 HTML templates
│           ├── base.html       # Shared layout, dark theme CSS
│           ├── dashboard.html  # Main overview
│           ├── live.html       # Live snapshot wall (multi-cam)
│           ├── alerts.html     # Alert list with thumbnails
│           ├── timeline.html   # Event timeline view
│           ├── cameras_manage.html
│           ├── add_camera.html
│           ├── scan.html       # LAN scan results UI
│           └── _poll_hint.html # Polling status indicator partial
├── worker/                     # Camera polling service
│   ├── Dockerfile
│   ├── worker.py               # Poll cameras, detect motion, POST to API
│   └── rtsp_grab.sh            # FFmpeg wrapper: RTSP → single JPEG frame
├── pi/                         # Raspberry Pi deployment helpers
│   ├── install.sh              # One-liner bootstrap script
│   ├── docker-compose.pi.yml   # Pi-specific compose overrides
│   ├── README_PI.md
│   └── UPDATE_STRATEGY.md      # Fleet update via Watchtower
├── .github/workflows/
│   └── docker.yml              # CI: multi-arch Docker build → GHCR
├── .env.example                # All supported environment variables
├── docker-compose.yml          # Dev/prod compose (host networking)
└── README.md                   # Quick start guide
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Uvicorn |
| ORM / Database | SQLModel, SQLite |
| Frontend | Jinja2 templates, vanilla JS, HTML/CSS |
| HTTP client | httpx (async) |
| Config | Pydantic Settings (reads `.env`) |
| Containerisation | Docker, Docker Compose |
| Camera protocols | Hikvision ISAPI, HTTP/HTTPS snapshots, RTSP |
| Authentication | HTTP Digest Auth, Basic Auth |
| Video frames | FFmpeg (RTSP → JPEG extraction) |
| CI/CD | GitHub Actions → GHCR (multi-arch: amd64 + arm64) |

---

## Database Schema

Three SQLModel tables, auto-created on startup. The database is seeded with a demo camera + motion rule if it is empty.

### Camera
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | str | |
| ip | str | |
| channel | int | Default 1 |
| scheme | str | `http` or `https`, default `https` |
| auth | str | `digest` or `basic`, default `digest` |
| username | str | |
| password | str | Stored plaintext (MVP) |
| snapshot_url | str? | Legacy override URL |
| enabled | bool | Default True |

### Rule
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | str | |
| camera_id | int FK | |
| label | str | `motion`, `person`, `vehicle`, `ppe_no_hivis` |
| min_conf | float | Default 0.5 |
| cooldown_sec | int | Default 120 s |
| enabled | bool | Default True |

### Alert
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| created_at | datetime | Indexed |
| camera_id | int | |
| rule_id | int | |
| label | str | |
| conf | float | 0.0–1.0 |
| snapshot_b64 | str? | Base64-encoded JPEG |
| acked | bool | Default False |

---

## API Routes

### UI (HTML responses via Jinja2)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard overview |
| GET | `/live` | Live multi-camera snapshot wall |
| GET | `/alerts` | Alert list with thumbnails |
| GET | `/timeline` | Event timeline |
| GET | `/cameras/manage` | Camera management UI |
| GET | `/ui/scan` | LAN discovery results |
| GET | `/ui/add` | Add / test camera form |

### JSON API
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/cameras` | List cameras (no passwords) |
| GET | `/worker/cameras` | List cameras with credentials (worker use) |
| POST | `/cameras` | Create camera |
| PUT | `/cameras/{id}` | Update camera |
| POST | `/cameras/test` | Test snapshot fetch; returns base64 preview |
| GET | `/cameras/{id}/snapshot.jpg` | Proxy live JPEG from camera |
| POST | `/discover` | Async LAN scan (120 s timeout) |
| GET | `/rules` | List rules |
| POST | `/rules` | Create rule |
| POST | `/ingest/detection` | Worker posts detections here (applies cooldown + rules) |
| POST | `/alerts/{id}/ack` | Acknowledge alert |
| GET | `/api/alerts/latest` | Polling: alerts after timestamp, optional unacked filter |

---

## Environment Variables

Defined in `.env.example`. Copy to `.env` before running.

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://127.0.0.1:8000` | Worker → API endpoint |
| `API_PORT` | `8000` | Uvicorn listening port |
| `DB_PATH` | `/data/techcamai.db` | SQLite file location |
| `POLL_INTERVAL_SEC` | `30` | Worker camera poll interval (seconds) |
| `CAMERA_SNAPSHOT_URLS` | `` | Legacy: comma-separated snapshot URLs |
| `PREFER_RTSP` | `1` | Prefer RTSP over HTTP for snapshots |
| `SMTP_HOST` | `` | Email notifications (all SMTP_* optional) |
| `SMTP_PORT` | `587` | |
| `SMTP_USER` | `` | |
| `SMTP_PASS` | `` | |
| `SMTP_FROM` | `` | |
| `SMTP_TO` | `` | |

---

## Development Workflow

### Running Locally with Docker Compose

```bash
cp .env.example .env          # configure as needed
docker compose up --build     # builds + starts api + worker
# Web UI: http://localhost:8000
```

Both services share a `/data` volume for the SQLite database. Host networking is used so the worker can reach LAN cameras directly.

### Running Without Docker (API only)

```bash
cd api
pip install fastapi uvicorn sqlmodel httpx jinja2 pydantic-settings
uvicorn app.main:app --reload --port 8000
```

### Worker Only

```bash
cd worker
pip install httpx
# Requires ffmpeg on PATH for RTSP support
API_BASE_URL=http://localhost:8000 python worker.py
```

---

## Code Conventions

### Python
- **Style**: PEP 8, snake_case for variables/functions, PascalCase for classes/models.
- **Models**: Use `SQLModel` for ORM + Pydantic validation in one class. Separate `Create`/`Update` DTOs from table models where needed.
- **Async**: Use `async def` + `httpx.AsyncClient` for all I/O (camera fetches, discovery). Synchronous DB calls are acceptable in route handlers (SQLite is fast enough).
- **Error handling**: Raise `HTTPException` for API errors. Log exceptions with `print()` (no logging framework currently).
- **Config**: Read all settings from environment via `pydantic_settings.BaseSettings`. Never hardcode credentials.

### Templates (Jinja2)
- Extend `base.html` for all full-page templates.
- UI theme: dark background with glassmorphism cards, CSS variables for colours. Keep styling in `base.html` or inline `<style>` blocks rather than separate CSS files.
- Use `_poll_hint.html` partial for any page that polls the API.

### JavaScript
- Vanilla JS only — no build step, no npm.
- Polling logic lives in `static/poll.js` (fetches `/api/alerts/latest`).
- Keep JS minimal; prefer server-side rendering.

### Docker
- Both `api/Dockerfile` and `worker/Dockerfile` use `python:3.12-slim`.
- Multi-arch builds target `linux/amd64` and `linux/arm64` (Raspberry Pi).
- Use `host` network mode in compose so containers can reach LAN camera IPs.

---

## CI/CD

GitHub Actions workflow at `.github/workflows/docker.yml`:
- **Trigger**: push to `master` or manual `workflow_dispatch`.
- **Steps**: checkout → QEMU + buildx setup → GHCR login → multi-arch build+push.
- **Images**: `ghcr.io/{owner}/techcamai-api:stable` and `ghcr.io/{owner}/techcamai-worker:stable`.
- `GITHUB_TOKEN` must have `packages: write` permission.

---

## Motion Detection (Worker)

The worker uses a **lightweight heuristic** (no ML models):

1. Fetch JPEG snapshot via HTTP or RTSP (FFmpeg).
2. Compare current frame to previous frame using:
   - SHA256 hash equality check (identical → no motion).
   - JPEG byte-size delta ratio to scale confidence (0.0–0.99).
3. Post to `/ingest/detection` if motion is detected.
4. API applies cooldown (`cooldown_sec` per rule) before persisting as an `Alert`.

This is intentionally simple. Future work may add real object detection (YOLO, etc.).

---

## Camera Discovery (`discover.py`)

1. Reads local IPv4 interfaces via `ip addr`.
2. Expands each `/prefix` into host list (skips `/31`, `/32`).
3. Scans TCP ports `80, 443, 554, 8000` with 350 ms timeout, up to 500 concurrent connections.
4. Probes Hikvision ISAPI endpoints to detect vendor.
5. Returns sorted list of `{ip, ports, vendor_hint}` dicts.

---

## Security Notes (MVP Limitations)

- **No API authentication**: all endpoints are open. Intended for LAN-only or trusted networks.
- **Passwords stored plaintext** in SQLite.
- **SSL verification disabled** (`verify=False`) when fetching camera snapshots — cameras often have self-signed certs.
- Do not expose the API port to the public internet without adding authentication middleware.

---

## Raspberry Pi Deployment

See `pi/README_PI.md` for full instructions. Quick summary:

```bash
# One-liner install on a Pi with Docker
curl -fsSL http://HOST:PORT/install.sh | sudo bash -s -- \
  --src http://HOST:PORT/techcamai.tgz \
  --camera-urls "http://user:pass@192.168.1.10/ISAPI/Streaming/channels/1/picture"
```

Fleet updates are managed via **Watchtower** pulling `:stable` images from GHCR. See `pi/UPDATE_STRATEGY.md`.

---

## Known Limitations / Future Work

- Motion detection only (no ML object detection yet).
- No user authentication on the web dashboard.
- No multi-user support.
- Passwords stored as plaintext.
- No WebSocket support — UI polls every few seconds instead.
- No persistent alert video clips; only single JPEG snapshots.
- SMTP email notifications plumbed in env but not fully tested.
