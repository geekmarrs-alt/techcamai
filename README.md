# TECHCAMAI

TECHCAMAI is a **Windows-only CCTV monitoring application** for a local mini PC.

It discovers LAN cameras and NVR/DVR channels, runs the operator dashboard locally,
captures alert clips, and keeps the user install flow away from terminals or Python.

---

## Quick Windows download

Download and double-click:

**TECHCAMAI_Quick_Install.bat**
`https://raw.githubusercontent.com/geekmarrs-alt/techcamai/master/TECHCAMAI_Quick_Install.bat`

The public download page lives at `web/download.html`.

## Install steps

1. Download `TECHCAMAI_Quick_Install.bat`
2. Double-click it
3. Allow it to run when Windows prompts
4. Wait for installation to complete
5. Use the `TechCamAI` desktop shortcut to launch the app

---

## What the installer does

- Downloads the latest TECHCAMAI code
- Sets up local Windows app files
- Creates a desktop quick-launch shortcut
- Opens the local dashboard in the browser
- Keeps the runtime local to the Windows mini PC

---

## Manual install (if you already downloaded the repo)

1. Open the repo folder
2. Double-click `windows_install.bat`
3. Launch from desktop shortcut `TechCamAI`

Detailed guide: `docs/WINDOWS_SETUP.md`
Windows desktop structure notes: `docs/WINDOWS_DESKTOP_STRUCTURE.md`

---

## First launch

When TECHCAMAI starts, open:
- Dashboard: `http://localhost:8000/`
- Camera setup: `http://localhost:8000/ui/add`
- Camera management: `http://localhost:8000/cameras/manage`
- Alerts: `http://localhost:8000/alerts`

## Operator surfaces

- `/` - dashboard v2 preview
- `/ui/scan` - LAN camera scan
- `/ui/add` - test/save camera or quick-add NVR channels
- `/cameras/manage` - camera inventory and editing
- `/live` - live wall
- `/alerts` - alert inbox
- `/timeline` - event flow
- `/api/assistant/query` - local assistant search across indexed alerts and clips

---

## Project structure

- `TECHCAMAI_Quick_Install.bat` - one-click installer bootstrap
- `windows_install.bat` - local installer for already-downloaded repo
- `windows/` - Windows installer and launcher scripts
- `desktop_app.py` - desktop launcher entrypoint
- `api/` - backend + dashboard
- `worker/` - camera polling and detection worker
- `docs/` - setup docs

---

## Notes

- This repository is maintained as one unified codebase.
- Primary install path is the Windows quick installer.
- Raspberry Pi, Linux fleet, and terminal-first setup paths are retired.
