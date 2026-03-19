# TECHCAMAI Product Shell

> This document defines the intended commercial product wrapper around the operator MVP.
> Nothing described here is implemented yet unless explicitly noted as current.
> Goal: keep decisions coherent when implementation begins, without pretending it exists now.

---

## Product positioning

TECHCAMAI is an edge-first AI camera monitoring platform for operators.
It runs on a Raspberry Pi on your LAN, processes camera streams locally,
and surfaces real-time alerts with clip evidence in a premium operator console.

**Key differentiators:**
- **Edge-native** — AI inference and clip capture happen on-site. No cloud dependency for the core loop.
- **Operator-focused** — The console is built for security operators, not IT admins or end customers.
- **Evidence-forward** — Every alert carries a clip. Operators see what triggered the alert.
- **Lightweight deployment** — Docker Compose on a Pi. No Kubernetes, no cloud agents.

**Audience (priority order):**
1. Security-conscious SMBs deploying IP cameras on-prem
2. Integrators and resellers adding monitoring to Hikvision/IP camera installs
3. Solo operators building their own CCTV back-end

**Non-audience right now:**
- Enterprise fleet operators expecting SOC integrations
- Residential consumers wanting a phone app

---

## Commercial tiers

> Direction update from Kris on 2026-03-16: TECHCAMAI should not be treated as a free-for-all product that anyone can download and use indefinitely without paying. Even if the current MVP is technically open/self-hostable in places, the commercial direction is licence/membership-first with controlled customer access and admin-managed provisioning.

### Community (current state — implemented)

- Self-hosted, single-site deployment
- All current MVP features: LAN scan, camera management, alert inbox, clip capture, dashboard
- No auth, no license key required
- Free — open-source or free binary distribution
- Camera soft-limit: 4 (honour system; not enforced in MVP)
- Support: community / GitHub issues

### Operator Pro (planned)

- License key activation via `TECHCAMAI_LICENSE_KEY` env var
- Camera limit: unlimited
- Email / webhook alert notifications
- Rule templates and scheduled suppression windows
- Extended clip retention settings
- Support: email, 48 h response SLA
- Price direction: per-site/per-month (e.g. £29–£49/site/mo)

### Enterprise (future)

- Multi-site / multi-Pi fleet dashboard
- Multi-tenant support (segregated operator workspaces)
- Fleet OTA management UI
- Machine-to-machine API access
- Custom integrations (VMS connectors, SIEM forwarding)
- Support: dedicated contact, contracted SLA
- Price direction: annual site licence or per-camera

---

## Website structure

The public product website is **not in this repo**. The `web/` directory is a placeholder.
See `web/README.md` for structure sketch.

Top-level pages:

```
techcamai.com/
├── /                    # Landing — hero, feature highlights, CTA
├── /features            # Feature breakdown (alert loop, clip capture, Pi deploy)
├── /pricing             # Tier comparison (Community / Pro / Enterprise)
├── /docs                # Getting started, Pi deployment, API reference
├── /download            # Community binary / Pi install one-liner
├── /login               # Hosted dashboard redirect (future — not yet built)
└── /contact             # Enterprise enquiry form
```

**Landing page must-haves:**
- Dashboard screenshot (operator console, dark mode)
- "Edge-first AI camera monitoring" as primary value prop
- "Self-host free" entry point prominently — no credit card
- Pi install one-liner
- Email capture for early access / beta list

---

## Auth / login design intent

**Current state:** No auth. The operator console is open on the LAN. This is intentional for the MVP.

**Intended design (not yet built):**

1. **Login page** at `/login`
   - Simple username/password form; no OAuth or SSO in initial version
   - Session cookie (JWT signed with `SECRET_KEY` env var)

2. **Protected routes** — all operator UI routes require an authenticated session
   - Middleware: `api/app/auth.py` (does not exist yet; hook comment in `base.html`)
   - Exempt: `/login`, `/health`, `/ingest/detection` (worker uses token header instead)
   - If a user is not authenticated (or does not have a valid login/code), they should be sent to the public website/login entry flow rather than dropped into the operator dashboard blindly

3. **Default credentials on first boot**
   - Username: `admin`
   - Password: generated on first start, printed to container logs once
   - Forced password change on first login

