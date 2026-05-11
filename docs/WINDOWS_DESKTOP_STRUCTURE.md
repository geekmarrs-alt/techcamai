# Windows desktop product structure

TECHCAMAI is now documented as a Windows-first desktop install path for operators who want a local CCTV command center on a workstation.

## Top-level structure

```text
api/                    # Local FastAPI command center and CCTV dashboard
api/app/main.py         # Camera, alert, playback, and assistant search APIs
api/app/templates/      # Operator UI rendered by the local desktop stack
worker/                 # Snapshot polling and clip capture worker
windows/                # Windows installer and desktop quick-launch scripts
web/download.html       # Controlled-access request page for desktop packages
docker-compose.yml      # Local runtime used by the Windows launcher
```

The Raspberry Pi files remain supported edge deployment references. Customer-facing install copy should point Windows users to approved desktop artifacts and `windows/install.ps1`, not public repository downloads.

## Windows desktop install flow

1. User requests access.
2. Approved user receives a private archive URL, signed release artifact, or workflow artifact.
3. User runs `windows/install.ps1` with the approved package URL, or runs `TECHCAMAI.exe`.
4. Installer places the app in `%USERPROFILE%\TechCamAI`.
5. Installer creates `TECHCAMAI Command Center.lnk` on the desktop.
6. The shortcut runs `windows\launch-techcamai.ps1`.
7. Launcher starts Docker Compose and opens `http://localhost:8000/`.

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
