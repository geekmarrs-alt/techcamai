# TECHCAMAI tomorrow walkthrough checklist

Use this in order. Keep it tight. Prove the loop.

## Before Kris joins
### 1. Sanity check the app
- [ ] `docker compose up -d --build`
- [ ] `docker compose ps` — api should show `(healthy)` before worker starts
- [ ] `curl -s http://127.0.0.1:8000/health` — confirm `"ok": true`, `"db": "ok"`, and `"worker_stale": false`
- [ ] open `/`
- [ ] open `/alerts`
- [ ] open `/timeline`
- [ ] open `/cameras/manage` — yellow banner at top will list any enabled cameras with no rules
- [ ] check worker logs: `docker compose logs worker --tail=30` — confirm startup line and poll activity

### 2. Confirm camera inventory truth
- [ ] list cameras
- [ ] note which are enabled
- [ ] note which enabled cameras have working snapshot access
- [ ] note which enabled cameras have rules
- [ ] disable or clearly label junk/demo rows before walkthrough if needed

### 3. Confirm rule coverage
- [ ] every enabled real camera has at least one enabled rule
- [ ] label/cooldown values make sense for demo

### 4. Confirm playback path
- [ ] worker is running
- [ ] clips directory is writable
- [ ] at least one recent alert shows a sane clip state (`pending`, `ready`, or explicit `failed`)

## During the walkthrough
### A. Open with the honest frame
Say:
- this is the operator MVP
- playback is in MVP state
- today we are proving the live alert loop and deployment shape

### B. Show the product spine
In this order:
1. dashboard (`/`)
2. camera management (`/cameras/manage`)
3. live wall (`/live`)
4. alerts (`/alerts`)
5. timeline (`/timeline`)

### C. Prove one fresh event
- [ ] trigger or post one controlled detection
- [ ] confirm alert appears on dashboard
- [ ] confirm alert appears in inbox
- [ ] confirm alert appears in timeline
- [ ] confirm clip becomes `ready` or fails with a visible reason (hover "Failed ⚠" pill for error detail)

### D. Show deployment lane briefly
- [ ] point to GitHub Actions image publish workflow
- [ ] point to Pi compose pull/restart path
- [ ] avoid getting dragged back into manual patch hell

## If something breaks
### If ingest works but clip fails
Say:
- alerting loop is working
- playback capture failed on this run
- failure is isolated to clip generation, not the whole pipeline

### If camera access fails
Say:
- integration issue on this camera/auth/channel
- operator flow is still valid
- this device needs credential/channel correction before beta use

### If deployment path is still messy
Say:
- the correct path is image publish → Pi pull
- any manual tarball/source-copy step is temporary debt, not the intended system

## Hard no-go areas for tomorrow
Do **not** oversell:
- login/auth
- billing/licensing
- production hardening
- multi-tenant product readiness
- fleet OTA maturity

## Success definition
Tomorrow is a success if Kris can see:
- a coherent operator product
- one real end-to-end alert path
- a believable playback story
- a sane deployment direction

That is enough.