4. **License key check**
   - Validated on startup by `api/app/shell.py` (scaffold exists)
   - Absent key → Community edition (camera soft-limit applies)
   - Valid key → Pro or Enterprise features unlock
   - Key format: `TCAM-XXXX-XXXX-XXXX` (alpha-numeric segments)

5. **Worker / ingest auth**
   - Worker sends `X-Worker-Token: <token>` header on `/ingest/detection`
   - Token derived from `SECRET_KEY` — avoids requiring a login session for the worker process
   - Currently not enforced; ingest endpoint is open

6. **Admin provisioning UI intent**
   - Kris needs an admin-only interface in the dashboard/product shell
   - Admin can create/manage customer licence keys
   - Admin can create/manage customer login credentials/access
   - This admin area should be clearly separated from normal operator views
   - Current state: planned only, not built

---

## Paywall placement

Features that gate behind Operator Pro:

| Feature                   | Community | Pro     |
|---------------------------|-----------|---------|
| Camera count              | 4         | Unlimited |
| Email alerts              | No        | Yes     |
| Webhook notifications     | No        | Yes     |
| Clip retention config     | Default   | Configurable |
| Rule templates            | No        | Yes     |
| Scheduled suppression     | No        | Yes     |

Features behind Enterprise (beyond Pro):

| Feature                   | Pro | Enterprise |
|---------------------------|-----|------------|
| Multi-site fleet view     | No  | Yes        |
| Multi-tenant workspaces   | No  | Yes        |
| Fleet OTA management      | No  | Yes        |
| M2M API access            | No  | Yes        |

**Rule:** Do not add fake gates to the current MVP. Gates ship only when the license-check path in `shell.py` is real.

---

## Integration touchpoints

Where the product shell hooks into the existing operator MVP:

### `api/app/shell.py` ← scaffold exists

Central module for edition detection and feature gating.

```python
from app.shell import current_edition, feature_allowed, camera_limit
```

- `current_edition()` → `Edition.COMMUNITY | PRO | ENTERPRISE`
- `feature_allowed("email_alerts")` → `True / False`
- `camera_limit()` → `int | None` (None = unlimited)

When license validation is implemented, only this module changes.
All call sites stay the same.

### `api/app/templates/base.html`

- Auth header bar above the `.app` grid: `<!-- [SHELL] auth-bar -->`
- Login redirect on 401 in `poll.js` / fetch handlers
- Edition badge in sidebar brand area (already added — shows "Developer Preview")

### `api/app/main.py`

- Startup event: call `shell.current_edition()`, log edition, store in `app.state`
- Auth middleware: session check on protected routes (see `auth.py` when built)
- `POST /license/activate` endpoint (future)
- `GET /api/me` → `{ username, edition, camera_limit }` (future)

### `worker/worker.py`

- Add `X-Worker-Token` header to all `requests` calls against the API
- Token = `HMAC(SECRET_KEY, "worker")` or a shared static token from env
- Currently no header is sent; ingest endpoint is open

### `.env.example`

Already updated to include:
- `SECRET_KEY` — session signing + worker token derivation
- `TECHCAMAI_LICENSE_KEY` — Pro/Enterprise activation (blank = Community)

---

## Deployment model

### Community / self-hosted (current)

- `docker compose up` locally or Pi Docker Compose stack
- No phone-home, no license server call in Community mode
- Future: single binary distribution via PyInstaller or compiled Pi image

### Hosted (future consideration)

- Operator console served from cloud
- Cameras remain on LAN; Pi acts as edge agent posting ingest data to hosted API
- Auth mandatory in this model
- Not a current priority — self-hosted is the core motion

---

## Honest current state

| Area                  | Status                                        |
|-----------------------|-----------------------------------------------|
| Operator console      | Real MVP, running                             |
| Auth / login          | Not built — hook comments in place            |
| License / billing     | Not built — `shell.py` scaffold exists        |
| Product website       | Not in this repo — `web/README.md` placeholder|
| Email alerts          | SMTP env vars present, not wired to rules     |
| Fleet management      | Not built                                     |
| Edition gating        | Shell stub only — no gates enforced           |
| Worker auth header    | Not enforced — ingest endpoint is open        |
