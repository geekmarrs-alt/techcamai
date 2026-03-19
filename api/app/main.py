from __future__ import annotations

import base64
from datetime import datetime, timezone, timedelta
import json
import re
import sqlite3
from pathlib import Path, PurePosixPath
from typing import Optional, List
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .discover import discover
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field, Session, create_engine, select


class Settings(BaseSettings):
    DB_PATH: str = "/data/techcamai.db"
    CLIPS_DIR: str = "/data/clips"


settings = Settings()

db_path = Path(settings.DB_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{db_path}", echo=False)
clips_dir = Path(settings.CLIPS_DIR)
clips_dir.mkdir(parents=True, exist_ok=True)


class Camera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # MVP camera config
    ip: Optional[str] = Field(default=None, index=True)
    channel: int = 1
    scheme: str = "https"  # http|https
    auth: str = "digest"   # digest|basic
    username: Optional[str] = None
    password: Optional[str] = None  # MVP: stored local plaintext on Pi

    # legacy (kept for now)
    snapshot_url: str = ""

    enabled: bool = True


class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    camera_id: int
    # MVP labels: motion for quick demo; person/vehicle reserved for later model plug-in
    label: str = "motion"  # motion|person|vehicle|ppe_no_hivis
    min_conf: float = 0.5
    cooldown_sec: int = 120
    enabled: bool = True


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(index=True)
    camera_id: int
    rule_id: int
    label: str
    conf: float
    snapshot_b64: Optional[str] = None
    clip_path: Optional[str] = None
    clip_status: str = "pending"
    clip_error: Optional[str] = None
    acked: bool = False


class DetectionIn(BaseModel):
    camera_snapshot_url: str
    camera_id: Optional[int] = None
    label: str
    conf: float
    snapshot_b64: Optional[str] = None


class CameraCreate(BaseModel):
    name: str
    ip: str
    username: str
    password: str
    channel: int = 1
    scheme: str = "https"
    auth: str = "digest"


class CameraTestRequest(BaseModel):
    ip: str
    username: str
    password: str
    channel: int = 1


class RuleCreate(BaseModel):
    name: str
    camera_id: int
    label: str = "motion"
    min_conf: float = 0.5
    cooldown_sec: int = 120


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    channel: Optional[int] = None
    scheme: Optional[str] = None
    auth: Optional[str] = None
    enabled: Optional[bool] = None


class AlertClipUpdate(BaseModel):
    clip_path: Optional[str] = None
    clip_status: str
    clip_error: Optional[str] = None


app = FastAPI(title="TECHCAMAI API", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
app.mount("/clips", StaticFiles(directory=str(clips_dir)), name="clips")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _fmt_dt_compact(value: Optional[datetime]) -> str:
    if not value:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%d %b %H:%M UTC")


def _fmt_dt_full(value: Optional[datetime]) -> str:
    if not value:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _fmt_relative(value: Optional[datetime]) -> str:
    if not value:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - value.astimezone(timezone.utc)
    seconds = max(int(delta.total_seconds()), 0)
    if seconds < 60:
        return "just now" if seconds < 5 else f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


def _clip_status_tone(status: Optional[str]) -> str:
    status = (status or "pending").lower()
    if status == "ready":
        return "ok"
    if status == "failed":
        return "bad"
    if status == "pending":
        return "warn"
    return ""


templates.env.filters["dt_compact"] = _fmt_dt_compact
templates.env.filters["dt_full"] = _fmt_dt_full
templates.env.filters["relative_time"] = _fmt_relative
templates.env.filters["clip_tone"] = _clip_status_tone


_ALLOWED_CLIP_STATUSES = {"pending", "ready", "failed"}
_RTSP_CHANNEL_RE = re.compile(r"/Streaming/Channels/(\d+)", re.IGNORECASE)
_HTTP_CHANNEL_RE = re.compile(r"/channels/(\d+)(?:/|$)", re.IGNORECASE)


def _normalize_clip_status(status: Optional[str]) -> str:
    value = (status or "pending").strip().lower()
    if value not in _ALLOWED_CLIP_STATUSES:
        raise HTTPException(status_code=400, detail=f"invalid clip_status: {status}")
    return value


def _normalize_clip_relpath(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    raw = str(value).strip().replace("\\", "/")
    if not raw:
        return None
    rel = PurePosixPath(raw)
    if rel.is_absolute() or ".." in rel.parts:
        raise HTTPException(status_code=400, detail="clip_path must stay within /clips")
    normalized = rel.as_posix().lstrip("/")
    if not normalized or normalized.startswith("../"):
        raise HTTPException(status_code=400, detail="clip_path must stay within /clips")
    return normalized


def _channel_hint_from_source_url(value: str) -> Optional[int]:
    for pattern in (_RTSP_CHANNEL_RE, _HTTP_CHANNEL_RE):
        match = pattern.search(value or "")
        if not match:
            continue
        raw = int(match.group(1))
        if raw >= 100:
            return raw // 100
        return raw
    return None


class DiscoverRequest(BaseModel):
    timeout_sec: int = 120


def _ensure_alert_columns() -> None:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        exists = cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='alert'"
        ).fetchone()
        if not exists:
            return

        cols = {row[1] for row in cur.execute("PRAGMA table_info(alert)").fetchall()}
        wanted = {
            "clip_path": "TEXT",
            "clip_status": "TEXT NOT NULL DEFAULT 'pending'",
            "clip_error": "TEXT",
        }
        for name, ddl in wanted.items():
            if name not in cols:
                cur.execute(f"ALTER TABLE alert ADD COLUMN {name} {ddl}")
        conn.commit()


@app.on_event("startup")
def startup() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_alert_columns()

    # seed minimal defaults if empty
    with Session(engine) as s:
        cams = s.exec(select(Camera)).all()
        if not cams:
            demo = Camera(name="Demo Cam", snapshot_url="")
            s.add(demo)
            s.commit()
            s.refresh(demo)
            r = Rule(name="Motion", camera_id=demo.id, label="motion", min_conf=0.35, cooldown_sec=10)
            s.add(r)
            s.commit()


def _worker_health() -> dict:
    """Return worker stale status for rendering in templates."""
    heartbeat_path = Path("/data/worker_heartbeat.json")
    if not heartbeat_path.exists():
        return {"worker_stale": None, "worker_last_seen": None}
    try:
        data = json.loads(heartbeat_path.read_text())
        age = datetime.now(timezone.utc).timestamp() - float(data.get("unix_ts", 0))
        stale = age > 90
        return {"worker_stale": stale, "worker_last_seen": data.get("ts")}
    except Exception:
        return {"worker_stale": True, "worker_last_seen": None}


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dashboard_context(poll: int = 0) -> dict:
    now = datetime.now(timezone.utc)
    with Session(engine) as s:
        alerts = s.exec(select(Alert).order_by(Alert.created_at.desc()).limit(50)).all()
        cameras = s.exec(select(Camera).order_by(Camera.id.desc()).limit(50)).all()
        cams = {c.id: c for c in cameras}
        rules = {r.id: r for r in s.exec(select(Rule)).all()}

    enabled_cameras = [c for c in cameras if c.enabled]
    unacked_alerts = [a for a in alerts if not a.acked]
    featured_alert = unacked_alerts[0] if unacked_alerts else (alerts[0] if alerts else None)
    featured_camera = None
    if featured_alert:
        featured_camera = cams.get(featured_alert.camera_id)
    if not featured_camera and enabled_cameras:
        featured_camera = enabled_cameras[0]
    if not featured_camera and cameras:
        featured_camera = cameras[0]

    supporting_cameras = [c for c in enabled_cameras if not featured_camera or c.id != featured_camera.id][:4]
    alert_feed_items = sorted(alerts[:6], key=lambda a: (a.acked, -int((_as_utc(a.created_at) or now).timestamp())))
    recent_playback_alerts = [a for a in alerts if getattr(a, "clip_status", None) in {"ready", "pending", "failed"}][:5]

    cameras_with_rules = len({r.camera_id for r in rules.values() if r.enabled})
    clip_ready_count = len([a for a in alerts if getattr(a, "clip_status", None) == "ready"])
    clip_failed_count = len([a for a in alerts if getattr(a, "clip_status", None) == "failed"])
    clip_pending_count = len([a for a in alerts if getattr(a, "clip_status", None) == "pending"])
    alerts_last_24h = len([a for a in alerts if _as_utc(a.created_at) and (now - _as_utc(a.created_at)).total_seconds() <= 86400])
    cameras_without_rules = max(0, len(enabled_cameras) - cameras_with_rules)
    featured_camera_alerts = [a for a in alerts if featured_camera and a.camera_id == featured_camera.id]
    featured_camera_last_alert = featured_camera_alerts[0] if featured_camera_alerts else None

    if featured_alert and featured_camera:
        focus_summary = (
            f"{featured_camera.name} is staged because it has the freshest operator-relevant activity. "
            f"Keep this feed big, keep triage nearby, and avoid burying the incident behind menus."
        )
    elif featured_camera:
        focus_summary = (
            f"{featured_camera.name} is on stage because it is the best available live feed right now. "
            f"Once incidents start landing, the wall should pivot around them automatically."
        )
    else:
        focus_summary = "No featured camera yet. Add or enable a camera so the dashboard has something real to orbit around."

    worker = _worker_health()
    return {
        "active": "overview",
        "alerts": alerts,
        "cameras": cameras,
        "cams": cams,
        "rules": rules,
        "poll": int(poll),
        "worker_stale": worker["worker_stale"],
        "worker_last_seen": worker["worker_last_seen"],
        "featured_camera": featured_camera,
        "featured_alert": featured_alert,
        "supporting_cameras": supporting_cameras,
        "alert_feed_items": alert_feed_items,
        "recent_playback_alerts": recent_playback_alerts,
        "featured_camera_alert_count": len([a for a in featured_camera_alerts if not a.acked]),
        "featured_camera_last_alert": featured_camera_last_alert,
        "focus_summary": focus_summary,
        "now_ts": int(now.timestamp()),
        "page_title": "Command dashboard",
        "total_cameras": len(cameras),
        "enabled_cameras": len(enabled_cameras),
        "unacked_alerts": len(unacked_alerts),
        "clip_ready_count": clip_ready_count,
        "clip_failed_count": clip_failed_count,
        "clip_pending_count": clip_pending_count,
        "alerts_last_24h": alerts_last_24h,
        "cameras_with_rules": cameras_with_rules,
        "cameras_without_rules": cameras_without_rules,
    }


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, poll: int = 0):
    return templates.TemplateResponse(request, "dashboard_v2_preview.html", _dashboard_context(poll=poll))


@app.get("/preview/dashboard-v1", response_class=HTMLResponse)
def dashboard_v1_preview(request: Request, poll: int = 0):
    return templates.TemplateResponse(request, "dashboard.html", _dashboard_context(poll=poll))


@app.get("/preview/dashboard-v2", response_class=HTMLResponse)
def dashboard_v2_preview(request: Request, poll: int = 0):
    return templates.TemplateResponse(request, "dashboard_v2_preview.html", _dashboard_context(poll=poll))


@app.get("/ui/scan", response_class=HTMLResponse)
@app.post("/ui/scan", response_class=HTMLResponse)
async def ui_scan(request: Request):
    devices = await discover(timeout_sec=30)
    return templates.TemplateResponse(request, "scan.html", {"active": "scan", "devices": devices})


class UiTestForm(BaseModel):
    ip: str
    username: str
    password: str
    channel: int = 1


@app.get("/ui/add", response_class=HTMLResponse)
def ui_add_get(request: Request, ip: str = ""):
    return templates.TemplateResponse(request, "add_camera.html", {"active": "add", "ip": ip, "result": None})


@app.post("/ui/add", response_class=HTMLResponse)
async def ui_add_post(request: Request):
    form = await request.form()
    ip = (form.get("ip") or "").strip()
    username = (form.get("username") or "").strip()
    password = (form.get("password") or "").strip()
    channel = int(form.get("channel") or 1)

    result = None
    if form.get("action") == "test":
        try:
            result = await test_camera(CameraTestRequest(ip=ip, username=username, password=password, channel=channel))
        except HTTPException as e:
            result = {"ok": False, "error": str(e.detail)}

    if form.get("action") == "save":
        with Session(engine) as s:
            c = Camera(
                name=f"Cam {ip}",
                ip=ip,
                channel=channel,
                scheme="https",
                auth="digest",
                username=username,
                password=password,
            )
            s.add(c)
            s.commit()
        result = {"ok": True, "saved": True}

    return templates.TemplateResponse(request, "add_camera.html", {"active": "add", "ip": ip, "result": result})


def _camera_snapshot_urls(ip: str, channel: int, scheme: str) -> list[str]:
    # Prefer Hikvision channel layout (101) first for ch=1.
    ch_variants = []
    if channel < 100:
        ch_variants += [channel * 100 + 1, channel * 100 + 2, channel]
    else:
        ch_variants += [channel]

    urls: list[str] = []
    for ch in ch_variants:
        urls += [
            f"{scheme}://{ip}/ISAPI/Streaming/channels/{ch}/picture",
            f"{scheme}://{ip}/Streaming/channels/{ch}/picture",
        ]
    return urls


async def _fetch_camera_snapshot(cam: Camera) -> bytes:
    if not cam.ip:
        raise HTTPException(status_code=400, detail="camera has no ip")

    urls = _camera_snapshot_urls(cam.ip, cam.channel or 1, cam.scheme or "https")

    auth = None
    if (cam.auth or "digest").lower() == "basic":
        auth = (cam.username or "", cam.password or "")
    else:
        auth = httpx.DigestAuth(cam.username or "", cam.password or "")

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
        last_err = None
        for u in urls:
            try:
                r = await client.get(u, auth=auth)
                if r.status_code != 200:
                    last_err = f"{u} -> HTTP {r.status_code}"
                    continue
                if not r.content:
                    last_err = f"{u} -> empty body"
                    continue
                return r.content
            except Exception as e:
                last_err = f"{u} -> {e}"
                continue

    raise HTTPException(status_code=502, detail=f"snapshot fetch failed: {last_err}")


@app.get("/cameras/{camera_id}/snapshot.jpg")
async def camera_snapshot(camera_id: int):
    with Session(engine) as s:
        cam = s.get(Camera, camera_id)
        if not cam:
            raise HTTPException(status_code=404, detail="camera not found")
        if not cam.enabled:
            raise HTTPException(status_code=400, detail="camera disabled")
        jpeg = await _fetch_camera_snapshot(cam)
        return Response(content=jpeg, media_type="image/jpeg")


@app.get("/live", response_class=HTMLResponse)
def ui_live(request: Request):
    with Session(engine) as s:
        cameras = s.exec(select(Camera).where(Camera.enabled == True).order_by(Camera.id.desc())).all()  # noqa: E712
    return templates.TemplateResponse(
        request,
        "live.html",
        {"active": "live", "cameras": cameras, "now_ts": int(datetime.now(timezone.utc).timestamp())},
    )


@app.get("/alerts", response_class=HTMLResponse)
def ui_alerts(request: Request, show: str = "unacked", poll: int = 0):
    with Session(engine) as s:
        q = select(Alert).order_by(Alert.created_at.desc()).limit(200)
        if show != "all":
            q = q.where(Alert.acked == False)  # noqa: E712
        alerts = s.exec(q).all()
        cams = {c.id: c for c in s.exec(select(Camera)).all()}
        rules = {r.id: r for r in s.exec(select(Rule)).all()}
    return templates.TemplateResponse(
        request,
        "alerts.html",
        {"active": "alerts", "alerts": alerts, "cams": cams, "rules": rules, "poll": int(poll)},
    )


@app.get("/timeline", response_class=HTMLResponse)
def ui_timeline(request: Request, poll: int = 0):
    now = datetime.now(timezone.utc)
    with Session(engine) as s:
        alerts = s.exec(select(Alert).order_by(Alert.created_at.desc()).limit(500)).all()
        cams = {c.id: c for c in s.exec(select(Camera)).all()}
        rules = {r.id: r for r in s.exec(select(Rule)).all()}

    # Hourly alert counts for the activity strip: 24 buckets, index 0 = oldest hour, 23 = current hour.
    hourly_counts = [0] * 24
    for a in alerts:
        ts = a.created_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_sec = (now - ts).total_seconds()
        bucket = int(age_sec // 3600)
        if 0 <= bucket < 24:
            hourly_counts[23 - bucket] += 1

    return templates.TemplateResponse(
        request,
        "timeline.html",
        {
            "active": "timeline",
            "alerts": alerts,
            "cams": cams,
            "rules": rules,
            "poll": int(poll),
            "hourly_counts": hourly_counts,
        },
    )


@app.get("/cameras/manage", response_class=HTMLResponse)
def ui_cameras_manage(request: Request):
    with Session(engine) as s:
        cameras = s.exec(select(Camera).order_by(Camera.id.desc())).all()
        rules = s.exec(select(Rule).where(Rule.enabled == True)).all()  # noqa: E712
    camera_rule_ids = {r.camera_id for r in rules}
    return templates.TemplateResponse(request, "cameras_manage.html", {
        "active": "cameras",
        "cameras": cameras,
        "camera_rule_ids": camera_rule_ids,
    })


@app.post("/ui/cameras/{camera_id}/toggle")
def ui_camera_toggle(camera_id: int):
    with Session(engine) as s:
        c = s.get(Camera, camera_id)
        if not c:
            raise HTTPException(status_code=404, detail="camera not found")
        c.enabled = not bool(c.enabled)
        s.add(c)
        s.commit()
    return RedirectResponse(url="/cameras/manage", status_code=303)


@app.post("/ui/cameras/{camera_id}/delete")
def ui_camera_delete(camera_id: int):
    with Session(engine) as s:
        c = s.get(Camera, camera_id)
        if not c:
            raise HTTPException(status_code=404, detail="camera not found")
        s.delete(c)
        s.commit()
    return RedirectResponse(url="/cameras/manage", status_code=303)


@app.post("/ui/cameras/{camera_id}/update")
async def ui_camera_update(camera_id: int, request: Request):
    form = await request.form()
    raw_password = (form.get("password") or "").strip()

    patch = CameraUpdate(
        name=(form.get("name") or "").strip() or None,
        ip=(form.get("ip") or "").strip() or None,
        username=(form.get("username") or "").strip() or None,
        # SECURITY: do not echo stored passwords back into UI; only update if provided.
        password=raw_password or None,
        channel=int(form.get("channel") or 1),
        scheme=(form.get("scheme") or "https").strip() or None,
        auth=(form.get("auth") or "digest").strip() or None,
    )
    update_camera(camera_id, patch)
    return RedirectResponse(url=f"/cameras/manage#cam-{camera_id}", status_code=303)


@app.get("/health")
def health():
    db_ok = True
    try:
        with Session(engine) as s:
            s.exec(select(Camera).limit(1)).all()
    except Exception:
        db_ok = False

    worker_ts: Optional[str] = None
    worker_stale: Optional[bool] = None
    heartbeat_path = Path("/data/worker_heartbeat.json")
    if heartbeat_path.exists():
        try:
            data = json.loads(heartbeat_path.read_text())
            worker_ts = data.get("ts")
            age = datetime.now(timezone.utc).timestamp() - float(data.get("unix_ts", 0))
            # Stale = no heartbeat for 3× the default 30s poll interval
            worker_stale = age > 90
        except Exception:
            worker_stale = True

    return {
        "ok": db_ok,
        "ts": datetime.now(timezone.utc).isoformat(),
        "db": "ok" if db_ok else "error",
        "worker_last_seen": worker_ts,
        "worker_stale": worker_stale,
    }


@app.get("/api/alerts/latest")
def api_alerts_latest(since: int = 0, limit: int = 50, unacked_only: int = 1):
    """Polling endpoint for "live" UI.

    - since: unix seconds (UTC). Only return alerts newer than this.
    - unacked_only: 1 (default) returns only unacked alerts.

    Returns minimal JSON; UI just reloads the page if anything new appears.
    """
    since_dt = datetime.fromtimestamp(max(0, int(since)), tz=timezone.utc)
    limit = max(1, min(int(limit), 200))

    with Session(engine) as s:
        q = select(Alert).where(Alert.created_at >= since_dt)
        if int(unacked_only) == 1:
            q = q.where(Alert.acked == False)  # noqa: E712
        q = q.order_by(Alert.created_at.desc()).limit(limit)
        alerts = s.exec(q).all()

    return {
        "ok": True,
        "now_ts": int(datetime.now(timezone.utc).timestamp()),
        "count": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "created_at": a.created_at.isoformat(),
                "camera_id": a.camera_id,
                "rule_id": a.rule_id,
                "label": a.label,
                "conf": a.conf,
                "acked": a.acked,
                "clip_path": a.clip_path,
                "clip_status": a.clip_status,
            }
            for a in alerts
        ],
    }


