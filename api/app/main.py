from __future__ import annotations

import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
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


settings = Settings()

db_path = Path(settings.DB_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{db_path}", echo=False)


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
    acked: bool = False


class DetectionIn(BaseModel):
    camera_snapshot_url: str
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


app = FastAPI(title="TECHCAMAI API", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


class DiscoverRequest(BaseModel):
    timeout_sec: int = 120


@app.on_event("startup")
def startup() -> None:
    SQLModel.metadata.create_all(engine)

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


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, poll: int = 0):
    with Session(engine) as s:
        alerts = s.exec(select(Alert).order_by(Alert.created_at.desc()).limit(50)).all()
        cameras = s.exec(select(Camera).order_by(Camera.id.desc()).limit(50)).all()
        cams = {c.id: c for c in cameras}
        rules = {r.id: r for r in s.exec(select(Rule)).all()}
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "active": "overview",
            "alerts": alerts,
            "cameras": cameras,
            "cams": cams,
            "rules": rules,
            "poll": int(poll),
        },
    )


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
def ui_add_get(request: Request, ip: str):
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
    with Session(engine) as s:
        alerts = s.exec(select(Alert).order_by(Alert.created_at.desc()).limit(500)).all()
        cams = {c.id: c for c in s.exec(select(Camera)).all()}
    return templates.TemplateResponse(
        request,
        "timeline.html",
        {"active": "timeline", "alerts": alerts, "cams": cams, "poll": int(poll)},
    )


@app.get("/cameras/manage", response_class=HTMLResponse)
def ui_cameras_manage(request: Request):
    with Session(engine) as s:
        cameras = s.exec(select(Camera).order_by(Camera.id.desc())).all()
    return templates.TemplateResponse(request, "cameras_manage.html", {"active": "cameras", "cameras": cameras})


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
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}


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
        cam = s.exec(select(Camera).where(Camera.snapshot_url == det.camera_snapshot_url)).first()
        if not cam:
            # Fallback: match by hostname/IP in the snapshot URL.
            try:
                host = urlparse(det.camera_snapshot_url).hostname
            except Exception:
                host = None
            if host:
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
