import os
import pytest
from app.shell import current_edition, Edition, _DEMO_KEY

def test_edition_community_by_default():
    if "TECHCAMAI_LICENSE_KEY" in os.environ:
        del os.environ["TECHCAMAI_LICENSE_KEY"]
    assert current_edition() == Edition.COMMUNITY

def test_edition_community_invalid_format():
    os.environ["TECHCAMAI_LICENSE_KEY"] = "INVALID-KEY"
    assert current_edition() == Edition.COMMUNITY

def test_edition_community_invalid_checksum():
    # Correct format, but wrong checksum (S4)
    os.environ["TECHCAMAI_LICENSE_KEY"] = "TCAM-PRO1-0001-0000"
    assert current_edition() == Edition.COMMUNITY

def test_edition_pro_demo_key():
    os.environ["TECHCAMAI_LICENSE_KEY"] = _DEMO_KEY
    assert current_edition() == Edition.PRO

def test_edition_pro_valid_key():
    # TCAM-PRO1-0001-4E89 is valid for PRO (calculated manually)
    os.environ["TECHCAMAI_LICENSE_KEY"] = "TCAM-PRO1-0001-4E89"
    assert current_edition() == Edition.PRO

def test_edition_enterprise_valid_key():
    # TCAM-ENT1-0001-D73D is valid for ENTERPRISE (calculated manually)
    os.environ["TECHCAMAI_LICENSE_KEY"] = "TCAM-ENT1-0001-D73D"
    assert current_edition() == Edition.ENTERPRISE

def test_edition_community_unknown_prefix():
    # Valid checksum but unknown segment prefix (not PRO or ENT)
    # Payload: TCAM-UNK1-0001 + salt
    import hashlib
    salt = "TECHCAMAI-LICENSE-SALT-2026"
    payload = f"TCAM-UNK1-0001{salt}"
    checksum = hashlib.sha256(payload.encode()).hexdigest()[:4].upper()

    os.environ["TECHCAMAI_LICENSE_KEY"] = f"TCAM-UNK1-0001-{checksum}"
    assert current_edition() == Edition.COMMUNITY