@app.post("/discover")
async def discover_cameras(req: DiscoverRequest):
    # 2 minutes default, local subnets only
    timeout_sec = max(5, min(int(req.timeout_sec), 120))
    devices = await discover(timeout_sec=timeout_sec)
    return {"ok": True, "count": len(devices), "devices": devices}


@app.get("/cameras")
def list_cameras():
    # public-safe list (no passwords)
    with Session(engine) as s:
        cams = s.exec(select(Camera)).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "ip": c.ip,
                "channel": c.channel,
                "scheme": c.scheme,
                "auth": c.auth,
                "username": c.username,
                "enabled": c.enabled,
            }
            for c in cams
        ]


@app.get("/worker/cameras")
def worker_cameras():
    # MVP: worker runs on same box, so we return creds.
    # Filter out auto-created junk rows.
    with Session(engine) as s:
        cams = s.exec(
            select(Camera)
            .where(Camera.enabled == True)  # noqa: E712
            .where(Camera.ip != None)       # noqa: E711
            .where(Camera.username != None) # noqa: E711
            .where(Camera.password != None) # noqa: E711
        ).all()
        return cams


@app.post("/cameras")
def create_camera(cam: CameraCreate):
    if not cam.ip:
        raise HTTPException(status_code=400, detail="ip required")
    with Session(engine) as s:
        c = Camera(
            name=cam.name,
            ip=cam.ip,
            channel=cam.channel,
            scheme=cam.scheme,
            auth=cam.auth,
            username=cam.username,
            password=cam.password,
        )
        s.add(c)
        s.commit()
        s.refresh(c)
        return c


