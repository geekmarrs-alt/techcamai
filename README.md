# TECHCAMAI

**Edge-first AI camera monitoring for Windows.**

Download, double-click, done. No installers, no dependencies, no terminal.

---

## Download

Go to **[Releases](../../releases/latest)** and download **`TECHCAMAI.exe`**.

That's it. Double-click the file and the operator dashboard opens in your browser.

> **Windows SmartScreen** may show a warning the first time — click *More info* → *Run anyway*. This is normal for unsigned executables and will be resolved with code signing in a future release.

---

## What it does

TECHCAMAI turns IP cameras on your local network into a monitored security system.

| Feature | What you get |
|---|---|
| **LAN camera discovery** | Scans your network for Hikvision and ONVIF-compatible cameras |
| **Camera management** | Add, edit, test, enable/disable cameras from the dashboard |
| **Motion detection** | Automatic frame-by-frame motion detection on all enabled cameras |
| **Alert inbox** | Every detection becomes an alert you can review and acknowledge |
| **Clip capture** | Triggered alerts record a short video clip from the camera |
| **Live wall** | Real-time snapshot view of all your cameras at once |
| **Timeline** | Chronological event view with 24-hour activity strip |
| **Operator dashboard** | Dark-themed command centre designed for fast triage |

### Planned features (shown in dashboard, not yet active)
- AI-powered scene summaries
- Voice control / natural language queries
- Smart alert triage and clustering
- Person / vehicle detection via ML model

---

## How it works

When you launch `TECHCAMAI.exe`:

1. A small status window appears confirming the app is running
2. Your default browser opens to the operator dashboard at `http://localhost:8000`
3. A `data/` folder is created next to the `.exe` to store your camera database and clips
4. The LAN scanner detects cameras on your local network via the `/ui/scan` page

### Firewall
Windows Firewall will prompt on first run — click **Allow** so the dashboard can load in your browser.

### Stopping
Close the status window or click **Stop & Exit** to shut down.

### Your data
Everything is stored locally in the `data/` folder next to the `.exe`:
- `techcamai.db` — camera config, rules, and alerts (SQLite)
- `clips/` — captured video clips

Move the `.exe` and `data/` folder together to keep your setup portable.

---

## Operator console pages

| Page | URL | What it does |
|---|---|---|
| Dashboard | `/` | Command centre with camera wall, alert feed, system pulse |
| Live wall | `/live` | Real-time snapshot grid of all enabled cameras |
| Alerts | `/alerts` | Alert inbox — review, play clips, acknowledge |
| Timeline | `/timeline` | Chronological event flow with 24h activity strip |
| Cameras | `/cameras/manage` | Camera inventory — edit config, enable/disable, delete |
| LAN scan | `/ui/scan` | Scan your network for cameras |
| Add camera | `/ui/add` | Test connection and save a new camera |
| API docs | `/docs` | Auto-generated REST API reference |

---

## Raspberry Pi deployment

For headless deployment on a Pi, see:
- `pi/README_PI.md`
- `pi/UPDATE_STRATEGY.md`

This uses Docker Compose with images published to GHCR via GitHub Actions.

---

## Building from source

If you want to build the `.exe` yourself:

```
pip install -r requirements.txt psutil pyinstaller
pyinstaller techcamai.spec
```

Output: `dist/TECHCAMAI.exe`

The GitHub Actions workflow `build-windows-exe` does this automatically on Windows when you push a version tag (e.g. `v0.1.0`) or trigger it manually from the Actions tab.

---

## Current state

This is an operator MVP, not a finished commercial product. It is useful for real camera monitoring on a local network. The AI and voice features shown in the dashboard are planned — the placeholders are there so the UI is ready when the backend catches up.
