# TECHCAMAI playback MVP implementation notes — 2026-03-13

What changed:
- Alerts now carry `clip_path`, `clip_status`, and `clip_error` metadata.
- API startup applies a lightweight SQLite migration for those new alert columns.
- `/clips` is now served from the shared data volume.
- Worker now captures a short post-trigger MP4 clip with `ffmpeg` after an alert is created.
- Worker patches the created alert with clip status/path using `PUT /alerts/{id}/clip`.
- Alerts, timeline, and dashboard UI now show clip state and playback links/player.
- Local and Pi compose files now mount `/data` into the worker too, so clips and DB live in the same shared volume.

Current MVP behaviour:
1. motion detection triggers an alert
2. alert is created immediately
3. worker tries to capture a ~12 second RTSP clip
4. alert updates to `ready` with a playable `/clips/...mp4` path, or `failed` with an error

Deliberate scope limit:
- no pre-roll buffer yet
- no retention cleanup yet
- no download/auth hardening beyond current local-Pi MVP shape

Config knobs:
- `CLIP_CAPTURE_ENABLED=1`
- `CLIP_DURATION_SEC=12`
- `CLIPS_DIR=/data/clips`

Tested here:
- Python compile check for `api/app/main.py` and `worker/worker.py`
- shell syntax check for `worker/rtsp_grab.sh` and `worker/rtsp_clip.sh`
- FastAPI smoke test with `TestClient` covering:
  - app startup
  - alert creation via `/ingest/detection`
  - clip metadata update via `PUT /alerts/{id}/clip`
  - alerts page render with clip URL
  - timeline page render with clip status
  - dashboard page render after repairing the broken template

Not fully tested here:
- real RTSP capture against a live camera stream in this environment
- browser playback on the actual Pi deployment
