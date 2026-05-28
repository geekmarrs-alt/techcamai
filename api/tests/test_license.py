import os
import unittest
from unittest.mock import patch
from app.shell import current_edition, Edition

class TestLicenseValidation(unittest.TestCase):

    def setUp(self):
        # Clear lru_cache before each test to ensure fresh evaluation
        current_edition.cache_clear()

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": ""})
    def test_missing_key(self):
        self.assertEqual(current_edition(), Edition.COMMUNITY)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAI-DEMO-2026"})
    def test_demo_key(self):
        self.assertEqual(current_edition(), Edition.PRO)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "tcai-demo-2026"})
    def test_demo_key_lowercase(self):
        self.assertEqual(current_edition(), Edition.PRO)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAM-PRO1-1234-DDBE"})
    def test_valid_pro_key(self):
        self.assertEqual(current_edition(), Edition.PRO)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAM-ENT1-5678-B568"})
    def test_valid_enterprise_key(self):
        self.assertEqual(current_edition(), Edition.ENTERPRISE)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAM-PRO1-1234-XXXX"})
    def test_invalid_checksum(self):
        self.assertEqual(current_edition(), Edition.COMMUNITY)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "BOGUS-KEY"})
    def test_invalid_format(self):
        self.assertEqual(current_edition(), Edition.COMMUNITY)

    @patch.dict(os.environ, {"TECHCAMAI_LICENSE_KEY": "TCAM-XXX1-1234-F165"})
    def test_unknown_prefix(self):
        # Valid checksum for TCAM-XXX1-1234 is F165
        # (calculated via: python3 -c "import hashlib; print(hashlib.sha256('TCAM-XXX1-1234TECHCAMAI-LICENSE-SALT-2026'.encode()).hexdigest()[:4].upper())")
        self.assertEqual(current_edition(), Edition.COMMUNITY)
