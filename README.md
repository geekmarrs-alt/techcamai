# TECHCAMAI

**Edge-first AI camera monitoring for Windows.**

![Dashboard](api/app/static/techcamai-logo-512.png)

---

## Download & install (30 seconds)

1. Go to the **[Releases page](../../releases/latest)**
2. Download **`TECHCAMAI.exe`** (one file, ~30 MB)
3. Put it anywhere on your PC (Desktop, Documents, wherever you like)
4. Double-click it

Your browser opens automatically to the operator dashboard. That's it — no installer, no setup wizard, no dependencies.

> **First-run notes:**
> - **Windows SmartScreen** may show a warning — click *More info* → *Run anyway*. This is normal for unsigned apps.
> - **Windows Firewall** will ask to allow network access — click *Allow*. This lets the dashboard load in your browser and enables LAN camera scanning.

---

## Quick-start walkthrough

Once the app is running, here's how to get your cameras monitored in under 2 minutes:

### 1. Open the dashboard

After double-clicking `TECHCAMAI.exe`, two things appear:
- A small **status window** confirming the app is running
- Your **browser** opens to the command dashboard at `http://localhost:8000`

The sidebar on the left is your main navigation. Everything is one click away.

### 2. Scan your network for cameras

Click **LAN scan** in the sidebar. TECHCAMAI scans your local network and lists any IP cameras it finds (Hikvision cameras are detected automatically). Click **Add / test** next to any camera to onboard it.

### 3. Add a camera manually

If your camera wasn't found by the scan, click **Add / test** in the sidebar:
- Enter the camera's **IP address** (e.g. `192.168.1.100`)
- Enter the **username** and **password**
- Set the **channel** (usually `1`)
- Click **Test snapshot** to verify the connection
- Click **Save camera** to add it

### 4. Monitor

Once cameras are saved, TECHCAMAI monitors them automatically:
- **Live wall** — click **Live** in the sidebar to see all camera feeds updating in real time
- **Motion detection** — the system compares frames and triggers alerts when motion is detected
- **Alert inbox** — click **Alerts** to see every detection with timestamp, camera name, and confidence score

### 5. Respond to alerts

When an alert appears:
- Open the **Alerts** inbox
- Review the detection details
- If a clip was captured, click **Play clip** to watch the footage
- Click **Acknowledge** to mark the alert as reviewed
- The dashboard counter updates to show how many alerts still need attention

### 6. Manage your cameras

Click **Cameras** in the sidebar to:
- Edit camera names, IP addresses, and credentials
- Enable or disable individual cameras
- Delete cameras you no longer need
- Check which cameras have detection rules assigned

---

## Dashboard pages

| Sidebar link | What it does |
|---|---|
| **Overview** | Command dashboard — camera wall, alert feed, system pulse, quick stats |
| **Live** | Snapshot wall showing all enabled cameras with auto-refresh |
| **Alerts** | Alert inbox — review detections, play clips, acknowledge |
| **Timeline** | Chronological event flow with 24-hour activity strip |
| **Cameras** | Camera inventory — edit settings, enable/disable, delete |
| **LAN scan** | Scan your local network to discover IP cameras |
| **Add / test** | Manually add a camera by IP and test the connection |

The API documentation is also available at `/docs` for integration and automation.

---

## Your data

Everything is stored locally in a `data/` folder created next to the `.exe`:

| File | What it stores |
|---|---|
| `data/techcamai.db` | Camera config, detection rules, alerts (SQLite database) |
| `data/clips/` | Captured video clips from triggered alerts |

**Portable:** move the `.exe` and the `data/` folder together to any other PC and your entire setup comes with you.

**Fresh start:** delete the `data/` folder and relaunch — the app creates a clean database automatically.

---

## Stopping the app

Close the small status window, or click **Stop & Exit** on it. The server shuts down and the dashboard becomes unavailable until you launch again.

---

## Planned features

These are visible in the dashboard as placeholder panels, ready for when the backend is built:

- **AI scene summaries** — per-camera description of the last detection window
- **Voice control** — ask about cameras, incidents, or coverage by voice or text
- **Smart triage** — auto-cluster incidents by proximity and confidence
- **Person / vehicle detection** — ML model for object classification beyond motion

---

## Raspberry Pi deployment

For headless 24/7 monitoring on a Raspberry Pi using Docker, see:
- [`pi/README_PI.md`](pi/README_PI.md) — setup instructions
- [`pi/UPDATE_STRATEGY.md`](pi/UPDATE_STRATEGY.md) — auto-update via Watchtower + GHCR

---

## Building from source

To build `TECHCAMAI.exe` yourself on a Windows machine:

```
pip install -r requirements.txt psutil pyinstaller
pyinstaller techcamai.spec
```

The output is `dist/TECHCAMAI.exe`.

This also runs automatically via GitHub Actions (`build-windows-exe` workflow) when you push a version tag (e.g. `v0.1.0`) or trigger it manually from the Actions tab.

---

## System requirements

- **Windows 10 or later** (64-bit)
- A modern web browser (Chrome, Edge, Firefox)
- IP cameras on the same local network (Hikvision recommended, any ONVIF/RTSP camera should work)

---

## Current state

TECHCAMAI is a working operator MVP for local camera monitoring. It is not a finished commercial product — there is no login, no multi-tenant support, and no billing. The AI and voice features shown in the dashboard are planned. The core monitoring, alerting, and camera management features are fully functional.
