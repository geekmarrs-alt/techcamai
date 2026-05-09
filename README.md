# TECHCAMAI

TECHCAMAI is now a **Windows-only CCTV monitoring application**.

---

## One-click Windows download and install

Download this single file:

**TECHCAMAI_Quick_Install.bat**
`https://raw.githubusercontent.com/geekmarrs-alt/techcamai/master/TECHCAMAI_Quick_Install.bat`

### Install steps (non-technical)
1. Download `TECHCAMAI_Quick_Install.bat`
2. Double-click it
3. Allow it to run when Windows prompts
4. Wait for installation to complete
5. Use the `TechCamAI` desktop shortcut to launch the app

---

## What the installer does

- Downloads the latest TECHCAMAI code
- Installs required Python dependencies
- Sets up local app files
- Creates a desktop quick-launch shortcut

---

## Manual install (if you already downloaded the repo)

1. Open the repo folder
2. Double-click `windows_install.bat`
3. Launch from desktop shortcut `TechCamAI`

Detailed guide: `docs/WINDOWS_SETUP.md`

---

## First launch

When TECHCAMAI starts, open:
- Dashboard: `http://localhost:8000/`
- Camera setup: `http://localhost:8000/ui/add`
- Camera management: `http://localhost:8000/cameras/manage`
- Alerts: `http://localhost:8000/alerts`

---

## Project structure

- `TECHCAMAI_Quick_Install.bat` - one-click installer bootstrap
- `windows_install.bat` - local installer for already-downloaded repo
- `desktop_app.py` - desktop launcher entrypoint
- `api/` - backend + dashboard
- `worker/` - camera polling and detection worker
- `docs/` - setup docs

---

## Notes

- This repository is maintained as one unified codebase.
- Primary install path is the Windows quick installer.
