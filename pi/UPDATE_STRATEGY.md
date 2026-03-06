# TECHCAMAI Pi Update Strategy (MVP → Production)

Goal: reliable, low-touch updates across deployed Raspberry Pi units, without bricking demos.

## Recommended MVP: Docker images + Watchtower

### Why
- Dead simple operations.
- Rollback is as easy as pinning an older tag/digest.
- No custom OTA agent needed (yet).

### How it works
1. Build/push images:
   - `techcamai-api` and `techcamai-worker` to a registry (GHCR recommended).
2. Each Pi runs `docker-compose.pi.yml`.
3. Watchtower checks for newer images on a schedule and restarts updated services.

### Staged rollout (important)
Use tags:
- `:beta` for 1–2 test units
- `:stable` for the rest

Promote by retagging the same image digest from `beta` → `stable` after validation.

### Safety / guardrails
- Prefer immutable digests for critical deployments.
- Add healthchecks (next step) so bad deploys fail fast.
- Keep `/data` volume stable so DB survives updates.

## Next step after MVP: Signed updates + rollback policy
If you want a more “firmware” feel:
- Signed manifest served from your infra
- Pi updater verifies signature, downloads bundle, switches version, runs healthcheck
- Auto-rollback on failure

We can build that once the demo is stable.

## Management / access
Recommended for any fleet:
- Tailscale on each Pi (remote SSH, metrics, emergency fixes)

