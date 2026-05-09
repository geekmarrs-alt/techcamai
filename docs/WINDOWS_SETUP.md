# TECHCAMAI Windows setup and usage

This guide gives you a clean path to run TECHCAMAI on a Windows PC.

## 1) Prerequisites

Install these first:
- Docker Desktop for Windows (WSL2 backend enabled)
- Git for Windows
- PowerShell 5.1+ (included on modern Windows)

Verify:

```powershell
docker --version
docker compose version
git --version
```

## 2) Download the application

### Option A: direct ZIP download (recommended for non-developers)

Download:

`https://github.com/geekmarrs-alt/techcamai/archive/refs/heads/master.zip`

Extract it somewhere like:

`C:\techcamai\techcamai-master`

### Option B: git clone

```powershell
git clone https://github.com/geekmarrs-alt/techcamai.git
cd techcamai
```

## 3) Start the application (easy mode)

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start-techcamai.ps1
```

What this does:
1. Copies `.env.example` to `.env` if needed
2. Runs `docker compose up --build -d`
3. Shows startup status and URLs

Open:
- Dashboard: http://localhost:8000/
- API docs: http://localhost:8000/docs

## 4) One-step download + run on Windows

If you already have this repository checked out, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\download-and-start.ps1
```

It downloads the latest `master.zip`, extracts it, and starts the app automatically.

## 5) Common commands

From repo root:

```powershell
# Start
docker compose up -d

# Rebuild + start
docker compose up --build -d

# Stop
docker compose down

# View logs
docker compose logs -f api
docker compose logs -f worker
```

## 6) Updating

If using ZIP download, download a fresh `master.zip` and restart.

If using git:

```powershell
git checkout master
git pull origin master
docker compose up --build -d
```

## 7) Troubleshooting

- **Port 8000 already in use**: stop the process using port 8000, then restart compose.
- **Docker not running**: start Docker Desktop and wait until it shows "Engine running".
- **UI not loading**: check `docker compose ps`, then inspect logs:
  - `docker compose logs api --tail 100`
  - `docker compose logs worker --tail 100`
