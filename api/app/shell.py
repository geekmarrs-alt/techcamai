"""
TECHCAMAI product shell — edition detection and feature gating.

This module is the single integration point for commercial features.
Import from here when adding auth checks, edition gates, or camera-limit enforcement.

Current state: Community / Developer Preview — no gates enforced.
When Operator Pro is ready, this module reads TECHCAMAI_LICENSE_KEY and validates it.
All call sites stay the same; only this module changes.

See docs/PRODUCT_SHELL.md for the full commercial-tier spec.
"""

import hashlib
import os
from enum import Enum
from functools import lru_cache


class Edition(str, Enum):
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Features gated by edition. Value = minimum edition required.
_FEATURE_GATES: dict[str, Edition] = {
    "unlimited_cameras": Edition.PRO,
    "email_alerts": Edition.PRO,
    "webhook_alerts": Edition.PRO,
    "clip_retention_config": Edition.PRO,
    "rule_templates": Edition.PRO,
    "scheduled_suppression": Edition.PRO,
    "multi_site": Edition.ENTERPRISE,
    "fleet_dashboard": Edition.ENTERPRISE,
    "api_access": Edition.ENTERPRISE,
}

_EDITION_RANK: dict[Edition, int] = {
    Edition.COMMUNITY: 0,
    Edition.PRO: 1,
    Edition.ENTERPRISE: 2,
}

CAMERA_LIMIT_COMMUNITY = 4


@lru_cache(maxsize=1)
def current_edition() -> Edition:
    """Return the active edition based on TECHCAMAI_LICENSE_KEY env var.

    Validation logic:
    - Demo key 'TCAI-DEMO-2026' -> PRO
    - Format 'TCAM-XXXX-XXXX-XXXX'
    - Checksum: segment4 == SHA256('TCAM-' + segment2 + '-' + segment3 + salt)[:4]
    - Edition: segment2 starts with PRO -> PRO, ENT -> ENTERPRISE
    """
    key = os.environ.get("TECHCAMAI_LICENSE_KEY", "").strip().upper()
    if not key:
        return Edition.COMMUNITY

    if key == "TCAI-DEMO-2026":
        return Edition.PRO

    parts = key.split("-")
    if len(parts) != 4 or parts[0] != "TCAM":
        return Edition.COMMUNITY

    # TCAM-XXXX-XXXX-XXXX
    # 0    1    2    3
    segment2 = parts[1]
    segment3 = parts[2]
    segment4 = parts[3]

    salt = "TECHCAMAI-LICENSE-SALT-2026"
    payload = f"TCAM-{segment2}-{segment3}{salt}"
    expected_checksum = hashlib.sha256(payload.encode()).hexdigest()[:4].upper()

    if segment4 != expected_checksum:
        return Edition.COMMUNITY

    if segment2.startswith("ENT"):
        return Edition.ENTERPRISE
    if segment2.startswith("PRO"):
        return Edition.PRO

    return Edition.COMMUNITY


def feature_allowed(feature: str) -> bool:
    """Return True if the current edition permits the named feature."""
    gate = _FEATURE_GATES.get(feature)
    if gate is None:
        return True  # unknown features are not gated
    return _EDITION_RANK[current_edition()] >= _EDITION_RANK[gate]


def camera_limit() -> int | None:
    """Return max cameras for current edition, or None for unlimited."""
    if current_edition() == Edition.COMMUNITY:
        return CAMERA_LIMIT_COMMUNITY
    return None


def edition_label() -> str:
    """Return a human-readable edition label for display in the UI."""
    labels = {
        Edition.COMMUNITY: "Developer Preview",
        Edition.PRO: "Operator Pro",
        Edition.ENTERPRISE: "Enterprise",
    }
    return labels[current_edition()]
