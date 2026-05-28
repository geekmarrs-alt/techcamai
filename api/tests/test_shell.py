import os
from unittest.mock import patch
from app.shell import Edition, current_edition, feature_allowed, camera_limit, edition_label

def test_current_edition_no_key():
    with patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": ""}):
        assert current_edition() == Edition.COMMUNITY

def test_current_edition_with_key_still_community():
    # Current implementation always returns COMMUNITY even with a key
    with patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAM-ANY-KEY"}):
        assert current_edition() == Edition.COMMUNITY

def test_feature_allowed_community():
    with patch("app.shell.current_edition", return_value=Edition.COMMUNITY):
        # Unknown features allowed
        assert feature_allowed("unknown_feature") is True
        # Community features (none explicitly gated higher than community yet that are not gated at all)
        # Actually any feature NOT in _FEATURE_GATES returns True.
        # Features in _FEATURE_GATES:
        assert feature_allowed("unlimited_cameras") is False
        assert feature_allowed("multi_site") is False

def test_feature_allowed_pro():
    with patch("app.shell.current_edition", return_value=Edition.PRO):
        assert feature_allowed("unlimited_cameras") is True
        assert feature_allowed("email_alerts") is True
        assert feature_allowed("multi_site") is False

def test_feature_allowed_enterprise():
    with patch("app.shell.current_edition", return_value=Edition.ENTERPRISE):
        assert feature_allowed("unlimited_cameras") is True
        assert feature_allowed("multi_site") is True
        assert feature_allowed("fleet_dashboard") is True

def test_camera_limit():
    with patch("app.shell.current_edition", return_value=Edition.COMMUNITY):
        assert camera_limit() == 4

    with patch("app.shell.current_edition", return_value=Edition.PRO):
        assert camera_limit() is None

    with patch("app.shell.current_edition", return_value=Edition.ENTERPRISE):
        assert camera_limit() is None

def test_edition_label():
    with patch("app.shell.current_edition", return_value=Edition.COMMUNITY):
        assert edition_label() == "Developer Preview"

    with patch("app.shell.current_edition", return_value=Edition.PRO):
        assert edition_label() == "Operator Pro"

    with patch("app.shell.current_edition", return_value=Edition.ENTERPRISE):
        assert edition_label() == "Enterprise"
