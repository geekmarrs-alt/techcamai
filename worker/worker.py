from __future__ import annotations

import base64
import hashlib
import os
import random
import subprocess
import time
from typing import List

import httpx
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_BASE_URL: str = "http://127.0.0.1:8000"
    POLL_INTERVAL_SEC: int = 30
    CAMERA_SNAPSHOT_URLS: str = ""  # legacy comma-separated

    # Prefer RTSP for broad compatibility; HTTP snapshot often 401/403 on Hik/OEM.
    PREFER_RTSP: int = 1


S = Settings()


def parse_urls(raw: str) -> List[str]:
    urls = [u.strip() for u in (raw or "").split(",")]
    return [u for u in urls if u]


def fetch_snapshot_bytes(url: str, auth: httpx.Auth | None = None, verify: bool = False) -> bytes | None:
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, verify=verify) as c:
            r = c.get(url, auth=auth)
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            if "image" not in content_type and not r.content.startswith(b"\xff\xd8"):
                return None
            return r.content
    except Exception:
        return None


def fetch_rtsp_frame(rtsp_url: str) -> bytes | None:
    """Grab one frame via ffmpeg.

    This is intentionally dumb + robust for MVP: spawn ffmpeg, write /tmp frame, read bytes.
    """
    out = f"/tmp/techcamai_rtsp_{abs(hash(rtsp_url))}.jpg"
    try:
        subprocess.run(["/app/rtsp_grab.sh", rtsp_url, out], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(out, "rb") as f:
            b = f.read()
        if not b.startswith(b"\xff\xd8"):
            return None
        return b
    except Exception:
        return None


def jpeg_b64(jpeg: bytes | None) -> str | None:
    if not jpeg:
        return None
    return base64.b64encode(jpeg).decode("ascii")


def fake_detect() -> tuple[str, float]:
    # Legacy stub kept for fallback.
    label = random.choice(["person", "vehicle"])
    conf = random.uniform(0.3, 0.99)
    return label, conf


def motion_detect(prev_jpeg: bytes | None, cur_jpeg: bytes | None) -> tuple[str, float]:
    """Cheap MVP "motion" detector.

    We avoid heavy deps (opencv/pillow) and just compare JPEG bytes.
    It’s not perfect, but it creates *real* events for demos.

    conf is based on relative byte delta and digest mismatch.
    """
    if not cur_jpeg:
        return "motion", 0.0

    if not prev_jpeg:
        # first frame: don't spam
        return "motion", 0.0

    if prev_jpeg == cur_jpeg:
        return "motion", 0.0

    # Compute a rough change score.
    # If JPEG sizes differ a lot, treat as higher motion.
    a, b = len(prev_jpeg), len(cur_jpeg)
    if a == 0:
        return "motion", 0.0
    size_delta = abs(a - b) / max(a, 1)

    # Also compare sha256; mismatch already guaranteed, but we use it to scale a tiny bit.
    h1 = hashlib.sha256(prev_jpeg).digest()
    h2 = hashlib.sha256(cur_jpeg).digest()
    diff = sum(x != y for x, y in zip(h1, h2)) / len(h1)

    score = min(1.0, (size_delta * 1.2) + (diff * 0.2))
    # Clamp into a useful range
    conf = max(0.0, min(0.99, score))
    return "motion", conf


def post_detection(snapshot_url: str, label: str, conf: float, snapshot_b64: str | None):
    payload = {
        "camera_snapshot_url": snapshot_url,
        "label": label,
        "conf": conf,
        "snapshot_b64": snapshot_b64,
    }
    with httpx.Client(timeout=10.0) as c:
        r = c.post(f"{S.API_BASE_URL}/ingest/detection", json=payload)
        r.raise_for_status()
        return r.json()


def _camera_snapshot_url(cam: dict) -> str:
    ip = cam.get("ip")
    scheme = cam.get("scheme") or "https"
    channel = int(cam.get("channel") or 1)
    # Prefer ISAPI first, but we can add fallbacks later
    return f"{scheme}://{ip}/ISAPI/Streaming/channels/{channel}/picture"


def _camera_rtsp_url(cam: dict) -> str:
    ip = cam.get("ip")
    channel = int(cam.get("channel") or 1)
    # Hikvision-style: channel 1 main stream is 101
    ch = channel
    if ch < 100:
        ch = ch * 100 + 1
    user = cam.get("username") or ""
    pw = cam.get("password") or ""
    return f"rtsp://{user}:{pw}@{ip}:554/Streaming/Channels/{ch}"


def _camera_auth(cam: dict) -> httpx.Auth | None:
    user = cam.get("username")
    pw = cam.get("password")
    if not user or not pw:
        return None
    auth = (cam.get("auth") or "digest").lower()
    if auth == "basic":
        return httpx.BasicAuth(user, pw)
    return httpx.DigestAuth(user, pw)


def get_cameras() -> list[dict]:
    # MVP: local worker endpoint returns creds
    with httpx.Client(timeout=5.0) as c:
        r = c.get(f"{S.API_BASE_URL}/worker/cameras")
        r.raise_for_status()
        return r.json()


def main():
    prev_by_url: dict[str, bytes] = {}

    while True:
        try:
            cams = get_cameras()
        except Exception as e:
            print(f"[worker] Could not fetch cameras: {e}")
            cams = []

        # legacy env fallback
        urls = parse_urls(S.CAMERA_SNAPSHOT_URLS)
        legacy = [{"ip": None, "snapshot_url": u} for u in urls]

        if not cams and not legacy:
            print("[worker] No cameras configured yet.")

        for cam in cams:
            # Prefer RTSP for broad camera compatibility.
            if int(S.PREFER_RTSP) == 1:
                rtsp = _camera_rtsp_url(cam)
                cur = fetch_rtsp_frame(rtsp)
                key = rtsp
            else:
                url = _camera_snapshot_url(cam)
                auth = _camera_auth(cam)
                cur = fetch_snapshot_bytes(url, auth=auth, verify=False)
                key = url

            prev = prev_by_url.get(key)
            label, conf = motion_detect(prev, cur)
            prev_by_url[key] = cur or prev_by_url.get(key) or b""

            if conf <= 0.01:
                continue

            snap_b64 = jpeg_b64(cur)
            try:
                res = post_detection(key, label, conf, snap_b64)
                trig = res.get("triggered", [])
                if trig:
                    print(f"[worker] Triggered {len(trig)} alert(s) for {cam.get('ip')} label={label} conf={conf:.2f}")
            except Exception as e:
                print(f"[worker] Error posting detection for {cam.get('ip')}: {e}")

        # legacy URLs (no auth)
        for l in legacy:
            u = l["snapshot_url"]

            cur = fetch_snapshot_bytes(u)
            prev = prev_by_url.get(u)
            label, conf = motion_detect(prev, cur)
            prev_by_url[u] = cur or prev_by_url.get(u) or b""

            if conf <= 0.01:
                continue

            snap_b64 = jpeg_b64(cur)
            try:
                res = post_detection(u, label, conf, snap_b64)
                trig = res.get("triggered", [])
                if trig:
                    print(f"[worker] Triggered {len(trig)} alert(s) for {u} label={label} conf={conf:.2f}")
            except Exception as e:
                print(f"[worker] Error posting detection for {u}: {e}")

        time.sleep(max(1, int(S.POLL_INTERVAL_SEC)))


if __name__ == "__main__":
    main()
