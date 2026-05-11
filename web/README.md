# web/

Windows download page and future home of the TECHCAMAI product website.

The operator console lives in `api/`. This directory is a placeholder.
See `docs/PRODUCT_SHELL.md` for the full commercial-tier and website spec.

---

## Intended page structure

```
web/
├── index.html             # Landing — hero, features, CTA, Windows download
├── features.html          # Feature breakdown (alert loop, clip capture, Windows launcher)
├── pricing.html           # Tier comparison (Developer Preview / Pro / Enterprise)
├── download.html          # Controlled-access installer request / desktop/Pi onboarding
├── docs/
│   ├── index.html         # Getting started
│   ├── windows-install.html # Windows install + desktop shortcut flow
│   └── api-reference.html # /ingest/detection, /health, /api/assistant/query
├── login.html             # Hosted dashboard redirect — future, not yet built
├── contact.html           # Enterprise enquiry form
└── assets/
    ├── brand/             # Logos (copy from api/app/static/)
    └── screenshots/       # Dashboard screenshots for marketing use
```

---

## Landing page content checklist

- [ ] Hero: "Edge-first AI camera monitoring" + dashboard screenshot (dark mode)
- [ ] Sub-headline: runs locally on Windows or a Raspberry Pi on your LAN, no cloud dependency for the core loop
- [ ] CTA 1: "Request access" → /download or /contact
- [ ] CTA 2: "Get early access" → email capture form
- [ ] Feature strip: alert loop · clip capture · Windows desktop · Pi deployment · operator console
- [ ] Windows/Pi install instructions shown only after approved access
- [ ] Pricing preview: Developer Preview (approved access) / Pro (£X/site/mo) / Enterprise (contact)
- [ ] Footer: docs, contact, legal

---

## Build approach (when ready)

Keep it static. Plain HTML/CSS is fine for the marketing layer.
If templating is needed: Astro or Eleventy — both output static HTML with minimal overhead.
Do not add a React/Vue/Next.js build pipeline for a five-page marketing site.

---

## Brand assets

Copy from `api/app/static/`:
- `techcamai-icon.svg`
- `techcamai-logo.svg`
- `techcamai-logo-512.png`

---

## Domain

Placeholder: techcamai.com (not confirmed at time of writing).

## Distribution note

Do not publish public downloads, source archives, desktop builds, or GitHub links from the marketing site until the release has written licence terms and an approved distribution channel. The current repository is proprietary; see `../LICENSE`.
