import os
import unittest
from unittest.mock import patch
from amazon_tracking import affiliate_link, attribution_metadata

class AmazonTrackingTests(unittest.TestCase):
    def test_not_approved(self):
        with patch.dict(os.environ, {}, clear=False):
            with self.assertRaises(ValueError):
                affiliate_link("https://www.amazon.com.br/s?k=carregador")
    def test_attribution_not_sales(self):
        self.assertEqual(attribution_metadata("ev-accessories")["sales_confirmed"], 0)

if __name__ == "__main__":
    unittest.main()