@app.put("/cameras/{camera_id}")
def update_camera(camera_id: int, patch: CameraUpdate):
    with Session(engine) as s:
        c = s.get(Camera, camera_id)
        if not c:
            raise HTTPException(status_code=404, detail="camera not found")

        data = patch.model_dump(exclude_unset=True)
        # SECURITY: empty password means "keep existing".
        if "password" in data and (data["password"] is None or str(data["password"]).strip() == ""):
            data.pop("password", None)

        for k, v in data.items():
            setattr(c, k, v)

        s.add(c)
        s.commit()
        s.refresh(c)
        return {"ok": True}


@app.post("/cameras/test")
async def test_camera(req: CameraTestRequest):
    # Hikvision-first: try common snapshot endpoints.
    # Return base64 jpeg so UI can preview.
    # Many Hikvision devices use channel numbering like 101 for channel 1 main stream.
    ch_variants = [req.channel]
    if req.channel < 100:
        ch_variants += [req.channel * 100 + 1, req.channel * 100 + 2]

    urls = []
    for ch in ch_variants:
        urls += [
            f"https://{req.ip}/ISAPI/Streaming/channels/{ch}/picture",
            f"http://{req.ip}/ISAPI/Streaming/channels/{ch}/picture",
            f"https://{req.ip}/Streaming/channels/{ch}/picture",
            f"http://{req.ip}/Streaming/channels/{ch}/picture",
        ]
    # Hikvision often uses Digest auth; try digest first.
    digest = httpx.DigestAuth(req.username, req.password)

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
        last_err = None
        for u in urls:
            try:
                r = await client.get(u, auth=digest)
                if r.status_code != 200:
                    last_err = f"{u} -> HTTP {r.status_code}"
                    continue
                if not r.content:
                    last_err = f"{u} -> empty body"
                    continue
                # assume jpeg
                b64 = base64.b64encode(r.content).decode("ascii")
                return {"ok": True, "url": u, "jpeg_b64": b64}
            except Exception as e:
                last_err = f"{u} -> {e}"
                continue

    raise HTTPException(status_code=400, detail=f"Snapshot test failed: {last_err}")


