# TECHCAMAI Windows desktop install

Windows is the primary desktop packaging target for this operator build.

## Quick download / install

Open PowerShell and run:

```powershell
powershell -ExecutionPolicy Bypass -Command "iwr https://raw.githubusercontent.com/geekmarrs-alt/techcamai/master/windows/install.ps1 -OutFile $env:TEMP\install-techcamai.ps1; & $env:TEMP\install-techcamai.ps1"
```

The installer:

1. Downloads the current TECHCAMAI package.
2. Installs it to `%USERPROFILE%\TechCamAI`.
3. Creates a `TECHCAMAI Command Center` shortcut on the Windows desktop.
4. Starts Docker Compose and opens `http://localhost:8000/` when Docker Desktop is available.

## Desktop quick launch

The desktop shortcut runs `windows\launch-techcamai.ps1`.
That script starts the local stack and opens the command dashboard in the default browser.

## File structure

```text
windows/
|-- install.ps1           # one-command Windows installer and desktop shortcut creator
|-- launch-techcamai.ps1  # local desktop launcher used by the shortcut
`-- README.md             # Windows packaging notes
```

## CCTV setup flow

- Add one IP camera directly from `/ui/add`.
- Add an NVR/DVR by entering the recorder IP and using **Quick add NVR channels**.
- Each saved recorder channel is treated as its own camera for live view, alerts, and clip playback.
