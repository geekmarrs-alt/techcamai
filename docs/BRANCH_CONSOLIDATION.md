# Branch consolidation notes

This branch is intended to become the one coherent line of development for TECHCAMAI.

## Integrated here

- Proprietary `LICENSE` and README ownership notices.
- Removal of checked-in release/backup artifacts.
- API smoke-test isolation and repo-relative playback tests.
- Camera API safety fixes: public camera responses do not expose passwords, unsafe literal IP targets are rejected, and camera passwords are encrypted at rest.
- TLS verification controls for camera snapshot checks.
- Optional worker/API bearer-token protection through `SECRET_KEY`.
- License key validation in `api/app/shell.py`.
- Windows desktop packaging files: `techcamai_app.py`, `techcamai.spec`, icon, and private `build-windows-exe` workflow.
- Cross-platform LAN detection via `psutil` with Linux fallback.
- Windows controlled-install scripts and docs.
- Local assistant query endpoint and NVR channel bulk-add flow.
- Central dependency manifests for root, API, and worker.
- Docs cleanup: dated root notes moved under `docs/archive/2026-03-13/`.

## Branches to close after merge

The following branch themes are represented here and should not remain as competing development lines after this branch merges:

- `cursor/proprietary-docs-protection-1357`
- `cursor/fix-flaky-ci-tests-f579`
- `cursor/fix-camera-security-regressions-b025`
- `cursor/windows-assistant-download-e4d9`
- `cursor/add-agents-md-0bae`
- `fix/plaintext-camera-passwords-*`
- `fix/ssrf-camera-test-*`
- `security-fix-tls-verification-*`
- `security-fix-worker-auth-*`
- `implement-license-validation-*`

Large legacy website/rebuild branches were not merged wholesale because they conflict with the proprietary controlled-release direction and mix experiments with source cleanup. Reuse specific assets only through reviewed commits on `master`.

## Go-forward rule

After this merges, treat `master` as the only source-of-truth branch. New work should be short-lived, reviewed, merged, and deleted instead of becoming a parallel product direction.
