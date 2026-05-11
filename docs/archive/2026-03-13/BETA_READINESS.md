# TECHCAMAI beta readiness — 2026-03-13

## Executive truth
TECHCAMAI is **close to a believable private beta demo** for an operator workflow.

It is **not** ready to be sold as a polished commercial dashboard product yet.

The gap is no longer "there is nothing here." The gap is now mostly:
- runtime validation
- deployment cleanliness
- failure-state visibility
- product/commercial wrapper still missing

---

## 1) What feels launch-near
These are the parts that look like a real system already.

### Operator flow exists
A user can move through a coherent path:
1. scan or add a camera
2. manage saved cameras
3. run worker polling
4. create alerts from detections
5. review alerts in inbox/timeline
6. open playable clips when capture succeeds

### Dashboard direction is credible
The broken dashboard recovery state has been replaced with a usable preview direction:
- command-style overview
- live stage concept
- alert feed
- playback panel
- summary metrics

That is enough for a walkthrough without apologising every 30 seconds.

### Playback MVP is real in code
Present in repo:
- alert clip metadata fields
- `/clips` static serving
- worker-side clip capture attempt via `ffmpeg`
- API patch route for clip status/path
- alerts/timeline/dashboard UI surfaces for clip state

### Deployment lane is clearer than before
The intended path is now understandable:
- repo push
- GitHub Actions builds GHCR images
- Pi pulls images and restarts

That is the right shape, even if tomorrow still needs proof it works cleanly end to end.

---

## 2) What still needs beta validation
These are the parts that can still embarrass tomorrow's run-through if nobody checks them first.

### A. Live camera + rule truth
Need confirmation of all three:
- which cameras are enabled
- which enabled cameras actually have rules
- whether snapshot access still works with current creds/auth/channel

Why it matters:
A pretty dashboard means nothing if a real enabled camera silently has no rule or no usable feed.

### B. End-to-end ingest proof
Need one controlled test that proves:
- worker or manual ingest creates a new alert
- alert appears in `/api/alerts/latest`
- alert appears on `/alerts`
- alert appears on dashboard
- clip status moves to `ready` or fails with a visible reason

Why it matters:
This is the single most important demo proof.

### C. Playback on actual target hardware
Still unproven here:
- RTSP capture reliability against live feeds
- MP4 playback in browser on Pi deployment
- storage behaviour over repeated captures

Why it matters:
Playback is one of the current headline differentiators. If it flakes, it will be noticed instantly.

### D. Failure visibility
Still too easy to end up with operator confusion around:
- wrong credentials
- unreachable camera
- dead/slow snapshot endpoint
- enabled camera with no rule
- clip capture failure

Why it matters:
Beta users forgive rough edges. They do not forgive silent lies.

### E. Product shell is still absent
Not present in this recovered app:
- auth
- licence handling
- billing/paywall
- tenant/admin separation

Why it matters:
This limits what can honestly be called "launch-ready." Fine for private beta. Not fine for public product claims.

---

## 3) Honest status by area

| Area | Status | Notes |
|---|---|---|
| Recovered API app | Good | Compiles; routes and templates present |
| Dashboard walkthrough | Good | Default route now points at v2 preview, with v1 fallback still available |
| Camera onboarding | Mixed | UI exists; needs live credential/channel validation |
| Rule coverage | Risky | No proof here that all enabled cameras have rules |
| Alert ingest | Promising | Route exists; needs one live end-to-end proof tomorrow |
| Playback MVP | Promising | Implemented in code; needs real RTSP/browser validation |
| Pi deployment path | Good shape, not fully proven | GHCR workflow exists; should be validated with real image publish/pull |
| Failure-state UX | Weak | Still needs clearer operator status and less silent confusion |
| Commercial/product layer | Missing | Out of scope for tomorrow's operator beta walkthrough |

---

## 4) Best possible framing for tomorrow
Say this plainly:

> This is a solid operator MVP with a believable deployment path and a real playback direction. Tomorrow is about proving the live loop cleanly, not pretending the whole product stack is finished.

That framing is honest and strong.

---

## 5) Tomorrow's priority order
1. **Verify live camera/rule truth**
2. **Trigger one fresh alert end to end**
3. **Confirm clip capture/playback behaviour**
4. **Check Pi image/update path**
5. **Only then discuss next-layer polish**

If time gets tight, do not waste it on aesthetic tweaks. Prove the pipeline.

---

## 6) Red flags to call out immediately if seen tomorrow
- enabled camera with no rule
- alert creates but no clip status update ever arrives
- clip marked ready but browser playback fails
- snapshot fetch takes ages or hangs awkwardly
- Pi can only update via manual source shuffling instead of image pull
- demo depends on historical alerts because fresh ingest will not fire

Any one of those is survivable if named quickly.
Trying to hide them is what kills confidence.
