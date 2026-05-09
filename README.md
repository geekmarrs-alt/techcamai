# TECHCAMAI

TECHCAMAI is an operator-focused CCTV monitoring application with:
- Web dashboard
- Alert timeline
- Worker-based camera polling and detection
- Windows desktop launcher support

---

## Windows quick install (single file)

If you want the easiest path, download **one file** and run it:

**Direct download (installer file):**  
`https://raw.githubusercontent.com/geekmarrs-alt/techcamai/master/TECHCAMAI_Quick_Install.bat`

### How to use it
1. Download `TECHCAMAI_Quick_Install.bat`
2. Double-click it
3. It downloads the latest repo, installs dependencies, and creates a Desktop shortcut (`TechCamAI`)
4. Launch from your Desktop shortcut

---

## Manual Windows install (repo already downloaded)

If you already downloaded/cloned the repo:
1. Open the repo folder
2. Double-click `windows_install.bat`
3. Wait for setup to finish
4. Launch from Desktop shortcut `TechCamAI`

Detailed Windows guide: `docs/WINDOWS_SETUP.md`

---

## Docker quick start (all platforms)

```bash
cp .env.example .env
docker compose up --build -d
```

Open:
- Dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Project structure

- `api/` - FastAPI backend + operator UI
- `worker/` - polling and detection worker
- `scripts/windows/` - helper scripts for Windows startup/download
- `pi/` - Raspberry Pi deployment scripts
- `docs/` - setup and operational documentation

---

## Common pages

- `/` dashboard
- `/ui/scan` discover cameras
- `/ui/add` add/test camera
- `/cameras/manage` camera inventory and edits
- `/alerts` alert inbox
- `/timeline` timeline view

---

## Developer notes

- Main branch: `master`
- Keep short-lived feature branches and merge quickly
- Delete merged branches regularly to avoid branch sprawl
