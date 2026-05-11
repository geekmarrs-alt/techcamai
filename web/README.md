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
├── pricing.html           # Tier comparison (Community / Pro / Enterprise)
├── download.html          # Windows installer + desktop launcher
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

- [ ] Hero: "Windows-first AI camera monitoring" + dashboard screenshot (dark mode)
- [ ] Sub-headline: runs locally on a Windows workstation, no cloud dependency for the core loop
- [ ] CTA 1: "Download for Windows" → /download
- [ ] CTA 2: "Get early access" → email capture form
- [ ] Feature strip: alert loop · clip capture · Windows desktop launcher · operator console
- [ ] Windows install one-liner (from `windows/README.md`)
- [ ] Pricing preview: Community (free) / Pro (£X/site/mo) / Enterprise (contact)
- [ ] Footer: GitHub, docs, contact

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