@app.get("/rules")
def list_rules():
    with Session(engine) as s:
        return s.exec(select(Rule)).all()


@app.post("/rules")
def create_rule(rule: RuleCreate):
    with Session(engine) as s:
        cam = s.get(Camera, rule.camera_id)
        if not cam:
            raise HTTPException(status_code=404, detail="camera not found")
        r = Rule(
            name=rule.name,
            camera_id=rule.camera_id,
            label=rule.label,
            min_conf=rule.min_conf,
            cooldown_sec=rule.cooldown_sec,
        )
        s.add(r)
        s.commit()
        s.refresh(r)
        return r


def _cooldown_hit(s: Session, rule: Rule, now: datetime) -> bool:
    cutoff = now - timedelta(seconds=rule.cooldown_sec)
    last = s.exec(
        select(Alert)
        .where(Alert.rule_id == rule.id)
        .where(Alert.created_at >= cutoff)
        .order_by(Alert.created_at.desc())
        .limit(1)
    ).first()
    return last is not None


@app.post("/ingest/detection")
def ingest_detection(det: DetectionIn):
    now = datetime.now(timezone.utc)

    with Session(engine) as s:
        cam = None

        if det.camera_id is not None:
            cam = s.get(Camera, int(det.camera_id))

        if not cam:
            cam = s.exec(select(Camera).where(Camera.snapshot_url == det.camera_snapshot_url)).first()

        if not cam:
            # Fallback: match by hostname/IP and, when possible, channel.
            try:
                host = urlparse(det.camera_snapshot_url).hostname
            except Exception:
                host = None
            if host:
                channel_hint = _channel_hint_from_source_url(det.camera_snapshot_url)
                if channel_hint is not None:
                    cam = s.exec(
                        select(Camera)
                        .where(Camera.ip == host)
                        .where(Camera.channel == channel_hint)
                    ).first()
                if not cam:
                    cam = s.exec(select(Camera).where(Camera.ip == host)).first()

        if not cam:
            return {"ok": True, "triggered": []}

        rules = s.exec(select(Rule).where(Rule.camera_id == cam.id).where(Rule.enabled == True)).all()  # noqa: E712
        triggered: List[Alert] = []
        for r in rules:
            if r.label != det.label:
                continue
            if det.conf < r.min_conf:
                continue
            if _cooldown_hit(s, r, now):
                continue
            a = Alert(
                created_at=now,
                camera_id=cam.id,
                rule_id=r.id,
                label=det.label,
                conf=float(det.conf),
                snapshot_b64=det.snapshot_b64,
                acked=False,
            )
            s.add(a)
            s.commit()
            s.refresh(a)
            triggered.append(a)

        return {"ok": True, "triggered": triggered}


