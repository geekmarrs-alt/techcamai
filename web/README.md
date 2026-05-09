# web/

Future home of the TECHCAMAI product website.

The operator console lives in `api/`. This directory is a placeholder.
This project is currently focused on the Windows desktop/operator application.

---

## Intended page structure

```
web/
├── index.html             # Landing — hero, features, CTA
├── features.html          # Feature breakdown (alerts, playback, worker)
├── pricing.html           # Tier comparison (Community / Pro / Enterprise)
├── download.html          # Windows installer download page
├── docs/
│   ├── index.html         # Getting started
│   ├── windows-setup.html # Windows setup flow
│   └── api-reference.html # API references
├── login.html             # Hosted dashboard redirect — future, not yet built
├── contact.html           # Enterprise enquiry form
└── assets/
    ├── brand/             # Logos (copy from api/app/static/)
    └── screenshots/       # Dashboard screenshots for marketing use
```

---

## Landing page content checklist

- [ ] Hero: "Edge-first AI camera monitoring" + dashboard screenshot (dark mode)
- [ ] Sub-headline: Windows-first setup with one-click installer
- [ ] CTA 1: "Download for Windows" → /download
- [ ] CTA 2: "Get early access" → email capture form
- [ ] Feature strip: alert loop · clip capture · operator console
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
