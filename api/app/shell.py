"""
TECHCAMAI product shell — edition detection and feature gating.

This module is the single integration point for commercial features.
Import from here when adding auth checks, edition gates, or camera-limit enforcement.

Current state: Community / Developer Preview — no gates enforced.
When Operator Pro is ready, this module reads TECHCAMAI_LICENSE_KEY and validates it.
All call sites stay the same; only this module changes.

See docs/PRODUCT_SHELL.md for the full commercial-tier spec.
"""

import os
from enum import Enum


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


def current_edition() -> Edition:
    """Return the active edition based on TECHCAMAI_LICENSE_KEY env var.

    Currently always returns COMMUNITY — license validation not yet implemented.
    When ready: validate key format and signature here.
    Key format: TCAM-XXXX-XXXX-XXXX
    """
    key = os.environ.get("TECHCAMAI_LICENSE_KEY", "").strip()
    if not key:
        return Edition.COMMUNITY
    # TODO: implement key validation — for now any key value still returns COMMUNITY
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
