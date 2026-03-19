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

## Publishing / update flow

For a proper image-based release instead of manual source copying:

1. Commit changes to the repo that owns the GitHub remote.
2. Push to `master` so `.github/workflows/docker.yml` publishes fresh `:stable` images to GHCR.
3. On the Pi, let Watchtower update automatically or run a manual pull + restart.

Helper scripts:

```bash
./pi/scripts/check-publish-path.sh
./pi/scripts/build-pi-bundle.sh
```

The real "done" moment is when GitHub Actions `build-and-push` is green for that commit and the Pi has pulled the new `:stable` images.

## Troubleshooting

### Is the stack running?
```bash
docker compose -f pi/docker-compose.pi.yml ps
```
All three services (api, worker, watchtower) should show `Up` or `Up (healthy)`.

### Is the API up?
```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
```
Healthy output: `"ok": true, "db": "ok"`.
If `db` is `"error"`, the SQLite file may be missing — check the `/data` volume is mounted correctly.

### Is the worker polling?
The health endpoint reports the worker heartbeat:
```bash
curl -s http://127.0.0.1:8000/health
# Look for "worker_last_seen" and "worker_stale"
```
`worker_stale: true` means the worker hasn't polled in >90s. Check worker logs:
```bash
docker compose -f pi/docker-compose.pi.yml logs worker --tail 50
```

### No alerts appearing?
1. Check that enabled cameras have rules: open `/cameras/manage` — cameras without rules show a yellow **"no rules"** badge.
2. Check worker logs for snapshot errors: `docker compose logs worker --tail 100`
3. Verify camera credentials by visiting `/ui/add?ip=<camera-ip>` and clicking "Test snapshot".

### Camera snapshot fails (401/403)
- Try switching `Auth` from `digest` → `basic` (or vice versa) in `/cameras/manage`.
- Confirm the ISAPI path. Most Hikvision cameras use `https://<ip>/ISAPI/Streaming/channels/101/picture` for channel 1.
- Use `curl -v --digest -u admin:password https://<ip>/ISAPI/Streaming/channels/101/picture` from the Pi to test directly.

### Clip capture fails (clip_status: failed)
- RTSP capture requires ffmpeg and network reach to port 554 on the camera.
- Check clip error via `/alerts` page.
- Test RTSP directly: `ffprobe -v error rtsp://<user>:<pass>@<ip>:554/Streaming/Channels/101`

### Service won't restart after crash
Both api and worker have `restart: unless-stopped`. Check for a hard stop:
```bash
docker compose -f pi/docker-compose.pi.yml start api worker
```

### Watchtower is updating too aggressively
Set `WATCHTOWER_SCHEDULE` in the compose file to a less frequent cron, or remove Watchtower and pull manually:
```bash
docker compose -f pi/docker-compose.pi.yml pull && docker compose -f pi/docker-compose.pi.yml up -d
```
