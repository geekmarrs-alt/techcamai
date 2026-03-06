from __future__ import annotations

import asyncio
import ipaddress
import json
import subprocess
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional

import httpx


@dataclass
class DiscoveredDevice:
    ip: str
    ports: List[int]
    vendor_hint: Optional[str] = None
    hikvision_isapi: bool = False
    onvif_hint: bool = False


def _local_ipv4_networks() -> List[ipaddress.IPv4Network]:
    """Best-effort: derive directly-connected IPv4 networks from `ip -j addr`.

    We intentionally avoid default-route guessing. Only networks actually configured
    on interfaces are returned.
    """
    try:
        out = subprocess.check_output(["ip", "-j", "addr"], text=True)
        data = json.loads(out)
    except Exception:
        return []

    nets: List[ipaddress.IPv4Network] = []
    for iface in data:
        for a in iface.get("addr_info", []) or []:
            if a.get("family") != "inet":
                continue
            local = a.get("local")
            prefixlen = a.get("prefixlen")
            if not local or prefixlen is None:
                continue
            ip = ipaddress.IPv4Address(local)
            # skip loopback/link-local
            if ip.is_loopback or ip.is_link_local:
                continue
            net = ipaddress.IPv4Network(f"{local}/{prefixlen}", strict=False)
            # skip /32 host routes
            if net.prefixlen == 32:
                continue
            nets.append(net)

    # de-dupe
    uniq = []
    seen = set()
    for n in nets:
        if n.with_prefixlen in seen:
            continue
        seen.add(n.with_prefixlen)
        uniq.append(n)
    return uniq


async def _tcp_connect(ip: str, port: int, timeout: float) -> bool:
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except Exception:
        return False


async def _probe_hik_isapi(client: httpx.AsyncClient, ip: str) -> bool:
    # Hikvision ISAPI tends to return 401 with WWW-Authenticate realm=... when unauth.
    # We accept any response that looks like ISAPI.
    urls = [
        f"http://{ip}/ISAPI/System/deviceInfo",
        f"http://{ip}/ISAPI/Streaming/channels/1/picture",
    ]
    for u in urls:
        try:
            r = await client.get(u)
            if r.status_code in (200, 401, 403):
                if "ISAPI" in (r.headers.get("server") or "") or "Hikvision" in (r.text or ""):
                    return True
                # some firmwares don't advertise; treat common ISAPI paths as hint if not 404
                if r.status_code != 404:
                    return True
        except Exception:
            continue
    return False


async def discover(timeout_sec: int = 120, max_hosts: int = 2048) -> List[DiscoveredDevice]:
    """Zero-config discovery.

    MVP approach:
    - derive local interface networks
    - sweep common ports
    - probe for Hikvision ISAPI hints

    NOTE: ONVIF WS-Discovery multicast should be added next; this is the safe fallback.
    """

    nets = _local_ipv4_networks()
    if not nets:
        return []

    # Flatten hosts (cap to max_hosts to avoid melting /16s)
    hosts: List[str] = []
    for n in nets:
        for h in n.hosts():
            hosts.append(str(h))
            if len(hosts) >= max_hosts:
                break
        if len(hosts) >= max_hosts:
            break

    ports_to_check = [80, 443, 554, 8000]
    per_connect_timeout = 0.35

    async with httpx.AsyncClient(timeout=2.0, follow_redirects=True) as client:
        sem = asyncio.Semaphore(500)

        async def scan_host(ip: str) -> Optional[DiscoveredDevice]:
            async with sem:
                open_ports = []
                for p in ports_to_check:
                    if await _tcp_connect(ip, p, per_connect_timeout):
                        open_ports.append(p)

                if not open_ports:
                    return None

                dev = DiscoveredDevice(ip=ip, ports=open_ports)
                if 80 in open_ports or 8000 in open_ports:
                    dev.hikvision_isapi = await _probe_hik_isapi(client, ip)
                    if dev.hikvision_isapi:
                        dev.vendor_hint = "hikvision"

                # crude ONVIF hint: RTSP open often correlates, but not definitive
                if 554 in open_ports:
                    dev.onvif_hint = True

                return dev

        tasks = [scan_host(ip) for ip in hosts]
        results: List[DiscoveredDevice] = []

        try:
            for coro in asyncio.as_completed(tasks, timeout=float(timeout_sec)):
                r = await coro
                if r:
                    results.append(r)
        except TimeoutError:
            pass

    # Sort: Hikvision first, then by IP
    results.sort(key=lambda d: (0 if d.vendor_hint == "hikvision" else 1, d.ip))
    return results


def discover_sync(timeout_sec: int = 120) -> List[dict]:
    return [asdict(d) for d in asyncio.run(discover(timeout_sec=timeout_sec))]
