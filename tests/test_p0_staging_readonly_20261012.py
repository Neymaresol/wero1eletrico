"""Read-only staging endpoint checks. Never writes to the database."""
import json
import os
import unittest
from urllib.request import urlopen

BASE = os.getenv("WERO_ELETRICO_STAGING_URL", "").rstrip("/")

@unittest.skipUnless(BASE, "WERO_ELETRICO_STAGING_URL not set")
class StagingSmoke(unittest.TestCase):
    def get(self, path):
        with urlopen(BASE + path, timeout=15) as response:
            self.assertEqual(response.status, 200)
            return json.load(response)

    def test_health(self):
        self.assertEqual(self.get("/health").get("status"), "ok")

    def test_offers_do_not_expose_unapproved_links(self):
        data = self.get("/api/storefront/offers")
        self.assertIsInstance(data.get("offers"), list)
        self.assertFalse(data.get("affiliate_urls_exposed", False))

if __name__ == "__main__":
    unittest.main()
