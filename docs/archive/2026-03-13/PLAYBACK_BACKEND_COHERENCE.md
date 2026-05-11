# TECHCAMAI playback/backend coherence pass — 2026-03-13

## What got tightened

### 1. Detection routing is no longer host-only
Before this pass, the worker posted detections using the RTSP URL as `camera_snapshot_url`.
The API then fell back to matching **only by host/IP** if `snapshot_url` did not match.

That was fine for one camera per IP, but wrong for:
- multi-channel NVRs
- cameras exposed through a shared recorder IP
- any setup where channel 1 and channel 2 live behind the same host

Now the path is more coherent:
- worker posts `camera_id` with each detection when it knows the camera
- API prefers explicit `camera_id`
- API also parses channel hints from RTSP / HTTP source URLs and uses them during fallback matching

That removes the nastiest backend/UI mismatch in the current playback path: alerts landing on the wrong camera while the UI assumes camera-specific playback.

### 2. Clip metadata updates are now validated
`PUT /alerts/{id}/clip` used to accept whatever `clip_status` and `clip_path` the caller sent.
That left a few bad outcomes open:
- nonsense status values
- absolute paths
- `../` traversal-like paths
- `ready` clips without an actual clip path
- stale clip paths sticking around after `failed`

Now:
- `clip_status` must be one of `pending | ready | failed`
- `clip_path` must stay relative to `/clips`
- `ready` requires a clip path
- non-ready states clear the clip path

This makes the playback UI’s assumptions much more honest.

### 3. Add-camera copy now matches reality
The add-camera page still said save only stored a URL and that worker wiring was “next”.
That was stale and misleading.

The UI copy now reflects the real MVP backend shape:
- IP
- auth mode
- username
- password
- channel
- worker clip capture

## What still blocks a polished beta

### No pre-roll
Current clips are post-trigger captures only.
That means the operator can miss the few seconds before motion crossed threshold.
For an actual surveillance product, pre-roll matters.

### Clip capture is synchronous per triggered alert
The worker captures clips inline after each triggered alert.
That is acceptable for MVP demos but brittle under bursty activity:
- one slow RTSP capture can delay later polling
- multiple cameras firing together will serialize

A small job queue or background capture process would make this much sturdier.

### No retention / cleanup policy
Clips accumulate under `/data/clips` forever right now.
That is fine for a short test box and bad for unattended beta deployments.

### No signed/authenticated clip access model yet
Playback is served directly from `/clips`.
That is okay for trusted local MVP deployment, not okay for a broader hosted/security-sensitive version.

### Legacy `snapshot_url` path is still hanging around
The code still supports the old `snapshot_url` matching path for compatibility.
It works, but it is legacy baggage.
The cleaner long-term model is:
- camera ids everywhere internally
- source URL only as debug metadata

## Bottom line

The playback path is more coherent now.
The worst mismatch — backend detection attribution being too vague for a UI that assumes camera-specific playback — is materially reduced.

It is still an MVP, not a polished beta, because pre-roll, retention, and async capture are still missing.