@app.put("/alerts/{alert_id}/clip")
def update_alert_clip(alert_id: int, patch: AlertClipUpdate):
    clip_status = _normalize_clip_status(patch.clip_status)
    clip_path = _normalize_clip_relpath(patch.clip_path)
    clip_error = (patch.clip_error or None)

    if clip_status == "ready" and not clip_path:
        raise HTTPException(status_code=400, detail="clip_path required when clip_status=ready")
    if clip_status != "ready":
        clip_path = None

    with Session(engine) as s:
        a = s.get(Alert, alert_id)
        if not a:
            raise HTTPException(status_code=404, detail="alert not found")
        a.clip_path = clip_path
        a.clip_status = clip_status
        a.clip_error = clip_error
        s.add(a)
        s.commit()
        s.refresh(a)
        return {"ok": True, "alert_id": a.id, "clip_status": a.clip_status, "clip_path": a.clip_path}


@app.post("/alerts/{alert_id}/ack")
def ack_alert(alert_id: int, request: Request, poll: int = 0):
    with Session(engine) as s:
        a = s.get(Alert, alert_id)
        if not a:
            raise HTTPException(status_code=404, detail="alert not found")
        a.acked = True
        s.add(a)
        s.commit()

    # UX: bounce back to where the operator was.
    ref = request.headers.get("referer") or "/alerts"
    # If polling is enabled, keep the operator on the polling view.
    if "poll=1" not in ref and poll:
        sep = "&" if "?" in ref else "?"
        ref = f"{ref}{sep}poll=1"
    return RedirectResponse(url=ref, status_code=303)
