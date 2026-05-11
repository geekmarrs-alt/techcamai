# TECHCAMAI Windows desktop install

Windows is the only supported customer packaging target for this operator build.

## Quick download / install

Download `TECHCAMAI.exe` from the latest GitHub release and double-click it.
For a helper installer, download `TECHCAMAI_Quick_Install.bat` and double-click it.

The installer:

1. Downloads the current `TECHCAMAI.exe`.
2. Installs it to `%USERPROFILE%\TechCamAI`.
3. Creates a `TechCamAI` shortcut on the Windows desktop.
4. Launches the Windows app.

## Desktop quick launch

The desktop shortcut runs `windows\launch-techcamai.ps1`.
That script starts `TECHCAMAI.exe`, which opens the command dashboard in the default browser.

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
