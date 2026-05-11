# Windows desktop product structure

TECHCAMAI is documented as a Windows-only desktop install path for operators who want a local CCTV command center on a mini PC.

## Top-level structure

```text
techcamai_app.py        # Windows desktop entry point bundled into TECHCAMAI.exe
techcamai.spec          # PyInstaller Windows build definition
api/                    # Local FastAPI command center and CCTV dashboard
api/app/main.py         # Camera, alert, playback, and assistant search APIs
api/app/templates/      # Operator UI rendered inside the local app
worker/                 # Snapshot polling and clip capture source used by the product
windows/                # Windows installer and desktop quick-launch scripts
web/download.html       # Public quick-download page for the Windows release
```

Raspberry Pi and Docker publishing paths are retired. Customer-facing setup points to the latest `TECHCAMAI.exe` release.

## Windows desktop install flow

1. User opens the download page or latest GitHub release.
2. User downloads `TECHCAMAI.exe`.
3. User double-clicks the app.
4. App starts the local dashboard and opens `http://localhost:8000/`.
5. Optional helper installer places the app in `%USERPROFILE%\TechCamAI` and creates a desktop shortcut.

## AI assistant wiring

The dashboard AI rail calls `POST /api/assistant/query`.
It currently searches the local alert/clip index by:

- time window, such as "between 2am and 3am"
- object synonym, such as "car" mapping to `vehicle`
- camera name, IP, rule name, and alert label keywords

Browser voice support uses Web Speech APIs:

- speech recognition fills the assistant query box
- speech synthesis reads the assistant answer back

Colour phrases such as "red car" are recognised but not used as a hard filter until the vision metadata pipeline stores colour/scene attributes per alert or recording.

## CCTV onboarding

- Single IP cameras are added from `/ui/add`.
- NVR/DVR units use the same screen with **Quick add NVR channels**.
- Each recorder channel becomes a separate saved camera entry, so alerts, live views, and clip playback stay channel-specific.
