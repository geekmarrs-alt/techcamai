# TECHCAMAI dashboard rebuild spec — 2026-03-13

This is the build-prep spec for the next TECHCAMAI dashboard pass.

It uses the shared dashboard mockup as **design reference**, not a literal clone.
Brand is **TECHCAMAI**.

## 1. Goal

Rebuild the operator dashboard into a premium desktop-first surveillance console with:
- a **dominant central camera wall**
- **alerts and playback** treated as first-class, not side clutter
- reusable UI blocks that map cleanly to the current FastAPI + Jinja app
- clearer operator state, less visual noise, less "MVP demo page" energy

This is not the public marketing/paywall site.
This spec is for the logged-in operator console / product surface.

## 2. Design intent

Keep the dark, high-end control-room feel, but improve usability.

### Visual tone
- Deep charcoal / navy base
- Cyan, electric blue, and restrained violet accent lighting
- Dense but not cramped
- Glass/panel layering without turning into unreadable dribbble nonsense
- High-contrast text and controls
- Camera surfaces should feel like the product, not decoration

### UX tone
- Fast triage
- Clear status at a glance
- Minimal operator clicks for common tasks
- Important things move toward the middle of the screen
- Secondary admin/setup tasks move outward

## 3. Primary layout model

## Desktop-first layout

Use a 3-column shell:

1. **Left rail**
   - brand
   - primary navigation
   - system health / recording state / AI state summary
   - quick actions

2. **Center stage**
   - main dashboard hero becomes a **camera wall / focus area**
   - this is the visual anchor of the product
   - should show 1 large focus feed + supporting tiles, or a 2x2 wall depending on camera count

3. **Right rail**
   - live alert stack
   - playback queue / recent incidents
   - timeline shortcuts / operator notes / quick filters

### Priority order on desktop
1. Camera visibility
2. Active alerts
3. Playback/review
4. System summary
5. Camera/admin management

## 4. Information architecture

### Primary nav
- Overview
- Live wall
- Alerts
- Playback / Timeline
- Cameras
- Rules
- Discover / Add camera
- Settings (later)

### Dashboard page sections

#### A. Top command bar
Purpose: orient operator fast.

Contents:
- page title: `Command dashboard` or `Operations overview`
- site/time range / current shift label
- quick buttons:
  - Scan LAN
  - Add camera
  - Open alerts
  - Open playback
- optional live status chip cluster:
  - Recording state
  - AI worker state
  - Cameras online
  - Unacked alerts

#### B. Main camera stage
Purpose: dominate the page.

Recommended layout:
- one featured feed panel
- 3–5 supporting camera tiles beside/below it
- if there are many cameras, show “expanded wall” CTA instead of cramming all of them

Tile contents:
- camera name
- location / short metadata
- online / degraded / offline state
- latest frame image
- alert badge if recent activity exists
- quick actions:
  - open live
  - playback last alert
  - camera settings

#### C. Alert stack
Purpose: immediate triage.

Each alert card should show:
- severity / label
- camera name
- timestamp
- confidence
- thumbnail
- clip status
- quick actions:
  - acknowledge
  - play clip
  - jump to live

Sort order:
- unacked first
- newest first

#### D. Playback / incident review panel
Purpose: make evidence review obvious.

Contents:
- latest playable clips
- “clip pending” vs “clip failed” vs “clip ready” states
- quick scrub/open action
- timeline anchor points for recent incidents

#### E. System summary strip
Purpose: summary without stealing the screen.

Metrics:
- total cameras
- enabled cameras
- cameras with rule coverage
- unacked alerts
- clips ready / failed
- worker health (later once exposed)

## 5. Recommended dashboard composition

### Default desktop arrangement
- Header / command bar at top
- 2-column main body under it:
  - left: camera stage (~65–70%)
  - right: alert + playback stack (~30–35%)
- slim summary strip beneath or above main body
- admin tasks lower down

### Why
The current MVP spends too much visual budget on generic summary cards and not enough on live operational context.
TECHCAMAI should look like surveillance software, not a SaaS analytics page wearing tactical black lipstick.

## 6. Component model

Build reusable Jinja partials or macro-based blocks around these modules:

