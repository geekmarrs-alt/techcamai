# TECHCAMAI Windows setup and usage

TECHCAMAI is now distributed to users as a Windows desktop app.

## Fastest option

1. Open the latest GitHub release.
2. Download `TECHCAMAI.exe`.
3. Put it anywhere on the Windows mini PC.
4. Double-click it.

The app creates a local `data/` folder beside the `.exe`, starts the dashboard, and opens the browser automatically.

## Helper installer

Download and double-click:

`https://raw.githubusercontent.com/geekmarrs-alt/techcamai/master/TECHCAMAI_Quick_Install.bat`

The helper downloads the latest `TECHCAMAI.exe`, places it in `%USERPROFILE%\TechCamAI`, creates a desktop shortcut, and launches it.

## First-run prompts

- Windows SmartScreen may warn on unsigned builds. Choose **More info** then **Run anyway**.
- Windows Firewall may ask for network access. Choose **Allow** so LAN camera discovery can work.

## Using the app

- Dashboard: `http://localhost:8000/`
- LAN scan: `http://localhost:8000/ui/scan`
- Add camera / NVR channel: `http://localhost:8000/ui/add`
- Camera inventory: `http://localhost:8000/cameras/manage`
- Alerts: `http://localhost:8000/alerts`

## Updating

Download the newest `TECHCAMAI.exe` from the latest release and replace the old file.

## Troubleshooting

- **Port 8000 already in use**: close the other app using port 8000, then reopen TECHCAMAI.
- **Dashboard did not open**: double-click `TECHCAMAI.exe` again, or open `http://localhost:8000/` in the browser.
- **LAN scan finds nothing**: confirm the PC is on the same local network as the cameras and allow TECHCAMAI through Windows Firewall.
