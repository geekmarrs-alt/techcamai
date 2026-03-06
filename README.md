# TECHCAMAI — MVP (WIP)

Edge-first camera snapshot ingestion + AI-ish detection + rules + alerts feed.

## Quick start (dev)

```bash
cd projects/techcamai
cp .env.example .env
docker compose up --build
```

Then open:
- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/

## Status
- Skeleton Compose + FastAPI API + SQLite
- Worker polls camera snapshot URLs and posts detections to API
- Basic rules + alert creation (cooldown)