- `dashboard_shell`
- `command_bar`
- `summary_metrics`
- `camera_stage`
- `camera_focus_card`
- `camera_tile`
- `alert_feed`
- `alert_card`
- `playback_panel`
- `incident_row`
- `system_health_panel`
- `quick_actions_panel`

## 7. Data mapping to current FastAPI app

Current available server-side data:
- `cameras`
- `alerts`
- `cams`
- `rules`

### Derived dashboard data needed in route layer
The route should prepare more view-ready state instead of making the template do gymnastics.

Recommended derived fields:
- `enabled_camera_count`
- `camera_rule_count_by_id`
- `recent_alert_count`
- `unacked_alert_count`
- `clip_ready_count`
- `clip_failed_count`
- `camera_last_alert_by_id`
- `featured_camera_ids`
- `recent_playback_alerts`
- `alert_feed_items`

### Recommended server-side helper shape
Use a light dashboard view-model function in `main.py` later, e.g.:

```python
build_dashboard_view(cameras, alerts, rules) -> dict
```

That keeps Jinja cleaner and future React/Vue extraction easier if TECHCAMAI grows out of templates later.

## 8. Camera wall behaviour

### Focus feed rules
- If there is a camera with the most recent unacked alert, feature it
- Else feature most recently active enabled camera
- Else feature the first enabled camera

### Supporting tiles
- Sort by most recent alert activity
- Then by enabled state
- Then name/id

### Empty states
If no cameras exist:
- show onboarding CTA
- explain scan/add flow

If cameras exist but no snapshots work:
- show explicit degraded state
- do not fake healthy video wall tiles

## 9. Alert and playback rules

### Alert severity model for UI
Current backend labels are simple, so UI should not pretend there is a mature severity engine.

For now:
- `motion` = standard
- future `person`, `vehicle`, `ppe_no_hivis` can get differentiated chips

### Clip state display
- `ready` = strong CTA to play
- `pending` = visible but quiet
- `failed` = obvious, with error text if available

### Operator actions
Each alert card should support:
- ack
- open clip
- jump to live wall
- jump to camera settings (secondary)

## 10. Usability improvements over mockup reference

Deliberate improvements to keep:
- cleaner hierarchy
- fewer decorative stats competing with camera imagery
- stronger playback visibility
- clearer alert action targets
- less tiny low-contrast text
- less overpacked side clutter

## 11. Responsive behaviour

The layout is **desktop-first**.
Do not optimise the main experience around mobile.

### Breakpoint guidance
- `>= 1440px`: full 3-column shell, richer camera stage
- `>= 1100px`: desktop layout preserved
- `800px–1099px`: compress right rail beneath main wall
- `< 800px`: collapse to stacked admin-safe layout, but still prioritise alerts and live view

## 12. Technical implementation direction

### Phase 1 — now
- create rebuild spec
- create preview template/scaffold inside FastAPI app
- keep current routes working
- do not over-entangle with backend changes yet

### Phase 2
- introduce dashboard view-model helper in route layer
- split template into partials
- move repeated styles into a dedicated stylesheet
- add real health signals once backend exposes them

### Phase 3
- improve playback workflow
- add rules surface
- add multi-site / tenancy considerations if product scope expands

## 13. File structure recommendation

Near-term Jinja structure:

```text
api/app/templates/
  dashboard.html
  dashboard_v2_preview.html
  partials/
    dashboard_command_bar.html
    dashboard_summary_metrics.html
    dashboard_camera_stage.html
    dashboard_alert_feed.html
    dashboard_playback_panel.html
```

Optional later static split:

```text
api/app/static/css/dashboard-v2.css
api/app/static/js/dashboard-v2.js
```

## 14. What should not happen

- Do not copy the mockup literally if it harms clarity
- Do not bury alerts below decorative sections
- Do not treat playback as a footnote
- Do not overload the top of the page with generic metric cards
- Do not mix setup/admin flows into the center stage
- Do not use the wrong name; it is **TECHCAMAI**

## 15. Immediate build recommendation

Build the next real dashboard around this order:
1. command bar
2. camera stage
3. alert feed
4. playback panel
5. summary metrics
6. admin/supporting blocks

If time is tight, ship a clean overview that nails those five things before touching fancy extras.

That will look more premium, feel more useful, and give Kris something that resembles an actual surveillance product instead of a half-finished internal tool.
