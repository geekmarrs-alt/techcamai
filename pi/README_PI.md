# TECHCAMAI — Raspberry Pi (MVP install)

Goal: one command on the Pi to install + run TECHCAMAI.

## Prereqs
- Raspberry Pi OS (Lite or Desktop)
- Network: Ethernet recommended for first test (Wi‑Fi ok later)

## Install (one-liner)
Host provides 2 files over HTTP:
- `install.sh`
- `techcamai.tgz`

Example (replace HOST/PORT):

```bash
curl -fsSL http://HOST:PORT/install.sh | sudo bash -s -- \
  --src http://HOST:PORT/techcamai.tgz \
  --camera-urls "http://user:pass@192.168.0.30/ISAPI/Streaming/channels/1/picture"
```

Then open: `http://<pi-ip>:8000/`

## Notes
- Docker is installed if missing.
- Compose stack runs under `/opt/techcamai/techcamai`.
